from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import Company, MonthlyCustomer, ParkingPass
from app.models.enums import PassType
from app.schemas.insights import ConversionLead, ConversionLeads

router = APIRouter(prefix="/api/insights", tags=["insights"])

# Look back this far, and only pitch a company that's shown up at least this
# many times — one-off daily buyers aren't monthly candidates.
WINDOW_DAYS = 90
MIN_VISITS = 3


def _tier(visits: int, total_spent: float, monthly: float) -> str:
    # Hot: they already spend as much (or more) than a monthly plan, or they're
    # here constantly. Warm: frequent enough to be worth a call. Cold: on the radar.
    if total_spent >= monthly or visits >= 8:
        return "hot"
    if visits >= 5:
        return "warm"
    return "cold"


@router.get("/conversion-leads", response_model=ConversionLeads)
def conversion_leads(db: Session = Depends(get_db)) -> ConversionLeads:
    """Daily/weekly customers who come often enough that a monthly plan would
    likely save them money and lock in recurring revenue for the plaza — ranked
    hottest (biggest spend) first. Companies already on a monthly plan are
    excluded; so are one-off visitors below MIN_VISITS."""
    since = date.today() - timedelta(days=WINDOW_DAYS)
    monthly_default = float(settings.monthly_price)

    rows = db.execute(
        select(
            Company.id,
            Company.name,
            Company.phone,
            func.count(ParkingPass.id),
            func.coalesce(func.sum(ParkingPass.price), 0),
        )
        .join(ParkingPass, ParkingPass.company_id == Company.id)
        .where(
            ParkingPass.pass_type.in_([PassType.daily, PassType.weekly]),
            ParkingPass.issue_date >= since,
            Company.id.not_in(select(MonthlyCustomer.company_id)),
        )
        .group_by(Company.id)
        .having(func.count(ParkingPass.id) >= MIN_VISITS)
        .order_by(func.sum(ParkingPass.price).desc())
        .limit(10)
    ).all()

    leads = [
        ConversionLead(
            company_id=cid,
            company_name=name,
            phone=phone,
            visits=visits,
            total_spent=float(total),
            suggested_monthly=monthly_default,
            tier=_tier(visits, float(total), monthly_default),
        )
        for cid, name, phone, visits, total in rows
    ]
    return ConversionLeads(window_days=WINDOW_DAYS, leads=leads)
