from pydantic import Field
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

    # Total parking spots on the lot — drives the occupancy / available-spots
    # readout on the dashboard. Override with PARKING_CAPACITY in .env.
    parking_capacity: int = 150

    # The plaza's own timezone. Every "today" — pass expiry, today's revenue, the
    # daily report — is decided in THIS zone, never the server's. A cloud VM runs
    # on UTC, and without this the business day would roll over at 8pm Michigan
    # time: passes expiring early, evening takings landing on tomorrow.
    timezone: str = "America/Detroit"

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Base URL the customer-facing app is reachable at — used to build the
    # QR-code verify link printed on each pass (a guard scans it with a phone).
    # Point at the real domain in production.
    public_base_url: str = "http://localhost:3001"

    # Empty until the owner creates a Stripe account and pastes in real keys —
    # card payments stay disabled (not broken) until these are set.
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""

    # Twilio SMS for monthly renewal reminders. Empty until the owner adds
    # real credentials — reminders are recorded either way (and can be shown /
    # read to the customer), but an actual text is only sent when these are set.
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    # A2P 10DLC best practice: send through the registered Messaging Service
    # (MG...) rather than the raw number, so carrier campaign association is
    # applied correctly. Falls back to the from-number if unset.
    twilio_messaging_service_sid: str = ""

    # Automatic daily renewal-reminder sweep (texts monthly customers 7/3/1
    # days before, then daily once overdue, until they renew). On by default;
    # SMS only actually sends once Twilio creds above are set.
    auto_reminders_enabled: bool = True

    # Shared secret that lets an external cron (the compose `cron` service, a
    # systemd timer, Task Scheduler) trigger the reminder sweep without a JWT.
    # The in-process scheduler only runs while the app is up; the external
    # trigger is the belt-and-braces that survives restarts. Empty = disabled.
    scheduler_token: str = ""

    # POSTed to on every ERROR-level log line (Slack/Discord/ntfy-style webhook).
    # A truck stop has no ops team watching a log file — if payments break at
    # 2am, this is how anyone finds out before an angry driver tells them.
    alert_webhook_url: str = ""


settings = Settings()
