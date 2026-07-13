from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.clock import business_today
from app.core.database import get_db
from app.core.pass_status import live_status
from app.core.pass_token import verify_pass_token
from app.core.rate_limit import verify_limiter
from app.models import ParkingPass
from app.schemas.verify import PassVerifyResult

# Deliberately its own router with NO login dependency — a guard scans a pass
# QR with their phone and must reach this without signing in. Trust comes from
# the HMAC signature in the token, not from auth: only a token this server
# actually signed (i.e. a real issued pass) resolves; a fabricated code fails.
router = APIRouter(prefix="/api/verify", tags=["verify"])


@router.get("/{token}", response_model=PassVerifyResult, dependencies=[Depends(verify_limiter)])
def verify_pass(token: str, db: Session = Depends(get_db)) -> PassVerifyResult:
    pass_id = verify_pass_token(token)
    if pass_id is None:
        return PassVerifyResult(valid=False)

    parking_pass = db.get(ParkingPass, pass_id)
    if parking_pass is None:
        return PassVerifyResult(valid=False)

    return PassVerifyResult(
        valid=True,
        status=live_status(parking_pass.expiration_date, business_today(), parking_pass.status),
        company_name=parking_pass.company.name if parking_pass.company else None,
        truck_number=parking_pass.vehicle.truck_number,
        trailer_number=parking_pass.vehicle.trailer_number,
        license_plate=parking_pass.vehicle.license_plate,
        pass_type=parking_pass.pass_type,
        issue_date=parking_pass.issue_date,
        expiration_date=parking_pass.expiration_date,
        price=float(parking_pass.price),
        receipt_number=parking_pass.receipt_number,
    )
