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


@pytest.fixture(autouse=True)
def _pooled_lot_by_default(monkeypatch):
    """Legacy spot tests predate lot zoning: they describe the single pooled lot
    (the old "grab the longest-empty free spot for anyone") at small capacities,
    where the production default (MONTHLY_ZONE_COUNT=1 -> spots 1..25 are the
    monthly area) would swallow the whole test lot and starve daily/weekly of a
    spot. Default the split OFF here so those tests still describe the pooled lot;
    the reserved-spot suite opts back into the monthly/daily split via its own
    monkeypatch (same monkeypatch instance, so it wins and teardown restores the
    real default of 1). Production behaviour is unchanged."""
    from app.core.config import settings

    monkeypatch.setattr(settings, "monthly_zone_count", 0)


@pytest.fixture(autouse=True)
def _reset_rate_limits():
    """The limiters are module-level singletons keyed by client IP, and every
    TestClient request comes from the same host — without this, one test's
    requests would eat the next test's budget and it would 429 for no reason."""
    from app.core import rate_limit

    limiters = [
        rate_limit.login_limiter,
        rate_limit.register_limiter,
        rate_limit.checkout_limiter,
        rate_limit.lookup_limiter,
        rate_limit.verify_limiter,
    ]
    for limiter in limiters:
        limiter.reset()
    yield
    for limiter in limiters:
        limiter.reset()


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
def engine():
    """One in-memory database per test, shared by BOTH the `db` session and the
    `client`'s request sessions. They used to build an engine each, so a test that
    seeded through `db` and then called the API through `client` was quietly
    talking to two different databases and the API saw an empty one."""
    eng = _fresh_engine()
    try:
        yield eng
    finally:
        eng.dispose()


@pytest.fixture
def db(engine) -> Session:
    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(engine):
    """FastAPI TestClient wired to the same in-memory DB via a get_db override.
    Built without the lifespan context, so the reminder scheduler never starts."""
    from fastapi.testclient import TestClient

    from app.core.database import get_db
    from app.main import app

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
