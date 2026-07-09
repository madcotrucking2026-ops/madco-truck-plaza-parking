from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import MonthlyCustomerStatus, PaymentMethod, ReminderStatus


class MonthlyCustomer(Base):
    __tablename__ = "monthly_customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), unique=True)

    monthly_price: Mapped[float] = mapped_column(Numeric(10, 2))
    number_of_trucks: Mapped[int] = mapped_column(Integer, default=1)
    fueling_customer: Mapped[bool] = mapped_column(Boolean, default=False)
    preferred_payment_method: Mapped[PaymentMethod | None] = mapped_column(
        Enum(PaymentMethod, name="preferred_payment_method")
    )
    billing_cycle_day: Mapped[int] = mapped_column(Integer, default=1)
    renewal_date: Mapped[date] = mapped_column(Date)

    status: Mapped[MonthlyCustomerStatus] = mapped_column(
        Enum(MonthlyCustomerStatus, name="monthly_customer_status"),
        default=MonthlyCustomerStatus.truck_parked,
    )
    reminder_status: Mapped[ReminderStatus] = mapped_column(
        Enum(ReminderStatus, name="reminder_status"), default=ReminderStatus.pending
    )
    current_balance: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    notes: Mapped[str | None] = mapped_column(String(2000))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped["Company"] = relationship(back_populates="monthly_customer")
    payments: Mapped[list["Payment"]] = relationship(back_populates="monthly_customer")
    reminders: Mapped[list["Reminder"]] = relationship(back_populates="monthly_customer")

    @property
    def company_name(self) -> str:
        return self.company.name if self.company else ""
