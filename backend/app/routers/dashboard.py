from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Company, ParkingPass, Payment
from app.models.enums import PassType
from app.schemas.dashboard import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)) -> DashboardStats:
    today = date.today()
    tomorrow = today + timedelta(days=1)
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    def revenue_since(start: date) -> float:
        return db.scalar(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(func.date(Payment.paid_at) >= start)
        ) or 0.0

    def active_count(pass_type: PassType) -> int:
        return db.scalar(
            select(func.count(ParkingPass.id)).where(
                ParkingPass.pass_type == pass_type, ParkingPass.expiration_date >= today
            )
        ) or 0

    todays_revenue = db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(func.date(Payment.paid_at) == today)
    ) or 0.0
    todays_vehicles = db.scalar(
        select(func.count(ParkingPass.id)).where(ParkingPass.issue_date == today)
    ) or 0
    expired_passes = db.scalar(
        select(func.count(ParkingPass.id)).where(ParkingPass.expiration_date < today)
    ) or 0
    expiring_today = db.scalar(
        select(func.count(ParkingPass.id)).where(ParkingPass.expiration_date == today)
    ) or 0
    expiring_tomorrow = db.scalar(
        select(func.count(ParkingPass.id)).where(ParkingPass.expiration_date == tomorrow)
    ) or 0
    companies_needing_follow_up = db.scalar(
        select(func.count(Company.id)).where(Company.needs_follow_up.is_(True))
    ) or 0
    occupied_spaces = db.scalar(
        select(func.count(ParkingPass.id)).where(ParkingPass.expiration_date >= today)
    ) or 0

    return DashboardStats(
        todays_revenue=todays_revenue,
        todays_vehicles=todays_vehicles,
        active_daily_passes=active_count(PassType.daily),
        active_weekly_passes=active_count(PassType.weekly),
        active_monthly_passes=active_count(PassType.monthly),
        expired_passes=expired_passes,
        expiring_today=expiring_today,
        expiring_tomorrow=expiring_tomorrow,
        companies_needing_follow_up=companies_needing_follow_up,
        occupied_spaces=occupied_spaces,
        monthly_revenue=revenue_since(month_start),
        weekly_revenue=revenue_since(week_start),
    )
