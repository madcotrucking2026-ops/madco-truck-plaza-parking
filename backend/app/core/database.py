from collections.abc import Generator

from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
elif settings.database_url.startswith("postgresql"):
    # The database's clock is the PLAZA's clock. Timestamps are stored as naive
    # plaza-local wall time (see core/clock.py), and the revenue queries bucket
    # them with SQL date(). On Postgres those columns are timestamptz: without
    # this, a naive insert is interpreted in the SERVER's timezone (UTC on any
    # cloud box) and date() re-extracts UTC days — silently reintroducing the
    # "evening payments land on tomorrow's books" bug that was already fixed
    # once on SQLite. Pinning the session timezone makes Postgres agree with
    # the plaza end to end.
    connect_args = {"options": f"-c timezone={settings.timezone}"}
else:
    connect_args = {}
engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_startup_migrations() -> None:
    """`Base.metadata.create_all()` only creates missing *tables* — it never
    alters an existing one. No Alembic is wired up yet (see main.py comment),
    so new columns on a table that already exists on disk need a one-off
    ADD COLUMN here. Safe to run every startup: skips whatever already exists.
    """
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    if "payments" in table_names:
        existing_columns = {col["name"] for col in inspector.get_columns("payments")}
        with engine.begin() as conn:
            if "stripe_payment_intent_id" not in existing_columns:
                conn.execute(text("ALTER TABLE payments ADD COLUMN stripe_payment_intent_id VARCHAR(255)"))
            conn.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS ix_payments_stripe_payment_intent_id ON payments (stripe_payment_intent_id)"
                )
            )

    if "users" in table_names:
        existing_columns = {col["name"] for col in inspector.get_columns("users")}
        with engine.begin() as conn:
            if "failed_login_attempts" not in existing_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0"))
            if "locked_until" not in existing_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN locked_until TIMESTAMP"))

    # Backfill: an install that already had a user before SetupLock existed
    # (e.g. this project's own dev database) would otherwise look like it
    # still needs first-time setup, even though an admin account is already
    # sitting right there.
    if "users" in table_names and "setup_lock" in table_names:
        with engine.begin() as conn:
            has_user = conn.execute(text("SELECT 1 FROM users LIMIT 1")).first() is not None
            has_lock = conn.execute(text("SELECT 1 FROM setup_lock WHERE id = 1")).first() is not None
            if has_user and not has_lock:
                conn.execute(text("INSERT INTO setup_lock (id) VALUES (1)"))

    _backfill_pass_qr_codes(table_names)


def _backfill_pass_qr_codes(table_names: list[str]) -> None:
    """Passes issued before the signed-QR system stored their plaintext receipt
    number in `qr_code`; those fail scan verification. Rewrite any non-URL
    qr_code to a proper signed verify URL so every pass is scannable. Also
    self-heals when PUBLIC_BASE_URL changes at deploy time (any qr_code not
    matching the current base is regenerated). Lazy imports avoid a circular
    import (models depend on this module's Base).
    """
    if "parking_passes" not in table_names:
        return

    from app.core.config import settings
    from app.core.pass_token import make_pass_token
    from app.models import ParkingPass

    with SessionLocal() as db:
        prefix = f"{settings.public_base_url}/verify/"
        stale = db.scalars(
            select(ParkingPass).where(
                (ParkingPass.qr_code.is_(None)) | (ParkingPass.qr_code.notlike(f"{prefix}%"))
            )
        ).all()
        for p in stale:
            p.qr_code = f"{prefix}{make_pass_token(p.id)}"
        if stale:
            db.commit()
