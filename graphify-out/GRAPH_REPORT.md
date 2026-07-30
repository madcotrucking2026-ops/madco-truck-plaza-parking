# Graph Report - .  (2026-07-30)

## Corpus Check
- 194 files · ~66,094 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1295 nodes · 3512 edges · 79 communities (60 shown, 19 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 171 edges (avg confidence: 0.61)
- Token cost: 161,298 input · 0 output

## Community Hubs (Navigation)
- Stripe Checkout & Finalize
- Auth, Users & RBAC
- Monthly Customers & Conversion
- Kiosk, Lot Check & Issue Pages
- Audit, Companies & Morning Report UI
- Shadcn UI Primitives
- App Shell, Nav & Theme
- Logging, Alerts & Startup Migrations
- Clock, Database & ORM Models
- Audit Trail, Pass Status & Payments
- Dashboard & Company Profile UI
- Passes UI & Renewal Dialogs
- Pass Issue & Cancel Endpoints
- Company Schemas & Enums
- TypeScript Config
- Payment Requests (Pay Links)
- Stripe Client & Pricing Intents
- Morning Report Insights
- Monthly Customers & Settings UI
- Receipt Codes & Renewal Dates
- Shadcn Component Registry
- Plaza Timezone & Full-Lot Tests
- Monthly Renewal Reminders
- Frontend Dev Dependencies
- Deploy Services & CI Jobs
- Spot Picker & Holding Tests
- Security Hardening Tests
- Frontend Runtime Dependencies
- Product Feature Requirements
- Payment Model & Dashboard Stats
- Demo Seeding & Test Fixtures
- Signed Pass QR Tokens
- Lot Check Endpoint & Tests
- Pricing, Payment & Reminder Rules
- Spot Inventory Spec & Tasks
- Build Standards & Tech Stack
- Spot State Filters & Overstay
- Pass Pricing Rules
- Reports Summary Schemas
- Payments UI & Stat Cards
- Insights Schemas & DB Deps
- Company Profile Aggregation
- Auth API Tests
- Brand, Design & Deploy Rationale
- Config & JWT Secret
- Spot Assignment Tests
- Frontend Package Scripts
- Root Layout, Fonts & Theme
- In-Memory Rate Limiter
- Spot Seeding & Capacity Tests
- Spot Model & Endpoints
- Next.js Scaffold Assets
- Audit Log Endpoint
- Alembic Environment
- Global Search
- Revenue Chart
- Dashboard Schemas
- Next Config & CSP
- Kiosk Booking Layout
- Login Layout
- Pay Link Layout
- Verify Page Layout
- Load Swarm Test Script
- ESLint Config
- Lucide Icons
- Next.js Package
- React DOM Package
- Sonner Toasts
- Stripe React SDK
- Tailwind Merge
- Tailwind Animate CSS
- PostCSS Config
- Future Feature Backlog

## God Nodes (most connected - your core abstractions)
1. `cn()` - 80 edges
2. `_issue_pass_and_payment()` - 65 edges
3. `business_today()` - 64 edges
4. `PassType` - 64 edges
5. `PaymentMethod` - 53 edges
6. `ensure_spots()` - 46 edges
7. `VehicleType` - 46 edges
8. `_get()` - 42 edges
9. `PassStatus` - 35 edges
10. `ParkingPass` - 35 edges

## Surprising Connections (you probably didn't know these)
- `Sticky Monthly Spot + Grace Window` --semantically_similar_to--> `Spot Holder Logic (Car Saves the Truck's Spot)`  [INFERRED] [semantically similar]
  docs/superpowers/specs/2026-07-28-spot-inventory-design.md → CLAUDE.md
- `dev service: postgres (port 5432 exposed)` --semantically_similar_to--> `prod service: postgres:16-alpine + healthcheck`  [INFERRED] [semantically similar]
  docker-compose.yml → docker-compose.prod.yml
- `Task 8: Dashboard lot grid + overstay chip + lot check spot` --references--> `Brand Colour Palette`  [INFERRED]
  docs/superpowers/plans/2026-07-28-spot-inventory.md → CLAUDE.md
- `Spot Surfaces (ticket hero, lot check, dashboard grid, morning report)` --references--> `AI Parking Inspector (Walk-the-Lot Verdict Card)`  [INFERRED]
  docs/superpowers/specs/2026-07-28-spot-inventory-design.md → CLAUDE.md
- `Spot Surfaces (ticket hero, lot check, dashboard grid, morning report)` --implements--> `Smart Dashboard (Business Intelligence, Not Counters)`  [INFERRED]
  docs/superpowers/specs/2026-07-28-spot-inventory-design.md → CLAUDE.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Single-box production stack (five services + TLS profile)** — docker_compose_prod_postgres, docker_compose_prod_backend, docker_compose_prod_frontend, docker_compose_prod_nginx, docker_compose_prod_cron, docker_compose_prod_certbot [EXTRACTED 1.00]
- **Derived-state spot dispatch flow (hold → pick → assign → overstay reassign)** — docs_superpowers_specs_2026_07_28_spot_inventory_design_derived_state, docs_superpowers_specs_2026_07_28_spot_inventory_design_holding_predicate, docs_superpowers_specs_2026_07_28_spot_inventory_design_assignment_algorithm, docs_superpowers_specs_2026_07_28_spot_inventory_design_full_lot_never_strand_money, docs_superpowers_specs_2026_07_28_spot_inventory_design_asphalt_gap [EXTRACTED 1.00]
- **CI quality gates (pytest, tsc, vitest, build, advisory lint)** — _github_workflows_ci_backend_job, _github_workflows_ci_frontend_job, _github_workflows_ci_lint_non_blocking, backend_requirements_dev_test_deps [EXTRACTED 1.00]
- **Untouched create-next-app public/ asset set (vendor branding, not Madco brand)** — frontend_public_file_document_icon, frontend_public_globe_globe_icon, frontend_public_window_window_icon, frontend_public_next_nextjs_wordmark, frontend_public_vercel_vercel_triangle_logo [INFERRED 0.85]

## Communities (79 total, 19 thin omitted)

### Community 0 - "Stripe Checkout & Finalize"
Cohesion: 0.07
Nodes (62): finalize(), _finalize_intent(), _finalize_payment_request(), issue_stranded_pass(), _ours(), PassType, post, Request (+54 more)

### Community 1 - "Auth, Users & RBAC"
Cohesion: 0.07
Nodes (60): AuthStatus, get_current_user(), Session, require_admin(), create_access_token(), decode_access_token(), hash_password(), verify_password() (+52 more)

### Community 2 - "Monthly Customers & Conversion"
Cohesion: 0.07
Nodes (54): MonthlyCustomerStatus, ReminderStatus, MonthlyCustomer, conversion_leads(), _monthly_equivalent(), What this company effectively spends per month right now. The window is 90…, Daily/weekly customers who come often enough that a monthly plan would likely…, _tier() (+46 more)

### Community 3 - "Kiosk, Lot Check & Issue Pages"
Cohesion: 0.09
Nodes (41): BookPage(), PASS_TYPES, PayWay, expiryPhrase(), LotCheckInner(), PAYMENT_LABEL, shortDate(), STATUS_STYLE (+33 more)

### Community 4 - "Audit, Companies & Morning Report UI"
Cohesion: 0.07
Nodes (38): ACTION_STYLE, AuditLogPage(), fmt(), styleFor(), currency(), GROUPS, MorningReportPage(), telHref() (+30 more)

### Community 5 - "Shadcn UI Primitives"
Cohesion: 0.09
Nodes (37): Badge(), badgeVariants, Card(), CardAction(), CardContent(), CardDescription(), CardFooter(), CardHeader() (+29 more)

### Community 6 - "App Shell, Nav & Theme"
Cohesion: 0.09
Nodes (32): CommandPalette(), Field(), AppShell(), isPublicPath(), MobileNav(), SidebarNav(), ThemeToggle(), Button() (+24 more)

### Community 7 - "Logging, Alerts & Startup Migrations"
Cohesion: 0.07
Nodes (33): ERROR-level logs become a phone notification, not a line in a file. A truck…, WebhookAlertHandler, `Base.metadata.create_all()` only creates missing *tables* — it never alters an…, run_startup_migrations(), Admin or manager — the money tier. An attendant's job is the front desk: issue,…, require_manager(), configure_logging(), get_logger() (+25 more)

### Community 8 - "Clock, Database & ORM Models"
Cohesion: 0.17
Nodes (18): business_now(), plaza_tz(), datetime, What day is it *at the plaza*. Two separate bugs live here if you get this…, Wall-clock time at the plaza, naive — stored as-is so `date(paid_at)` in SQL is…, Base, AuditLog, Reminder (+10 more)

### Community 9 - "Audit Trail, Pass Status & Payments"
Cohesion: 0.12
Nodes (25): log_audit(), Session, live_status(), date, Per-client sliding-window rate limiting, as a FastAPI dependency. Deliberately…, AuditAction, create_payment(), list_payments() (+17 more)

### Community 10 - "Dashboard & Company Profile UI"
Cohesion: 0.09
Nodes (21): CompanyProfilePage(), fmtDate(), fmtDateTime(), money(), money2(), currency(), DashboardPage(), LEAD_TIER (+13 more)

### Community 11 - "Passes UI & Renewal Dialogs"
Cohesion: 0.15
Nodes (19): currency(), PassesPage(), PAY_CHOICES, PayChoice, PassTicket(), PAY_CHOICES, PayChoice, Dialog() (+11 more)

### Community 12 - "Pass Issue & Cancel Endpoints"
Cohesion: 0.11
Nodes (27): ParkingPass, cancel_pass(), _expiration_for(), _find_or_create_vehicle(), get_pass(), issue_pass(), _issue_pass_and_payment(), PassType (+19 more)

### Community 13 - "Company Schemas & Enums"
Cohesion: 0.25
Nodes (23): Spot inventory. State is DERIVED: a spot is free iff no live pass holds it.…, PassStatus, PassType, PaymentMethod, CompanyBase, CompanyCreate, CompanyLookupResult, CompanyMonthlyTruck (+15 more)

### Community 14 - "TypeScript Config"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 15 - "Payment Requests (Pay Links)"
Cohesion: 0.16
Nodes (26): VehicleType, PaymentRequest, A pending card payment a manager hands off to the customer to self-pay. Created…, create_intent(), create_payment_request(), finalize(), finalize_request(), get_payment_request() (+18 more)

### Community 16 - "Stripe Client & Pricing Intents"
Cohesion: 0.13
Nodes (23): is_configured(), _lookup_monthly_rate(), The company's established per-month rate, or None if it has no monthly plan on…, _validate_weekly_span(), cancel_intent(), _compute_price(), create_intent(), _metadata_from_payload() (+15 more)

### Community 17 - "Morning Report Insights"
Cohesion: 0.17
Nodes (23): _money(), morning_report(), date, Session, The manager's 7am briefing: who to call today, and why. The dashboard already…, _revenue_on(), _daily(), _FakeUser (+15 more)

### Community 18 - "Monthly Customers & Settings UI"
Cohesion: 0.13
Nodes (18): currency(), MonthlyCustomer, MonthlyCustomersPage(), STATUS_LABEL, ComingSoon(), AddStaffCard(), Role, ROLES (+10 more)

### Community 19 - "Receipt Codes & Renewal Dates"
Cohesion: 0.16
Nodes (18): generate_receipt_number(), date, add_months(), date, apply_renewal(), list_passes(), Validates a proposed renewal and returns (renewal_start, price) WITHOUT…, Applies a validated renewal: extends the pass, records a Payment, and updates… (+10 more)

### Community 20 - "Shadcn Component Registry"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 21 - "Plaza Timezone & Full-Lot Tests"
Cohesion: 0.14
Nodes (18): business_today(), date, The plaza's current calendar day. Use this everywhere `date.today()` was used,…, Kiritimati (UTC+14) and Niue (UTC-11) are 25 hours apart, so their calendar…, The invariant the money depends on: the day a payment is recorded under is the…, test_a_payment_is_stamped_with_the_plazas_day(), test_the_day_comes_from_the_plazas_timezone_not_the_hosts(), _fill_the_lot() (+10 more)

### Community 22 - "Monthly Renewal Reminders"
Cohesion: 0.18
Nodes (19): _already_reminded_today(), _do_send(), list_reminders(), monthly_renewal_list(), date, MonthlyCustomer, Session, Every monthly customer with how their renewal stands, soonest first. Shared… (+11 more)

### Community 23 - "Frontend Dev Dependencies"
Cohesion: 0.10
Nodes (21): eslint, eslint-config-next, devDependencies, eslint, eslint-config-next, playwright, tailwindcss, @tailwindcss/postcss (+13 more)

### Community 24 - "Deploy Services & CI Jobs"
Cohesion: 0.14
Nodes (20): CI job: Frontend · typecheck + test + build (Node 20), Non-blocking lint (react-hooks/set-state-in-effect), Nightly Off-Box Backups (14 kept, host bind mount), One-Command Docker Deployment, Service: cron (reminder sweep + nightly pg_dump), Service: frontend (Next.js), Service: nginx (only published port, /api routing), Service: postgres (named volume) (+12 more)

### Community 25 - "Spot Picker & Holding Tests"
Cohesion: 0.24
Nodes (18): ensure_spots(), free_spot_count(), pick_free_spot(), Session, Idempotent: rows exist for 1..capacity, and exactly those are active. Shrinking…, FCFS with a memory: longest-vacant first (NULLS FIRST — a never-used spot is…, _issue(), A spot is held while its pass is live: daily through expiry day, monthly… (+10 more)

### Community 26 - "Security Hardening Tests"
Cohesion: 0.13
Nodes (16): _intent_body(), Rate limiting and input validation on the unauthenticated surface. Each test…, A crafted end_date decades out turns into an absurd computed price., A negative price would record a NEGATIVE payment against the drawer., Blocks two things the per-account lockout does NOT: a spray across many…, Public and unauthenticated: it answers "does this company exist, what is its…, An unbounded password field means megabytes fed straight into bcrypt on an…, Unbounded here would flow into Stripe metadata and the database. (+8 more)

### Community 27 - "Frontend Runtime Dependencies"
Cohesion: 0.11
Nodes (19): @base-ui/react, class-variance-authority, clsx, cmdk, dependencies, @base-ui/react, class-variance-authority, clsx (+11 more)

### Community 28 - "Product Feature Requirements"
Cohesion: 0.15
Nodes (18): AI Insights — Automatic Morning Manager Report, AI Parking Inspector (Walk-the-Lot Verdict Card), AI Search (Truck / Trailer / Plate in One Second), Audit Log (Everything Tracked), Company Profiles (Risk + Loyalty Scores), Colour-Coded Status Notifications, Immutable Payment History, Search Everywhere (CTRL+K Command Palette) (+10 more)

### Community 29 - "Payment Model & Dashboard Stats"
Cohesion: 0.16
Nodes (13): Payment, What the payment was for — the vehicle on its pass., dashboard_stats(), Session, A payment taken at 10:30pm plaza time belongs to that day's revenue. The same…, test_tonights_takings_are_on_tonights_books(), _issue_active(), Dashboard occupancy: capacity, available spots, occupancy %. (+5 more)

### Community 30 - "Demo Seeding & Test Fixtures"
Cohesion: 0.18
Nodes (13): _issue(), main(), _phone(), Seed realistic demo data into the dev database so every screen populates. Run…, seed(), client(), db(), fixture (+5 more)

### Community 31 - "Signed Pass QR Tokens"
Cohesion: 0.24
Nodes (11): _backfill_pass_qr_codes(), Passes issued before the signed-QR system stored their plaintext receipt number…, make_pass_token(), Returns the pass id if the token's signature is valid, else None., _sign(), verify_pass_token(), _issue(), Customer finds a squatter in their assigned spot: one tap moves them and flags… (+3 more)

### Community 32 - "Lot Check Endpoint & Tests"
Cohesion: 0.26
Nodes (13): lot_check(), Session, _issue(), Lot check — the flagship feature: the manager walks up to a truck, types its…, A renewed pass writes a second Payment row. Reporting the original one would…, Standing at the truck, the manager needs to know which spot it SHOULD be in —…, test_a_daily_walkup_is_not_a_monthly_customer(), test_a_renewal_reports_the_LATEST_payment_not_the_first() (+5 more)

### Community 33 - "Pricing, Payment & Reminder Rules"
Cohesion: 0.14
Nodes (14): Accepted Payment Methods, AI Sales Opportunities (Hot/Warm/Cold Leads), Daily/Weekly Customer Frequency Tracking, Monthly Customers (Company Fleet Accounts), Monthly Price Override (Per-Company Pricing), Monthly Reminder System (7/3/1-Day Cadence), Parking Pass Fields (Minimal Data Capture), Parking Types — Daily / Weekly / Monthly (+6 more)

### Community 34 - "Spot Inventory Spec & Tasks"
Cohesion: 0.22
Nodes (14): Spot Inventory Is Config (PARKING_CAPACITY / SPOT_GRACE_DAYS), PARKING_CAPACITY env (default 150), Task 10: E2E proof + DEPLOY.md docs + memory, Task 1: Spot model, migration, idempotent seeding, Task 2: Holding predicate + free-spot picker, Task 3: Assign at issue time (sticky monthly, full lot never blocks), Task 4: Kiosk pre-check — refuse checkout when full, Assignment Algorithm (in-transaction, FOR UPDATE SKIP LOCKED) (+6 more)

### Community 35 - "Build Standards & Tech Stack"
Cohesion: 0.15
Nodes (13): CI job: Backend · pytest (Python 3.11), bcrypt<4.1 pin (passlib 1.7.4 self-test breakage), Backend dev/test dependency set (pytest, httpx), Backend runtime dependency set, Coding Standards (No Hardcoded Values, Env Vars Only), Parking Rules — FCFS, No Reservations, No Refunds, Tech Stack — Next.js / FastAPI / Postgres / Docker, Spot Inventory Implementation Plan (+5 more)

### Community 36 - "Spot State Filters & Overstay"
Cohesion: 0.15
Nodes (13): _held_spot_ids(), holding_filter(), _live_window_filter(), The date/status part of 'this pass occupies the lot': not cancelled, and inside…, Boolean clause: this pass currently HOLDS its spot. Evaluated per-query against…, A spot the system may hand to the NEXT customer: active, not held by a live…, _sellable_filter(), clear_overstay() (+5 more)

### Community 37 - "Pass Pricing Rules"
Cohesion: 0.24
Nodes (12): _monthly_rate_for(), _months_between(), _price_for(), date, Whole calendar months between two dates, rounding UP for any partial overage…, The established PER-MONTH rate — never multiplied by month count. An existing…, Pricing math: partial-month rounding and per-type price., test_daily_price_scales_with_days() (+4 more)

### Community 38 - "Reports Summary Schemas"
Cohesion: 0.41
Nodes (10): Session, reports_summary(), CompanyStat, OutstandingBalance, PaymentMethodStat, BaseModel, ReportsSummary, RevenuePoint (+2 more)

### Community 39 - "Payments UI & Stat Cards"
Cohesion: 0.24
Nodes (10): bucketOf(), currency(), inPeriod(), METHOD_STYLE, MethodBadge(), Payment, PaymentsPage(), Period (+2 more)

### Community 40 - "Insights Schemas & DB Deps"
Cohesion: 0.33
Nodes (8): get_db(), Session, CallItem, ConversionLead, ConversionLeads, MorningReport, BaseModel, One line of the morning report: a person to call, and the reason to call them.…

### Community 41 - "Company Profile Aggregation"
Cohesion: 0.31
Nodes (10): company_profile(), Everything about one company in one place: totals, trucks, recent passes and…, _find_company(), Match a company by name case-insensitively, ignoring surrounding whitespace —…, _issue(), Company profile aggregation: totals, per-truck rollup, monthly fields., test_profile_404_for_unknown_company(), test_profile_aggregates_visits_trucks_and_spend() (+2 more)

### Community 42 - "Auth API Tests"
Cohesion: 0.33
Nodes (8): _login(), Auth endpoints + route protection (FastAPI TestClient over an in-memory DB)., _register(), test_login_locks_out_after_five_failures(), test_login_success_and_wrong_password(), test_me_requires_a_valid_token(), test_register_returns_token_then_second_is_forbidden(), test_status_flips_after_setup()

### Community 43 - "Brand, Design & Deploy Rationale"
Cohesion: 0.20
Nodes (11): Brand Colour Palette, Core Principle — The Software Remembers Everything, Modern Skeuomorphism Design Philosophy, MTPMS — AI Truck Parking Management System, Success Metric — No More Paper Passes, Typography — Inter + JetBrains Mono, Schema = Alembic Only (Self-Upgrading at Startup), Service: backend (self-migrating FastAPI) (+3 more)

### Community 44 - "Config & JWT Secret"
Cohesion: 0.22
Nodes (4): Settings, load_or_create_jwt_secret(), The external reminder trigger: a shared-secret header, not a user account. Its…, BaseSettings

### Community 45 - "Spot Assignment Tests"
Cohesion: 0.31
Nodes (9): _issue(), Assignment is part of issuing a pass — same transaction, no separate step., Sticky: a lapsed monthly who comes back gets the number they always had., Money already taken must NEVER fail for lack of a spot — pass issues with…, test_full_lot_issues_pass_with_no_spot(), test_issue_assigns_a_spot(), test_renewal_keeps_the_spot(), test_returning_monthly_gets_their_old_spot() (+1 more)

### Community 46 - "Frontend Package Scripts"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, start, test (+1 more)

### Community 47 - "Root Layout, Fonts & Theme"
Cohesion: 0.24
Nodes (6): inter, jetbrainsMono, metadata, viewport, ThemeProvider(), Toaster()

### Community 48 - "In-Memory Rate Limiter"
Cohesion: 0.28
Nodes (5): _client_key(), Request, RateLimiter, Allow `times` requests per `seconds` per client, else 429., Tests only — start from a clean window.

### Community 49 - "Spot Seeding & Capacity Tests"
Cohesion: 0.22
Nodes (8): ensure_spots(): the painted lot exists in the database, sized by config., A deployment that predates spots has live passes with spot_id NULL — the grid…, Regression: the session is autoflush=False, so the picker's not-in-held…, test_backfill_gives_each_stray_its_OWN_spot(), test_capacity_grow_reactivates_and_extends(), test_capacity_shrink_deactivates_never_deletes(), test_seeds_capacity_spots_once(), test_startup_backfills_spots_for_live_legacy_passes()

### Community 50 - "Spot Model & Endpoints"
Cohesion: 0.29
Nodes (5): One painted spot. Free/occupied is NEVER stored here — it is derived from live…, Spot, The lot, painted by query. `expiring` = holder's last day is today or tomorrow…, BaseModel, SpotState

### Community 51 - "Next.js Scaffold Assets"
Cohesion: 0.48
Nodes (7): Document/File Glyph Icon (16x16, #666), Monochrome 16x16 Glyph Icon System (#666, evenodd fill), Globe / Web Glyph Icon (16x16, #666), create-next-app Default Scaffold Assets, Next.js Wordmark Logo (394x80, black), Vercel Triangle Logo (white, 1155x1000), Browser Window Glyph Icon (16x16, #666)

### Community 52 - "Audit Log Endpoint"
Cohesion: 0.40
Nodes (4): list_audit_log(), Session, AuditLogRead, BaseModel

### Community 55 - "Revenue Chart"
Cohesion: 0.83
Nodes (3): currency(), formatDate(), RevenueChart()

## Knowledge Gaps
- **137 isolated node(s):** `$schema`, `style`, `rsc`, `tsx`, `config` (+132 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `business_today()` connect `Plaza Timezone & Full-Lot Tests` to `Monthly Customers & Conversion`, `Clock, Database & ORM Models`, `Audit Trail, Pass Status & Payments`, `Company Schemas & Enums`, `Morning Report Insights`, `Receipt Codes & Renewal Dates`, `Monthly Renewal Reminders`, `Spot Picker & Holding Tests`, `Payment Model & Dashboard Stats`, `Demo Seeding & Test Fixtures`, `Signed Pass QR Tokens`, `Lot Check Endpoint & Tests`, `Spot State Filters & Overstay`, `Reports Summary Schemas`, `Insights Schemas & DB Deps`, `Company Profile Aggregation`, `Spot Assignment Tests`, `Spot Seeding & Capacity Tests`, `Spot Model & Endpoints`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `_get()` connect `Auth, Users & RBAC` to `Lot Check Endpoint & Tests`, `Stripe Checkout & Finalize`, `Monthly Customers & Conversion`, `Spot State Filters & Overstay`, `Reports Summary Schemas`, `Company Profile Aggregation`, `Audit Trail, Pass Status & Payments`, `Pass Issue & Cancel Endpoints`, `Payment Requests (Pay Links)`, `Morning Report Insights`, `Receipt Codes & Renewal Dates`, `Audit Log Endpoint`, `Monthly Renewal Reminders`, `Payment Model & Dashboard Stats`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `_issue_pass_and_payment()` connect `Pass Issue & Cancel Endpoints` to `Stripe Checkout & Finalize`, `Auth, Users & RBAC`, `Monthly Customers & Conversion`, `Clock, Database & ORM Models`, `Audit Trail, Pass Status & Payments`, `Company Schemas & Enums`, `Payment Requests (Pay Links)`, `Stripe Client & Pricing Intents`, `Morning Report Insights`, `Receipt Codes & Renewal Dates`, `Plaza Timezone & Full-Lot Tests`, `Spot Picker & Holding Tests`, `Payment Model & Dashboard Stats`, `Demo Seeding & Test Fixtures`, `Signed Pass QR Tokens`, `Lot Check Endpoint & Tests`, `Pass Pricing Rules`, `Company Profile Aggregation`, `Spot Assignment Tests`, `Spot Seeding & Capacity Tests`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `PassType` (e.g. with `ParkingPass` and `CompanyBase`) actually correct?**
  _`PassType` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `PaymentMethod` (e.g. with `MonthlyCustomer` and `Payment`) actually correct?**
  _`PaymentMethod` has 22 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `style`, `rsc` to the rest of the system?**
  _137 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Stripe Checkout & Finalize` be split into smaller, more focused modules?**
  _Cohesion score 0.06947996589940324 - nodes in this community are weakly interconnected._