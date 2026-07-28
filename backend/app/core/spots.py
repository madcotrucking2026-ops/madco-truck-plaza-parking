"""Spot inventory. State is DERIVED: a spot is free iff no live pass holds it.

There is deliberately no stored free/occupied status and no midnight release
job — the moment a pass's holding window lapses, the queries here stop counting
it and the spot is sellable. A crashed cron cannot strand the lot in a stale
state, because there is no cron.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Spot


def ensure_spots(db: Session) -> None:
    """Idempotent: rows exist for 1..capacity, and exactly those are active.
    Shrinking capacity deactivates (never deletes — spots carry history)."""
    existing = {s.number: s for s in db.scalars(select(Spot))}
    for n in range(1, settings.parking_capacity + 1):
        if n not in existing:
            db.add(Spot(number=n, active=True))
        elif not existing[n].active:
            existing[n].active = True
    for n, spot in existing.items():
        if n > settings.parking_capacity and spot.active:
            spot.active = False
    db.commit()
