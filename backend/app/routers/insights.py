from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.clock import business_today
from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Company, MonthlyCustomer, ParkingPass, Payment, User, Vehicle
from app.models.enums import PassStatus, PassType
from app.schemas.insights import CallItem, ConversionLead, ConversionLeads, MorningReport

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
    since = business_today() - timedelta(days=WINDOW_DAYS)
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


# The owner reads this with coffee, before he walks the lot. Order matters: money
# already owed, then money about to walk off the lot, then money he could win.
PRIORITY_RANK = {"now": 0, "today": 1, "worth_a_call": 2}


def _revenue_on(db: Session, day: date) -> float:
    return float(
        db.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(func.date(Payment.paid_at) == day)) or 0
    )


@router.get("/morning-report", response_model=MorningReport)
def morning_report(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> MorningReport:
    """The manager's 7am briefing: who to call today, and why.

    The dashboard already shows numbers. What it does NOT do is hand the owner a
    list he can work straight down with a phone in his hand — the renewals he's
    already late chasing, the passes about to expire under trucks sitting on his
    lot, and the daily regulars who'd be worth more on a monthly plan. Those live
    on three different screens; this assembles them into one, in the order money
    is at risk.
    """
    from app.routers.dashboard import dashboard_stats  # lazy: keeps the router graph acyclic
    from app.routers.reminders import monthly_renewal_list

    today = business_today()
    stats = dashboard_stats(db=db)
    calls: list[CallItem] = []

    # 1. Monthly renewals — overdue first. This is money already owed.
    for mc in monthly_renewal_list(db):
        days = mc.days_until_renewal
        if days < 0:
            reason = f"Renewal is {-days} day{'s' if days != -1 else ''} overdue — {_money(mc.monthly_price)}/mo"
            priority = "now"
        elif days == 0:
            reason = f"Renews today — {_money(mc.monthly_price)}/mo"
            priority = "today"
        elif days <= 3:
            reason = f"Renews in {days} day{'s' if days != 1 else ''} — {_money(mc.monthly_price)}/mo"
            priority = "today"
        else:
            continue  # not this morning's problem

        calls.append(
            CallItem(
                priority=priority,
                kind="renewal_overdue" if days < 0 else "renewal_due",
                company_id=None,
                company_name=mc.company_name,
                phone=mc.phone,
                reason=reason,
                amount=mc.monthly_price,
                monthly_customer_id=mc.monthly_customer_id,
            )
        )

    # 2. Daily/weekly passes running out today — a truck is sitting on a spot that
    #    stops being paid for tonight. Cancelled passes are not on the lot.
    expiring = db.execute(
        select(ParkingPass, Company, Vehicle)
        .join(Vehicle, ParkingPass.vehicle_id == Vehicle.id)
        .join(Company, ParkingPass.company_id == Company.id, isouter=True)
        .where(
            ParkingPass.expiration_date == today,
            ParkingPass.status != PassStatus.cancelled,
            ParkingPass.pass_type != PassType.monthly,
        )
    ).all()
    for parking_pass, company, vehicle in expiring:
        truck = vehicle.truck_number or vehicle.trailer_number or vehicle.license_plate or "—"
        calls.append(
            CallItem(
                priority="today",
                kind="pass_expiring",
                company_id=company.id if company else None,
                company_name=company.name if company else "—",
                phone=company.phone if company else None,
                reason=f"{parking_pass.pass_type.value.title()} pass on truck {truck} expires today",
                amount=float(parking_pass.price),
                pass_id=parking_pass.id,
            )
        )

    # 3. Regulars worth putting on a monthly plan. Only the hot ones — a morning
    #    report that lists every lukewarm maybe is a report nobody reads.
    #
    #    The reason line must state honestly which way the money goes. A frequent
    #    visitor is not automatically a saver: someone here 8 days a month spends
    #    $160, so a $250 plan costs them MORE. Telling the owner to "offer the $250
    #    plan" without saying that sends him into a call he cannot win, and after a
    #    few of those he stops reading this page. Savers first — those close
    #    themselves.
    for lead in conversion_leads(db).leads:
        if lead.tier != "hot":
            continue

        saving = lead.current_monthly_equivalent - lead.suggested_monthly
        if saving >= 0:
            reason = (
                f"{lead.visits} visits in {WINDOW_DAYS} days — already spends "
                f"{_money(lead.current_monthly_equivalent)}/mo, so the "
                f"{_money(lead.suggested_monthly)}/mo plan SAVES them {_money(saving)}/mo"
            )
        else:
            reason = (
                f"{lead.visits} visits in {WINDOW_DAYS} days, but only "
                f"{_money(lead.current_monthly_equivalent)}/mo — the "
                f"{_money(lead.suggested_monthly)}/mo plan costs them {_money(-saving)}/mo MORE. "
                f"Sell it as unlimited parking, not as a saving"
            )

        calls.append(
            CallItem(
                priority="worth_a_call",
                kind="lead",
                company_id=lead.company_id,
                company_name=lead.company_name,
                phone=lead.phone,
                # Rank by what they already spend: the biggest spender is both the
                # easiest yes and the most revenue.
                amount=lead.current_monthly_equivalent,
                reason=reason,
            )
        )

    calls.sort(key=lambda c: (PRIORITY_RANK[c.priority], -(c.amount or 0)))

    return MorningReport(
        generated_for=today,
        yesterday_revenue=_revenue_on(db, today - timedelta(days=1)),
        todays_revenue=stats.todays_revenue,
        month_to_date_revenue=stats.monthly_revenue,
        occupied_spaces=stats.occupied_spaces,
        available_spaces=stats.available_spaces,
        capacity=stats.capacity,
        calls=calls,
        all_clear=not calls,
    )


def _money(v: float) -> str:
    return f"${v:,.0f}" if float(v).is_integer() else f"${v:,.2f}"
