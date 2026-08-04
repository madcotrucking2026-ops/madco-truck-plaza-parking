"""The lot, painted by query.

`expiring` = holder's last day is today or tomorrow (matches the dashboard's
attention list); `grace` = a monthly past expiry but inside the grace window —
the spot is still theirs, and the colour tells the manager why it isn't free.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clock import business_today
from app.core.database import get_db
from app.core.spots import holding_filter, spot_label
from app.models import ParkingPass, Spot
from app.schemas.spot import SpotState

router = APIRouter(prefix="/api/spots", tags=["spots"])


@router.get("", response_model=list[SpotState])
def lot_state(db: Session = Depends(get_db)) -> list[SpotState]:
    today = business_today()
    holders = {p.spot_id: p for p in db.scalars(select(ParkingPass).where(holding_filter()))}

    out: list[SpotState] = []
    for spot in db.scalars(select(Spot).order_by(Spot.number)):
        p = holders.get(spot.id)
        if not spot.active:
            state = "inactive"
        elif spot.overstay_reported:
            state = "overstay"
        elif p is None:
            state = "free"
        elif p.expiration_date < today:
            state = "grace"  # only a monthly can hold past expiry
        elif p.expiration_date <= today + timedelta(days=1):
            state = "expiring"
        else:
            state = "occupied"
        out.append(
            SpotState(
                number=spot.number,
                label=spot_label(spot.number),
                state=state,
                company_name=p.company.name if p and p.company else None,
                truck_number=p.vehicle.truck_number if p and p.vehicle else None,
                pass_id=p.id if p else None,
                expiration_date=p.expiration_date if p else None,
            )
        )
    return out


@router.post("/{number}/clear-overstay")
def clear_overstay(number: int, db: Session = Depends(get_db)) -> dict:
    """Staff dealt with the squatter — put the spot back to normal."""
    spot = db.scalar(select(Spot).where(Spot.number == number))
    if spot is None:
        raise HTTPException(status_code=404, detail="No such spot.")
    spot.overstay_reported = False
    spot.overstay_reported_at = None
    db.commit()
    return {"cleared": True}
