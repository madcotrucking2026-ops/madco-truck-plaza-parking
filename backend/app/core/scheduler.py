import asyncio

from app.core.logging_config import get_logger

log = get_logger(__name__)

# How often the background loop wakes to run the reminder sweep. The sweep is
# idempotent per day per customer (it won't text anyone twice in a day), so
# running a few times a day is safe and means a reminder still goes out even if
# the server was down at the exact turn of the day.
_SWEEP_INTERVAL_SECONDS = 6 * 60 * 60


def _run_sweep_once() -> None:
    # Lazy imports so this module has no import-time dependency on the DB/routers
    # (avoids circulars and lets the app import cleanly).
    from app.core.database import SessionLocal
    from app.routers.reminders import run_scheduled_reminders

    with SessionLocal() as db:
        run_scheduled_reminders(db, triggered_by="scheduler")


async def reminder_scheduler_loop() -> None:
    log.info("Reminder scheduler started (every %sh).", _SWEEP_INTERVAL_SECONDS // 3600)
    while True:
        try:
            # Run the sync DB sweep off the event loop so it never blocks requests.
            await asyncio.to_thread(_run_sweep_once)
        except Exception:  # noqa: BLE001 — a bad sweep must not kill the loop
            log.exception("Reminder sweep failed; will retry next interval.")
        await asyncio.sleep(_SWEEP_INTERVAL_SECONDS)
