"""Spot inventory. State is DERIVED: a spot is free iff no live pass holds it.

There is deliberately no stored free/occupied status and no midnight release
job — the moment a pass's holding window lapses, the queries here stop counting
it and the spot is sellable. A crashed cron cannot strand the lot in a stale
state, because there is no cron.
"""

from datetime import timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.audit import log_audit
from app.core.clock import business_now
from app.core.config import settings
from app.core.pass_status import NOON
from app.models import ParkingPass, Spot
from app.models.enums import AuditAction, PassStatus, PassType


def spot_label(number: int) -> str:
    """Display label for a spot: 1 -> 'A1', 26 -> 'B1', 150 -> 'F25'. The integer
    number stays the stable key (URLs, grid keys, existing passes); this is only
    how it reads on a pass and the board. Falls back to the bare number when
    zoning is off (spots_per_zone <= 0) or the zone index runs past 'Z'."""
    per = settings.spots_per_zone
    if per <= 0:
        return str(number)
    zone_index = (number - 1) // per
    if zone_index > 25:
        return str(number)
    within = (number - 1) % per + 1
    return f"{chr(ord('A') + zone_index)}{within}"


def monthly_spot_limit() -> int:
    """Highest spot number in the MONTHLY area (Zone A by default). 0 when the
    split is off (monthly_zone_count or spots_per_zone is 0) — then nothing is a
    monthly-reserved spot and every spot is in the pooled daily area."""
    return settings.monthly_zone_count * settings.spots_per_zone


def is_monthly_spot(number: int) -> bool:
    """True if this spot number falls in the monthly (reserved) area."""
    return 1 <= number <= monthly_spot_limit()


# Pass types that hold a RESERVED spot in the monthly zone (released only on
# close-out or cancel): monthly and yearly. Daily/weekly are pooled.
_RESERVED_TYPES = (PassType.monthly, PassType.yearly)


def release_reserved_spot(db: Session, vehicle_id: int) -> None:
    """Free a monthly truck's reserved spot(s) back to the pool. Called on
    close-out (the truck is leaving for good) — the ONLY thing that releases a
    reservation; a pass expiring on its own never does."""
    for spot in db.scalars(select(Spot).where(Spot.reserved_vehicle_id == vehicle_id)):
        spot.reserved_vehicle_id = None


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
        spot = pick_free_spot(db, parking_pass.pass_type, parking_pass.vehicle_id)
        if spot is None:
            break  # genuinely more live passes than spots — dashboard shows it
        parking_pass.spot_id = spot.id
        # The session is autoflush=False: without this flush the next
        # pick_free_spot's not-in-held subquery can't see the assignment just
        # made and hands EVERY stray the same spot (live bug: 10 passes on
        # spot 1). Flush publishes each assignment before the next pick.
        db.flush()

    # Reserve the spot each LIVE monthly pass currently sits on, so monthly
    # customers that predate this feature keep their spot under the reservation
    # rules. Idempotent (skips spots already reserved); only touches monthlies
    # still holding a spot — a long-lapsed one is already back in the pool.
    for monthly_pass in db.scalars(
        select(ParkingPass).where(
            ParkingPass.pass_type.in_(_RESERVED_TYPES),
            ParkingPass.spot_id.is_not(None),
            _live_window_filter(),
        )
    ):
        spot = db.get(Spot, monthly_pass.spot_id)
        if spot is not None and spot.reserved_vehicle_id is None:
            spot.reserved_vehicle_id = monthly_pass.vehicle_id

    db.commit()


def _live_window_filter():
    """The date/status part of 'this pass occupies the lot': not cancelled, and
    inside its holding window (daily/weekly through expiry day, monthly through
    expiry + grace). Shared by holding_filter (has a spot) and the startup
    backfill (should have one but doesn't)."""
    now = business_now()
    today = now.date()
    grace_cutoff = today - timedelta(days=settings.spot_grace_days)
    # A daily pass vacates its spot at NOON on its expiry day (client checkout
    # rule): before noon it still holds through today; from noon on, today's daily
    # expiries have released. Weekly holds the whole expiry day (midnight); monthly
    # holds through the grace window.
    daily_holds = (
        ParkingPass.expiration_date >= today
        if now.time() < NOON
        else ParkingPass.expiration_date > today
    )
    return (ParkingPass.status != PassStatus.cancelled) & or_(
        (ParkingPass.pass_type == PassType.daily) & daily_holds,
        (ParkingPass.pass_type == PassType.weekly) & (ParkingPass.expiration_date >= today),
        ParkingPass.pass_type.in_(_RESERVED_TYPES) & (ParkingPass.expiration_date >= grace_cutoff),
    )


def holding_filter():
    """Boolean clause: this pass currently HOLDS its spot.

    Evaluated per-query against the plaza's calendar — release at day-rollover
    is implicit, with no job to run and no stored status to drift.
    """
    return ParkingPass.spot_id.is_not(None) & _live_window_filter()


def _held_spot_ids():
    return select(ParkingPass.spot_id).where(holding_filter())


def _sellable_filter():
    """A spot the system may hand to the NEXT daily/weekly customer: active, not
    held by a live pass, not overstay-flagged, and NOT reserved. A flagged spot
    has a reported squatter physically on it, and selling it sends the next
    arrival straight into the blocked spot the last customer just escaped (staff
    clearing the flag returns it to the pool). A reserved spot belongs to a
    monthly truck and is out of the daily pool even while empty — held for them
    by the reservation, not by a live pass."""
    return (
        Spot.active
        & ~Spot.overstay_reported
        & Spot.reserved_vehicle_id.is_(None)
        & Spot.id.not_in(_held_spot_ids())
    )


def free_spot_count(db: Session) -> int:
    return db.scalar(select(func.count(Spot.id)).where(_sellable_filter())) or 0


def pick_free_spot(
    db: Session,
    pass_type: PassType,
    vehicle_id: int | None,
    prefer_spot_id: int | None = None,
) -> Spot | None:
    """Assign a physical spot, reservation- and type-aware.

    Monthly is per-truck and OWNS its spot: (1) if the truck already has a
    reserved spot, reuse it — renewals never move; (2) else honour a cashier
    `prefer_spot_id` override (any sellable spot); (3) else the lowest-numbered
    free spot in the monthly area; (4) else spill to the lowest-numbered free
    DAILY spot. Steps 2–4 stamp `reserved_vehicle_id` onto the chosen spot.

    Daily/weekly are pooled in the DAILY area only (never a monthly-area or
    reserved spot), using FCFS-with-a-memory: longest-vacant first (NULLS FIRST —
    a never-used spot is the safest bet), so the spot whose truck may still be
    rolling out is the LAST one re-issued. `prefer_spot_id` still honoured.

    Concurrency (Postgres): the candidate row is taken FOR UPDATE SKIP LOCKED,
    then RE-VERIFIED with a fresh statement. The lock alone is not enough: an
    assignment INSERTS a pass but never writes the spot row, so a transaction
    whose snapshot predates a just-committed assignment can lock the released
    row and the engine's row-recheck sees nothing changed — the 110-customer
    swarm sold four spots twice exactly this way. A fresh statement gets a fresh
    snapshot (READ COMMITTED), so the re-verify sees the committed pass and the
    loop moves to the next candidate. SQLite (dev) serializes writers, where
    this is just a cheap second read.
    """

    def _locked(stmt):
        if db.get_bind().dialect.name == "postgresql":
            return stmt.with_for_update(skip_locked=True)
        return stmt

    def _still_free(spot: Spot) -> bool:
        # Fresh statement -> fresh snapshot. The lock we now hold on the spot row
        # blocks rival pickers; this check closes the stale-snapshot window.
        return db.scalar(select(func.count()).where(ParkingPass.spot_id == spot.id, _live_window_filter())) == 0

    def _pick(area_clause, order_by) -> Spot | None:
        """Lock the best candidate in `area_clause`, re-verify on a fresh
        snapshot, and retry the next one if it was resold under our feet.
        Shared by the monthly (number-asc) and daily (longest-vacant) pickers so
        the race-safety is written once."""
        taken: set[int] = set()
        while True:
            candidate = db.scalar(
                _locked(
                    select(Spot)
                    .where(_sellable_filter(), area_clause, Spot.id.not_in(taken))
                    .order_by(*order_by)
                    .limit(1)
                )
            )
            if candidate is None:
                return None
            if _still_free(candidate):
                return candidate
            taken.add(candidate.id)  # resold under our feet — never offer it again this pick

    def _preferred(area_clause=None) -> Spot | None:
        # A cashier override: the exact spot, if it is sellable + still free. When
        # `area_clause` is given the preference must also fall in that area (daily
        # overrides can't reach into the monthly zone). A reserved spot is never
        # sellable, so an override onto another truck's spot simply misses here.
        if prefer_spot_id is None:
            return None
        clause = _sellable_filter() if area_clause is None else (_sellable_filter() & area_clause)
        spot = db.scalar(_locked(select(Spot).where(Spot.id == prefer_spot_id, clause)))
        return spot if spot is not None and _still_free(spot) else None

    limit = monthly_spot_limit()
    in_monthly_area = Spot.number <= limit
    in_daily_area = Spot.number > limit

    if pass_type in _RESERVED_TYPES:
        # 1. Reuse: their own spot is theirs — no lock/re-verify, it can't be sold
        #    out from under them (sellable excludes reserved spots).
        if vehicle_id is not None:
            reused = db.scalar(select(Spot).where(Spot.reserved_vehicle_id == vehicle_id, Spot.active))
            if reused is not None:
                return reused
        # 2. Cashier override to a specific spot (any sellable spot); else
        # 3. lowest free monthly spot; else 4. spill to the lowest free daily spot.
        spot = (
            _preferred()
            or _pick(in_monthly_area, (Spot.number.asc(),))
            or _pick(in_daily_area, (Spot.number.asc(),))
        )
        if spot is not None:
            spot.reserved_vehicle_id = vehicle_id  # stamp the reservation on the locked row
        return spot

    # Daily / weekly: pooled DAILY area only, longest-vacant first. A preference
    # is honoured only when it lands in the daily area on a still-free spot.
    return _preferred(in_daily_area) or _pick(
        in_daily_area, (Spot.last_vacated_at.asc().nulls_first(), Spot.number.asc())
    )


class MoveError(Exception):
    """A move the cashier asked for that can't be honored. `status` is the HTTP
    code the router should surface, `detail` the message the cashier reads."""

    def __init__(self, status: int, detail: str):
        self.status = status
        self.detail = detail
        super().__init__(detail)


def move_pass_to_spot(db: Session, pass_id: int, to_number: int) -> ParkingPass:
    """Cashier override: put a truck in a specific FREE spot.

    Race-safe against the auto-assigner: the target is locked and re-verified free
    with the same mechanism pick_free_spot uses, so a spot handed out in the last
    few seconds raises 409 rather than double-selling. Frees the old spot instantly
    (derived state — no separate release), and audits who moved which truck where.
    Truck-to-truck swapping is intentionally not supported (v1); the target must be
    an open spot.
    """
    parking_pass = db.get(ParkingPass, pass_id)
    if parking_pass is None:
        raise MoveError(404, "Pass not found.")

    target = db.scalar(select(Spot).where(Spot.number == to_number))
    if target is None:
        raise MoveError(404, "No such spot.")
    if parking_pass.spot_id == target.id:
        raise MoveError(400, "That truck is already in that spot.")
    if not target.active:
        raise MoveError(400, "That spot is out of service.")
    if target.overstay_reported:
        raise MoveError(400, "That spot is flagged as blocked — clear it first.")
    if target.reserved_vehicle_id is not None and target.reserved_vehicle_id != parking_pass.vehicle_id:
        raise MoveError(400, "That spot is reserved for another truck.")

    # Lock + fresh-snapshot re-verify, exactly as the auto-assigner does.
    if db.get_bind().dialect.name == "postgresql":
        db.execute(select(Spot.id).where(Spot.id == target.id).with_for_update(skip_locked=True))
    still_free = db.scalar(select(func.count()).where(ParkingPass.spot_id == target.id, _live_window_filter())) == 0
    if not still_free:
        raise MoveError(409, "That spot was just taken — pick another.")

    old = db.get(Spot, parking_pass.spot_id) if parking_pass.spot_id else None
    truck = parking_pass.vehicle.truck_number or parking_pass.vehicle.trailer_number or parking_pass.vehicle.license_plate or "—"
    if old is not None:
        old.last_vacated_at = business_now()
    parking_pass.spot_id = target.id

    # A monthly truck's fixed spot follows the move: release the old spot back to
    # the pool and reserve the target to them. Daily/weekly carry no reservation.
    if parking_pass.pass_type in _RESERVED_TYPES:
        if old is not None:
            old.reserved_vehicle_id = None
        target.reserved_vehicle_id = parking_pass.vehicle_id

    from_label = spot_label(old.number) if old else "no spot"
    log_audit(
        db,
        AuditAction.edited,
        "parking_pass",
        f"Cashier moved {truck} from {from_label} to {spot_label(target.number)}",
        entity_id=parking_pass.id,
    )
    db.commit()
    return parking_pass
