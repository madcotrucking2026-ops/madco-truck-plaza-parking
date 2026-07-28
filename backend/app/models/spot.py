from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Spot(Base):
    """One painted spot. Free/occupied is NEVER stored here — it is derived from
    live passes (core/spots.py), so it cannot drift from the money records."""

    __tablename__ = "spots"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    spot_type: Mapped[str] = mapped_column(String(32), default="standard")
    # Capacity changes deactivate/reactivate; rows are never deleted (history).
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    # NULL = never occupied -> sorts as "vacant longest" (NULLS FIRST).
    last_vacated_at: Mapped[datetime | None] = mapped_column(DateTime)
    overstay_reported: Mapped[bool] = mapped_column(Boolean, default=False)
    overstay_reported_at: Mapped[datetime | None] = mapped_column(DateTime)
