"""DATABASE_URL normalization — managed Postgres hosts (Neon/Render/Supabase)
hand out a bare postgres:// URL; SQLAlchemy needs the psycopg driver named, so a
pasted connection string must Just Work."""
import pytest

from app.core.config import Settings


@pytest.mark.parametrize(
    "raw, expected",
    [
        # Neon/Heroku style — bare postgres://, query string preserved.
        ("postgres://u:p@h/db?sslmode=require", "postgresql+psycopg://u:p@h/db?sslmode=require"),
        # Plain postgresql:// gets the driver added.
        ("postgresql://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        # Already-correct URLs are left alone.
        ("postgresql+psycopg://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        # SQLite (dev + our prod choice for one location) is untouched.
        ("sqlite:///./mtpms.db", "sqlite:///./mtpms.db"),
    ],
)
def test_database_url_is_normalized_for_sqlalchemy(raw, expected):
    assert Settings(database_url=raw).database_url == expected
