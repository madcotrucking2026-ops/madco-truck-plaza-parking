from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import VehicleType


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"))

    vehicle_type: Mapped[VehicleType] = mapped_column(Enum(VehicleType, name="vehicle_type"))
    truck_number: Mapped[str | None] = mapped_column(String(50), index=True)
    trailer_number: Mapped[str | None] = mapped_column(String(50), index=True)
    license_plate: Mapped[str | None] = mapped_column(String(20), index=True)
    driver_name: Mapped[str | None] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped["Company | None"] = relationship(back_populates="vehicles")
    passes: Mapped[list["ParkingPass"]] = relationship(back_populates="vehicle")
