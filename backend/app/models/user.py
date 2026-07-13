from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.clock import business_now
from app.core.database import Base
from app.models.enums import EmployeeRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[EmployeeRole] = mapped_column(Enum(EmployeeRole, name="employee_role"), default=EmployeeRole.attendant)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Login lockout tracking — reset to 0/None on any successful login.
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=business_now, server_default=func.now())
