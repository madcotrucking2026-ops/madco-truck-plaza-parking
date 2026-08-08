"""Owner-editable runtime config: parking capacity + default prices.

These are env/config defaults, optionally OVERRIDDEN by rows in the app_settings
table (set from the Settings screen). Overrides are loaded onto the in-memory
`settings` object at startup, so every existing reader (`_price_for`,
`ensure_spots`, the dashboard occupancy) keeps reading `settings.x` and simply
sees the effective value. Single-process app, so mutating the global is fine.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import AppSetting

# The knobs the owner can edit, each with the caster from its stored string.
EDITABLE: dict[str, type] = {
    "parking_capacity": int,
    "daily_price": float,
    "weekly_price": float,
    "monthly_price": float,
}


def effective() -> dict:
    """Current live values — the env default unless a saved override replaced it."""
    return {k: getattr(settings, k) for k in EDITABLE}


def load_overrides(db: Session) -> None:
    """Apply saved overrides onto `settings` (called once at startup, so DB values
    win over env). A corrupt stored value is ignored, keeping the env default."""
    for row in db.scalars(select(AppSetting).where(AppSetting.key.in_(EDITABLE))):
        try:
            setattr(settings, row.key, EDITABLE[row.key](row.value))
        except (TypeError, ValueError):
            continue


def save_overrides(db: Session, values: dict) -> None:
    """Upsert {key: value} for EDITABLE keys and apply them to `settings`. The
    caller commits (and re-runs ensure_spots if capacity changed)."""
    for key, val in values.items():
        if key not in EDITABLE:
            continue
        row = db.get(AppSetting, key)
        if row is None:
            db.add(AppSetting(key=key, value=str(val)))
        else:
            row.value = str(val)
        setattr(settings, key, EDITABLE[key](val))
