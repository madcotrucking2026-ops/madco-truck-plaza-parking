# Graph Report - madco-truck-plaza-parking  (2026-08-04)

## Corpus Check
- 186 files · ~68,513 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1344 nodes · 3606 edges · 84 communities (67 shown, 17 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 201 edges (avg confidence: 0.65)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ca27371a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_reminders_sweep.py
- test_stranded_charges.py
- ensure_spots
- passes.py
- _get
- issue/page.tsx
- test_morning_report.py
- core/spots.py
- payments/page.tsx
- cn
- PaymentRequest
- models/__init__.py
- PassType
- api.ts
- stripe_payments.py
- renew-dialog.tsx
- compilerOptions
- app/page.tsx
- monthly-customers/page.tsx
- components.json
- button.tsx
- devDependencies
- prod service: backend
- enums.py
- reminders.py
- test_security.py
- test_report_occupied.py
- dependencies
- Task 2: Holding predicate + free-spot picker
- Service: backend (self-migrating FastAPI)
- AI Search
- Monthly Reminder System
- get_db
- Payment
- _price_for
- routers/reports.py
- MonthlyCustomer
- Tech Stack
- test_auth_api.py
- package.json
- app/layout.tsx
- RateLimiter
- test_spot_holding.py
- Core Principle: The Software Remembers Everything
- verify/[token]/page.tsx
- config.py
- Monochrome 16x16 Glyph Icon System (#666, evenodd fill)
- seed_demo.py
- test_cron_endpoint.py
- database.py
- test_webhook_payment_request.py
- Go-Live Checklist
- revenue-chart.tsx
- next.config.ts
- book/layout.tsx
- login/layout.tsx
- pay/[token]/layout.tsx
- verify/[token]/layout.tsx
- swarm_test.py
- business_today
- eslint.config.mjs
- lucide-react
- next
- react-dom
- sonner
- @stripe/react-stripe-js
- tailwind-merge
- tw-animate-css
- postcss.config.mjs
- test_lot_check.py
- ParkingPass
- payments.py
- Global Constraints
- Architecture: labels + polling + one move endpoint (engine untouched)
- routers/insights.py
- WebhookAlertHandler
- _log_unhandled
- _FakeMeta

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

## Communities (84 total, 17 thin omitted)

### Community 0 - "test_reminders_sweep.py"
Cohesion: 0.09
Nodes (39): _already_reminded_today(), cron_trigger(), _do_send(), list_reminders(), monthly_renewal_list(), date, MonthlyCustomer, post (+31 more)

### Community 1 - "test_stranded_charges.py"
Cohesion: 0.22
Nodes (24): Cards Stripe accepted that produced no pass here — money taken, nothing given.…, stranded_charges(), _configured(), _FakeCharge, _FakeUser, _intent(), _listing(), The stranded-charge detector: cards Stripe accepted that produced no pass. This… (+16 more)

### Community 2 - "ensure_spots"
Cohesion: 0.17
Nodes (19): ensure_spots(), Idempotent: rows exist for 1..capacity, and exactly those are active. Shrinking…, _issue(), Assignment is part of issuing a pass — same transaction, no separate step., Sticky: a lapsed monthly who comes back gets the number they always had., Money already taken must NEVER fail for lack of a spot — pass issues with…, test_full_lot_issues_pass_with_no_spot(), test_issue_assigns_a_spot() (+11 more)

### Community 3 - "passes.py"
Cohesion: 0.11
Nodes (33): generate_receipt_number(), date, add_months(), date, apply_renewal(), cancel_pass(), _expiration_for(), _find_or_create_vehicle() (+25 more)

### Community 4 - "_get"
Cohesion: 0.07
Nodes (56): AuthStatus, create_access_token(), hash_password(), verify_password(), health(), Company, EmployeeRole, User (+48 more)

### Community 5 - "issue/page.tsx"
Cohesion: 0.10
Nodes (39): BookPage(), PASS_TYPES, PayWay, expiryPhrase(), LotCheckInner(), PAYMENT_LABEL, shortDate(), STATUS_STYLE (+31 more)

### Community 6 - "test_morning_report.py"
Cohesion: 0.07
Nodes (48): dashboard_stats(), Session, conversion_leads(), _money(), _monthly_equivalent(), morning_report(), date, Session (+40 more)

### Community 7 - "core/spots.py"
Cohesion: 0.14
Nodes (17): _held_spot_ids(), holding_filter(), _live_window_filter(), Spot inventory. State is DERIVED: a spot is free iff no live pass holds it.…, The date/status part of 'this pass occupies the lot': not cancelled, and inside…, Boolean clause: this pass currently HOLDS its spot. Evaluated per-query against…, A spot the system may hand to the NEXT customer: active, not held by a live…, _sellable_filter() (+9 more)

### Community 8 - "payments/page.tsx"
Cohesion: 0.07
Nodes (35): ACTION_STYLE, AuditLogPage(), fmt(), styleFor(), currency(), GROUPS, MorningReportPage(), telHref() (+27 more)

### Community 9 - "cn"
Cohesion: 0.10
Nodes (36): Badge(), badgeVariants, Card(), CardAction(), CardContent(), CardDescription(), CardFooter(), CardHeader() (+28 more)

### Community 10 - "PaymentRequest"
Cohesion: 0.18
Nodes (18): PaymentRequest, A pending card payment a manager hands off to the customer to self-pay. Created…, create_intent(), create_payment_request(), finalize(), finalize_request(), get_payment_request(), _get_request() (+10 more)

### Community 11 - "models/__init__.py"
Cohesion: 0.14
Nodes (19): business_now(), plaza_tz(), datetime, What day is it *at the plaza*. Two separate bugs live here if you get this…, Wall-clock time at the plaza, naive — stored as-is so `date(paid_at)` in SQL is…, Base, Reminder, A singleton row (always id=1) inserted atomically alongside the very first… (+11 more)

### Community 12 - "PassType"
Cohesion: 0.09
Nodes (57): live_status(), date, PassStatus, PassType, PaymentMethod, VehicleType, company_profile(), Everything about one company in one place: totals, trucks, recent passes and… (+49 more)

### Community 13 - "api.ts"
Cohesion: 0.10
Nodes (29): CommandPalette(), AppShell(), isPublicPath(), MobileNav(), SidebarNav(), api, AuthStatus, ConversionLead (+21 more)

### Community 14 - "stripe_payments.py"
Cohesion: 0.10
Nodes (31): is_configured(), issue_pass(), _lookup_monthly_rate(), The company's established per-month rate, or None if it has no monthly plan on…, _validate_weekly_span(), cancel_intent(), _compute_price(), create_intent() (+23 more)

### Community 15 - "renew-dialog.tsx"
Cohesion: 0.14
Nodes (21): currency(), PassesPage(), Field(), PAY_CHOICES, PayChoice, vehicleOf(), PassTicket(), PAY_CHOICES (+13 more)

### Community 16 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 17 - "app/page.tsx"
Cohesion: 0.11
Nodes (17): CompanyProfilePage(), fmtDate(), fmtDateTime(), money(), money2(), currency(), DashboardPage(), LEAD_TIER (+9 more)

### Community 18 - "monthly-customers/page.tsx"
Cohesion: 0.13
Nodes (18): currency(), MonthlyCustomer, MonthlyCustomersPage(), STATUS_LABEL, ComingSoon(), AddStaffCard(), Role, ROLES (+10 more)

### Community 19 - "components.json"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 20 - "button.tsx"
Cohesion: 0.14
Nodes (15): LEGEND, LotGrid(), STATE_CLASS, ThemeToggle(), Button(), buttonVariants, Sheet(), SheetContent() (+7 more)

### Community 21 - "devDependencies"
Cohesion: 0.10
Nodes (21): eslint, eslint-config-next, devDependencies, eslint, eslint-config-next, playwright, tailwindcss, @tailwindcss/postcss (+13 more)

### Community 22 - "prod service: backend"
Cohesion: 0.14
Nodes (20): CI job: Frontend · typecheck + test + build (Node 20), Non-blocking lint (react-hooks/set-state-in-effect), Nightly Off-Box Backups (14 kept, host bind mount), One-Command Docker Deployment, Service: cron (reminder sweep + nightly pg_dump), Service: frontend (Next.js), Service: nginx (only published port, /api routing), Service: postgres (named volume) (+12 more)

### Community 23 - "enums.py"
Cohesion: 0.23
Nodes (11): log_audit(), Session, AuditLog, AuditAction, list_audit_log(), Session, AuditLogRead, BaseModel (+3 more)

### Community 24 - "reminders.py"
Cohesion: 0.13
Nodes (21): get_current_user(), Session, Admin or manager — the money tier. An attendant's job is the front desk: issue,…, require_admin(), require_manager(), configure_logging(), get_logger(), Console + rotating-file logging for the app. Called once at startup. File… (+13 more)

### Community 25 - "test_security.py"
Cohesion: 0.13
Nodes (16): _intent_body(), Rate limiting and input validation on the unauthenticated surface. Each test…, A crafted end_date decades out turns into an absurd computed price., A negative price would record a NEGATIVE payment against the drawer., Blocks two things the per-account lockout does NOT: a spray across many…, Public and unauthenticated: it answers "does this company exist, what is its…, An unbounded password field means megabytes fed straight into bcrypt on an…, Unbounded here would flow into Stripe metadata and the database. (+8 more)

### Community 26 - "test_report_occupied.py"
Cohesion: 0.16
Nodes (16): make_pass_token(), Returns the pass id if the token's signature is valid, else None., _sign(), verify_pass_token(), post, Session, The asphalt gap: no sensors, so an expired truck can still sit in a spot the…, report_occupied() (+8 more)

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

### Community 32 - "get_db"
Cohesion: 0.13
Nodes (16): get_db(), Session, Per-client sliding-window rate limiting, as a FastAPI dependency. Deliberately…, BaseModel, SearchResultItem, client(), db(), engine() (+8 more)

### Community 33 - "Payment"
Cohesion: 0.29
Nodes (4): Payment, What the payment was for — the vehicle on its pass., A payment taken at 10:30pm plaza time belongs to that day's revenue. The same…, test_tonights_takings_are_on_tonights_books()

### Community 34 - "_price_for"
Cohesion: 0.26
Nodes (11): _monthly_rate_for(), _months_between(), _price_for(), Whole calendar months between two dates, rounding UP for any partial overage…, The established PER-MONTH rate — never multiplied by month count. An existing…, Pricing math: partial-month rounding and per-type price., test_daily_price_scales_with_days(), test_monthly_override_only_for_new_company() (+3 more)

### Community 35 - "routers/reports.py"
Cohesion: 0.41
Nodes (10): Session, reports_summary(), CompanyStat, OutstandingBalance, PaymentMethodStat, BaseModel, ReportsSummary, RevenuePoint (+2 more)

### Community 36 - "MonthlyCustomer"
Cohesion: 0.20
Nodes (19): MonthlyCustomerStatus, ReminderStatus, MonthlyCustomer, create_monthly_customer(), list_monthly_customers(), MonthlyCustomer, post, Session (+11 more)

### Community 37 - "Tech Stack"
Cohesion: 0.12
Nodes (19): Brand Colors, Docker Deployment, FastAPI, Framer Motion, Modern Skeuomorphism UI Style, Next.js, Nginx, Color Coded Notifications (+11 more)

### Community 38 - "test_auth_api.py"
Cohesion: 0.33
Nodes (8): _login(), Auth endpoints + route protection (FastAPI TestClient over an in-memory DB)., _register(), test_login_locks_out_after_five_failures(), test_login_success_and_wrong_password(), test_me_requires_a_valid_token(), test_register_returns_token_then_second_is_forbidden(), test_status_flips_after_setup()

### Community 39 - "package.json"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, start, test (+1 more)

### Community 40 - "app/layout.tsx"
Cohesion: 0.24
Nodes (6): inter, jetbrainsMono, metadata, viewport, ThemeProvider(), Toaster()

### Community 41 - "RateLimiter"
Cohesion: 0.28
Nodes (5): _client_key(), Request, RateLimiter, Allow `times` requests per `seconds` per client, else 429., Tests only — start from a clean window.

### Community 42 - "test_spot_holding.py"
Cohesion: 0.17
Nodes (18): free_spot_count(), pick_free_spot(), Session, FCFS with a memory: longest-vacant first (NULLS FIRST — a never-used spot is…, One painted spot. Free/occupied is NEVER stored here — it is derived from live…, Spot, _issue(), A spot is held while its pass is live: daily through expiry day, monthly… (+10 more)

### Community 43 - "Core Principle: The Software Remembers Everything"
Cohesion: 0.22
Nodes (9): Engineering Identity Mandate, AI Development Rules (Plan, Build, Verify, Optimize), Coding Standards, Core Principle: The Software Remembers Everything, Feature Justification Rule, Reusable Claude Skill Folder, Madco Truck Plaza Parking Management System, Manual Processes Replaced (+1 more)

### Community 44 - "verify/[token]/page.tsx"
Cohesion: 0.32
Nodes (6): currency(), Look, lookFor(), VerifyPage(), PassVerifyResult, ReassignResult

### Community 45 - "config.py"
Cohesion: 0.23
Nodes (8): Settings, load_or_create_jwt_secret(), _auth(), _issue(), One call paints the whole lot. States derived, matching the holding rules., test_overstay_state_and_clear(), test_states_cover_the_lot(), BaseSettings

### Community 46 - "Monochrome 16x16 Glyph Icon System (#666, evenodd fill)"
Cohesion: 0.48
Nodes (7): Document/File Glyph Icon (16x16, #666), Monochrome 16x16 Glyph Icon System (#666, evenodd fill), Globe / Web Glyph Icon (16x16, #666), create-next-app Default Scaffold Assets, Next.js Wordmark Logo (394x80, black), Vercel Triangle Logo (white, 1155x1000), Browser Window Glyph Icon (16x16, #666)

### Community 47 - "seed_demo.py"
Cohesion: 0.53
Nodes (5): _issue(), main(), _phone(), Seed realistic demo data into the dev database so every screen populates. Run…, seed()

### Community 49 - "database.py"
Cohesion: 0.17
Nodes (10): Alembic environment — wired to the app's own settings and metadata, so there is…, _backfill_pass_qr_codes(), `Base.metadata.create_all()` only creates missing *tables* — it never alters an…, Passes issued before the signed-QR system stored their plaintext receipt number…, run_startup_migrations(), _alembic_config(), Schema management at startup — Alembic is the single mechanism. Replaces the…, Bring the schema to head, whatever state the database is in. Three cases: *… (+2 more)

### Community 50 - "test_webhook_payment_request.py"
Cohesion: 0.26
Nodes (14): _finalize_payment_request(), Webhook safety net for pay-link payments. Imported lazily to keep the router…, _FakeIntent, _pending_request(), The webhook safety net for manager-created pay links. The bug this guards: the…, Customer pays, phone dies. Stripe's webhook must still produce the pass., Both paths race on a good connection. Second one must return the same pass, not…, If Stripe charged something other than the quote, no retry will ever fix it.… (+6 more)

### Community 51 - "Go-Live Checklist"
Cohesion: 0.50
Nodes (4): ALERT_WEBHOOK_URL Error Alerting (1/min rate limit), Go-Live Checklist, purge_demo Script (Wipe Demo Data, Keep Logins), Twilio A2P Activation (No Code Change)

### Community 52 - "revenue-chart.tsx"
Cohesion: 0.83
Nodes (3): currency(), formatDate(), RevenueChart()

### Community 61 - "business_today"
Cohesion: 0.17
Nodes (14): business_today(), date, The plaza's current calendar day. Use this everywhere `date.today()` was used,…, Kiritimati (UTC+14) and Niue (UTC-11) are 25 hours apart, so their calendar…, The invariant the money depends on: the day a payment is recorded under is the…, test_a_payment_is_stamped_with_the_plazas_day(), test_the_day_comes_from_the_plazas_timezone_not_the_hosts(), _fill_the_lot() (+6 more)

### Community 75 - "test_lot_check.py"
Cohesion: 0.26
Nodes (13): lot_check(), Session, _issue(), Lot check — the flagship feature: the manager walks up to a truck, types its…, A renewed pass writes a second Payment row. Reporting the original one would…, Standing at the truck, the manager needs to know which spot it SHOULD be in —…, test_a_daily_walkup_is_not_a_monthly_customer(), test_a_renewal_reports_the_LATEST_payment_not_the_first() (+5 more)

### Community 76 - "ParkingPass"
Cohesion: 0.35
Nodes (9): ParkingPass, _finalize_intent(), Shared by the client-driven /finalize call (fast path, for immediate UI…, _md(), Stripe finalize core (_finalize_intent) — the path that turns a confirmed…, test_finalize_is_idempotent(), test_finalize_issues_pass_from_metadata(), test_finalize_rejects_intent_without_pass_metadata() (+1 more)

### Community 77 - "payments.py"
Cohesion: 0.33
Nodes (8): create_payment(), list_payments(), post, Session, PaymentCreate, PaymentRead, BaseModel, Payment

### Community 78 - "Global Constraints"
Cohesion: 0.20
Nodes (9): Global Constraints, Self-review, Task 1: `spot_label` helper + config, Task 2: expose `spot_label` on every spot-bearing payload, Task 3: move-a-truck endpoint, Task 4: `SpotState` label + `spot_label` frontend types; zone grouping helper, Task 5: the `/availability` page — live board + move flow, Task 6: E2E in a real browser + docs (+1 more)

### Community 79 - "Architecture: labels + polling + one move endpoint (engine untouched)"
Cohesion: 0.22
Nodes (8): 1. Zone labels (derived — no migration, no data change), 2. The cashier availability page (`/availability`), 3. Cashier override — move a truck to a free spot, Architecture: labels + polling + one move endpoint (engine untouched), Decisions (settled with the owner, 2026-08-04), Testing, What does NOT change, Zone Availability + Cashier Override — Design

### Community 80 - "routers/insights.py"
Cohesion: 0.50
Nodes (6): CallItem, ConversionLead, ConversionLeads, MorningReport, BaseModel, One line of the morning report: a person to call, and the reason to call them.…

### Community 81 - "WebhookAlertHandler"
Cohesion: 0.29
Nodes (3): ERROR-level logs become a phone notification, not a line in a file. A truck…, WebhookAlertHandler, LogRecord

### Community 82 - "_log_unhandled"
Cohesion: 0.40
Nodes (5): _log_unhandled(), Request, Exception, exception_handler, JSONResponse

## Knowledge Gaps
- **155 isolated node(s):** `Task 1: `spot_label` helper + config`, `Task 2: expose `spot_label` on every spot-bearing payload`, `Task 3: move-a-truck endpoint`, `Task 4: `SpotState` label + `spot_label` frontend types; zone grouping helper`, `Task 5: the `/availability` page — live board + move flow` (+150 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `business_today()` connect `business_today` to `test_reminders_sweep.py`, `ensure_spots`, `passes.py`, `routers/reports.py`, `test_morning_report.py`, `core/spots.py`, `test_spot_holding.py`, `models/__init__.py`, `PassType`, `test_lot_check.py`, `payments.py`, `seed_demo.py`, `routers/insights.py`, `config.py`, `enums.py`, `reminders.py`, `test_report_occupied.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `_get()` connect `_get` to `test_reminders_sweep.py`, `test_stranded_charges.py`, `passes.py`, `MonthlyCustomer`, `routers/reports.py`, `test_morning_report.py`, `core/spots.py`, `PaymentRequest`, `test_lot_check.py`, `PassType`, `payments.py`, `ParkingPass`, `stripe_payments.py`, `enums.py`, `test_report_occupied.py`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `_issue_pass_and_payment()` connect `passes.py` to `Payment`, `_price_for`, `ensure_spots`, `_get`, `MonthlyCustomer`, `test_morning_report.py`, `test_spot_holding.py`, `PaymentRequest`, `ParkingPass`, `PassType`, `stripe_payments.py`, `seed_demo.py`, `models/__init__.py`, `test_lot_check.py`, `config.py`, `enums.py`, `test_report_occupied.py`, `business_today`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `PassType` (e.g. with `ParkingPass` and `CompanyBase`) actually correct?**
  _`PassType` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `PaymentMethod` (e.g. with `MonthlyCustomer` and `Payment`) actually correct?**
  _`PaymentMethod` has 22 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Task 1: `spot_label` helper + config`, `Task 2: expose `spot_label` on every spot-bearing payload`, `Task 3: move-a-truck endpoint` to the rest of the system?**
  _155 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_reminders_sweep.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08658536585365853 - nodes in this community are weakly interconnected._