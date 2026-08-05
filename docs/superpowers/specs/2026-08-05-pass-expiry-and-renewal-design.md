# Pass expiry + renewal — design spec (2026-08-05)

Client rules for how passes expire and how renewals are priced. **Not built yet —
this is the agreed spec, pending Nikhil's sign-off before implementation.**

## Why

Two things are wrong / missing today:
1. **Late renewals renew from *today*, not from the old end date.** Current code:
   `renewal_start = max(business_today(), expiration_date)` ([passes.py:302](../../../backend/app/routers/passes.py#L302)).
   A loyal monthly customer who pays a few days late gets pushed forward and loses
   the days his spot was held. The client wants renewals to **continue from where
   the last pass ended**.
2. **Daily passes should expire at noon**, like a hotel checkout. Today every pass
   expires at midnight (date-only). Client wants **daily only** to expire at 12:00 PM.

## The rules (agreed)

### R1 — Daily passes expire at 12:00 PM (noon), plaza time
- A daily pass with end date Aug 6 is valid until **12:00 PM Aug 6**, then Expired.
- At 12:00 PM the truck is expired and **its spot frees** (resellable that afternoon).
- Pricing unchanged: **$20 × days**. (Aug 5 → Aug 6 = 1 day = $20.)
- **Weekly and monthly are unchanged** — they expire at end of day (midnight after the
  end date), exactly as now. Noon is daily-only.

### R2 — A renewal always starts from the old pass's end date (all types)
- Never from "today," even when the customer is late. Remove the `max(today, …)` floor.
- The customer/cashier chooses how far it runs; the price is `rate × span`.

### R3 — Late renewal, two modes: **Continue** vs **Close-out**
When a customer renews after lapsing, the cashier picks one:

**Continue** (staying on the plan) — charge whole periods from the old end that carry
him **past today** and forward:
- Monthly Jul 8 → Aug 8, renews late **Sep 11**, continuing → **Aug 8 → Oct 8 = 2 months.**
  (1 month = Aug 8→Sep 8 is already past on Sep 11, so it takes 2 months to be current.)
- Few days late → it lands on **1 month** on its own.

**Close-out** (he's leaving, settle up) — charge only the time actually used: whole
periods from the old end **plus the extra days** up to his leaving day, then close the account:
- Monthly Jul 8 → Aug 8, leaves **Sep 11** → **1 month (Aug 8→Sep 8) + 3 extra days (Sep 8→Sep 11).**
- **Extra days are billed at the daily rate ($20/day)** → 3 days = $60. Total = 1 month + $60.

### R4 — Auto pre-fill (owner never calculates)
On the Renew screen for a lapsed customer:
- **Start** locks to the old end date (never typed).
- **Continue** pre-fills the end to the first period-anniversary **after today** (catch-up).
- **Close-out** pre-fills the end to **today** and computes whole-periods + extra-days.
- Price fills in automatically; the cashier can bump the span up (e.g. 3 months) in one tap.

### R5 — Daily / weekly renewal
- Same backdate rule (R2): renewal starts from the old end (daily = the noon boundary).
- Daily: a truck still parked and extending renews from its old noon-expiry (12 PM Aug 6
  → 12 PM Aug 9 = 3 days = $60). A truck that **left and came back** is a *new* pass, not
  a renewal (cashier issues fresh).
- Weekly stays whole 7-day weeks; a catch-up weekly renewal is N whole weeks.

## Worked examples (the client's own)
| Case | Old pass | Renews | Result | Charge |
|---|---|---|---|---|
| Monthly, on time | Aug 5 → Sep 5 | before Sep 5 | Sep 5 → Oct 5 | 1 × rate |
| Monthly, few days late, continue | Aug 5 → Sep 5 | Sep 10 | **Sep 5 → Oct 5** | 1 × rate |
| Monthly, weeks late, continue | Jul 8 → Aug 8 | Sep 11 | **Aug 8 → Oct 8** (2 mo) | 2 × rate |
| Monthly, close-out | Jul 8 → Aug 8 | leaves Sep 11 | **Aug 8 → Sep 11** | 1 × rate + 3×$20 |
| Daily, extend | Aug 5 → Aug 6 (noon) | at desk | 12 PM Aug 6 → 12 PM Aug 9 | 3 × $20 = $60 |

## Technical approach (for implementation)
- **R2 (anchor):** in `renewal_quote`, set `renewal_start = parking_pass.expiration_date`
  (drop the `max(business_today(), …)`). Single line + its callers/tests.
- **R1 (noon):** `expiration_date` stays a `date`; add a central helper
  `pass_expired(pass_type, expiration_date, now) -> bool` — daily: `now >= noon(expiration_date)`;
  weekly/monthly: `now.date() > expiration_date`. Route every expiry/spot decision through it
  (`live_status` callers, the spot free/occupied derivation, lot-check, verify, dashboard,
  passes list, morning report). This is the largest ripple — needs its own task + tests, because
  the spot engine must free a daily spot at noon.
- **R3/R4 (modes):** add `mode: "continue" | "close_out"` to `RenewPassRequest`; `renewal_quote`
  branches on it for end-date default + price (close-out = whole-periods × rate + extra-days × daily
  rate, and sets the monthly customer inactive). New `defaultRenewalEnd` helpers on the frontend.
- **Frontend:** the renew dialog gets two actions (Renew-continuing / Close-out) with pre-filled
  dates + live price, mirroring the issue form's look.

## Decisions made (flag at sign-off if wrong)
- **Extra days on close-out = daily rate ($20/day)**, not prorated monthly. [Nikhil to confirm]
- **Close-out is for monthly/weekly**; daily just extends forward (a returning daily truck = new pass).
- Noon = **daily only**; weekly/monthly keep midnight/date-based expiry.

## Test matrix (every case gets a test)
On-time renew · few-days-late continue · weeks-late continue (2-month catch-up) ·
close-out with leftover days ($20/day) · daily noon expiry (before/after 12 PM) ·
daily spot frees at noon · weekly multi-week catch-up · monthly unchanged midnight expiry.

## Out of scope / risks
- Schema stays as-is (no new column); noon lives in logic, not the DB. If the client later wants
  a *configurable* checkout time, that becomes a setting — not now.
- The noon change touches the spot engine; the swarm/concurrency tests must still pass.
