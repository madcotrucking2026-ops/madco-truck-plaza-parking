from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.clock import business_now
from app.core.database import Base
from app.models.enums import ReminderStatus


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True)
    monthly_customer_id: Mapped[int] = mapped_column(ForeignKey("monthly_customers.id"))

    scheduled_date: Mapped[date] = mapped_column(Date)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[ReminderStatus] = mapped_column(
        Enum(ReminderStatus, name="reminder_send_status"), default=ReminderStatus.pending
    )
    message: Mapped[str | None] = mapped_column(String(500))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=business_now, server_default=func.now())

    monthly_customer: Mapped["MonthlyCustomer"] = relationship(back_populates="reminders")
