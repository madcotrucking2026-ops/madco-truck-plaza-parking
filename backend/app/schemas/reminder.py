from datetime import date, datetime

from pydantic import BaseModel


class ReminderCustomer(BaseModel):
    monthly_customer_id: int
    company_name: str
    phone: str | None
    monthly_price: float
    renewal_date: date
    days_until_renewal: int  # negative if already overdue
    reminder_status: str
    last_reminder_at: datetime | None


class RemindersOverview(BaseModel):
    sms_configured: bool
    auto_enabled: bool
    customers: list[ReminderCustomer]


class SendReminderResult(BaseModel):
    sent: bool  # True if an SMS actually went out; False if only recorded (SMS not configured)
    message: str
    reminder_status: str


class SweepResult(BaseModel):
    enabled: bool
    checked: int = 0
    sent: int = 0
    skipped: int = 0
