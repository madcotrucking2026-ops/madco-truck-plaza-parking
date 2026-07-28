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

    # Backfill: a deployment that predates spots (or a capacity increase after a
    # full-lot day) can have LIVE passes with no spot — the grid would then show
    # a green empty lot while trucks sit on it. Give each one a spot, oldest
    # tenants first. Idempotent: matches nothing once every live pass has one,
    # and NULL-spot afterwards means the genuine full-lot race, which the
    # dashboard surfaces as "paid, awaiting spot".
    strays = db.scalars(
        select(ParkingPass)
        .where(ParkingPass.spot_id.is_(None), _live_window_filter())
        .order_by(ParkingPass.issue_date.asc(), ParkingPass.id.asc())
    ).all()
    for parking_pass in strays:
        spot = pick_free_spot(db)
        if spot is None:
            break  # genuinely more live passes than spots — dashboard shows it
        parking_pass.spot_id = spot.id
        # The session is autoflush=False: without this flush the next
        # pick_free_spot's not-in-held subquery can't see the assignment just
        # made and hands EVERY stray the same spot (live bug: 10 passes on
        # spot 1). Flush publishes each assignment before the next pick.
        db.flush()

    db.commit()


def _live_window_filter():
    """The date/status part of 'this pass occupies the lot': not cancelled, and
    inside its holding window (daily/weekly through expiry day, monthly through
    expiry + grace). Shared by holding_filter (has a spot) and the startup
    backfill (should have one but doesn't)."""
    today = business_today()
    grace_cutoff = today - timedelta(days=settings.spot_grace_days)
    return (ParkingPass.status != PassStatus.cancelled) & or_(
        (ParkingPass.pass_type != PassType.monthly) & (ParkingPass.expiration_date >= today),
        (ParkingPass.pass_type == PassType.monthly) & (ParkingPass.expiration_date >= grace_cutoff),
    )


def holding_filter():
    """Boolean clause: this pass currently HOLDS its spot.

    Evaluated per-query against the plaza's calendar — release at day-rollover
    is implicit, with no job to run and no stored status to drift.
    """
    return ParkingPass.spot_id.is_not(None) & _live_window_filter()


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
