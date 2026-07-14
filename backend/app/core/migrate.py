"""Schema management at startup — Alembic is the single mechanism.

Replaces the old `Base.metadata.create_all()` + hand-rolled ALTERs, which could
only ever add things and silently diverged from the models on any change to an
existing table. Every schema change from here on is an Alembic revision:

    .venv/Scripts/python.exe -m alembic revision --autogenerate -m "what changed"
"""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.core.database import engine, run_startup_migrations
from app.core.logging_config import get_logger

log = get_logger(__name__)

_BACKEND_DIR = Path(__file__).resolve().parents[2]


def _alembic_config() -> Config:
    cfg = Config(str(_BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND_DIR / "alembic"))
    return cfg


def upgrade_database() -> None:
    """Bring the schema to head, whatever state the database is in.

    Three cases:
      * fresh database (prod Postgres, new dev)   -> run all migrations
      * pre-Alembic database (the old create_all
        path — this project's own dev SQLite)      -> apply the legacy column
        shims so it truly matches the baseline, then STAMP it as baseline
        rather than re-running CREATEs against existing tables
      * already-stamped database                   -> upgrade to head (no-op
        when current)
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    cfg = _alembic_config()

    if "alembic_version" not in tables and "parking_passes" in tables:
        run_startup_migrations()  # late-added columns on genuinely old dev dbs
        command.stamp(cfg, "head")
        log.info("Pre-Alembic database detected — stamped at baseline.")
        return

    command.upgrade(cfg, "head")
