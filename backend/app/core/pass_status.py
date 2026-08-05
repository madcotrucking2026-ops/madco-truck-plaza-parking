from datetime import date, datetime, time

from app.models.enums import PassStatus, PassType

# A daily pass is a truck-stop checkout: good until NOON on its expiry date, not
# the end of the day. Weekly and monthly keep the whole-day model (they expire
# the instant the plaza's date rolls past the expiry date — midnight after).
NOON = time(12, 0)


def pass_expired(pass_type: PassType, expiration_date: date, now: datetime) -> bool:
    """Has this pass's paid window ended, at the plaza clock `now`?

    `now` is the plaza's wall-clock (see clock.business_now) — the caller passes it
    so the daily NOON cutoff can compare the time of day, not just the date."""
    if pass_type == PassType.daily:
        return now >= datetime.combine(expiration_date, NOON)
    return now.date() > expiration_date


def live_status(
    pass_type: PassType,
    expiration_date: date,
    now: datetime,
    stored_status: PassStatus | None = None,
) -> PassStatus:
    if stored_status == PassStatus.cancelled:
        return PassStatus.cancelled
    if pass_expired(pass_type, expiration_date, now):
        return PassStatus.expired
    if (expiration_date - now.date()).days <= 1:
        return PassStatus.expiring_soon
    return PassStatus.active
