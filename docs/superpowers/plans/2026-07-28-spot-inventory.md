# Spot Inventory & Auto-Assignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The system dispatches parking: every pass gets an auto-assigned numbered spot (FCFS, longest-vacant-first), monthly spots are sticky with a grace window, and a sensor-less overstay flow lets customers self-reassign.

**Architecture:** Derived state — a spot is free iff no live pass holds it (a query, never a stored status; no cron). Assignment runs inside the existing `_issue_pass_and_payment` transaction with `FOR UPDATE SKIP LOCKED` on Postgres. Spec: `docs/superpowers/specs/2026-07-28-spot-inventory-design.md`.

**Tech Stack:** FastAPI, SQLAlchemy 2, Alembic, Postgres/SQLite, Next.js 16, existing pytest fixtures (`db`, `client` in `backend/tests/conftest.py`).

## Global Constraints

- All date logic uses `business_today()` / `business_now()` from `app.core.clock` — NEVER `date.today()`.
- New settings: `spot_grace_days: int = 3` in `app/core/config.py`. Capacity reuses existing `parking_capacity`.
- Alembic is the only schema mechanism: one new revision; no edits to the baseline.
- Follow existing code style: comments explain constraints, not narration; schemas in `app/schemas/`; routers thin, logic in helpers.
- Frontend: Base UI conventions (`render={<Link/>}` needs `nativeButton={false}`); ink-token colours (`--danger-ink` etc.); mono font for numbers.
- Run backend tests from `backend/`: `.venv/Scripts/python.exe -m pytest tests/ -q`.

---

### Task 1: Spot model, migration, idempotent seeding

**Files:**
- Create: `backend/app/models/spot.py`
- Modify: `backend/app/models/__init__.py` (export `Spot`)
- Modify: `backend/app/models/parking_pass.py` (add `spot_id` FK + `spot` relationship)
- Create: `backend/app/core/spots.py` (seeding only in this task; assignment comes in Task 2)
- Modify: `backend/app/main.py` (call `ensure_spots()` after `upgrade_database()`)
- Create: `backend/alembic/versions/<autogen>_spots_and_pass_spot_id.py`
- Test: `backend/tests/test_spots_seed.py`

**Interfaces:**
- Produces: `Spot` model (`id, number, spot_type, active, last_vacated_at, overstay_reported, overstay_reported_at`), `ParkingPass.spot_id / .spot`, `ensure_spots(db) -> None`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_spots_seed.py
"""ensure_spots(): the painted lot exists in the database, sized by config."""
from sqlalchemy import func, select

from app.core.config import settings
from app.core.spots import ensure_spots
from app.models import Spot


def test_seeds_capacity_spots_once(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 300)
    ensure_spots(db)
    ensure_spots(db)  # idempotent — second run adds nothing
    assert db.scalar(select(func.count()).select_from(Spot)) == 300
    assert db.scalar(select(func.min(Spot.number))) == 1
    assert db.scalar(select(func.max(Spot.number))) == 300


def test_capacity_shrink_deactivates_never_deletes(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 300)
    ensure_spots(db)
    monkeypatch.setattr(settings, "parking_capacity", 280)
    ensure_spots(db)
    assert db.scalar(select(func.count()).select_from(Spot)) == 300  # history kept
    assert db.scalar(select(func.count()).select_from(Spot).where(Spot.active)) == 280


def test_capacity_grow_reactivates_and_extends(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 10)
    ensure_spots(db)
    monkeypatch.setattr(settings, "parking_capacity", 12)
    ensure_spots(db)
    assert db.scalar(select(func.count()).select_from(Spot).where(Spot.active)) == 12
```

- [ ] **Step 2: Run to verify failure** — `pytest tests/test_spots_seed.py -q` → FAIL (`ImportError: Spot`).

- [ ] **Step 3: Implement**

```python
# backend/app/models/spot.py
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Spot(Base):
    """One painted spot. Free/occupied is NEVER stored here — it is derived from
    live passes (core/spots.py), so it cannot drift from the money records."""

    __tablename__ = "spots"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    spot_type: Mapped[str] = mapped_column(String(32), default="standard")
    # Capacity changes deactivate/reactivate; rows are never deleted (history).
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    # NULL = never occupied -> sorts as "vacant longest" (NULLS FIRST).
    last_vacated_at: Mapped[datetime | None] = mapped_column(DateTime)
    overstay_reported: Mapped[bool] = mapped_column(Boolean, default=False)
    overstay_reported_at: Mapped[datetime | None] = mapped_column(DateTime)
```

```python
# backend/app/models/parking_pass.py — add alongside existing columns:
    spot_id: Mapped[int | None] = mapped_column(ForeignKey("spots.id"), index=True)
    spot: Mapped["Spot | None"] = relationship()
# (add `Spot` to the TYPE_CHECKING imports; ForeignKey already imported)
```

```python
# backend/app/models/__init__.py — add:
from app.models.spot import Spot
# and "Spot" to __all__
```

```python
# backend/app/core/spots.py
"""Spot inventory. State is DERIVED: a spot is free iff no live pass holds it."""
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
```

```python
# backend/app/main.py — after upgrade_database():
from app.core.spots import ensure_spots
from app.core.database import SessionLocal

with SessionLocal() as _db:
    ensure_spots(_db)
```

- [ ] **Step 4: Generate the migration** — `.venv/Scripts/python.exe -m alembic revision --autogenerate -m "spots and pass spot_id"`, inspect it (spots table + parking_passes.spot_id only), then `pytest tests/ -q` → all pass (the `db` fixture uses `create_all`, migration is exercised by startup).

- [ ] **Step 5: Commit** — `git add -A && git commit -m "feat(spots): inventory table, pass FK, idempotent capacity seeding"`.

---

### Task 2: Holding predicate + free-spot picker

**Files:**
- Modify: `backend/app/core/spots.py`
- Modify: `backend/app/core/config.py` (add `spot_grace_days: int = 3`)
- Test: `backend/tests/test_spot_holding.py`

**Interfaces:**
- Consumes: `Spot`, `ParkingPass.spot_id` (Task 1).
- Produces: `holding_filter()` (SQLAlchemy boolean clause: pass currently holds its spot), `pick_free_spot(db, prefer_spot_id: int | None = None) -> Spot | None`, `free_spot_count(db) -> int`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_spot_holding.py
"""A spot is held while its pass is live: daily through expiry day, monthly
through expiry + grace, cancelled never. Assignment prefers longest-vacant."""
from datetime import timedelta

from app.core.clock import business_now, business_today
from app.core.config import settings
from app.core.spots import ensure_spots, free_spot_count, pick_free_spot
from app.models.enums import PassStatus, PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment


def _issue(db, truck, ptype=PassType.daily, days=1, price=None):
    return _issue_pass_and_payment(
        db, company_name=f"Co {truck}", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number=truck, trailer_number=None, license_plate=None, pass_type=ptype,
        issue_date=business_today(), end_date=business_today() + timedelta(days=days),
        price_override=price, payment_method=PaymentMethod.cash, check_number=None,
    )


def test_live_pass_holds_its_spot(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 2)
    ensure_spots(db)
    _issue(db, "T1"); db.commit()
    assert free_spot_count(db) == 1


def test_cancelled_pass_frees_immediately(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 1)
    ensure_spots(db)
    p = _issue(db, "T1"); db.commit()
    p.status = PassStatus.cancelled; db.commit()
    assert free_spot_count(db) == 1


def test_expired_monthly_holds_through_grace(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 1)
    monkeypatch.setattr(settings, "spot_grace_days", 3)
    ensure_spots(db)
    p = _issue(db, "T1", ptype=PassType.monthly, days=30, price=250); db.commit()
    p.expiration_date = business_today() - timedelta(days=2); db.commit()  # 2d overdue
    assert free_spot_count(db) == 0  # inside grace: still theirs
    p.expiration_date = business_today() - timedelta(days=4); db.commit()  # 4d overdue
    assert free_spot_count(db) == 1  # grace over: pool


def test_picker_prefers_longest_vacant(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 3)
    ensure_spots(db)
    spots = {s.number: s for s in db.query(__import__("app.models", fromlist=["Spot"]).Spot)}
    spots[1].last_vacated_at = business_now()                      # just vacated
    spots[2].last_vacated_at = business_now() - timedelta(days=9)  # long vacant
    db.commit()                                                    # 3 never occupied
    assert pick_free_spot(db).number == 3   # NULLS FIRST
    spots[3].last_vacated_at = business_now(); db.commit()
    assert pick_free_spot(db).number == 2   # then oldest vacancy


def test_picker_honors_preference_when_free(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 3)
    ensure_spots(db)
    preferred = db.query(__import__("app.models", fromlist=["Spot"]).Spot).filter_by(number=2).one()
    assert pick_free_spot(db, prefer_spot_id=preferred.id).number == 2
```

- [ ] **Step 2: Run** — `pytest tests/test_spot_holding.py -q` → FAIL (`ImportError`). NOTE: `_issue_pass_and_payment` does not assign spots yet — the first three tests also FAIL after implementing helpers; that is expected and fixed in Task 3. Mark them `@pytest.mark.xfail(strict=True, reason="assignment lands in Task 3")` for THIS commit and remove the marks in Task 3.

- [ ] **Step 3: Implement**

```python
# backend/app/core/config.py — with the other business settings:
    # Days past expiry a monthly customer's spot stays theirs before returning
    # to the pool. Lines up with the 7/3/1-day reminder cadence.
    spot_grace_days: int = 3
```

```python
# backend/app/core/spots.py — append:
from datetime import timedelta

from sqlalchemy import func, or_, select

from app.core.clock import business_today
from app.models import ParkingPass, Spot
from app.models.enums import PassStatus, PassType


def holding_filter():
    """Boolean clause: this pass currently HOLDS its spot. Daily/weekly hold
    through their expiry day; monthly also through the grace window; cancelled
    never. Derived per-query — there is deliberately no stored status to drift."""
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


def _held_spot_ids(db):
    return select(ParkingPass.spot_id).where(holding_filter())


def free_spot_count(db) -> int:
    return db.scalar(
        select(func.count(Spot.id)).where(Spot.active, Spot.id.not_in(_held_spot_ids(db)))
    ) or 0


def pick_free_spot(db, prefer_spot_id: int | None = None) -> Spot | None:
    """FCFS with a memory: longest-vacant first, so a spot whose truck may still
    be rolling out is the LAST one re-issued. `prefer_spot_id` = monthly sticky.
    On Postgres the row is locked SKIP LOCKED so concurrent checkouts can't
    collide; SQLite serializes writes anyway."""
    def _locked(stmt):
        if db.bind.dialect.name == "postgresql":
            return stmt.with_for_update(skip_locked=True)
        return stmt

    if prefer_spot_id is not None:
        preferred = db.scalar(_locked(
            select(Spot).where(
                Spot.id == prefer_spot_id, Spot.active, Spot.id.not_in(_held_spot_ids(db))
            )
        ))
        if preferred is not None:
            return preferred

    return db.scalar(_locked(
        select(Spot)
        .where(Spot.active, Spot.id.not_in(_held_spot_ids(db)))
        .order_by(Spot.last_vacated_at.asc().nulls_first(), Spot.number.asc())
        .limit(1)
    ))
```

- [ ] **Step 4: Run** — picker/preference tests PASS, the three xfail'd holding tests XFAIL. `pytest tests/ -q` green overall.

- [ ] **Step 5: Commit** — `git commit -m "feat(spots): holding predicate, grace window, longest-vacant-first picker"`.

---

### Task 3: Assign at issue time (+ sticky monthly, full-lot never blocks paid money)

**Files:**
- Modify: `backend/app/routers/passes.py` (`_issue_pass_and_payment`)
- Modify: `backend/tests/test_spot_holding.py` (remove Task-2 xfail marks)
- Test: `backend/tests/test_spot_assignment.py`

**Interfaces:**
- Consumes: `pick_free_spot` (Task 2).
- Produces: every pass issued through `_issue_pass_and_payment` carries `spot_id` (or None when the lot is full); monthly reuse of the company's previous spot.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_spot_assignment.py
"""Assignment is part of issuing a pass — same transaction, no separate step."""
from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.core.spots import ensure_spots
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment, apply_renewal


def _issue(db, truck, company=None, ptype=PassType.daily, days=1, price=None):
    return _issue_pass_and_payment(
        db, company_name=company or f"Co {truck}", phone="313-555-0100",
        vehicle_type=VehicleType.truck, truck_number=truck, trailer_number=None,
        license_plate=None, pass_type=ptype, issue_date=business_today(),
        end_date=business_today() + timedelta(days=days), price_override=price,
        payment_method=PaymentMethod.cash, check_number=None,
    )


def test_issue_assigns_a_spot(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    p = _issue(db, "T1"); db.commit()
    assert p.spot is not None and 1 <= p.spot.number <= 5


def test_two_passes_two_spots(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    a = _issue(db, "T1"); b = _issue(db, "T2"); db.commit()
    assert a.spot_id != b.spot_id


def test_renewal_keeps_the_spot(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    p = _issue(db, "T1"); db.commit()
    before = p.spot_id
    apply_renewal(db, p, business_today() + timedelta(days=3), PaymentMethod.cash)
    db.commit()
    assert p.spot_id == before


def test_returning_monthly_gets_their_old_spot(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    old = _issue(db, "M1", company="Sticky Freight", ptype=PassType.monthly, days=30, price=250)
    db.commit()
    old_spot = old.spot_id
    old.expiration_date = business_today() - timedelta(days=10)  # long lapsed, past grace
    db.commit()
    new = _issue(db, "M1", company="Sticky Freight", ptype=PassType.monthly, days=30, price=250)
    db.commit()
    assert new.spot_id == old_spot


def test_full_lot_issues_pass_with_no_spot(db, monkeypatch):
    """Money already taken must NEVER fail for lack of a spot — pass issues with
    spot_id NULL and staff resolve it (dashboard chip, Task 7)."""
    monkeypatch.setattr(settings, "parking_capacity", 1)
    ensure_spots(db)
    _issue(db, "T1"); db.commit()
    p2 = _issue(db, "T2"); db.commit()
    assert p2.spot_id is None
    assert p2.receipt_number  # the pass itself is fully valid
```

- [ ] **Step 2: Run** — FAIL (`p.spot is None`).

- [ ] **Step 3: Implement** — in `_issue_pass_and_payment` (backend/app/routers/passes.py), after the ParkingPass object is constructed and before the final flush/receipt block, add:

```python
    # Assign the physical spot in the SAME transaction that records the money.
    # Monthly customers are sticky: their previous spot is preferred if free.
    prefer = None
    if pass_type == PassType.monthly and company is not None:
        prev = db.scalar(
            select(ParkingPass.spot_id)
            .where(ParkingPass.company_id == company.id, ParkingPass.spot_id.is_not(None))
            .order_by(ParkingPass.id.desc())
            .limit(1)
        )
        prefer = prev
    spot = pick_free_spot(db, prefer_spot_id=prefer)
    # Full lot: never block a pass over space — spot stays NULL and the
    # dashboard surfaces "paid, awaiting spot" for staff (kiosk pre-checks
    # capacity, so this is a rare race, not a flow).
    parking_pass.spot = spot
```

with `from app.core.spots import pick_free_spot` added to imports. Remove the three `xfail` marks from `tests/test_spot_holding.py`.

- [ ] **Step 4: Run** — `pytest tests/ -q` → ALL green (including the un-xfail'd holding tests).

- [ ] **Step 5: Commit** — `git commit -m "feat(spots): auto-assign at issue, sticky monthly, full lot never blocks paid money"`.

---

### Task 4: Kiosk pre-check — refuse checkout when the lot is full

**Files:**
- Modify: `backend/app/routers/stripe_payments.py` (`create_intent`)
- Modify: `backend/app/routers/payment_requests.py` (`create_intent` for pay-links)
- Test: `backend/tests/test_full_lot_checkout.py`

**Interfaces:**
- Consumes: `free_spot_count` (Task 2).
- Produces: 409 `"The lot is full right now — please check back later."` from both intent-creation endpoints when no spot is free.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_full_lot_checkout.py
"""Never take a card for a spot that doesn't exist. Pre-check at intent time."""
from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.core.spots import ensure_spots
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment


def test_kiosk_refuses_when_full(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 1)
    monkeypatch.setattr("app.routers.stripe_payments.is_configured", lambda: True)
    ensure_spots(db)
    _issue_pass_and_payment(
        db, company_name="Filler", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number="F1", trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=business_today(), end_date=business_today() + timedelta(days=1),
        price_override=None, payment_method=PaymentMethod.cash, check_number=None,
    )
    db.commit()
    r = client.post("/api/payments/stripe/create-intent", json={
        "client_request_id": "abc123", "company_name": "Latecomer", "phone": "313-555-0101",
        "vehicle_type": "truck", "truck_number": "L1", "pass_type": "daily",
        "issue_date": business_today().isoformat(),
    })
    assert r.status_code == 409
    assert "full" in r.json()["detail"].lower()
```

- [ ] **Step 2: Run** — FAIL (Stripe create reached / non-409).

- [ ] **Step 3: Implement** — first line of both `create_intent` bodies, after `_require_configured()`:

```python
    if free_spot_count(db) == 0:
        raise HTTPException(status_code=409, detail="The lot is full right now — please check back later.")
```

(import `free_spot_count` from `app.core.spots` in both routers).

- [ ] **Step 4: Run** — `pytest tests/ -q` → green.
- [ ] **Step 5: Commit** — `git commit -m "feat(spots): refuse checkout when the lot is full"`.

---

### Task 5: Report-occupied endpoint (self-service reassign + overstay flag)

**Files:**
- Modify: `backend/app/routers/verify.py`
- Modify: `backend/app/schemas/verify.py` (add `spot_number` to `PassVerifyResult`; add `ReassignResult`)
- Test: `backend/tests/test_report_occupied.py`

**Interfaces:**
- Consumes: `pick_free_spot`, `holding_filter` (Task 2); existing `verify_pass_token` HMAC.
- Produces: `POST /api/verify/{token}/report-occupied` → `{spot_number: int}`; old spot flagged `overstay_reported` + sent to back of queue; 409 when lot full; 404 bad token.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_report_occupied.py
"""Customer finds a squatter in their assigned spot: one tap moves them and
flags the spot for staff. Public, HMAC-token-authed — works at 3am."""
from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.core.pass_token import make_pass_token
from app.core.spots import ensure_spots
from app.models import Spot
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment


def _issue(db, truck):
    return _issue_pass_and_payment(
        db, company_name=f"Co {truck}", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number=truck, trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=business_today(), end_date=business_today() + timedelta(days=1),
        price_override=None, payment_method=PaymentMethod.cash, check_number=None,
    )


def test_reassigns_and_flags_old_spot(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 3)
    ensure_spots(db)
    p = _issue(db, "T1"); db.commit()
    old_spot_id = p.spot_id
    r = client.post(f"/api/verify/{make_pass_token(p.id)}/report-occupied")
    assert r.status_code == 200
    db.expire_all()
    assert p.spot_id != old_spot_id
    old = db.get(Spot, old_spot_id)
    assert old.overstay_reported is True
    assert old.last_vacated_at is not None  # back of the assignment queue
    assert r.json()["spot_number"] == p.spot.number


def test_full_lot_says_see_the_desk(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 1)
    ensure_spots(db)
    p = _issue(db, "T1"); db.commit()
    r = client.post(f"/api/verify/{make_pass_token(p.id)}/report-occupied")
    assert r.status_code == 409


def test_forged_token_is_404(db, client):
    assert client.post("/api/verify/not-a-token/report-occupied").status_code == 404
```

- [ ] **Step 2: Run** — FAIL (405/404 route missing).

- [ ] **Step 3: Implement** — in `backend/app/routers/verify.py`:

```python
@router.post("/{token}/report-occupied", response_model=ReassignResult, dependencies=[Depends(lookup_limiter)])
def report_occupied(token: str, db: Session = Depends(get_db)) -> ReassignResult:
    """The asphalt gap: no sensors, so an expired truck can still sit in a spot
    the system already resold. The customer standing in front of it taps once:
    old spot flagged for staff AND sent to the back of the assignment queue,
    new spot issued, pass updated — no phone call, no desk, no waiting."""
    pass_id = verify_pass_token(token)
    parking_pass = db.get(ParkingPass, pass_id) if pass_id is not None else None
    if parking_pass is None or parking_pass.spot_id is None:
        raise HTTPException(status_code=404, detail="Pass not found.")

    old = db.get(Spot, parking_pass.spot_id)
    replacement = pick_free_spot(db)
    if replacement is None or replacement.id == old.id:
        raise HTTPException(status_code=409, detail="No other spots are open — please see the front desk.")

    old.overstay_reported = True
    old.overstay_reported_at = business_now()
    old.last_vacated_at = business_now()
    parking_pass.spot = replacement
    log_audit(db, AuditAction.edited, "parking_pass",
              f"Spot {old.number} reported occupied — reassigned to {replacement.number}",
              entity_id=parking_pass.id)
    db.commit()
    return ReassignResult(spot_number=replacement.number)
```

Schema additions in `backend/app/schemas/verify.py`:

```python
class ReassignResult(BaseModel):
    spot_number: int
# and on PassVerifyResult:
    spot_number: int | None = None
```

Populate `spot_number=parking_pass.spot.number if parking_pass.spot else None` in the existing `verify_pass` return. Imports: `business_now`, `pick_free_spot`, `Spot`, `log_audit`, `AuditAction`, `lookup_limiter`.

- [ ] **Step 4: Run** — `pytest tests/ -q` → green.
- [ ] **Step 5: Commit** — `git commit -m "feat(spots): self-service report-occupied reassign with overstay flag"`.

---

### Task 6: Lot state endpoint (`GET /api/spots`)

**Files:**
- Create: `backend/app/routers/spots.py`
- Create: `backend/app/schemas/spot.py`
- Modify: `backend/app/main.py` (include router, `_require_login` tier)
- Test: `backend/tests/test_spots_endpoint.py`

**Interfaces:**
- Consumes: `holding_filter` (Task 2).
- Produces: `GET /api/spots` → `[{number, state, company_name, truck_number, pass_id, expiration_date}]` where `state ∈ free|occupied|expiring|grace|overstay|inactive`; also `POST /api/spots/{number}/clear-overstay` (any logged-in role — it's lot work).

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_spots_endpoint.py
"""One call paints the whole lot. States derived, matching the holding rules."""
from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.core.spots import ensure_spots
from app.models import Spot
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment


def _auth(client):
    r = client.post("/api/auth/register",
                    json={"name": "Owner", "email": "o@x.com", "password": "ownerpass123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _issue(db, truck, ptype=PassType.daily, days=1, price=None):
    return _issue_pass_and_payment(
        db, company_name=f"Co {truck}", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number=truck, trailer_number=None, license_plate=None, pass_type=ptype,
        issue_date=business_today(), end_date=business_today() + timedelta(days=days),
        price_override=price, payment_method=PaymentMethod.cash, check_number=None,
    )


def test_states_cover_the_lot(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 4)
    monkeypatch.setattr(settings, "spot_grace_days", 3)
    ensure_spots(db)
    headers = _auth(client)

    occupied = _issue(db, "T1", days=5)            # comfortably live
    expiring = _issue(db, "T2", days=1)            # expires tomorrow
    monthly = _issue(db, "T3", ptype=PassType.monthly, days=30, price=250)
    db.commit()
    monthly.expiration_date = business_today() - timedelta(days=1)  # in grace
    db.commit()

    spots = {s["number"]: s for s in client.get("/api/spots", headers=headers).json()}
    assert spots[occupied.spot.number]["state"] == "occupied"
    assert spots[expiring.spot.number]["state"] == "expiring"
    assert spots[monthly.spot.number]["state"] == "grace"
    free = [s for s in spots.values() if s["state"] == "free"]
    assert len(free) == 1 and free[0]["company_name"] is None


def test_overstay_state_and_clear(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 2)
    ensure_spots(db)
    headers = _auth(client)
    spot = db.query(Spot).filter_by(number=1).one()
    spot.overstay_reported = True
    db.commit()
    spots = {s["number"]: s for s in client.get("/api/spots", headers=headers).json()}
    assert spots[1]["state"] == "overstay"
    assert client.post("/api/spots/1/clear-overstay", headers=headers).status_code == 200
    db.expire_all()
    assert spot.overstay_reported is False
```

- [ ] **Step 2: Run** — FAIL (404).

- [ ] **Step 3: Implement**

```python
# backend/app/schemas/spot.py
from datetime import date

from pydantic import BaseModel


class SpotState(BaseModel):
    number: int
    state: str  # free | occupied | expiring | grace | overstay | inactive
    company_name: str | None = None
    truck_number: str | None = None
    pass_id: int | None = None
    expiration_date: date | None = None
```

```python
# backend/app/routers/spots.py
"""The lot, painted by query. `expiring` = holder's last day is today or
tomorrow; `grace` = monthly past expiry but inside the grace window."""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clock import business_today
from app.core.database import get_db
from app.core.spots import holding_filter
from app.models import ParkingPass, Spot
from app.schemas.spot import SpotState

router = APIRouter(prefix="/api/spots", tags=["spots"])


@router.get("", response_model=list[SpotState])
def lot_state(db: Session = Depends(get_db)) -> list[SpotState]:
    today = business_today()
    holders = {
        p.spot_id: p
        for p in db.scalars(select(ParkingPass).where(holding_filter()))
    }
    out: list[SpotState] = []
    for spot in db.scalars(select(Spot).order_by(Spot.number)):
        p = holders.get(spot.id)
        if not spot.active:
            state = "inactive"
        elif spot.overstay_reported:
            state = "overstay"
        elif p is None:
            state = "free"
        elif p.expiration_date < today:
            state = "grace"                    # only monthlies can hold past expiry
        elif p.expiration_date <= today + timedelta(days=1):
            state = "expiring"
        else:
            state = "occupied"
        out.append(SpotState(
            number=spot.number, state=state,
            company_name=p.company.name if p and p.company else None,
            truck_number=p.vehicle.truck_number if p and p.vehicle else None,
            pass_id=p.id if p else None,
            expiration_date=p.expiration_date if p else None,
        ))
    return out


@router.post("/{number}/clear-overstay")
def clear_overstay(number: int, db: Session = Depends(get_db)) -> dict:
    spot = db.scalar(select(Spot).where(Spot.number == number))
    if spot is None:
        raise HTTPException(status_code=404, detail="No such spot.")
    spot.overstay_reported = False
    spot.overstay_reported_at = None
    db.commit()
    return {"cleared": True}
```

`backend/app/main.py`: `app.include_router(spots.router, dependencies=_require_login)` (attendants walk the lot) + import.

- [ ] **Step 4: Run** — `pytest tests/ -q` → green.
- [ ] **Step 5: Commit** — `git commit -m "feat(spots): lot state endpoint + overstay clear"`.

---

### Task 7: Spot number on ticket, kiosk confirmation, verify page (+ occupied button)

**Files:**
- Modify: `frontend/src/lib/api.ts` (`PassRead`/`PassListItem` gain `spot_number: number | null`; `PassVerifyResult` too; add `ReassignResult`)
- Modify: `backend/app/schemas/pass_.py` (`PassRead`/`PassListItem`: `spot_number: int | None = None`; populate from `spot.number` — add a `@computed_field` or set in routers via `from_attributes` property on model: simplest is a `spot_number` property on `ParkingPass` returning `self.spot.number if self.spot else None`)
- Modify: `frontend/src/components/passes/pass-ticket.tsx` (hero spot block)
- Modify: `frontend/src/app/verify/[token]/page.tsx` (show spot + "Spot occupied?" button)
- Test: `backend/tests/test_pass_read_spot.py` + existing vitest suite stays green

**Interfaces:**
- Consumes: Tasks 3, 5.
- Produces: every pass surface shows "PARK IN SPOT N"; verify page can self-reassign.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_pass_read_spot.py
from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.core.spots import ensure_spots
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment
from app.schemas.pass_ import PassRead


def test_pass_read_carries_spot_number(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    p = _issue_pass_and_payment(
        db, company_name="Co", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number="T1", trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=business_today(), end_date=business_today() + timedelta(days=1),
        price_override=None, payment_method=PaymentMethod.cash, check_number=None,
    )
    db.commit()
    assert PassRead.model_validate(p).spot_number == p.spot.number
```

- [ ] **Step 2: Run** — FAIL (`spot_number` missing).

- [ ] **Step 3: Implement** — model property + schema field:

```python
# backend/app/models/parking_pass.py
    @property
    def spot_number(self) -> int | None:
        return self.spot.number if self.spot else None
```

```python
# backend/app/schemas/pass_.py — on PassRead AND PassListItem:
    spot_number: int | None = None
```

(`model_config = ConfigDict(from_attributes=True)` already reads properties. `PassListItem` is hand-built in `passes.py` list endpoint — add `spot_number=p.spot_number` there.)

Frontend `pass-ticket.tsx` — insert as the FIRST block of the ticket body:

```tsx
{pass.spot_number != null && (
  <div className="rounded-xl bg-[var(--forest-700)] p-4 text-center">
    <p className="text-xs font-semibold uppercase tracking-widest text-[var(--ivory-100)]/70">
      Park in spot
    </p>
    <p className="font-mono text-5xl font-bold tabular-nums text-[var(--ivory-100)]">
      {pass.spot_number}
    </p>
  </div>
)}
```

Verify page (`verify/[token]/page.tsx`) — show the same block from `result.spot_number`, plus below it:

```tsx
{result.valid && result.spot_number != null && (
  <Button
    variant="outline"
    className="w-full"
    disabled={reassigning}
    onClick={async () => {
      setReassigning(true);
      try {
        const r = await api.post<ReassignResult>(`/api/verify/${token}/report-occupied`, {});
        toast.success(`New spot: ${r.spot_number}. Sorry about that — staff have been notified.`);
        load(); // re-fetch the verify payload so the page shows the new spot
      } catch (err) {
        toast.error(err instanceof ApiError ? err.message : "Couldn't reassign — please see the front desk.");
      } finally {
        setReassigning(false);
      }
    }}
  >
    Spot occupied? Get a new one
  </Button>
)}
```

(`const [reassigning, setReassigning] = useState(false);` — follow the page's existing load/refetch shape.)

- [ ] **Step 4: Verify** — `pytest tests/ -q` green; `cd frontend && npx tsc --noEmit` clean; Playwright hand-check: issue a cash pass at `/passes/issue`, ticket shows the forest "PARK IN SPOT N" block; open its QR verify URL, tap "Spot occupied?", page shows the NEW number.
- [ ] **Step 5: Commit** — `git commit -m "feat(spots): spot number on ticket and verify page, self-service reassign button"`.

---

### Task 8: Dashboard lot grid + overstay chip; Lot Check shows the spot

**Files:**
- Create: `frontend/src/components/dashboard/lot-grid.tsx`
- Modify: `frontend/src/app/page.tsx` (grid replaces the occupancy sub-card; overstay chip above stats when any `state === "overstay"`)
- Modify: `frontend/src/lib/api.ts` (`SpotState` type)
- Modify: `backend/app/routers/lot_check.py` + `backend/app/schemas/pass_.py` (`LotCheckResult.spot_number`)
- Modify: `frontend/src/app/lot-check/page.tsx` (spot in verdict card)
- Test: extend `backend/tests/test_lot_check.py`

**Interfaces:**
- Consumes: `GET /api/spots` (Task 6), `spot_number` fields (Task 7).

- [ ] **Step 1: Failing test (lot check)**

```python
# append to backend/tests/test_lot_check.py
def test_lot_check_names_the_spot(db, monkeypatch):
    from app.core.config import settings
    from app.core.spots import ensure_spots
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    p = _issue(db, "7911")
    db.commit()
    assert lot_check(q="7911", db=db).spot_number == p.spot.number
```

- [ ] **Step 2: Run** — FAIL. **Step 3:** add `spot_number: int | None = None` to `LotCheckResult`, populate `spot_number=parking_pass.spot_number` in `lot_check()`; surface in the lot-check page verdict card (`Spot {result.spot_number}` in the detail rows, mono font). **Step 4:** `pytest tests/ -q` green.

- [ ] **Step 5: Lot grid component**

```tsx
// frontend/src/components/dashboard/lot-grid.tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type SpotState } from "@/lib/api";

const STATE_CLASS: Record<string, string> = {
  free: "bg-[var(--success)]/25",
  occupied: "bg-[var(--forest-700)]",
  expiring: "bg-[var(--warning)]/70",
  grace: "bg-[var(--amber-500)]/50",
  overstay: "bg-[var(--danger)]",
  inactive: "bg-black/10",
};

/** The whole lot at a glance: 300 cells, colour = derived state, tap = the pass. */
export function LotGrid() {
  const [spots, setSpots] = useState<SpotState[] | null>(null);
  useEffect(() => {
    api.get<SpotState[]>("/api/spots").then(setSpots).catch(() => setSpots(null));
  }, []);
  if (!spots) return null;

  return (
    <div className="card-paper rounded-2xl p-4">
      <div className="grid grid-cols-15 gap-1 sm:grid-cols-20">
        {spots.map((s) => {
          const cell = (
            <div
              title={`Spot ${s.number}${s.company_name ? ` — ${s.company_name}` : ""} (${s.state})`}
              className={`flex aspect-square items-center justify-center rounded font-mono text-[9px] tabular-nums ${STATE_CLASS[s.state]} ${s.state === "occupied" || s.state === "overstay" ? "text-[var(--ivory-100)]" : "text-[var(--cream-foreground)]/70"}`}
            >
              {s.number}
            </div>
          );
          return s.pass_id ? (
            <Link key={s.number} href={`/passes?q=${s.truck_number ?? ""}`}>{cell}</Link>
          ) : (
            <span key={s.number}>{cell}</span>
          );
        })}
      </div>
    </div>
  );
}
```

Add `SpotState` to `api.ts` mirroring the backend schema. Mount `<LotGrid />` in `page.tsx` under the stat cards; add an overstay chip above stats when `spots.some(s => s.state === "overstay")` — reuse the stranded-charge banner styling, linking each flagged number to Lot Check, with a "Cleared" button calling `POST /api/spots/{n}/clear-overstay`. Tailwind v4: define `grid-cols-15`/`grid-cols-20` via arbitrary values `grid-cols-[repeat(15,minmax(0,1fr))]` if the named classes don't exist.

- [ ] **Step 6: Verify** — `npx tsc --noEmit` clean; browser: dashboard shows the grid, colours match seeded data, overstay chip appears when a spot is flagged (flag one via the report-occupied flow), "Cleared" clears it.
- [ ] **Step 7: Commit** — `git commit -m "feat(spots): dashboard lot grid, overstay chip, lot-check spot"`.

---

### Task 9: Morning report — overstays to chase

**Files:**
- Modify: `backend/app/routers/insights.py` (`morning_report`)
- Test: extend `backend/tests/test_morning_report.py`

**Interfaces:**
- Consumes: `Spot.overstay_reported` (Task 5), CallItem shape (existing).
- Produces: one `CallItem(priority="today", kind="overstay")` per flagged spot.

- [ ] **Step 1: Failing test**

```python
# append to backend/tests/test_morning_report.py
def test_overstays_make_the_morning_report(db, monkeypatch):
    from app.core.config import settings
    from app.core.spots import ensure_spots
    from app.models import Spot
    monkeypatch.setattr(settings, "parking_capacity", 3)
    ensure_spots(db)
    spot = db.query(Spot).filter_by(number=2).one()
    spot.overstay_reported = True
    db.commit()

    calls = morning_report(db=db, _user=_FakeUser()).calls
    overstay = next(c for c in calls if c.kind == "overstay")
    assert overstay.priority == "today"
    assert "Spot 2" in overstay.reason
```

- [ ] **Step 2: Run** — FAIL. **Step 3:** in `morning_report`, after the expiring-passes block:

```python
    # 2b. Spots a customer reported blocked — a truck squatting past its pass.
    for spot in db.scalars(select(Spot).where(Spot.overstay_reported)):
        calls.append(CallItem(
            priority="today", kind="overstay", company_id=None,
            company_name=f"Spot {spot.number}", phone=None,
            reason=f"Spot {spot.number} reported occupied by an expired truck — go move it along",
            amount=None,
        ))
```

(import `Spot`; `kind` is a free string in the schema — no enum change.)

- [ ] **Step 4: Run** — `pytest tests/ -q` green. **Step 5: Commit** — `git commit -m "feat(spots): overstays surface in the morning report"`.

---

### Task 10: E2E proof + docs + memory

**Files:**
- Modify: `DEPLOY.md` (capacity + grace settings in the architecture notes)
- Scratchpad Playwright script (not committed)

- [ ] **Step 1: E2E in the real browser (dev stack):** seed capacity, issue a pass at the kiosk with a Stripe test card → confirmation shows "PARK IN SPOT N"; open the pass's verify URL → tap "Spot occupied?" → page shows a NEW spot; dashboard shows the old spot red; clear it. Fix anything found.
- [ ] **Step 2: DEPLOY.md** — add to Architecture notes: "`PARKING_CAPACITY` sizes the spot inventory (rows are added/deactivated idempotently at startup); `SPOT_GRACE_DAYS` (default 3) is how long a lapsed monthly keeps their spot."
- [ ] **Step 3: Full suites** — backend pytest, frontend vitest + tsc + build: all green.
- [ ] **Step 4: Commit** — `git commit -m "feat(spots): e2e verified, deploy docs"`. Update the project memory (spot system shipped; Pa client = capacity 300 via env).

---

## Self-review notes

- Spec coverage: auto-assign (T3), FCFS longest-vacant (T2), sticky monthly + grace (T2/T3), full-lot refusal + never-block-paid-money (T3/T4), report-occupied (T5/T7), lot grid + overstay chip (T6/T8), lot check (T8), morning report (T9), seeding/capacity (T1), uptime = existing stack (no task needed — already shipped).
- Type consistency: `spot_number: int | None` everywhere; `SpotState.state` string union matches Task 6 endpoint and Task 8 `STATE_CLASS` keys exactly.
- No placeholders; every step has runnable code or an exact command.
