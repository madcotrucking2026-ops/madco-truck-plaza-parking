# Zone Availability + Cashier Override — Design

**Client:** Madco itself. 150 spots, physically painted into 6 zones A–F, 25 each
(A1–A25, B1–B25 … F1–F25). Pain: no way to see availability. We already are the
availability authority (derived state); this adds the zone skin, a live board, and
a manual override.

## Decisions (settled with the owner, 2026-08-04)

| Question | Decision |
|---|---|
| Who picks the exact spot? | **System auto-picks**, unchanged. Zones are display labels on the existing longest-vacant dispatcher. |
| Fill order | **Longest-empty first** — the current engine, untouched. |
| Zones | **All 6 identical.** No reserved zones, no size rules. |
| Live board | A **cashier page inside the app**, grouped by zone, per-zone free counts, **auto-refresh every 5s**. No public/driver board, no wall screen. |
| Cashier override | Cashier can **move a truck to a different FREE spot** from the board. No truck-to-truck swapping in v1. |
| Who can move | Any logged-in staff (the "cashier" = the desk role). Login-gated, NOT attendant-exclusive — the owner must not be locked out. **Flag at review if managers/admins should be blocked.** |

## Architecture: labels + polling + one move endpoint (engine untouched)

The spot-assignment engine (`app/core/spots.py`), holding predicate, sticky monthly,
overstay flow, and full-lot handling do **not** change. This feature is three thin
additions on top.

### 1. Zone labels (derived — no migration, no data change)

A spot's identity stays its integer `number` (the stable key for URLs, grid keys,
existing passes). A **display label** is derived:

```
spot_label(n):
  if SPOTS_PER_ZONE <= 0: return str(n)          # non-zoned deployments unchanged
  zone_index = (n - 1) // SPOTS_PER_ZONE
  within     = (n - 1) %  SPOTS_PER_ZONE + 1
  if zone_index > 25: return str(n)              # ran out of letters; degrade safely
  return f"{chr(ord('A') + zone_index)}{within}" # 1->A1, 25->A25, 26->B1, 150->F25
```

New config `spots_per_zone: int = 25` (env `SPOTS_PER_ZONE`). Set 0 to disable
zoning and fall back to bare numbers. Because Madco isn't live yet, "spot N = the
Nth painted spot reading A1→F25" is a convention we define — the asphalt and the
database agree by construction.

`spot_label` is exposed wherever `spot_number` already is: `SpotState`, `PassRead`,
`PassListItem`, `LotCheckResult`, `PassVerifyResult`. Backend is the single source
so the pass ticket, verify page, and lot check all say "B14", not "39".

### 2. The cashier availability page (`/availability`)

New login-gated route + sidebar item ("Availability"). Reuses `GET /api/spots`.

- Spots grouped into 6 labeled zone blocks A–F (derive zone from `number`).
- Per-zone header with a live **free count** (`A · 18 free`), plus a lot-wide total.
- Cells colored by the existing state palette (free/occupied/expiring/grace/
  overstay/inactive), labeled with the within-zone number.
- **Auto-refresh every 5s** via `setInterval` on the fetch; cleared on unmount and
  **paused while the tab is hidden** (visibilitychange) so a forgotten tab doesn't
  poll forever. A subtle "updated Ns ago" / live dot shows it's fresh.

### 3. Cashier override — move a truck to a free spot

`POST /api/spots/move` (login-gated) — body `{pass_id, to_number}`.

In one transaction: verify the target spot is **active, free (not held), and not
overstay-flagged**; verify the pass is live; repoint `pass.spot_id`; stamp the old
spot's `last_vacated_at` (back of the queue); audit-log it (who moved which truck
from where to where). Race-safe: re-check the target is free under the same lock
`pick_free_spot` uses; if it was taken in the last few seconds, 409 "that spot was
just taken — pick another." Moving a paid-but-spotless pass (the full-lot race case)
is allowed — it simply assigns one.

UX on the page: tap an **occupied** cell → a panel shows the truck/company →
"Move to another spot" arms move-mode → tap any **free** cell → confirm → POST →
refetch. Tapping a free cell outside move-mode does nothing; move-mode is
cancelable.

### What does NOT change

Assignment order, pricing, Stripe, reminders, RBAC tiers, the overstay flow, the
holding predicate, sticky monthly. Purely additive.

### Testing

Backend unit: `spot_label` boundaries (1→A1, 25→A25, 26→B1, 150→F25, 0/disabled→
bare, overflow→bare); `spot_label` present on every pass payload and `SpotState`;
move to a free spot repoints + frees old + audits; move to an occupied/overstay/
inactive spot rejected; move under a just-taken race → 409; move a spotless pass
assigns one; move needs a login (401). Frontend: page groups by zone, per-zone
counts correct, 5s poll fires and pauses when hidden, move flow issues the POST and
refetches. E2E (real browser): issue a pass → its ticket shows a zone label; open
`/availability`, watch it refresh, move a truck to a free spot, see both cells flip.
