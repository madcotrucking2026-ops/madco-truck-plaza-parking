from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import log_audit
from app.core.clock import business_now
from app.core.database import get_db
from app.core.pass_status import live_status
from app.models import Company, MonthlyCustomer, ParkingPass, Payment, Vehicle
from app.models.enums import AuditAction
from app.schemas.pass_ import LotCheckResult

router = APIRouter(prefix="/api/lot-check", tags=["lot-check"])


@router.get("", response_model=LotCheckResult)
def lot_check(q: str = Query(..., min_length=1), db: Session = Depends(get_db)) -> LotCheckResult:
    stmt = (
        select(ParkingPass)
        .join(Vehicle, ParkingPass.vehicle_id == Vehicle.id)
        .join(Company, ParkingPass.company_id == Company.id, isouter=True)
        .where(
            (Vehicle.truck_number == q)
            | (Vehicle.trailer_number == q)
            | (Vehicle.license_plate == q)
            | (Company.name.ilike(f"%{q}%"))
            | (Company.usdot_number == q)
            | (Company.phone == q)
        )
        .order_by(ParkingPass.issue_date.desc())
    )
    parking_pass = db.scalars(stmt).first()

    log_audit(db, AuditAction.search_performed, "lot_check", f'Searched "{q}"')
    db.commit()

    if parking_pass is None:
        return LotCheckResult(found=False)

    # The payment that bought the pass they're sitting on — a renewal writes a new
    # Payment row, so the LATEST one is the one that matters. Same-day renewals tie
    # on paid_at (same second), and ordering on that alone hands back whichever row
    # the database feels like — often the ORIGINAL payment, which would tell the
    # manager the truck paid cash when it just renewed by card. Break the tie on id.
    last_payment = db.scalars(
        select(Payment)
        .where(Payment.parking_pass_id == parking_pass.id)
        .order_by(Payment.paid_at.desc(), Payment.id.desc())
    ).first()

    is_monthly_customer = False
    if parking_pass.company_id is not None:
        is_monthly_customer = (
            db.scalar(select(MonthlyCustomer.id).where(MonthlyCustomer.company_id == parking_pass.company_id))
            is not None
        )

    return LotCheckResult(
        found=True,
        status=live_status(parking_pass.pass_type, parking_pass.expiration_date, business_now(), parking_pass.status),
        company_name=parking_pass.company.name if parking_pass.company else None,
        phone=parking_pass.company.phone if parking_pass.company else None,
        truck_number=parking_pass.vehicle.truck_number,
        trailer_number=parking_pass.vehicle.trailer_number,
        license_plate=parking_pass.vehicle.license_plate,
        pass_type=parking_pass.pass_type,
        expiration_date=parking_pass.expiration_date,
        notes=parking_pass.notes,
        amount_paid=float(last_payment.amount) if last_payment else None,
        payment_method=last_payment.method if last_payment else None,
        paid_at=last_payment.paid_at.date() if last_payment else None,
        is_monthly_customer=is_monthly_customer,
        spot_number=parking_pass.spot_number,
        spot_label=parking_pass.spot_label,
    )
