from pydantic import BaseModel


class DashboardStats(BaseModel):
    todays_revenue: float
    todays_vehicles: int
    active_daily_passes: int
    active_weekly_passes: int
    active_monthly_passes: int
    expired_passes: int
    expiring_today: int
    expiring_tomorrow: int
    companies_needing_follow_up: int
    occupied_spaces: int
    capacity: int
    available_spaces: int
    occupancy_pct: int
    monthly_revenue: float
    weekly_revenue: float
