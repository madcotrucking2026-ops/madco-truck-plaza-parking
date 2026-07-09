from pydantic import BaseModel


class RevenuePoint(BaseModel):
    date: str
    amount: float


class CompanyStat(BaseModel):
    company_name: str
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


class OutstandingBalance(BaseModel):
    company_name: str
    balance: float


class ReportsSummary(BaseModel):
    revenue_series: list[RevenuePoint]
    revenue_30d: float
    passes_30d: int
    avg_price: float
    active_companies: int
    top_companies: list[CompanyStat]
    payment_methods: list[PaymentMethodStat]
    frequent_trucks: list[TruckStat]
    outstanding_balances: list[OutstandingBalance]
