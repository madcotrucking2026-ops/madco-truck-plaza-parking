"""Test fixtures: an isolated in-memory SQLite database per test.

The money-path helpers in app.routers.passes take a Session and do all their
queries/commits through it, so a session bound to a throwaway in-memory engine
exercises the real logic in full isolation — no dev DB, no network, no Stripe.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 — registers every table on Base.metadata
from app.core.database import Base


def _fresh_engine():
    # StaticPool keeps every connection pointed at the same in-memory database
    # (a plain sqlite:// pool would hand out fresh, empty DBs per connection).
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db() -> Session:
    engine = _fresh_engine()
    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client():
    """FastAPI TestClient wired to an isolated in-memory DB via get_db override.
    Built without the lifespan context, so the reminder scheduler never starts."""
    from fastapi.testclient import TestClient

    from app.core.database import get_db
    from app.main import app

    engine = _fresh_engine()
    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        s = TestSession()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)
        engine.dispose()
