from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SetupLock(Base):
    """A singleton row (always id=1) inserted atomically alongside the very
    first admin account. Its primary key makes bootstrap race-safe: two
    concurrent `POST /api/auth/register` calls can't both succeed, because
    only one INSERT with id=1 can ever land — the second raises an
    IntegrityError before any second admin account is created."""

    __tablename__ = "setup_lock"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
