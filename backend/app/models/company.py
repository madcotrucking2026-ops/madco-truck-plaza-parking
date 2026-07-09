from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    usdot_number: Mapped[str | None] = mapped_column(String(50), index=True)
    phone: Mapped[str | None] = mapped_column(String(30), index=True)
    email: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(String(2000))

    is_vip: Mapped[bool] = mapped_column(Boolean, default=False)
    needs_follow_up: Mapped[bool] = mapped_column(Boolean, default=False)
    high_risk: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="company")
    passes: Mapped[list["ParkingPass"]] = relationship(back_populates="company")
    monthly_customer: Mapped["MonthlyCustomer | None"] = relationship(back_populates="company", uselist=False)
