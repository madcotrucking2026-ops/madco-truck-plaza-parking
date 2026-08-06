from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PaymentMethod


class PaymentCreate(BaseModel):
    parking_pass_id: int | None = None
    monthly_customer_id: int | None = None
    # This endpoint is owner/manager only (the cashier can never reach it). A
    # negative amount is a REFUND the owner records; the magnitude is bounded so a
    # fat-fingered extra zero can't silently swing the day's revenue by millions.
    amount: float = Field(ge=-100_000, le=100_000)
    method: PaymentMethod
    reference_number: str | None = None
    check_number: str | None = None
    employee_name: str | None = None
    notes: str | None = None


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str | None
    truck_number: str | None = None
    pass_type: str | None = None
    amount: float
    method: PaymentMethod
    reference_number: str | None
    check_number: str | None
    receipt_number: str | None
    employee_name: str | None
    notes: str | None
    paid_at: datetime
