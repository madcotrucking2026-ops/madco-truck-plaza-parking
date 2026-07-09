import asyncio
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import Base, engine, run_startup_migrations
from app.core.deps import get_current_user
from app.core.logging_config import configure_logging, get_logger
from app.core.scheduler import reminder_scheduler_loop
from app.routers import (
    audit_log,
    auth,
    companies,
    dashboard,
    lot_check,
    monthly_customers,
    passes,
    payment_requests,
    payments,
    reminders,
    reports,
    search,
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

# Local dev convenience: create tables directly from models (SQLite by default).
# Swap for Alembic migrations before pointing this at the production Postgres database.
Base.metadata.create_all(bind=engine)
run_startup_migrations()
log.info("Application starting — DB ready, migrations applied.")


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
_require_login = [Depends(get_current_user)]

app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(passes.router, dependencies=_require_login)
app.include_router(lot_check.router, dependencies=_require_login)
app.include_router(dashboard.router, dependencies=_require_login)
app.include_router(monthly_customers.router, dependencies=_require_login)
app.include_router(reminders.router, dependencies=_require_login)
app.include_router(payments.router, dependencies=_require_login)
app.include_router(audit_log.router, dependencies=_require_login)
app.include_router(search.router, dependencies=_require_login)
app.include_router(reports.router, dependencies=_require_login)
app.include_router(stripe_payments.router)
app.include_router(verify.router)  # public — no login (guard scans QR)
# payment_requests: create is manager-only (guarded inside the router); the
# customer self-pay + status-poll routes must stay public, so NOT mounted
# under _require_login.
app.include_router(payment_requests.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
