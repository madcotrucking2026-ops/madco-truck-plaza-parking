from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.clock import business_now
from app.core.database import Base
from app.models.enums import PassStatus, PassType


class ParkingPass(Base):
    __tablename__ = "parking_passes"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"))

    pass_type: Mapped[PassType] = mapped_column(Enum(PassType, name="pass_type"))
    status: Mapped[PassStatus] = mapped_column(Enum(PassStatus, name="pass_status"), default=PassStatus.active)

    price: Mapped[float] = mapped_column(Numeric(10, 2))
    issue_date: Mapped[date] = mapped_column(Date)
    expiration_date: Mapped[date] = mapped_column(Date)

    receipt_number: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)
    qr_code: Mapped[str | None] = mapped_column(String(255))
    barcode: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(String(2000))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=business_now, server_default=func.now())

    company: Mapped["Company | None"] = relationship(back_populates="passes")
    vehicle: Mapped["Vehicle"] = relationship(back_populates="passes")
    payments: Mapped[list["Payment"]] = relationship(back_populates="parking_pass")
