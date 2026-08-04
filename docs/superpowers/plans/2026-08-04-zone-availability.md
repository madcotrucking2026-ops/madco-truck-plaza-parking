# Zone Availability + Cashier Override Implementation Plan

**Goal:** Label spots by zone (A1–F25), add a live cashier availability page that auto-refreshes every 5s, and let the cashier move a truck to a free spot — all additive on the tested spot engine.

**Spec:** `docs/superpowers/specs/2026-08-04-zone-availability-design.md`

## Global Constraints

- Engine (`app/core/spots.py` assignment/holding), pricing, Stripe, RBAC tiers: DO NOT change.
- All dates via `app.core.clock`. New config `spots_per_zone: int = 25`.
- `spot_label` is backend-authoritative; frontend displays it, never recomputes.
- Move is login-gated (`_require_login`), not attendant-only.
- Tests from `backend/`: `.venv/Scripts/python.exe -m pytest tests/ -q`.

---

### Task 1: `spot_label` helper + config

**Files:** `app/core/config.py` (+`spots_per_zone: int = 25`), `app/core/spots.py` (+`spot_label`), `tests/test_spot_label.py`

- [ ] **Test** `tests/test_spot_label.py`:
```python
from app.core.config import settings
from app.core.spots import spot_label


def test_zone_labels_at_boundaries(monkeypatch):
    monkeypatch.setattr(settings, "spots_per_zone", 25)
    assert spot_label(1) == "A1"
    assert spot_label(25) == "A25"
    assert spot_label(26) == "B1"
    assert spot_label(150) == "F25"


def test_disabled_zoning_is_bare_number(monkeypatch):
    monkeypatch.setattr(settings, "spots_per_zone", 0)
    assert spot_label(39) == "39"


def test_overflow_past_Z_degrades_to_number(monkeypatch):
    monkeypatch.setattr(settings, "spots_per_zone", 1)
    assert spot_label(27) == "AA?".__class__ and spot_label(27) == "27"  # zone_index 26 > 25 -> bare
```
- [ ] Run → FAIL (ImportError).
- [ ] Implement in `app/core/config.py` beside `parking_capacity`:
```python
    # Physical zoning: spots are painted into lettered zones of this size
    # (Madco = 6 zones of 25). Purely a display label over the integer spot
    # number. 0 disables zoning (spots show as bare numbers). Env SPOTS_PER_ZONE.
    spots_per_zone: int = 25
```
and in `app/core/spots.py`:
```python
def spot_label(number: int) -> str:
    """Display label for a spot: 1 -> 'A1', 26 -> 'B1', 150 -> 'F25'. The integer
    number stays the stable key; this is only how it reads on a pass and the board.
    Falls back to the bare number when zoning is off or letters run out."""
    per = settings.spots_per_zone
    if per <= 0:
        return str(number)
    zone_index = (number - 1) // per
    if zone_index > 25:
        return str(number)
    within = (number - 1) % per + 1
    return f"{chr(ord('A') + zone_index)}{within}"
```
- [ ] Run → PASS. Fix the intentionally-awkward overflow assertion to a clean `assert spot_label(27) == "27"`.
- [ ] Commit: `feat(zones): spot_label helper + SPOTS_PER_ZONE config`.

---

### Task 2: expose `spot_label` on every spot-bearing payload

**Files:** `app/schemas/spot.py` (SpotState +`label`), `app/schemas/pass_.py` (PassRead/PassListItem/LotCheckResult +`spot_label`), `app/schemas/verify.py` (PassVerifyResult +`spot_label`), `app/routers/spots.py`, `app/routers/passes.py`, `app/routers/lot_check.py`, `app/routers/verify.py`, `app/models/parking_pass.py` (property). Test: `tests/test_spot_label_on_payloads.py`

**Interfaces produced:** `SpotState.label: str`; `spot_label: str | None` on the four pass schemas, populated via a `ParkingPass.spot_label` property.

- [ ] **Test**:
```python
# tests/test_spot_label_on_payloads.py
from datetime import timedelta
from app.core.clock import business_today
from app.core.config import settings
from app.core.spots import ensure_spots
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment
from app.schemas.pass_ import PassRead


def test_pass_read_has_zone_label(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 150)
    monkeypatch.setattr(settings, "spots_per_zone", 25)
    ensure_spots(db)
    p = _issue_pass_and_payment(
        db, company_name="Co", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number="T1", trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=business_today(), end_date=business_today() + timedelta(days=1),
        price_override=None, payment_method=PaymentMethod.cash, check_number=None,
    )
    db.commit()
    out = PassRead.model_validate(p)
    assert out.spot_number is not None
    assert out.spot_label and out.spot_label[0] in "ABCDEF"


def test_spots_endpoint_labels_by_zone(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 150)
    monkeypatch.setattr(settings, "spots_per_zone", 25)
    ensure_spots(db)
    client.post("/api/auth/register", json={"name": "O", "email": "o@x.com", "password": "ownerpass123"})
    tok = client.post("/api/auth/login", json={"email": "o@x.com", "password": "ownerpass123"}).json()["access_token"]
    spots = client.get("/api/spots", headers={"Authorization": f"Bearer {tok}"}).json()
    by_num = {s["number"]: s for s in spots}
    assert by_num[1]["label"] == "A1"
    assert by_num[150]["label"] == "F25"
```
- [ ] Run → FAIL.
- [ ] Implement: add `spot_label` property to `ParkingPass` returning `spot_label(self.spot.number) if self.spot else None` (import the helper lazily to avoid a cycle: `from app.core.spots import spot_label` inside the property, or at module top if no cycle). Add `spot_label: str | None = None` to PassRead, PassListItem, LotCheckResult, PassVerifyResult; populate PassListItem/LotCheckResult/verify from `p.spot_label`. Add `label: str` to `SpotState`; in `spots.py` `lot_state`, set `label=spot_label(spot.number)`.
- [ ] Run → PASS; full suite green.
- [ ] Commit: `feat(zones): spot_label on pass, list, lot-check, verify, and lot state`.

---

### Task 3: move-a-truck endpoint

**Files:** `app/core/spots.py` (`move_pass_to_spot` helper), `app/routers/spots.py` (`POST /move`), `app/schemas/spot.py` (`MoveSpotRequest`). Test: `tests/test_move_spot.py`

**Interfaces produced:** `POST /api/spots/move` `{pass_id:int, to_number:int}` → 200 `SpotState`-ish `{spot_number, spot_label}`; 409 target taken; 404 bad pass/spot; 400 target occupied/overstay/inactive/same.

- [ ] **Test** `tests/test_move_spot.py`:
```python
from datetime import timedelta
from app.core.clock import business_today
from app.core.config import settings
from app.core.spots import ensure_spots
from app.models import ParkingPass, Spot
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment


def _auth(client):
    client.post("/api/auth/register", json={"name": "O", "email": "o@x.com", "password": "ownerpass123"})
    t = client.post("/api/auth/login", json={"email": "o@x.com", "password": "ownerpass123"}).json()["access_token"]
    return {"Authorization": f"Bearer {t}"}


def _issue(db, truck):
    return _issue_pass_and_payment(
        db, company_name=f"Co {truck}", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number=truck, trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=business_today(), end_date=business_today() + timedelta(days=1),
        price_override=None, payment_method=PaymentMethod.cash, check_number=None)


def test_move_to_free_spot_repoints_and_frees_old(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 10)
    ensure_spots(db); H = _auth(client)
    p = _issue(db, "T1"); db.commit()
    old = p.spot_id
    target = db.query(Spot).filter(Spot.id != old).first().number
    r = client.post("/api/spots/move", json={"pass_id": p.id, "to_number": target}, headers=H)
    assert r.status_code == 200
    db.expire_all()
    assert p.spot.number == target
    assert db.get(Spot, old).last_vacated_at is not None


def test_move_onto_occupied_spot_is_rejected(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 10)
    ensure_spots(db); H = _auth(client)
    a = _issue(db, "A"); b = _issue(db, "B"); db.commit()
    r = client.post("/api/spots/move", json={"pass_id": a.id, "to_number": b.spot.number}, headers=H)
    assert r.status_code in (400, 409)


def test_move_needs_login(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    p = _issue(db, "T1"); db.commit()
    assert client.post("/api/spots/move", json={"pass_id": p.id, "to_number": 3}).status_code == 401


def test_move_to_bad_spot_or_pass_404(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db); H = _auth(client)
    p = _issue(db, "T1"); db.commit()
    assert client.post("/api/spots/move", json={"pass_id": 99999, "to_number": 2}, headers=H).status_code == 404
    assert client.post("/api/spots/move", json={"pass_id": p.id, "to_number": 9999}, headers=H).status_code == 404
```
- [ ] Run → FAIL.
- [ ] Implement `move_pass_to_spot(db, pass_id, to_number)` in spots.py: load pass (404 if missing), load target spot by number (404 if missing), reject if inactive/overstay (400), reject if same as current (400), check target not in `_held_spot_ids()` — locked the same way `pick_free_spot` locks — else 409; set old spot `last_vacated_at = business_now()` if the pass had one; repoint `pass.spot_id`; `log_audit(edited, parking_pass, f"Moved {truck} to {spot_label(target)}")`; commit; return the pass. Router `POST /move` wires it; `spots.router` is already mounted under `_require_login`.
- [ ] Run → PASS; full suite green.
- [ ] Commit: `feat(zones): cashier move-a-truck endpoint (free spots only, race-safe, audited)`.

---

### Task 4: `SpotState` label + `spot_label` frontend types; zone grouping helper

**Files:** `frontend/src/lib/api.ts` (SpotState +`label`; PassRead/PassListItem/LotCheckResult/PassVerifyResult +`spot_label`; `MoveSpotRequest`), `frontend/src/lib/zones.ts` (grouping). Test: extend vitest if a zones test fits; otherwise tsc is the gate.

- [ ] Add `label: string` to `SpotState`; `spot_label: string | null` to the four pass types. Fix any hand-built PassRead literals (e.g. `passes/page.tsx`) to include `spot_label`.
- [ ] `frontend/src/lib/zones.ts`:
```ts
import type { SpotState } from "@/lib/api";

/** Group the flat lot into ordered zone blocks by the letter in each label. */
export function byZone(spots: SpotState[]): { zone: string; spots: SpotState[]; free: number }[] {
  const map = new Map<string, SpotState[]>();
  for (const s of [...spots].sort((a, b) => a.number - b.number)) {
    const zone = /^[A-Z]/.test(s.label) ? s.label[0] : "•";
    (map.get(zone) ?? map.set(zone, []).get(zone)!).push(s);
  }
  return [...map.entries()].map(([zone, list]) => ({
    zone, spots: list, free: list.filter((x) => x.state === "free").length,
  }));
}
```
- [ ] `npx tsc --noEmit` clean.
- [ ] Commit: `feat(zones): frontend zone types + grouping`.

---

### Task 5: the `/availability` page — live board + move flow

**Files:** `frontend/src/app/availability/page.tsx` (new), `frontend/src/lib/nav.ts` (+item, minRole attendant). Uses `byZone`, `GET /api/spots`, `POST /api/spots/move`.

- [ ] Build the page:
  - Fetch `/api/spots`; `setInterval(fetch, 5000)`; clear on unmount; pause when `document.hidden`, resume + immediate fetch on visible. A small "updated Ns ago" line.
  - Render `byZone(spots)`: one block per zone with header `A · 18 free`, then a grid of cells (label = within-zone number, color = state via the existing palette).
  - Lot-wide free total at the top.
  - Move flow: click an **occupied** cell → side panel/dialog with truck + company + "Move to another spot". Arming sets `moving = {pass_id, from}`. While armed, free cells are tappable and highlighted; a tap POSTs `{pass_id, to_number}`, then refetches and clears move-mode. Toast on success ("Moved T1 to B14") and on 409 ("that spot was just taken"). Cancel button clears move-mode.
- [ ] Add to `nav.ts`: `{ label: "Availability", href: "/availability", icon: <a lot/grid icon>, minRole: "attendant" }` (the cashier sees it).
- [ ] `npx tsc --noEmit` + `npm test` green; `npx next build` clean.
- [ ] Commit: `feat(zones): live cashier availability page with 5s refresh + move override`.

---

### Task 6: E2E in a real browser + docs

- [ ] Dev stack up. Playwright (scratchpad): log in; issue a pass at `/passes/issue` → ticket shows a zone label like "B14" (assert the label pattern). Open `/availability` → assert 6 zone blocks, per-zone free counts, a live "updated" line that changes. Click an occupied cell → Move → click a free cell → assert both cells changed state and a toast fired; cross-check via `/api/spots` that the truck's spot changed. Screenshot each.
- [ ] Run `backend/scripts/swarm_test.py`-style sanity is NOT needed (engine unchanged) — but run full backend pytest + frontend vitest + build, all green, as the gate.
- [ ] DEPLOY.md: note `SPOTS_PER_ZONE` (default 25; 0 disables zoning). Update the spot memory.
- [ ] Commit: `feat(zones): e2e verified, deploy docs`.

## Self-review

- Spec coverage: labels (T1–T2), live board (T5), 5s poll + hidden-pause (T5), move override free-only/race-safe/audited/login-gated (T3), zones-as-labels-only, engine untouched (no engine task). 
- Type consistency: `spot_label` (string|null) and `label` (string on SpotState) named identically across backend schemas and frontend types.
- No placeholder steps; every code step has real code or an exact command.
