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
    customers: list[ReminderCustomer]
