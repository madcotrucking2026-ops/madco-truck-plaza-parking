# Lot organization + reserved monthly spots — design spec (2026-08-05)

Organize the lot by pass type and give monthly customers a fixed, reserved spot,
instead of the current "grab the longest-empty spot for anyone." **Not built yet —
agreed design, pending Nikhil's sign-off (this one adds a DB migration).**

## Why
Today `pick_free_spot` hands any pass the longest-vacant free spot, so monthly
regulars and daily turnover are scattered across the lot. The owner wants the lot
organized so a glance tells him what's what, and monthly trucks (which leave for
deliveries and come back) to always return to *their* spot.

## The rules (agreed)

### R1 — Zone split
- **Zone A (spots 1–25) = monthly area. Zones B–F (26–150) = daily area.**
- A setting controls how many leading zones are monthly (`MONTHLY_ZONE_COUNT`,
  default 1). Bumping it to 2 later makes A+B monthly with one config change.

### R2 — Monthly = a reserved spot, theirs for the whole paid period
- Monthly is per **truck (vehicle)**. A company with 12 trucks reserves 12 spots.
- On issuing a monthly pass:
  - if the truck already has a reserved spot → **reuse it** (renewals never move).
  - else → **auto-pick the next open spot in the monthly area** (lowest free number
    first: 1, 2, 3 …) and reserve it to that truck. **The cashier can override** and
    pick a specific spot.
- The spot is **held for the truck even when it's out on a run and the spot is
  empty** — daily/weekly can NEVER be assigned a reserved spot, empty or not.
- **No refunds**: a monthly who leaves mid-month keeps the spot until the paid end;
  money is not returned.

### R3 — Release only on close-out
- The reservation persists **until the customer is closed out** (the close-out
  renewal mode → MonthlyCustomer inactive), NOT when a pass expires. A monthly who
  forgets to renew keeps their spot waiting (matches "renew from where they left
  off"). Closing them out releases the spot back to the pool (then reusable by daily
  or a new monthly).
- This **supersedes the SPOT_GRACE_DAYS auto-release for monthlies** — the explicit
  reservation, not a grace timer, is what holds a monthly's spot now.

### R4 — Overflow
- Monthly area full and a new monthly truck arrives → **spill to the nearest open
  spot in the next zone** (into the daily area), and reserve that spot to the truck
  too. Never refuse.

### R5 — Weekly + daily = pooled daily area
- Weekly and daily park in the daily zones, pooled (existing longest-vacant picker,
  restricted to daily spots and excluding reserved spots). **No reservation** — the
  truck sits on the spot the whole stay and frees it when it leaves.

### R6 — The board shows reserved-but-empty
- A spot reserved to a monthly truck that is currently OUT (no live pass on it)
  shows a **new "reserved" state / colour** — not green "free" — so a cashier never
  sells it by accident. Reserved + truck present = occupied as normal.

## Data model + migration
- New column **`Spot.reserved_vehicle_id`** (nullable FK → vehicles.id). Non-null ⇒
  the spot is reserved to that truck and out of the daily pool. Alembic migration.
- The lot is still mostly derived; this adds ONE stored fact (the reservation),
  which is the minimum needed for "held even while empty."

## Behaviour changes by component
- **`pick_free_spot(db, pass_type, vehicle_id)`** — becomes type + reservation aware:
  monthly → reserved-spot-or-nearest-free-monthly-then-spill (and set the
  reservation); daily/weekly → nearest-longest-vacant among daily, non-reserved spots.
- **`_sellable_filter` / free-spot queries** — exclude reserved spots (empty
  reserved spots are not sellable).
- **`_live_window_filter` / holding** — a reserved spot with a live monthly pass
  still "holds"; a reserved-but-empty spot is held by the *reservation*, not a pass.
- **`lot_state` (GET /api/spots)** — emit `reserved` for reserved-empty spots.
- **`apply_renewal` close_out** — clear the reservation on that truck's spot(s).
- **Startup backfill** — reserve the current spot of every active monthly pass so
  existing monthlies keep their spot under the new rules.

## Frontend
- `SpotState.state` gains `reserved`; lot-grid + availability board add its colour
  and legend entry.
- Issue form (monthly) shows the auto-assigned spot with an override picker; a
  company profile can show each truck's reserved spot.

## Task breakdown (build order)
1. **Schema + config** — `Spot.reserved_vehicle_id` + migration; `MONTHLY_ZONE_COUNT`.
   Helpers: `is_monthly_spot(number)`, monthly/daily spot ranges. Tests.
2. **Reservation-aware picker** — `pick_free_spot(pass_type, vehicle_id)`: monthly
   reuse/assign/overflow + reserve; daily/weekly pooled-excluding-reserved. Free-spot
   queries exclude reserved. Tests (assign, renewal reuse, overflow, daily skips
   reserved).
3. **Release + close-out + backfill** — close_out clears reservation; startup
   backfills existing monthlies; reconcile with grace. Tests.
4. **Board `reserved` state** — lot_state emits it; schema; tests.
5. **Frontend** — reserved colour on lot-grid + availability + legend; issue-form
   spot display/override.

## Test matrix
Monthly auto-assigns lowest free monthly spot · renewal reuses the same spot ·
daily/weekly never get a reserved spot (even empty) · monthly overflow spills to
nearest daily spot · close-out releases the reservation · lapsed monthly keeps its
spot (not released) · board shows reserved-empty as `reserved` · cashier override.

## Open / risks
- **Capacity:** reserved-empties reduce sellable daily capacity while trucks are out.
  Accepted (lot runs ~80% empty; owner confirmed "hold their spot even when empty").
- **Migration** touches a live table (spots); additive nullable column, safe.
- Interacts with the just-shipped noon/renewal branch — this branch is cut on top of
  it (feat/pass-noon-expiry-and-renewal), so it inherits that work.
