from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.jwt_secret import load_or_create_jwt_secret


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Defaults to a local SQLite file so `uvicorn app.main:app` runs with zero setup.
    # Point DATABASE_URL at Postgres (see docker-compose.yml) once Docker is available.
    database_url: str = "sqlite:///./mtpms.db"
    # No hardcoded default on purpose — see jwt_secret.py. Only used if JWT_SECRET
    # isn't set via env/.env, in which case a random per-install secret is
    # generated once and persisted to a gitignored local file.
    jwt_secret: str = Field(default_factory=load_or_create_jwt_secret)
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 12

    daily_price: float = 20.0
    weekly_price: float = 100.0
    monthly_price: float = 250.0
    # Fallback annual rate for a yearly pass. Each yearly customer negotiates their
    # own price (typed at issue), so this is only used when none is entered.
    yearly_price: float = 2000.0

    # Total parking spots on the lot — sizes the spot inventory (rows are
    # seeded/deactivated idempotently at startup) and the occupancy readout.
    # Override with PARKING_CAPACITY in .env.
    parking_capacity: int = 150
    # Days past expiry a monthly customer's spot stays theirs before returning
    # to the pool. Lines up with the 7/3/1-day reminder cadence: four warnings
    # happen before anyone loses a spot. Override with SPOT_GRACE_DAYS.
    spot_grace_days: int = 3

    # Physical zoning: spots are painted into lettered zones of this size
    # (Madco = 6 zones of 25 -> A1..F25). Purely a DISPLAY label over the integer
    # spot number; the number stays the key. 0 disables zoning (bare numbers).
    # Override with SPOTS_PER_ZONE.
    spots_per_zone: int = 25

    # Lot organization: the first N zones are the MONTHLY area — each monthly truck
    # gets a fixed spot reserved there; the rest is the daily/weekly pool. 1 -> Zone
    # A (spots 1..spots_per_zone). 0 -> no dedicated monthly zone: monthlies still
    # reserve a fixed spot, just taken from anywhere in the pool (lowest free).
    # Override with MONTHLY_ZONE_COUNT.
    monthly_zone_count: int = 1

    # The plaza's own timezone. Every "today" — pass expiry, today's revenue, the
    # daily report — is decided in THIS zone, never the server's. A cloud VM runs
    # on UTC, and without this the business day would roll over at 8pm Michigan
    # time: passes expiring early, evening takings landing on tomorrow.
    timezone: str = "America/Detroit"

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Interactive API docs (/docs, /redoc) + the OpenAPI schema. On in dev for
    # convenience; set DOCS_ENABLED=false in prod so the schema/UI is never served
    # even if the routing topology ever changes to expose a non-/api path.
    docs_enabled: bool = True

    # Base URL the customer-facing app is reachable at — used to build the
    # QR-code verify link printed on each pass (a guard scans it with a phone).
    # Point at the real domain in production.
    public_base_url: str = "http://localhost:3001"

    # Empty until the owner creates a Stripe account and pastes in real keys —
    # card payments stay disabled (not broken) until these are set.
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""

    # POSTed to on every ERROR-level log line (Slack/Discord/ntfy-style webhook).
    # A truck stop has no ops team watching a log file — if payments break at
    # 2am, this is how anyone finds out before an angry driver tells them.
    alert_webhook_url: str = ""

    @field_validator("database_url")
    @classmethod
    def _normalize_db_url(cls, v: str) -> str:
        # Managed Postgres hosts (Neon, Render, Supabase, Heroku) hand out a bare
        # `postgres://` or `postgresql://` URL. SQLAlchemy needs the driver named,
        # and we use psycopg 3 — so normalize to `postgresql+psycopg://`. This lets
        # you paste Neon's connection string straight into DATABASE_URL as-is.
        for prefix in ("postgres://", "postgresql://"):
            if v.startswith(prefix):
                return "postgresql+psycopg://" + v[len(prefix):]
        return v


settings = Settings()
