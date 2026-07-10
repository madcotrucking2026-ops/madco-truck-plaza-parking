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


@pytest.fixture
def db() -> Session:
    # StaticPool keeps every connection pointed at the same in-memory database
    # (a plain sqlite:// pool would hand out fresh, empty DBs per connection).
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
