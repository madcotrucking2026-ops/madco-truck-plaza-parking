from datetime import date

from pydantic import BaseModel, ConfigDict


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
