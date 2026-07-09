from datetime import date

from app.models.enums import PassStatus


def live_status(expiration_date: date, today: date, stored_status: PassStatus | None = None) -> PassStatus:
    if stored_status == PassStatus.cancelled:
        return PassStatus.cancelled
    if expiration_date < today:
        return PassStatus.expired
    if (expiration_date - today).days <= 1:
        return PassStatus.expiring_soon
    return PassStatus.active
