from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import PaymentMethod


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    parking_pass_id: Mapped[int | None] = mapped_column(ForeignKey("parking_passes.id"))
    monthly_customer_id: Mapped[int | None] = mapped_column(ForeignKey("monthly_customers.id"))

    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod, name="payment_method"))
    reference_number: Mapped[str | None] = mapped_column(String(100))
    check_number: Mapped[str | None] = mapped_column(String(100))
    receipt_number: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)
    employee_name: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(String(2000))
    # Set only for kiosk payments actually processed by Stripe — presence of a
    # value (not the `method` field) is what proves a charge was verified.
    # Unique so the same PaymentIntent can never be used to issue two passes.
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)

    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    parking_pass: Mapped["ParkingPass | None"] = relationship(back_populates="payments")
    monthly_customer: Mapped["MonthlyCustomer | None"] = relationship(back_populates="payments")

    @property
    def company_name(self) -> str | None:
        if self.parking_pass and self.parking_pass.company:
            return self.parking_pass.company.name
        if self.monthly_customer:
            return self.monthly_customer.company_name
        return None

    @property
    def truck_number(self) -> str | None:
        """What the payment was for — the vehicle on its pass."""
        if self.parking_pass and self.parking_pass.vehicle:
            v = self.parking_pass.vehicle
            return v.truck_number or v.trailer_number or v.license_plate
        return None

    @property
    def pass_type(self) -> str | None:
        return self.parking_pass.pass_type.value if self.parking_pass else None
