from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AppSetting(Base):
    """One owner-editable configuration value, stored as a string keyed by name
    (`parking_capacity`, `daily_price`, ...). It OVERRIDES the env/config default
    at runtime and is loaded onto `settings` at startup. Deliberately a tiny
    key/value table so a new knob never needs its own migration."""

    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(String(255))
