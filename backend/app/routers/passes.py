from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.audit import log_audit
from app.core.clock import business_today
from app.core.codes import generate_receipt_number
from app.core.config import settings
from app.core.database import get_db
from app.core.dates import add_months
from app.core.pass_status import live_status
from app.core.pass_token import make_pass_token
from app.core.spots import pick_free_spot
from app.models import Company, MonthlyCustomer, ParkingPass, Payment, Vehicle
from app.models.enums import AuditAction, PassStatus, PassType, PaymentMethod, VehicleType
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
    """The established PER-MONTH rate — never multiplied by month count.
    An existing company rate always wins; `override` only matters the first
    time a brand-new monthly company is set up."""
    if existing_monthly_price is not None:
        return existing_monthly_price
    if override is not None:
        return override
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
        return settings.weekly_price
    # Monthly: customers sometimes pay for several months at once (2, 3+) —
    # the total is the per-month rate times how many months this pass spans.
    rate = _monthly_rate_for(existing_monthly_price, override)
    return rate * _months_between(issue_date, expiration_date)


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
    # Monthly customers are sticky: their previous spot is preferred if free.
    prefer = None
    if pass_type == PassType.monthly:
        prefer = db.scalar(
            select(ParkingPass.spot_id)
            .where(ParkingPass.company_id == company.id, ParkingPass.spot_id.is_not(None))
            .order_by(ParkingPass.id.desc())
            .limit(1)
        )
    # Full lot: never block a paid pass over space — spot stays NULL and the
    # dashboard surfaces it for staff (the kiosk pre-checks capacity, so this
    # is a rare race, not a normal flow).
    spot = pick_free_spot(db, prefer_spot_id=prefer)

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

    # QR encodes a signed verify URL (needs the id, so set after flush). A
    # guard scans it with any phone camera and lands on a live status page.
    parking_pass.qr_code = f"{settings.public_base_url}/verify/{make_pass_token(parking_pass.id)}"

    payment = Payment(
        parking_pass_id=parking_pass.id,
        amount=price,
        method=payment_method,
        check_number=check_number,
        stripe_payment_intent_id=stripe_payment_intent_id,
        receipt_number=generate_receipt_number("PMT", issue_date),
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

    log_audit(
        db,
        AuditAction.created,
        "parking_pass",
        f"Issued {pass_type.value} pass for {company.name} (truck {truck_number or '—'})",
        entity_id=parking_pass.id,
    )

    db.commit()
    db.refresh(parking_pass)
    return parking_pass


@router.post("", response_model=PassRead)
def issue_pass(payload: IssuePassRequest, db: Session = Depends(get_db)) -> ParkingPass:
    _validate_weekly_span(payload.pass_type, payload.issue_date, payload.end_date)
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
    )


def renewal_quote(db: Session, parking_pass: ParkingPass, end_date: date) -> tuple[date, float]:
    """Validates a proposed renewal and returns (renewal_start, price) WITHOUT
    applying it. Shared by the direct renew endpoint and the customer-self-pay
    payment-request path so both price/validate renewals identically. Raises
    HTTPException(400) on an invalid date/span."""
    # Renew from today if the pass already lapsed (so a stale expiration
    # doesn't push the new period further into the past) — otherwise continue
    # seamlessly from the current expiration.
    renewal_start = max(business_today(), parking_pass.expiration_date)

    if end_date <= renewal_start:
        raise HTTPException(status_code=400, detail=f"New expiration must be after {renewal_start.isoformat()}.")

    if parking_pass.pass_type == PassType.weekly:
        span = (end_date - renewal_start).days
        if span != 7:
            raise HTTPException(
                status_code=400,
                detail=f"Weekly passes must be exactly 7 days ({renewal_start.isoformat()} → {end_date.isoformat()} is {span} days).",
            )

    monthly_customer = None
    if parking_pass.pass_type == PassType.monthly:
        monthly_customer = db.scalar(
            select(MonthlyCustomer).where(MonthlyCustomer.company_id == parking_pass.company_id)
        )
    price = _price_for(
        parking_pass.pass_type,
        renewal_start,
        end_date,
        None,
        monthly_customer.monthly_price if monthly_customer else None,
    )
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
        _, price = renewal_quote(db, parking_pass, end_date)

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
            monthly_customer.reminder_status = "pending"

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


@router.post("/{pass_id}/renew", response_model=PassRead)
def renew_pass(pass_id: int, payload: RenewPassRequest, db: Session = Depends(get_db)) -> ParkingPass:
    parking_pass = db.get(ParkingPass, pass_id)
    if parking_pass is None:
        raise HTTPException(status_code=404, detail="Pass not found")
    return apply_renewal(db, parking_pass, payload.end_date, payload.payment_method, payload.check_number)


@router.post("/{pass_id}/cancel", response_model=PassRead)
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


@router.get("", response_model=list[PassListItem])
def list_passes(db: Session = Depends(get_db)) -> list[PassListItem]:
    today = business_today()
    stmt = select(ParkingPass).order_by(ParkingPass.issue_date.desc(), ParkingPass.id.desc())
    return [
        PassListItem(
            id=p.id,
            pass_type=p.pass_type,
            status=live_status(p.expiration_date, today, p.status),
            price=p.price,
            issue_date=p.issue_date,
            expiration_date=p.expiration_date,
            receipt_number=p.receipt_number,
            qr_code=p.qr_code,
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


@router.get("/{pass_id}", response_model=PassRead)
def get_pass(pass_id: int, db: Session = Depends(get_db)) -> ParkingPass:
    parking_pass = db.get(ParkingPass, pass_id)
    if parking_pass is None:
        raise HTTPException(status_code=404, detail="Pass not found")
    return parking_pass
