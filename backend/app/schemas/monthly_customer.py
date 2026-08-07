from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import MonthlyCustomerStatus, PaymentMethod, ReminderStatus


class MonthlyCustomerCreate(BaseModel):
    company_id: int
    monthly_price: float
    number_of_trucks: int = 1
    fueling_customer: bool = False
    preferred_payment_method: PaymentMethod | None = None
    billing_cycle_day: int = 1
    renewal_date: date
    notes: str | None = None


class MonthlyCustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    company_name: str
    monthly_price: float
    number_of_trucks: int
    fueling_customer: bool
    preferred_payment_method: PaymentMethod | None
    billing_cycle_day: int
    renewal_date: date
    status: MonthlyCustomerStatus
    reminder_status: ReminderStatus
    notes: str | None


class MonthlyCustomerStatusUpdate(BaseModel):
    status: MonthlyCustomerStatus
