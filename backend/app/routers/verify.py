from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.audit import log_audit
from app.core.clock import business_now, business_today
from app.core.database import get_db
from app.core.pass_status import live_status
from app.core.pass_token import verify_pass_token
from app.core.rate_limit import lookup_limiter, verify_limiter
from app.core.spots import pick_free_spot
from app.models import ParkingPass, Spot
from app.models.enums import AuditAction
from app.schemas.verify import PassVerifyResult, ReassignResult

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
        spot_number=parking_pass.spot_number,
        spot_label=parking_pass.spot_label,
    )


@router.post("/{token}/report-occupied", response_model=ReassignResult, dependencies=[Depends(lookup_limiter)])
def report_occupied(token: str, db: Session = Depends(get_db)) -> ReassignResult:
    """The asphalt gap: no sensors, so an expired truck can still sit in a spot
    the system already resold. The customer standing in front of it taps once:
    old spot flagged for staff AND sent to the back of the assignment queue,
    new spot issued, pass updated — no phone call, no desk, no waiting."""
    pass_id = verify_pass_token(token)
    parking_pass = db.get(ParkingPass, pass_id) if pass_id is not None else None
    if parking_pass is None or parking_pass.spot_id is None:
        raise HTTPException(status_code=404, detail="Pass not found.")

    old = db.get(Spot, parking_pass.spot_id)
    replacement = pick_free_spot(db)
    if replacement is None or replacement.id == old.id:
        raise HTTPException(status_code=409, detail="No other spots are open — please see the front desk.")

    old.overstay_reported = True
    old.overstay_reported_at = business_now()
    old.last_vacated_at = business_now()
    parking_pass.spot_id = replacement.id
    log_audit(
        db, AuditAction.edited, "parking_pass",
        f"Spot {old.number} reported occupied — reassigned to {replacement.number}",
        entity_id=parking_pass.id,
    )
    db.commit()
    return ReassignResult(spot_number=replacement.number)
