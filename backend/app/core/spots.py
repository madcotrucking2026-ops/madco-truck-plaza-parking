"""Spot inventory. State is DERIVED: a spot is free iff no live pass holds it.

There is deliberately no stored free/occupied status and no midnight release
job — the moment a pass's holding window lapses, the queries here stop counting
it and the spot is sellable. A crashed cron cannot strand the lot in a stale
state, because there is no cron.
"""

from datetime import timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.clock import business_today
from app.core.config import settings
from app.models import ParkingPass, Spot
from app.models.enums import PassStatus, PassType


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


def holding_filter():
    """Boolean clause: this pass currently HOLDS its spot.

    Daily/weekly hold through their expiry day; monthly also through the grace
    window (a late payment shouldn't cost a regular their spot); cancelled never.
    Evaluated per-query against the plaza's calendar — release at day-rollover
    is implicit, with no job to run and no stored status to drift.
    """
    today = business_today()
    grace_cutoff = today - timedelta(days=settings.spot_grace_days)
    return (
        ParkingPass.spot_id.is_not(None)
        & (ParkingPass.status != PassStatus.cancelled)
        & or_(
            (ParkingPass.pass_type != PassType.monthly) & (ParkingPass.expiration_date >= today),
            (ParkingPass.pass_type == PassType.monthly) & (ParkingPass.expiration_date >= grace_cutoff),
        )
    )


def _held_spot_ids():
    return select(ParkingPass.spot_id).where(holding_filter())


def free_spot_count(db: Session) -> int:
    return db.scalar(
        select(func.count(Spot.id)).where(Spot.active, Spot.id.not_in(_held_spot_ids()))
    ) or 0


def pick_free_spot(db: Session, prefer_spot_id: int | None = None) -> Spot | None:
    """FCFS with a memory: longest-vacant first (NULLS FIRST — a never-used spot
    is the safest bet), so the spot whose truck may still be rolling out is the
    LAST one re-issued. `prefer_spot_id` implements monthly stickiness.

    On Postgres the candidate row is taken FOR UPDATE SKIP LOCKED, so two
    concurrent checkouts cannot be handed the same number — the database
    referees, not application code. SQLite (dev) serializes writes anyway.
    """

    def _locked(stmt):
        if db.get_bind().dialect.name == "postgresql":
            return stmt.with_for_update(skip_locked=True)
        return stmt

    if prefer_spot_id is not None:
        preferred = db.scalar(
            _locked(
                select(Spot).where(
                    Spot.id == prefer_spot_id, Spot.active, Spot.id.not_in(_held_spot_ids())
                )
            )
        )
        if preferred is not None:
            return preferred

    return db.scalar(
        _locked(
            select(Spot)
            .where(Spot.active, Spot.id.not_in(_held_spot_ids()))
            .order_by(Spot.last_vacated_at.asc().nulls_first(), Spot.number.asc())
            .limit(1)
        )
    )
