from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.audit import log_audit
from app.core.clock import business_now, business_today
from app.core.codes import generate_receipt_number
from app.core.config import settings
from app.core.database import get_db
from app.core.deps import require_manager
from app.core.dates import add_months
from app.core.pass_status import live_status
from app.core.spots import pick_free_spot, release_reserved_spot
from app.models import Company, MonthlyCustomer, ParkingPass, Payment, Spot, Vehicle
from app.models.enums import (
    AuditAction,
    MonthlyCustomerStatus,
    PassStatus,
    PassType,
    PaymentMethod,
    ReminderStatus,
    VehicleType,
)
from app.schemas.pass_ import IssuePassRequest, PassListItem, PassRead, RenewPassRequest

router = APIRouter(prefix="/api/passes", tags=["passes"])


def _expiration_for(pass_type: PassType, issue_date: date, end_date: date | None) -> date:
    if end_date is not None:
        return end_date
    if pass_type == PassType.daily:
        return issue_date + timedelta(days=1)
    if pass_type == PassType.weekly:
        return issue_date + timedelta(days=7)
    return add_months(issue_date, 1)


def _months_between(start: date, end: date) -> int:
    """Whole calendar months between two dates, rounding UP for any partial
    overage (7/5 -> 8/5 = 1, 7/5 -> 9/5 = 2, 7/5 -> 8/6 = 2 — one day past a
    full month starts a new billing month), never below 1."""
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day > start.day:
        months += 1
    return max(months, 1)


def _monthly_rate_for(existing_monthly_price: float | None, override: float | None) -> float:
    """The PER-MONTH rate for THIS truck — never multiplied by month count. Each
    truck of a company is priced on its OWN (SX Express: truck 1325 $250, 1236
    $210, 1397 $200; the company pays the sum), so a price the cashier types
    ALWAYS wins. The company's on-file rate is only a fallback when no price is
    entered for the truck, and the global default is the last resort."""
    if override is not None:
        return override
    if existing_monthly_price is not None:
        return existing_monthly_price
    return settings.monthly_price


def _price_for(
    pass_type: PassType,
    issue_date: date,
    expiration_date: date,
    override: float | None,
    existing_monthly_price: float | None = None,
) -> float:
    if pass_type == PassType.daily:
        days = max((expiration_date - issue_date).days, 1)
        return settings.daily_price * days
    if pass_type == PassType.weekly:
        # Per whole week — a single-week renewal (the common case) is unchanged;
        # a multi-week catch-up on a lapsed weekly bills each week.
        weeks = max((expiration_date - issue_date).days // 7, 1)
        return settings.weekly_price * weeks
    # Monthly: customers sometimes pay for several months at once (2, 3+) —
    # the total is the per-month rate times how many months this pass spans.
    rate = _monthly_rate_for(existing_monthly_price, override)
    return rate * _months_between(issue_date, expiration_date)


def _whole_months(start: date, end: date) -> int:
    """COMPLETE calendar months from start to end (floors — unlike _months_between,
    which rounds up for billing). Aug 8 -> Sep 11 is 1 whole month; the extra 3
    days are leftover."""
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        months -= 1
    return max(months, 0)


def _close_out_price(pass_type: PassType, start: date, end: date, existing_monthly_price: float | None) -> float:
    """A departing customer pays for time ACTUALLY used: whole periods at the
    period rate + leftover days at the daily rate. The leftover is capped at one
    more period's rate, so closing out never costs more than just continuing."""
    if pass_type == PassType.daily:
        return float(settings.daily_price) * max((end - start).days, 1)
    if pass_type == PassType.weekly:
        rate = float(settings.weekly_price)
        whole, leftover_days = divmod((end - start).days, 7)
    else:
        # mc.monthly_price is a DB Decimal; daily_price is a float — coerce so the
        # mixed arithmetic below doesn't TypeError.
        rate = float(_monthly_rate_for(existing_monthly_price, None))
        whole = _whole_months(start, end)
        leftover_days = (end - add_months(start, whole)).days
    leftover = min(leftover_days * float(settings.daily_price), rate)
    return whole * rate + leftover


def _validate_weekly_span(pass_type: PassType, issue_date: date, end_date: date | None) -> None:
    if pass_type == PassType.weekly and end_date is not None:
        span = (end_date - issue_date).days
        if span != 7:
            raise HTTPException(
                status_code=400,
                detail=f"Weekly passes must be exactly 7 days ({issue_date} → {end_date} is {span} days). Choose Daily for a custom range.",
            )


def _find_company(db: Session, name: str) -> Company | None:
    """Match a company by name case-insensitively, ignoring surrounding
    whitespace — the SAME normalization the company-profile lookup uses. Without
    this the freeform name a customer types at the kiosk/Stripe ("abc trucking")
    would miss the manager-created "ABC Trucking" and spawn a duplicate company,
    fragmenting its trucks, monthly rate, and history across two profiles."""
    # " ".join(split()) collapses runs of internal whitespace AND strips ends, so
    # "ABC  Trucking " and "abc trucking" resolve to the same company. Names are
    # stored canonicalized the same way on creation, so lower(column) always lines
    # up with this normalized input.
    return db.scalar(select(Company).where(func.lower(Company.name) == " ".join(name.split()).lower()))


def _find_or_create_vehicle(
    db: Session,
    company_id: int,
    vehicle_type: VehicleType,
    truck_number: str | None,
    trailer_number: str | None,
    license_plate: str | None,
) -> Vehicle:
    """Reuse the company's existing vehicle instead of inserting a new row every
    time the same truck comes back — otherwise visit-frequency, history, and the
    'all trucks under one company' counts fragment across duplicate vehicles.
    Matches on the strongest identifier provided (truck # > plate > trailer #),
    case-insensitive; falls back to creating one when nothing matches."""
    ident_field, ident_value = None, None
    if truck_number and truck_number.strip():
        ident_field, ident_value = Vehicle.truck_number, truck_number
    elif license_plate and license_plate.strip():
        ident_field, ident_value = Vehicle.license_plate, license_plate
    elif trailer_number and trailer_number.strip():
        ident_field, ident_value = Vehicle.trailer_number, trailer_number

    if ident_field is not None:
        existing = db.scalar(
            select(Vehicle).where(
                Vehicle.company_id == company_id,
                func.lower(func.trim(ident_field)) == ident_value.strip().lower(),
            )
        )
        if existing is not None:
            return existing

    vehicle = Vehicle(
        company_id=company_id,
        vehicle_type=vehicle_type,
        truck_number=truck_number,
        trailer_number=trailer_number,
        license_plate=license_plate,
    )
    db.add(vehicle)
    db.flush()
    return vehicle


def _lookup_monthly_rate(db: Session, company_name: str) -> float | None:
    """The company's established per-month rate, or None if it has no monthly
    plan on file yet (a brand-new monthly company — self-service checkouts,
    kiosk or Stripe, can never bootstrap a new rate; only the manager can)."""
    company = _find_company(db, company_name)
    if company is None:
        return None
    monthly_customer = db.scalar(select(MonthlyCustomer).where(MonthlyCustomer.company_id == company.id))
    return monthly_customer.monthly_price if monthly_customer else None


def _issue_pass_and_payment(
    db: Session,
    *,
    company_name: str,
    phone: str,
    vehicle_type: VehicleType,
    truck_number: str | None,
    trailer_number: str | None,
    license_plate: str | None,
    pass_type: PassType,
    issue_date: date,
    end_date: date | None,
    price_override: float | None,
    payment_method: PaymentMethod,
    check_number: str | None,
    stripe_payment_intent_id: str | None = None,
    price_from_charge: float | None = None,
    record_payment: bool = True,
    paid_on: date | None = None,
) -> ParkingPass:
    """Shared by the normal Issue Pass endpoint and the Stripe finalize/webhook
    endpoints — every code path that actually creates a pass + payment record
    goes through here, so pricing/monthly-customer logic can't drift between
    them.

    `price_from_charge`, when given, is used verbatim as the price instead of
    recomputing via `_price_for` — for a Stripe payment, the amount Stripe
    actually confirms it charged (`intent.amount_received`) IS the price by
    definition; there is no more authoritative number to recompute towards.
    """
    company = _find_company(db, company_name)
    monthly_customer = None
    if company is not None and pass_type == PassType.monthly:
        monthly_customer = db.scalar(select(MonthlyCustomer).where(MonthlyCustomer.company_id == company.id))
    if company is None:
        company = Company(name=" ".join(company_name.split()), phone=phone)
        db.add(company)
        db.flush()

    vehicle = _find_or_create_vehicle(
        db, company.id, vehicle_type, truck_number, trailer_number, license_plate
    )

    # Double-submit guard: a cashier double-click or a network retry must NEVER
    # issue the same truck twice and charge twice. If this exact truck already got
    # this same pass type today within the last few seconds, hand back that pass
    # instead of creating a second one. (The retired Stripe path is deduped by its
    # own unique intent-id constraint, so this only guards the manual desk issue.)
    if stripe_payment_intent_id is None:
        just_issued = db.scalar(
            select(ParkingPass)
            .where(
                ParkingPass.vehicle_id == vehicle.id,
                ParkingPass.pass_type == pass_type,
                ParkingPass.issue_date == issue_date,
                ParkingPass.created_at >= business_now() - timedelta(seconds=15),
            )
            .order_by(ParkingPass.id.desc())
        )
        if just_issued is not None:
            return just_issued

    expiration_date = _expiration_for(pass_type, issue_date, end_date)
    if price_from_charge is not None:
        price = price_from_charge
    else:
        price = _price_for(
            pass_type,
            issue_date,
            expiration_date,
            price_override,
            monthly_customer.monthly_price if monthly_customer else None,
        )
    receipt_number = generate_receipt_number("PASS", issue_date)

    # Assign the physical spot in the SAME transaction that records the money —
    # the pass is the source of truth for space exactly as it is for payment.
    # A monthly's stickiness (same spot every renewal) now comes from its spot
    # RESERVATION inside pick_free_spot, so no "prefer my last spot" hint is passed
    # here. Passing one would let a monthly's old, now-free DAILY spot win over its
    # Zone-A reserved spot — quietly dropping a monthly into the daily pool.
    # Full lot: never block a paid pass over space — spot stays NULL and the
    # dashboard surfaces it for staff (a rare race, not a normal flow).
    spot = pick_free_spot(db, pass_type, vehicle.id)

    parking_pass = ParkingPass(
        company_id=company.id,
        vehicle_id=vehicle.id,
        spot_id=spot.id if spot else None,
        pass_type=pass_type,
        status=PassStatus.active,
        price=price,
        issue_date=issue_date,
        expiration_date=expiration_date,
        receipt_number=receipt_number,
        barcode=truck_number or receipt_number,
    )
    db.add(parking_pass)
    db.flush()

    # Onboarding an already-paid customer records the pass but NOT the money, so
    # back-entry never lands in this month's revenue. A real sale (the default)
    # records the payment, optionally backdated to the day it was actually taken.
    if record_payment:
        payment = Payment(
            parking_pass_id=parking_pass.id,
            amount=price,
            method=payment_method,
            check_number=check_number,
            stripe_payment_intent_id=stripe_payment_intent_id,
            receipt_number=generate_receipt_number("PMT", issue_date),
            paid_at=datetime(paid_on.year, paid_on.month, paid_on.day, 12, 0) if paid_on else business_now(),
        )
        db.add(payment)

    if pass_type == PassType.monthly:
        if monthly_customer is None:
            monthly_customer = MonthlyCustomer(
                company_id=company.id,
                monthly_price=_monthly_rate_for(None, price_override),
                renewal_date=expiration_date,
                preferred_payment_method=payment_method,
            )
            db.add(monthly_customer)
        else:
            monthly_customer.renewal_date = expiration_date

    charge_note = "" if record_payment else " — no charge recorded (already paid)"
    log_audit(
        db,
        AuditAction.created,
        "parking_pass",
        f"Issued {pass_type.value} pass for {company.name} (truck {truck_number or '—'}){charge_note}",
        entity_id=parking_pass.id,
    )

    db.commit()
    db.refresh(parking_pass)
    return parking_pass


@router.post("", response_model=PassRead)
def issue_pass(payload: IssuePassRequest, db: Session = Depends(get_db)) -> ParkingPass:
    _validate_weekly_span(payload.pass_type, payload.issue_date, payload.end_date)
    if payload.paid_on is not None and payload.paid_on > business_today():
        raise HTTPException(status_code=400, detail="Payment date can't be in the future.")
    return _issue_pass_and_payment(
        db,
        company_name=payload.company_name,
        phone=payload.phone,
        vehicle_type=payload.vehicle_type,
        truck_number=payload.truck_number,
        trailer_number=payload.trailer_number,
        license_plate=payload.license_plate,
        pass_type=payload.pass_type,
        issue_date=payload.issue_date,
        end_date=payload.end_date,
        price_override=payload.price,
        payment_method=payload.payment_method,
        check_number=payload.check_number,
        record_payment=payload.record_payment,
        paid_on=payload.paid_on,
    )


def renewal_quote(
    db: Session, parking_pass: ParkingPass, end_date: date, mode: str = "continue"
) -> tuple[date, float]:
    """Validates a proposed renewal and returns (renewal_start, price) WITHOUT
    applying it. `mode` is "continue" (keep the plan going — whole periods) or
    "close_out" (the customer is leaving — pay for the exact time used, then the
    account closes). Raises HTTPException(400) on an invalid date/span."""
    # A renewal always continues from where the last pass ended — never from
    # "today," even when the customer pays late. A loyal customer whose spot was
    # held keeps paying from the old end date, with no free gap (client rule,
    # 2026-08). The end date the caller passes decides how far it runs.
    renewal_start = parking_pass.expiration_date

    if end_date <= renewal_start:
        raise HTTPException(status_code=400, detail=f"New expiration must be after {renewal_start.isoformat()}.")

    monthly_price = None
    if parking_pass.pass_type == PassType.monthly:
        # Per-truck pricing: this truck renews at ITS OWN rate, taken from the pass
        # being renewed (its price spread over its term), never a company-wide rate.
        term_months = _months_between(parking_pass.issue_date, parking_pass.expiration_date)
        monthly_price = float(parking_pass.price) / term_months

    if mode == "close_out":
        # A departing customer settles for the exact days used — any end date is
        # allowed (no whole-period requirement).
        return renewal_start, _close_out_price(parking_pass.pass_type, renewal_start, end_date, monthly_price)

    # continue: a weekly renewal lands on a whole number of weeks (a lapsed weekly
    # can catch up several).
    if parking_pass.pass_type == PassType.weekly:
        span = (end_date - renewal_start).days
        if span % 7 != 0:
            raise HTTPException(
                status_code=400,
                detail=f"Weekly renewals must be whole weeks ({renewal_start.isoformat()} → {end_date.isoformat()} is {span} days).",
            )
    # continue: a monthly renewal lands on a whole number of months from the old
    # end. Month arithmetic clamps (Jan 31 -> Feb 28 still counts as one month), so
    # probe forward instead of diffing days. Without this, a partial-month end date
    # is billed rounded UP (46 days -> 2 months) while granting only ~1.5.
    if parking_pass.pass_type == PassType.monthly:
        k = 1
        while k < 120 and add_months(renewal_start, k) < end_date:
            k += 1
        if add_months(renewal_start, k) != end_date:
            raise HTTPException(
                status_code=400,
                detail=f"Monthly renewals must run in whole months from {renewal_start.isoformat()} "
                f"(e.g. {add_months(renewal_start, 1).isoformat()} or {add_months(renewal_start, 2).isoformat()}). "
                "To settle a partial month, close the truck out instead.",
            )
    price = _price_for(parking_pass.pass_type, renewal_start, end_date, None, monthly_price)
    return renewal_start, price


def apply_renewal(
    db: Session,
    parking_pass: ParkingPass,
    end_date: date,
    payment_method: PaymentMethod,
    check_number: str | None = None,
    *,
    stripe_payment_intent_id: str | None = None,
    price_from_charge: float | None = None,
    mode: str = "continue",
) -> ParkingPass:
    """Applies a validated renewal: extends the pass, records a Payment, and
    updates the monthly customer. `price_from_charge` (a real Stripe amount)
    wins over the recomputed quote when present — same rule as issue."""
    # For a Stripe renewal the customer has ALREADY been charged an amount that
    # was locked when the payment request was created. Re-running renewal_quote
    # here would re-validate the date/span AFTER the charge, and its "renew from
    # today" floor can shift between link-creation and payment (e.g. a weekly span
    # is no longer exactly 7 days a day later), raising 400 and leaving the
    # customer charged with no pass. Trust the amount actually paid instead.
    if price_from_charge is not None:
        price = price_from_charge
    else:
        _, price = renewal_quote(db, parking_pass, end_date, mode)

    parking_pass.expiration_date = end_date
    parking_pass.price = price
    parking_pass.status = PassStatus.active

    db.add(
        Payment(
            parking_pass_id=parking_pass.id,
            amount=price,
            method=payment_method,
            check_number=check_number,
            stripe_payment_intent_id=stripe_payment_intent_id,
            receipt_number=generate_receipt_number("PMT", business_today()),
        )
    )

    if parking_pass.pass_type == PassType.monthly:
        monthly_customer = db.scalar(
            select(MonthlyCustomer).where(MonthlyCustomer.company_id == parking_pass.company_id)
        )
        if monthly_customer is not None:
            monthly_customer.renewal_date = end_date
            if mode == "close_out":
                # Per-truck close-out: THIS truck leaves and its reserved spot goes
                # back to the pool for anyone. A company with several trucks keeps
                # its account and its other trucks' spots — only when the LAST
                # monthly truck is closed out does the account go inactive. Every
                # active monthly truck holds a reserved spot, so a reservation on
                # ANY of the company's OTHER vehicles means it's still a going
                # concern (SA Express drops truck 123; trucks 345/1266/983 stay).
                release_reserved_spot(db, parking_pass.vehicle_id)
                other_trucks_left = db.scalar(
                    select(func.count())
                    .select_from(Spot)
                    .join(Vehicle, Spot.reserved_vehicle_id == Vehicle.id)
                    .where(
                        Vehicle.company_id == parking_pass.company_id,
                        Vehicle.id != parking_pass.vehicle_id,
                    )
                )
                if other_trucks_left:
                    monthly_customer.reminder_status = ReminderStatus.pending
                else:
                    monthly_customer.status = MonthlyCustomerStatus.inactive
                    monthly_customer.reminder_status = ReminderStatus.stopped
            else:
                monthly_customer.reminder_status = ReminderStatus.pending

    log_audit(
        db,
        AuditAction.renewed,
        "parking_pass",
        f"Renewed pass #{parking_pass.id} to {end_date.isoformat()} for {price:.2f}",
        entity_id=parking_pass.id,
    )
    db.commit()
    db.refresh(parking_pass)
    return parking_pass


@router.post("/{pass_id}/renew", response_model=PassRead, dependencies=[Depends(require_manager)])
def renew_pass(pass_id: int, payload: RenewPassRequest, db: Session = Depends(get_db)) -> ParkingPass:
    parking_pass = db.get(ParkingPass, pass_id)
    if parking_pass is None:
        raise HTTPException(status_code=404, detail="Pass not found")
    return apply_renewal(db, parking_pass, payload.end_date, payload.payment_method, payload.check_number, mode=payload.mode)


@router.post("/{pass_id}/cancel", response_model=PassRead, dependencies=[Depends(require_manager)])
def cancel_pass(pass_id: int, db: Session = Depends(get_db)) -> ParkingPass:
    """Removes a truck from a monthly plan (or cancels any pass) without
    deleting its history — payments and audit entries are never deleted."""
    parking_pass = db.get(ParkingPass, pass_id)
    if parking_pass is None:
        raise HTTPException(status_code=404, detail="Pass not found")

    parking_pass.status = PassStatus.cancelled

    log_audit(
        db,
        AuditAction.cancelled,
        "parking_pass",
        f"Cancelled pass #{parking_pass.id}",
        entity_id=parking_pass.id,
    )

    db.commit()
    db.refresh(parking_pass)
    return parking_pass


@router.get("", response_model=list[PassListItem], dependencies=[Depends(require_manager)])
def list_passes(db: Session = Depends(get_db)) -> list[PassListItem]:
    now = business_now()
    stmt = select(ParkingPass).order_by(ParkingPass.issue_date.desc(), ParkingPass.id.desc())
    return [
        PassListItem(
            id=p.id,
            pass_type=p.pass_type,
            status=live_status(p.pass_type, p.expiration_date, now, p.status),
            price=p.price,
            issue_date=p.issue_date,
            expiration_date=p.expiration_date,
            receipt_number=p.receipt_number,
            spot_number=p.spot_number,
            spot_label=p.spot_label,
            company_name=p.company.name if p.company else None,
            company_id=p.company_id,
            truck_number=p.vehicle.truck_number,
            trailer_number=p.vehicle.trailer_number,
            license_plate=p.vehicle.license_plate,
        )
        for p in db.scalars(stmt)
    ]


@router.get("/{pass_id}", response_model=PassRead, dependencies=[Depends(require_manager)])
def get_pass(pass_id: int, db: Session = Depends(get_db)) -> ParkingPass:
    parking_pass = db.get(ParkingPass, pass_id)
    if parking_pass is None:
        raise HTTPException(status_code=404, detail="Pass not found")
    return parking_pass
