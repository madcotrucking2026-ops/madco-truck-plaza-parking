import asyncio
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.deps import get_current_user, require_admin, require_manager
from app.core.logging_config import configure_logging, get_logger
from app.core.migrate import upgrade_database
from app.core.scheduler import reminder_scheduler_loop
from app.routers import (
    audit_log,
    auth,
    companies,
    dashboard,
    insights,
    lot_check,
    monthly_customers,
    passes,
    payment_requests,
    payments,
    reminders,
    reports,
    search,
    spots,
    stripe_payments,
    verify,
)

configure_logging()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the automatic renewal-reminder sweep in the background for the life
    # of the app; cancel it cleanly on shutdown.
    task = asyncio.create_task(reminder_scheduler_loop())
    try:
        yield
    finally:
        task.cancel()


app = FastAPI(title="Madco Truck Plaza Parking Management System", lifespan=lifespan)

# Alembic is the ONE schema mechanism — dev SQLite and prod Postgres run the same
# migrations. A pre-Alembic dev database is detected and stamped (see core/migrate.py).
upgrade_database()
# The painted lot exists in the database before the first request: rows for
# spots 1..PARKING_CAPACITY, idempotently (capacity changes are config).
from app.core.database import SessionLocal  # noqa: E402
from app.core.spots import ensure_spots  # noqa: E402

with SessionLocal() as _seed_db:
    ensure_spots(_seed_db)
log.info("Application starting — DB at head, migrations applied.")

# Taking cards with no webhook secret means the safety net is OFF: if a customer's
# phone dies between the charge clearing and the browser telling us about it, we
# keep their money and no pass is ever issued, with nothing to reconcile it. Never
# let that state be silent.
if settings.stripe_secret_key and not settings.stripe_webhook_secret:
    log.warning(
        "STRIPE_WEBHOOK_SECRET is not set — card payments will work, but a charge "
        "whose browser dies before finalize will NOT self-heal. Set it from the "
        "Stripe Dashboard webhook endpoint before taking real money."
    )
if settings.stripe_secret_key.startswith("sk_live_") and not settings.public_base_url.startswith("https://"):
    log.warning("LIVE Stripe key with a non-HTTPS PUBLIC_BASE_URL (%s).", settings.public_base_url)


@app.exception_handler(Exception)
async def _log_unhandled(request: Request, exc: Exception) -> JSONResponse:
    # Any error not already turned into an HTTPException lands here — log it
    # with a traceback so a real failure (payment, renew, etc.) is diagnosable
    # after the fact, and return a clean 500 instead of a raw stack trace.
    log.exception("Unhandled error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(status_code=500, content={"detail": "Something went wrong. Please try again."})

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manager-only routers — every route in these requires a valid login.
# `companies` is deliberately excluded here: it mixes the public `/lookup`
# endpoint (used by the unauthenticated /book kiosk) with manager-only ones,
# so those are protected individually inside companies.py instead.
# `stripe_payments` is deliberately excluded — its create-intent/finalize/
# cancel-intent routes are the kiosk's own payment flow and must stay
# reachable by an anonymous customer; its webhook route is protected by
# Stripe's signature verification instead of a login.
# Role tiers. Any login = the front desk job: issue, renew, look up, remind.
# Manager+ = the money: revenue, payment history, reports, business insights.
# Admin = the owner: staff accounts and the audit trail.
_require_login = [Depends(get_current_user)]
_require_manager = [Depends(require_manager)]
_require_admin = [Depends(require_admin)]

app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(passes.router, dependencies=_require_login)
app.include_router(lot_check.router, dependencies=_require_login)
app.include_router(dashboard.router, dependencies=_require_manager)
app.include_router(insights.router, dependencies=_require_manager)
app.include_router(monthly_customers.router, dependencies=_require_login)
app.include_router(reminders.router, dependencies=_require_login)
# /api/reminders/cron authenticates itself with the scheduler token, not a JWT.
app.include_router(reminders.cron_router)
app.include_router(payments.router, dependencies=_require_manager)
app.include_router(audit_log.router, dependencies=_require_admin)
app.include_router(search.router, dependencies=_require_login)
app.include_router(spots.router, dependencies=_require_login)  # attendants walk the lot
app.include_router(reports.router, dependencies=_require_manager)
app.include_router(stripe_payments.router)
app.include_router(verify.router)  # public — no login (guard scans QR)
# payment_requests: create is manager-only (guarded inside the router); the
# customer self-pay + status-poll routes must stay public, so NOT mounted
# under _require_login.
app.include_router(payment_requests.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
