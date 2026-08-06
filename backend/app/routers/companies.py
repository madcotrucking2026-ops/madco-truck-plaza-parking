from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from datetime import date

from app.core.clock import business_now, business_today
from app.core.database import get_db
from app.core.deps import get_current_user, require_manager
from app.core.pass_status import live_status
from app.core.rate_limit import lookup_limiter
from app.core.spots import spot_label
from app.models import Company, MonthlyCustomer, ParkingPass, Payment, Spot, User, Vehicle
from app.models.enums import PassStatus, PassType
from app.schemas.company import (
    CompanyCreate,
    CompanyLookupResult,
    CompanyMonthlyTruck,
    CompanyProfile,
    CompanyRead,
    ProfilePass,
    ProfilePayment,
    ProfileTruck,
)

router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.get("", response_model=list[CompanyRead])
def list_companies(
    q: str | None = None, db: Session = Depends(get_db), _user: User = Depends(require_manager)
) -> list[Company]:
    stmt = select(Company)
    if q:
        stmt = stmt.where(Company.name.ilike(f"%{q}%"))
    return list(db.scalars(stmt.order_by(Company.name)))


@router.post("", response_model=CompanyRead)
def create_company(
    payload: CompanyCreate, db: Session = Depends(get_db), _user: User = Depends(require_manager)
) -> Company:
    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/lookup", response_model=CompanyLookupResult, dependencies=[Depends(lookup_limiter)])
def lookup_company(
    name: str = Query(min_length=1, max_length=255), db: Session = Depends(get_db)
) -> CompanyLookupResult:
    """Used by Issue Pass (monthly) to auto-fill an existing company's negotiated
    monthly rate and show which trucks are already parking under it.

    NOTE: this is deliberately unauthenticated (the kiosk needs it before anyone
    signs in), which means it answers "does company X exist, what does it pay per
    month, and which trucks park under it" to anyone who can guess the name. The
    rate limit blunts wordlist enumeration; it does not eliminate the exposure.
    If that ever matters, gate the rate/trucks behind a matching phone number.
    """
    company = db.scalar(select(Company).where(func.lower(Company.name) == name.strip().lower()))
    if company is None:
        return CompanyLookupResult(found=False)

    monthly_customer = db.scalar(select(MonthlyCustomer).where(MonthlyCustomer.company_id == company.id))

    trucks_stmt = (
        select(ParkingPass)
        .join(Vehicle, ParkingPass.vehicle_id == Vehicle.id)
        .where(ParkingPass.company_id == company.id, ParkingPass.pass_type == PassType.monthly)
        .order_by(ParkingPass.issue_date.desc())
    )
    seen: set[str] = set()
    trucks: list[CompanyMonthlyTruck] = []
    for p in db.scalars(trucks_stmt):
        key = p.vehicle.truck_number or p.vehicle.license_plate or str(p.vehicle_id)
        if key in seen:
            continue
        seen.add(key)
        trucks.append(
            CompanyMonthlyTruck(
                truck_number=p.vehicle.truck_number,
                license_plate=p.vehicle.license_plate,
                price=p.price,
                expiration_date=p.expiration_date,
            )
        )

    return CompanyLookupResult(
        found=True,
        company_id=company.id,
        monthly_price=monthly_customer.monthly_price if monthly_customer else None,
        trucks=trucks,
    )


@router.get("/{company_id}", response_model=CompanyRead)
def get_company(
    company_id: int, db: Session = Depends(get_db), _user: User = Depends(require_manager)
) -> Company:
    company = db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/{company_id}/profile", response_model=CompanyProfile)
def company_profile(
    company_id: int, db: Session = Depends(get_db), _user: User = Depends(require_manager)
) -> CompanyProfile:
    """Everything about one company in one place: totals, trucks, recent passes
    and payments, monthly status + outstanding balance, and a simple loyalty
    score (a heuristic from visit count + currently-active passes)."""
    company = db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    today = business_today()
    passes = list(
        db.scalars(
            select(ParkingPass)
            .where(ParkingPass.company_id == company_id)
            .order_by(ParkingPass.issue_date.desc(), ParkingPass.id.desc())
        )
    )
    monthly_customer = db.scalar(select(MonthlyCustomer).where(MonthlyCustomer.company_id == company_id))

    # A Payment can hang off a pass OR directly off the monthly customer. Joining
    # only through passes would silently drop the latter from total_spent — an
    # under-reported figure on a money screen. Outer-join so both are counted.
    payment_filters = [ParkingPass.company_id == company_id]
    if monthly_customer is not None:
        payment_filters.append(Payment.monthly_customer_id == monthly_customer.id)
    payments = list(
        db.scalars(
            select(Payment)
            .outerjoin(ParkingPass, Payment.parking_pass_id == ParkingPass.id)
            .where(or_(*payment_filters))
            .order_by(Payment.paid_at.desc())
        )
    )

    total_spent = float(sum(p.amount for p in payments))
    active_passes = sum(
        1 for p in passes if p.status != PassStatus.cancelled and p.expiration_date >= today
    )
    issue_dates = [p.issue_date for p in passes]

    # Group passes into per-truck rows (visits + last seen).
    trucks_by_vehicle: dict[int, dict] = {}
    for p in passes:
        v = p.vehicle
        row = trucks_by_vehicle.setdefault(
            v.id,
            {"truck": v.truck_number, "plate": v.license_plate, "trailer": v.trailer_number,
             "visits": 0, "last": p.issue_date, "monthly_price": None},
        )
        row["visits"] += 1
        row["last"] = max(row["last"], p.issue_date)
        # Passes are newest-first, so the first monthly pass seen per truck is its
        # current per-truck rate (each truck is priced on its own).
        if p.pass_type == PassType.monthly and row["monthly_price"] is None:
            row["monthly_price"] = float(p.price)

    # Each truck's fixed reserved spot (monthly only), so the owner sees where
    # every truck lives on the lot without walking it.
    reserved_by_vehicle = {
        spot.reserved_vehicle_id: spot_label(spot.number)
        for spot in db.scalars(
            select(Spot).where(Spot.reserved_vehicle_id.in_(list(trucks_by_vehicle.keys())))
        )
    }

    # What the cashier collects from this company each month = the sum of the
    # per-truck rates for the trucks currently holding a spot. Each truck is priced
    # on its own; there is no single company rate.
    monthly_total = sum(
        row["monthly_price"]
        for vid, row in trucks_by_vehicle.items()
        if vid in reserved_by_vehicle and row["monthly_price"] is not None
    ) or None

    loyalty_score = min(100, len(passes) * 4 + active_passes * 10)

    return CompanyProfile(
        id=company.id,
        name=company.name,
        phone=company.phone,
        is_monthly=monthly_customer is not None,
        monthly_price=float(monthly_customer.monthly_price) if monthly_customer else None,
        monthly_total=monthly_total,
        renewal_date=monthly_customer.renewal_date if monthly_customer else None,
        outstanding_balance=float(monthly_customer.current_balance) if monthly_customer else 0.0,
        total_visits=len(passes),
        total_spent=total_spent,
        active_passes=active_passes,
        first_seen=min(issue_dates) if issue_dates else None,
        last_seen=max(issue_dates) if issue_dates else None,
        loyalty_score=loyalty_score,
        trucks=[
            ProfileTruck(
                truck_number=r["truck"], license_plate=r["plate"], trailer_number=r["trailer"],
                visits=r["visits"], last_seen=r["last"],
                reserved_spot=reserved_by_vehicle.get(vid),
                monthly_price=r["monthly_price"],
            )
            for vid, r in trucks_by_vehicle.items()
        ],
        recent_passes=[
            ProfilePass(
                id=p.id,
                pass_type=p.pass_type,
                status=live_status(p.pass_type, p.expiration_date, business_now(), p.status),
                price=float(p.price),
                issue_date=p.issue_date,
                expiration_date=p.expiration_date,
            )
            for p in passes[:10]
        ],
        recent_payments=[
            ProfilePayment(
                amount=float(pmt.amount),
                method=pmt.method,
                paid_at=pmt.paid_at,
                receipt_number=pmt.receipt_number,
            )
            for pmt in payments[:10]
        ],
    )
