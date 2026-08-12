from pydantic import BaseModel


class RevenuePoint(BaseModel):
    date: str
    amount: float


class CompanyStat(BaseModel):
    company_name: str
    company_id: int | None = None
    visits: int
    total_paid: float


class PaymentMethodStat(BaseModel):
    method: str
    count: int
    total: float


class TruckStat(BaseModel):
    truck_number: str | None
    company_name: str | None
    visits: int


class TrendPoint(BaseModel):
    label: str  # the bucket key: YYYY-MM-DD (day/week), YYYY-MM (month), YYYY (year)
    value: float


class TrendResponse(BaseModel):
    bucket: str
    metric: str
    points: list[TrendPoint]


class BusyBar(BaseModel):
    label: str  # weekday ("Mon"…"Sun") or hour ("0"…"23")
    value: int  # number of passes issued in that bucket


class BusynessResponse(BaseModel):
    """How busy the lot is by day-of-week and hour-of-day — the owner's actual
    question ("what days / what times is it busy"), not revenue."""
    total: int  # passes counted in the window (0 → not enough data yet)
    window_days: int
    by_weekday: list[BusyBar]  # always 7, Mon→Sun
    by_hour: list[BusyBar]  # always 24, 0→23 (plaza local hour)


class ReportsSummary(BaseModel):
    revenue_series: list[RevenuePoint]
    revenue_30d: float
    passes_30d: int
    avg_price: float
    active_companies: int
    top_companies: list[CompanyStat]
    payment_methods: list[PaymentMethodStat]
    frequent_trucks: list[TruckStat]
