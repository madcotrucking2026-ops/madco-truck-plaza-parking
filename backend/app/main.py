from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.deps import get_current_user, require_admin, require_manager
from app.core.logging_config import configure_logging, get_logger
from app.core.migrate import upgrade_database
from app.routers import (
    audit_log,
    auth,
    companies,
    dashboard,
    export,
    insights,
    lot_check,
    monthly_customers,
    passes,
    payments,
    reminders,
    reports,
    search,
    spots,
)
from app.routers import settings as settings_router  # aliased: `settings` is the config object

configure_logging()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # No background tasks — the renewal-reminder sweep was removed with texting.
    yield


app = FastAPI(
    title="Madco Truck Plaza Parking Management System",
    lifespan=lifespan,
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
)

# Alembic is the ONE schema mechanism — dev SQLite and prod Postgres run the same
# migrations. A pre-Alembic dev database is detected and stamped (see core/migrate.py).
upgrade_database()
# The painted lot exists in the database before the first request: rows for
# spots 1..PARKING_CAPACITY, idempotently (capacity changes are config).
from app.core.database import SessionLocal  # noqa: E402
from app.core.spots import ensure_spots  # noqa: E402

with SessionLocal() as _seed_db:
    from app.core.app_settings import load_overrides  # noqa: E402

    load_overrides(_seed_db)  # saved config overrides win over env before seeding
    ensure_spots(_seed_db)
log.info("Application starting — DB at head, migrations applied.")

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
app.include_router(lot_check.router, dependencies=_require_login)  # cashier walks the lot — needs the truck lookup
app.include_router(dashboard.router, dependencies=_require_manager)
app.include_router(insights.router, dependencies=_require_manager)
app.include_router(monthly_customers.router, dependencies=_require_manager)
app.include_router(reminders.router, dependencies=_require_manager)
app.include_router(payments.router, dependencies=_require_manager)
app.include_router(audit_log.router, dependencies=_require_admin)
app.include_router(export.router, dependencies=_require_admin)  # owner downloads a full CSV backup
app.include_router(search.router, dependencies=_require_manager)
app.include_router(spots.router, dependencies=_require_login)  # attendants walk the lot
app.include_router(reports.router, dependencies=_require_manager)
app.include_router(settings_router.router, dependencies=_require_login)  # GET: any staff (issue-form prices); PUT: admin-only (route dep)
# Customer self-service (the Stripe kiosk and pay-by-QR links) was retired
# 2026-08: the plaza went staff-only, and the cashier records card payments on
# their own terminal. The stripe_payments + payment_requests routers and their
# frontend pages are gone; card/debit are now plain recorded methods like cash.


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
