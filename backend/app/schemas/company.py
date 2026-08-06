from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import PassStatus, PassType, PaymentMethod


class CompanyBase(BaseModel):
    name: str
    usdot_number: str | None = None
    phone: str | None = None
    email: str | None = None
    notes: str | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyRead(CompanyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_vip: bool
    needs_follow_up: bool
    high_risk: bool


class CompanyMonthlyTruck(BaseModel):
    truck_number: str | None
    license_plate: str | None
    price: float
    expiration_date: date


class CompanyLookupResult(BaseModel):
    found: bool
    company_id: int | None = None
    monthly_price: float | None = None
    trucks: list[CompanyMonthlyTruck] = []


class ProfileTruck(BaseModel):
    truck_number: str | None
    license_plate: str | None
    trailer_number: str | None
    visits: int
    last_seen: date | None
    reserved_spot: str | None = None  # a monthly truck's fixed spot label, if any
    monthly_price: float | None = None  # this truck's own per-month rate, if monthly


class ProfilePass(BaseModel):
    id: int
    pass_type: PassType
    status: PassStatus
    price: float
    issue_date: date
    expiration_date: date


class ProfilePayment(BaseModel):
    amount: float
    method: PaymentMethod
    paid_at: datetime
    receipt_number: str | None


class CompanyProfile(BaseModel):
    id: int
    name: str
    phone: str | None
    is_monthly: bool
    monthly_price: float | None
    monthly_total: float | None = None  # sum of the company's per-truck monthly rates
    renewal_date: date | None
    outstanding_balance: float
    total_visits: int
    total_spent: float
    active_passes: int
    first_seen: date | None
    last_seen: date | None
    loyalty_score: int
    trucks: list[ProfileTruck]
    recent_passes: list[ProfilePass]
    recent_payments: list[ProfilePayment]
