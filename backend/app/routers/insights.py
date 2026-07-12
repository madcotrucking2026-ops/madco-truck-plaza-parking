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


def _monthly_equivalent(total_spent: float, window_days: int) -> float:
    """What this company effectively spends per month right now.

    The window is 90 days, so a raw total can NOT be compared to a monthly price:
    $280 over 90 days is ~$93/month, not $280/month. Comparing the two directly
    would tag a light user as a hot lead and have the owner pitch a plan that
    costs them three times what they pay today.
    """
    if window_days <= 0:
        return 0.0
    return total_spent / (window_days / 30)


def _tier(visits: int, monthly_equivalent: float, monthly: float) -> str:
    # Hot: they already spend a monthly plan's worth every month, or they're here
    # constantly. Warm: frequent enough to be worth a call. Cold: on the radar.
    if monthly_equivalent >= monthly or visits >= 8:
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
    ).all()

    leads = []
    for cid, name, phone, visits, total in rows:
        equivalent = _monthly_equivalent(float(total), WINDOW_DAYS)
        leads.append(
            ConversionLead(
                company_id=cid,
                company_name=name,
                phone=phone,
                visits=visits,
                total_spent=float(total),
                current_monthly_equivalent=round(equivalent, 2),
                suggested_monthly=monthly_default,
                tier=_tier(visits, equivalent, monthly_default),
            )
        )

    # Rank by how worth calling they are — hottest first, then by what they
    # already spend each month. Ordering by the raw 90-day total (as this used
    # to) put COLD leads above HOT ones, so the owner would call the wrong
    # company first. Tiering and ranking now agree.
    tier_rank = {"hot": 0, "warm": 1, "cold": 2}
    leads.sort(key=lambda l: (tier_rank[l.tier], -l.current_monthly_equivalent, -l.visits))
    return ConversionLeads(window_days=WINDOW_DAYS, leads=leads[:10])
