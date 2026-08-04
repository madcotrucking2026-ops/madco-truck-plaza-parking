# Graph Report - madco-truck-plaza-parking  (2026-08-04)

## Corpus Check
- 190 files · ~69,709 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1394 nodes · 3543 edges · 97 communities (67 shown, 30 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 174 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bd4055b6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- reminders.py
- passes.py
- PaymentMethod
- test_lot_check.py
- routers/auth.py
- issue/page.tsx
- test_morning_report.py
- test_dashboard.py
- payments/page.tsx
- cn
- payment_requests.py
- main.py
- test_spot_assignment.py
- api.ts
- test_stranded_charges.py
- bulk-renew-dialog.tsx
- compilerOptions
- [id]/page.tsx
- test_renewal.py
- components.json
- test_reminders_sweep.py
- devDependencies
- prod service: backend
- enums.py
- clock.py
- test_security.py
- test_report_occupied.py
- dependencies
- Task 2: Holding predicate + free-spot picker
- Service: backend (self-migrating FastAPI)
- AI Search
- Monthly Reminder System
- seed_demo.py
- ParkingPass
- _price_for
- routers/reports.py
- create_intent
- Tech Stack
- test_auth_api.py
- package.json
- mobile-nav.tsx
- RateLimiter
- ensure_spots
- Core Principle: The Software Remembers Everything
- test_move_spot.py
- Monochrome 16x16 Glyph Icon System (#666, evenodd fill)
- verify/[token]/page.tsx
- test_cron_endpoint.py
- stripe_payments.py
- routers/spots.py
- Go-Live Checklist
- test_spots_endpoint.py
- next.config.ts
- book/layout.tsx
- login/layout.tsx
- pay/[token]/layout.tsx
- verify/[token]/layout.tsx
- swarm_test.py
- _issue_pass_and_payment
- eslint.config.mjs
- lucide-react
- next
- react-dom
- sonner
- @stripe/react-stripe-js
- tailwind-merge
- tw-animate-css
- postcss.config.mjs
- LotCheckResult
- models/__init__.py
- WebhookAlertHandler
- Global Constraints
- Architecture: labels + polling + one move endpoint (engine untouched)
- test_insights.py
- get
- post
- routers/verify.py
- BaseModel
- Session
- core/spots.py
- SpotState
- date
- lot-check/page.tsx
- PassType
- model_validator
- IssuePassRequest
- PassListItem
- PassVerifyResult
- ReassignResult
- RenewPassRequest

## God Nodes (most connected - your core abstractions)
1. `cn()` - 80 edges
2. `_issue_pass_and_payment()` - 61 edges
3. `ensure_spots()` - 52 edges
4. `business_today()` - 52 edges
5. `PassType` - 51 edges
6. `PaymentMethod` - 46 edges
7. `VehicleType` - 39 edges
8. `_get()` - 34 edges
9. `ParkingPass` - 29 edges
10. `api` - 27 edges

## Surprising Connections (you probably didn't know these)
- `Sticky Monthly Spot + Grace Window` --semantically_similar_to--> `Spot Holder Logic`  [INFERRED] [semantically similar]
  docs/superpowers/specs/2026-07-28-spot-inventory-design.md → CLAUDE.md
- `Twilio A2P Activation (No Code Change)` --implements--> `Monthly Reminder System`  [INFERRED]
  DEPLOY.md → CLAUDE.md
- `dev service: postgres (port 5432 exposed)` --semantically_similar_to--> `prod service: postgres:16-alpine + healthcheck`  [INFERRED] [semantically similar]
  docker-compose.yml → docker-compose.prod.yml
- `Backend runtime dependency set` --implements--> `Tech Stack`  [INFERRED]
  backend/requirements.txt → CLAUDE.md
- `Stripe Webhook + Payment-Method Domain Setup` --implements--> `Accepted Payment Methods`  [INFERRED]
  DEPLOY.md → CLAUDE.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **CI quality gates (pytest, tsc, vitest, build, advisory lint)** — _github_workflows_ci_backend_job, _github_workflows_ci_frontend_job, _github_workflows_ci_lint_non_blocking, backend_requirements_dev_test_deps [EXTRACTED 1.00]
- **AI Intelligence Layer (search, inspection, dashboard, insights, leads)** — claude_ai_search, claude_ai_parking_inspector, claude_smart_dashboard, claude_ai_insights, claude_ai_sales_opportunities [INFERRED 0.85]
- **Pass Sale and Money Trail** — claude_parking_pass_fields, claude_parking_types, claude_accepted_payments, claude_payment_history, claude_audit_log, claude_parking_rules [EXTRACTED 1.00]
- **Monthly Customer Retention Flow** — claude_monthly_customers, claude_company_profiles, claude_monthly_reminder_system, claude_monthly_pass, claude_spot_holder_logic, claude_price_override [INFERRED 0.95]
- **Single-box production stack (five services + TLS profile)** — docker_compose_prod_postgres, docker_compose_prod_backend, docker_compose_prod_frontend, docker_compose_prod_nginx, docker_compose_prod_cron, docker_compose_prod_certbot [EXTRACTED 1.00]
- **Derived-state spot dispatch flow (hold → pick → assign → overstay reassign)** — docs_superpowers_specs_2026_07_28_spot_inventory_design_derived_state, docs_superpowers_specs_2026_07_28_spot_inventory_design_holding_predicate, docs_superpowers_specs_2026_07_28_spot_inventory_design_assignment_algorithm, docs_superpowers_specs_2026_07_28_spot_inventory_design_full_lot_never_strand_money, docs_superpowers_specs_2026_07_28_spot_inventory_design_asphalt_gap [EXTRACTED 1.00]
- **Untouched create-next-app public/ asset set (vendor branding, not Madco brand)** — frontend_public_file_document_icon, frontend_public_globe_globe_icon, frontend_public_window_window_icon, frontend_public_next_nextjs_wordmark, frontend_public_vercel_vercel_triangle_logo [INFERRED 0.85]

## Communities (97 total, 30 thin omitted)

### Community 0 - "reminders.py"
Cohesion: 0.10
Nodes (32): is_configured(), Twilio requires E.164 (+15551234567). Customer phones are stored loosely…, Send an SMS via Twilio. Returns True if it went out, False if SMS isn't…, send_sms(), to_e164(), _already_reminded_today(), cron_trigger(), _do_send() (+24 more)

### Community 1 - "passes.py"
Cohesion: 0.17
Nodes (18): cancel_pass(), get_pass(), issue_pass(), list_passes(), get, post, Session, Removes a truck from a monthly plan (or cancels any pass) without deleting its… (+10 more)

### Community 2 - "PaymentMethod"
Cohesion: 0.07
Nodes (61): live_status(), date, Company, MonthlyCustomerStatus, PassStatus, PaymentMethod, company_profile(), create_company() (+53 more)

### Community 3 - "test_lot_check.py"
Cohesion: 0.26
Nodes (13): lot_check(), get, Session, _issue(), Lot check — the flagship feature: the manager walks up to a truck, types its…, A renewed pass writes a second Payment row. Reporting the original one would…, Standing at the truck, the manager needs to know which spot it SHOULD be in —…, test_a_daily_walkup_is_not_a_monthly_customer() (+5 more)

### Community 4 - "routers/auth.py"
Cohesion: 0.09
Nodes (44): AuthStatus, create_access_token(), hash_password(), verify_password(), health(), EmployeeRole, auth_status(), create_staff_user() (+36 more)

### Community 5 - "issue/page.tsx"
Cohesion: 0.11
Nodes (39): BookPage(), PASS_TYPES, PayWay, IDENTIFIER_FIELD, IssuePassForm(), PASS_TYPES, PAY_CHOICES, PayChoice (+31 more)

### Community 6 - "test_morning_report.py"
Cohesion: 0.17
Nodes (23): _money(), morning_report(), date, Session, The manager's 7am briefing: who to call today, and why. The dashboard already…, _revenue_on(), _daily(), _FakeUser (+15 more)

### Community 7 - "test_dashboard.py"
Cohesion: 0.16
Nodes (13): Payment, What the payment was for — the vehicle on its pass., dashboard_stats(), Session, A payment taken at 10:30pm plaza time belongs to that day's revenue. The same…, test_tonights_takings_are_on_tonights_books(), _issue_active(), Dashboard occupancy: capacity, available spots, occupancy %. (+5 more)

### Community 8 - "payments/page.tsx"
Cohesion: 0.11
Nodes (23): ACTION_STYLE, AuditLogPage(), fmt(), styleFor(), bucketOf(), currency(), inPeriod(), METHOD_STYLE (+15 more)

### Community 9 - "cn"
Cohesion: 0.07
Nodes (52): currency(), MonthlyCustomer, MonthlyCustomersPage(), STATUS_LABEL, AddStaffCard(), Role, ROLES, Badge() (+44 more)

### Community 10 - "payment_requests.py"
Cohesion: 0.17
Nodes (18): Per-client sliding-window rate limiting, as a FastAPI dependency. Deliberately…, is_configured(), _lookup_monthly_rate(), The company's established per-month rate, or None if it has no monthly plan on…, create_intent(), create_payment_request(), finalize(), get_payment_request() (+10 more)

### Community 11 - "main.py"
Cohesion: 0.13
Nodes (18): _backfill_pass_qr_codes(), `Base.metadata.create_all()` only creates missing *tables* — it never alters an…, Passes issued before the signed-QR system stored their plaintext receipt number…, run_startup_migrations(), get_logger(), Child of the app logger, named for the calling module., _alembic_config(), Schema management at startup — Alembic is the single mechanism. Replaces the… (+10 more)

### Community 12 - "test_spot_assignment.py"
Cohesion: 0.31
Nodes (9): _issue(), Assignment is part of issuing a pass — same transaction, no separate step., Sticky: a lapsed monthly who comes back gets the number they always had., Money already taken must NEVER fail for lack of a spot — pass issues with…, test_full_lot_issues_pass_with_no_spot(), test_issue_assigns_a_spot(), test_renewal_keeps_the_spot(), test_returning_monthly_gets_their_old_spot() (+1 more)

### Community 13 - "api.ts"
Cohesion: 0.06
Nodes (38): currency(), GROUPS, MorningReportPage(), telHref(), currency(), DashboardPage(), LEAD_TIER, QUICK_ACTIONS (+30 more)

### Community 14 - "test_stranded_charges.py"
Cohesion: 0.07
Nodes (61): finalize(), _finalize_intent(), _finalize_payment_request(), issue_stranded_pass(), _ours(), post, Request, Session (+53 more)

### Community 15 - "bulk-renew-dialog.tsx"
Cohesion: 0.12
Nodes (20): currency(), PassesPage(), ComingSoon(), PAY_CHOICES, PayChoice, vehicleOf(), StaffListCard(), Button() (+12 more)

### Community 16 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 17 - "[id]/page.tsx"
Cohesion: 0.19
Nodes (9): CompanyProfilePage(), fmtDate(), fmtDateTime(), money(), money2(), InfoTip(), STATUS_STYLE, StatusBadge() (+1 more)

### Community 18 - "test_renewal.py"
Cohesion: 0.22
Nodes (14): add_months(), date, apply_renewal(), Validates a proposed renewal and returns (renewal_start, price) WITHOUT…, Applies a validated renewal: extends the pass, records a Payment, and updates…, renewal_quote(), _issue(), Renewal pricing/validation — and the charge-then-fail regression guard. (+6 more)

### Community 19 - "components.json"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 20 - "test_reminders_sweep.py"
Cohesion: 0.35
Nodes (12): The daily sweep: for every monthly customer, text a renewal reminder if one is…, run_scheduled_reminders(), auto_on(), _mc(), fixture, The daily renewal-reminder sweep: who gets a text and who's skipped. SMS isn't…, _reminder_count(), test_renewed_customer_is_not_due() (+4 more)

### Community 21 - "devDependencies"
Cohesion: 0.10
Nodes (21): eslint, eslint-config-next, devDependencies, eslint, eslint-config-next, playwright, tailwindcss, @tailwindcss/postcss (+13 more)

### Community 22 - "prod service: backend"
Cohesion: 0.14
Nodes (20): CI job: Frontend · typecheck + test + build (Node 20), Non-blocking lint (react-hooks/set-state-in-effect), Nightly Off-Box Backups (14 kept, host bind mount), One-Command Docker Deployment, Service: cron (reminder sweep + nightly pg_dump), Service: frontend (Next.js), Service: nginx (only published port, /api routing), Service: postgres (named volume) (+12 more)

### Community 23 - "enums.py"
Cohesion: 0.15
Nodes (18): log_audit(), Session, generate_receipt_number(), date, AuditLog, AuditAction, list_audit_log(), Session (+10 more)

### Community 24 - "clock.py"
Cohesion: 0.16
Nodes (15): business_now(), plaza_tz(), datetime, What day is it *at the plaza*. Two separate bugs live here if you get this…, Wall-clock time at the plaza, naive — stored as-is so `date(paid_at)` in SQL is…, Settings, Vehicle, DashboardStats (+7 more)

### Community 25 - "test_security.py"
Cohesion: 0.13
Nodes (16): _intent_body(), Rate limiting and input validation on the unauthenticated surface. Each test…, A crafted end_date decades out turns into an absurd computed price., A negative price would record a NEGATIVE payment against the drawer., Blocks two things the per-account lockout does NOT: a spray across many…, Public and unauthenticated: it answers "does this company exist, what is its…, An unbounded password field means megabytes fed straight into bcrypt on an…, Unbounded here would flow into Stripe metadata and the database. (+8 more)

### Community 26 - "test_report_occupied.py"
Cohesion: 0.30
Nodes (9): make_pass_token(), Returns the pass id if the token's signature is valid, else None., _sign(), verify_pass_token(), _issue(), Customer finds a squatter in their assigned spot: one tap moves them and flags…, test_full_lot_says_see_the_desk(), test_reassigns_and_flags_old_spot() (+1 more)

### Community 27 - "dependencies"
Cohesion: 0.11
Nodes (19): @base-ui/react, class-variance-authority, clsx, cmdk, dependencies, @base-ui/react, class-variance-authority, clsx (+11 more)

### Community 28 - "Task 2: Holding predicate + free-spot picker"
Cohesion: 0.16
Nodes (19): Spot Inventory Is Config (PARKING_CAPACITY / SPOT_GRACE_DAYS), Stripe Webhook + Payment-Method Domain Setup, PARKING_CAPACITY env (default 150), Task 10: E2E proof + DEPLOY.md docs + memory, Task 1: Spot model, migration, idempotent seeding, Task 2: Holding predicate + free-spot picker, Task 3: Assign at issue time (sticky monthly, full lot never blocks), Task 4: Kiosk pre-check — refuse checkout when full (+11 more)

### Community 29 - "Service: backend (self-migrating FastAPI)"
Cohesion: 0.15
Nodes (15): CI job: Backend · pytest (Python 3.11), bcrypt<4.1 pin (passlib 1.7.4 self-test breakage), Backend dev/test dependency set (pytest, httpx), Backend runtime dependency set, Inter (headings and body), JetBrains Mono (numbers), Typography System, Schema = Alembic Only (Self-Upgrading at Startup) (+7 more)

### Community 30 - "AI Search"
Cohesion: 0.16
Nodes (20): Accepted Payment Methods, AI Parking Inspector, AI Search, Audit Log, Dark Mode and Light Mode, Design Philosophy, Digitally Stored Customer Agreement, Future Features Roadmap (+12 more)

### Community 31 - "Monthly Reminder System"
Cohesion: 0.24
Nodes (15): AI Insights / Morning Manager Report, AI Sales Opportunities (Hot/Warm/Cold Leads), Celery Background Jobs, Company Profiles, Daily Customer Tracking, Daily Pass ($20, custom day range), Monthly Customers, Monthly Pass ($250 default, overridable) (+7 more)

### Community 32 - "seed_demo.py"
Cohesion: 0.16
Nodes (16): _issue(), main(), _phone(), Seed realistic demo data into the dev database so every screen populates. Run…, seed(), client(), db(), engine() (+8 more)

### Community 33 - "ParkingPass"
Cohesion: 0.24
Nodes (6): ParkingPass, _issue_with_intent(), A single Stripe PaymentIntent can never mint two passes., test_duplicate_payment_intent_is_rejected(), test_price_from_charge_is_used_verbatim(), Base

### Community 34 - "_price_for"
Cohesion: 0.20
Nodes (15): _expiration_for(), _monthly_rate_for(), _months_between(), _price_for(), Whole calendar months between two dates, rounding UP for any partial overage…, The established PER-MONTH rate — never multiplied by month count. An existing…, _validate_weekly_span(), Pricing math: partial-month rounding and per-type price. (+7 more)

### Community 35 - "routers/reports.py"
Cohesion: 0.41
Nodes (10): Session, reports_summary(), CompanyStat, OutstandingBalance, PaymentMethodStat, BaseModel, ReportsSummary, RevenuePoint (+2 more)

### Community 36 - "create_intent"
Cohesion: 0.22
Nodes (10): _compute_price(), create_intent(), _metadata_from_payload(), CreateIntentResponse, date, PassType, The single source of truth both create-intent and (as a sanity check only, not…, Stripe metadata values must be strings — this is the ONLY record of what a… (+2 more)

### Community 37 - "Tech Stack"
Cohesion: 0.12
Nodes (19): Brand Colors, Docker Deployment, FastAPI, Framer Motion, Modern Skeuomorphism UI Style, Next.js, Nginx, Color Coded Notifications (+11 more)

### Community 38 - "test_auth_api.py"
Cohesion: 0.33
Nodes (8): _login(), Auth endpoints + route protection (FastAPI TestClient over an in-memory DB)., _register(), test_login_locks_out_after_five_failures(), test_login_success_and_wrong_password(), test_me_requires_a_valid_token(), test_register_returns_token_then_second_is_forbidden(), test_status_flips_after_setup()

### Community 39 - "package.json"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, start, test (+1 more)

### Community 40 - "mobile-nav.tsx"
Cohesion: 0.07
Nodes (33): inter, jetbrainsMono, metadata, viewport, CommandPalette(), AppShell(), isPublicPath(), MobileNav() (+25 more)

### Community 41 - "RateLimiter"
Cohesion: 0.28
Nodes (5): _client_key(), Request, RateLimiter, Allow `times` requests per `seconds` per client, else 429., Tests only — start from a clean window.

### Community 42 - "ensure_spots"
Cohesion: 0.22
Nodes (19): ensure_spots(), free_spot_count(), pick_free_spot(), Session, FCFS with a memory: longest-vacant first (NULLS FIRST — a never-used spot is…, Idempotent: rows exist for 1..capacity, and exactly those are active. Shrinking…, _issue(), A spot is held while its pass is live: daily through expiry day, monthly… (+11 more)

### Community 43 - "Core Principle: The Software Remembers Everything"
Cohesion: 0.22
Nodes (9): Engineering Identity Mandate, AI Development Rules (Plan, Build, Verify, Optimize), Coding Standards, Core Principle: The Software Remembers Everything, Feature Justification Rule, Reusable Claude Skill Folder, Madco Truck Plaza Parking Management System, Manual Processes Replaced (+1 more)

### Community 44 - "test_move_spot.py"
Cohesion: 0.47
Nodes (8): _auth(), _issue(), Cashier override: move a truck to a FREE spot. Race-safe, audited, login-gated., test_move_needs_login(), test_move_onto_occupied_spot_is_rejected(), test_move_to_bad_spot_or_pass_404(), test_move_to_free_spot_repoints_and_frees_old(), test_move_to_same_spot_is_rejected()

### Community 46 - "Monochrome 16x16 Glyph Icon System (#666, evenodd fill)"
Cohesion: 0.48
Nodes (7): Document/File Glyph Icon (16x16, #666), Monochrome 16x16 Glyph Icon System (#666, evenodd fill), Globe / Web Glyph Icon (16x16, #666), create-next-app Default Scaffold Assets, Next.js Wordmark Logo (394x80, black), Vercel Triangle Logo (white, 1155x1000), Browser Window Glyph Icon (16x16, #666)

### Community 47 - "verify/[token]/page.tsx"
Cohesion: 0.32
Nodes (6): currency(), Look, lookFor(), VerifyPage(), PassVerifyResult, ReassignResult

### Community 49 - "stripe_payments.py"
Cohesion: 0.21
Nodes (21): PassType, VehicleType, finalize_request(), Turn a confirmed charge into the pass this request was for. Shared by TWO…, cancel_intent(), Best-effort cleanup when a customer abandons checkout. This endpoint is…, CreatePaymentRequest, PaymentRequestCreated (+13 more)

### Community 50 - "routers/spots.py"
Cohesion: 0.10
Nodes (29): move_pass_to_spot(), MoveError, A move the cashier asked for that can't be honored. `status` is the HTTP code…, Cashier override: put a truck in a specific FREE spot. Race-safe against the…, Display label for a spot: 1 -> 'A1', 26 -> 'B1', 150 -> 'F25'. The integer…, spot_label(), _log_unhandled(), Request (+21 more)

### Community 51 - "Go-Live Checklist"
Cohesion: 0.50
Nodes (4): ALERT_WEBHOOK_URL Error Alerting (1/min rate limit), Go-Live Checklist, purge_demo Script (Wipe Demo Data, Keep Logins), Twilio A2P Activation (No Code Change)

### Community 52 - "test_spots_endpoint.py"
Cohesion: 0.43
Nodes (5): _auth(), _issue(), One call paints the whole lot. States derived, matching the holding rules., test_overstay_state_and_clear(), test_states_cover_the_lot()

### Community 61 - "_issue_pass_and_payment"
Cohesion: 0.12
Nodes (24): business_today(), date, The plaza's current calendar day. Use this everywhere `date.today()` was used,…, _issue_pass_and_payment(), Shared by the normal Issue Pass endpoint and the Stripe finalize/webhook…, Kiritimati (UTC+14) and Niue (UTC-11) are 25 hours apart, so their calendar…, The invariant the money depends on: the day a payment is recorded under is the…, test_a_payment_is_stamped_with_the_plazas_day() (+16 more)

### Community 76 - "models/__init__.py"
Cohesion: 0.11
Nodes (24): Alembic environment — wired to the app's own settings and metadata, so there is…, Base, get_db(), Session, get_current_user(), Session, Admin or manager — the money tier. An attendant's job is the front desk: issue,…, require_admin() (+16 more)

### Community 77 - "WebhookAlertHandler"
Cohesion: 0.22
Nodes (5): ERROR-level logs become a phone notification, not a line in a file. A truck…, WebhookAlertHandler, configure_logging(), Console + rotating-file logging for the app. Called once at startup. File…, LogRecord

### Community 78 - "Global Constraints"
Cohesion: 0.20
Nodes (9): Global Constraints, Self-review, Task 1: `spot_label` helper + config, Task 2: expose `spot_label` on every spot-bearing payload, Task 3: move-a-truck endpoint, Task 4: `SpotState` label + `spot_label` frontend types; zone grouping helper, Task 5: the `/availability` page — live board + move flow, Task 6: E2E in a real browser + docs (+1 more)

### Community 79 - "Architecture: labels + polling + one move endpoint (engine untouched)"
Cohesion: 0.22
Nodes (8): 1. Zone labels (derived — no migration, no data change), 2. The cashier availability page (`/availability`), 3. Cashier override — move a truck to a free spot, Architecture: labels + polling + one move endpoint (engine untouched), Decisions (settled with the owner, 2026-08-04), Testing, What does NOT change, Zone Availability + Cashier Override — Design

### Community 80 - "test_insights.py"
Cohesion: 0.13
Nodes (22): conversion_leads(), _monthly_equivalent(), What this company effectively spends per month right now. The window is 90…, Daily/weekly customers who come often enough that a monthly plan would likely…, _tier(), CallItem, ConversionLead, ConversionLeads (+14 more)

### Community 83 - "routers/verify.py"
Cohesion: 0.31
Nodes (9): get, post, Session, The asphalt gap: no sensors, so an expired truck can still sit in a spot the…, report_occupied(), verify_pass(), PassVerifyResult, BaseModel (+1 more)

### Community 86 - "core/spots.py"
Cohesion: 0.31
Nodes (8): _held_spot_ids(), holding_filter(), _live_window_filter(), Spot inventory. State is DERIVED: a spot is free iff no live pass holds it.…, A spot the system may hand to the NEXT customer: active, not held by a live…, The date/status part of 'this pass occupies the lot': not cancelled, and inside…, Boolean clause: this pass currently HOLDS its spot. Evaluated per-query against…, _sellable_filter()

### Community 89 - "lot-check/page.tsx"
Cohesion: 0.31
Nodes (6): expiryPhrase(), LotCheckInner(), PAYMENT_LABEL, shortDate(), STATUS_STYLE, LotCheckResult

## Knowledge Gaps
- **157 isolated node(s):** `ConversionLead`, `ProfileTruck`, `ProfilePass`, `ProfilePayment`, `CreatePaymentRequest` (+152 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_get()` connect `routers/auth.py` to `reminders.py`, `PaymentMethod`, `routers/reports.py`, `test_morning_report.py`, `test_dashboard.py`, `payment_requests.py`, `test_stranded_charges.py`, `test_insights.py`, `stripe_payments.py`, `enums.py`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `business_today()` connect `_issue_pass_and_payment` to `reminders.py`, `seed_demo.py`, `PaymentMethod`, `routers/reports.py`, `test_morning_report.py`, `test_dashboard.py`, `ensure_spots`, `models/__init__.py`, `test_spot_assignment.py`, `test_insights.py`, `test_reminders_sweep.py`, `test_spots_endpoint.py`, `enums.py`, `clock.py`, `test_report_occupied.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Why does `ensure_spots()` connect `ensure_spots` to `test_lot_check.py`, `test_morning_report.py`, `main.py`, `test_move_spot.py`, `test_spot_assignment.py`, `test_spots_endpoint.py`, `core/spots.py`, `test_report_occupied.py`, `_issue_pass_and_payment`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `PassType` (e.g. with `CompanyBase` and `CompanyCreate`) actually correct?**
  _`PassType` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ConversionLead`, `ProfileTruck`, `ProfilePass` to the rest of the system?**
  _157 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `reminders.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10252100840336134 - nodes in this community are weakly interconnected._
- **Should `PaymentMethod` be split into smaller, more focused modules?**
  _Cohesion score 0.07033248081841433 - nodes in this community are weakly interconnected._