from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import log_audit
from app.core.database import get_db
from app.core.pass_status import live_status
from app.models import Company, ParkingPass, Vehicle
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

    today = date.today()
    return LotCheckResult(
        found=True,
        status=live_status(parking_pass.expiration_date, today, parking_pass.status),
        company_name=parking_pass.company.name if parking_pass.company else None,
        phone=parking_pass.company.phone if parking_pass.company else None,
        truck_number=parking_pass.vehicle.truck_number,
        trailer_number=parking_pass.vehicle.trailer_number,
        license_plate=parking_pass.vehicle.license_plate,
        pass_type=parking_pass.pass_type,
        expiration_date=parking_pass.expiration_date,
        notes=parking_pass.notes,
    )
