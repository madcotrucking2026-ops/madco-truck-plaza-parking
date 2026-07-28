# Spot Inventory & Auto-Assignment — Design

**Client:** 300-spot truck lot ("Pa"), all spots uniform truck-size, freshly numbered 1–300.
**Product decision:** the SYSTEM is the dispatcher. A customer books, the website picks the
spot and tells them where to park. No human in the loop. First come, first served, no
reservations. The same feature ships to every deployment (Madco runs it at capacity 150).

## Decisions (settled with the owner, 2026-07-28)

| Question | Decision |
|---|---|
| Who picks the spot? | The system, automatically, at payment time |
| Spot kinds | One uniform pool; `spot_type` stored (default `standard`) for future zoning, ignored by v1 assignment |
| Monthly customers | **Sticky spot + grace**: their number stays theirs while active and for `SPOT_GRACE_DAYS` (default 3) past expiry; then it returns to the pool |
| Expired-but-still-parked trucks (no sensors) | **Longest-vacant-first assignment** (squatters age out before their spot is re-issued) + **self-service "Spot occupied?"** button on the customer's pass page: one tap reassigns them and flags the old spot as overstay for staff |
| Uptime | Single-box Docker stack + restarts + healthchecks + error webhook + nightly off-box backups (~99.9%). Multi-node HA rejected as wrong trade at this scale. Paper fallback sign for the residue. |

## Architecture: derived state, one source of truth

**A spot is free when no live pass holds it.** Freeness is a query, never a stored status.
There is no midnight job to crash, no status column to drift. This mirrors how the money
path already works (the pass is the record of payment; now it is also the record of space)
and makes "spot state disagrees with pass state" unrepresentable.

A pass **holds** its spot while:

- `status != cancelled`, AND
- daily/weekly: `expiration_date >= today` (plaza timezone, like all date logic), OR
- monthly: `expiration_date + SPOT_GRACE_DAYS >= today`

Release is therefore implicit and instant: the day after expiry (plus grace for monthly),
the holding predicate stops matching and the spot is sellable — exactly the client's
"as soon as it expires, the next customer can have it."

### Data model

`spots` (new table)
- `id` PK
- `number` int, unique — what's painted on the asphalt
- `spot_type` varchar, default `'standard'`
- `active` bool, default true — capacity changes deactivate, never delete
- `last_vacated_at` datetime nullable — set when a holding pass is cancelled or reassigned;
  NULL means "never occupied" and sorts as vacant-longest
- `overstay_reported` bool default false + `overstay_reported_at` datetime nullable

`parking_passes.spot_id` (new FK, nullable — legacy passes and the paid-but-lot-full edge
case have none)

**Seeding:** at startup, `ensure_spots()` idempotently inserts missing numbers
`1..PARKING_CAPACITY` and flips `active` so exactly numbers ≤ capacity are active.
Capacity is already an env var — a 300-spot client is configuration, not code.

### Assignment algorithm

Runs inside the SAME transaction that issues the pass (kiosk finalize, desk issue,
pay-link finalize — all funnel through `_issue_pass_and_payment`):

1. Monthly sticky: if the company's most recent pass had a spot and that spot is not held
   by someone else, reuse it.
2. Otherwise: pick the free active spot ordered by `last_vacated_at ASC NULLS FIRST,
   number ASC` — longest-vacant first.
3. On Postgres the candidate row is taken `FOR UPDATE SKIP LOCKED`, so two concurrent
   checkouts cannot receive the same number (the database referees, not app code).
   On SQLite (dev) writes are serialized anyway; the same code runs without the hint.
4. Renewal never touches the spot — extending the pass extends the hold.

**Full lot:** the kiosk checks free count BEFORE creating a Stripe intent and refuses with
a clear message. If the lot fills in the seconds between intent and finalize, finalize
STILL issues the pass (never strand taken money) with `spot_id = NULL`, and the dashboard
shows a "paid, awaiting spot" chip for staff — same pattern as stranded charges.

### The asphalt gap (overstay flow)

`POST /api/verify/{token}/report-occupied` — public, authenticated by the pass's existing
HMAC token, rate-limited by the lookup limiter. Effect, in one transaction: flag the old
spot `overstay_reported`, stamp `last_vacated_at` (it goes to the BACK of the assignment
queue), assign the next spot, return the updated pass. 409 with "see the front desk" if
the lot is genuinely full. The customer's pass page (QR verify page) gets the button;
the response updates the page in place.

Overstay flags surface on the manager dashboard (red chip, styled like the
stranded-charges banner) and in Lot Check. A flag clears when staff tap "cleared" or
automatically when the spot is next assigned.

### Surfaces

- **Pass ticket / kiosk confirmation / QR verify page:** the spot number is the hero —
  big mono type, readable from a cab ("PARK IN SPOT 47").
- **Lot Check:** verdict card gains "Spot 47".
- **Dashboard:** occupancy numbers become a 300-cell grid (green free / forest occupied /
  amber expiring or grace / red overstay / grey inactive), tap a cell for the pass on it.
  `GET /api/spots` returns the derived state of every spot in one query.
- **Morning report:** new "overstays to chase" lines, priority `today`.

### What does NOT change

Payments, Stripe finalize/webhook idempotency, reminders, RBAC tiers, audit log,
company/vehicle dedup, receipts. The feature is additive; existing Madco passes simply
have no spot until their next issue.

### Testing

Unit: holding predicate (daily midnight, monthly grace, cancelled), assignment order
(NULLS FIRST, longest-vacant), sticky monthly, full-lot null-spot issue, report-occupied
(reassign + flag + 409-when-full + bad token), ensure_spots idempotency, spots state
endpoint, morning-report overstays. E2E (existing Playwright pattern): kiosk pay → spot
on confirmation; report-occupied from the verify page → new spot + dashboard flag.
