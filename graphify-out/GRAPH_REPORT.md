# Graph Report - madco-truck-plaza-parking  (2026-08-04)

## Corpus Check
- 178 files · ~62,100 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1296 nodes · 2991 edges · 121 communities (78 shown, 43 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 174 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `222ddef7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_reminders_sweep.py
- pass_.py
- PassType
- test_lot_check.py
- routers/auth.py
- payments/page.tsx
- test_morning_report.py
- issue/page.tsx
- models/__init__.py
- cn
- passes.py
- migrate.py
- CreateIntentResponse
- morning-report/page.tsx
- Request
- CreateIntentResponse
- compilerOptions
- app/page.tsx
- test_renewal.py
- components.json
- test_dedup.py
- devDependencies
- prod service: backend
- payments.py
- models/company.py
- test_security.py
- test_report_occupied.py
- dependencies
- Task 2: Holding predicate + free-spot picker
- Service: backend (self-migrating FastAPI)
- AI Search
- Monthly Reminder System
- conftest.py
- command.tsx
- _price_for
- _get
- models/payment.py
- Tech Stack
- test_auth_api.py
- package.json
- mobile-nav.tsx
- rate_limit.py
- test_spot_holding.py
- Core Principle: The Software Remembers Everything
- test_move_spot.py
- Monochrome 16x16 Glyph Icon System (#666, evenodd fill)
- api.ts
- test_cron_endpoint.py
- test_company_profile.py
- core/spots.py
- Go-Live Checklist
- clock.py
- next.config.ts
- ensure_spots
- login/layout.tsx
- _issue_pass_and_payment
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
- LotCheckResult
- enums.py
- logging_config.py
- Global Constraints
- Architecture: labels + polling + one move endpoint (engine untouched)
- routers/insights.py
- get
- reminders.py
- routers/verify.py
- BaseModel
- Session
- test_spots_endpoint.py
- input-group.tsx
- date
- renew-dialog.tsx
- PassType
- model_validator
- seed_demo.py
- get_logger
- PassVerifyResult
- ReassignResult
- schemas/spot.py
- sms.py
- Request
- get
- Company
- revenue-chart.tsx
- post
- post
- Session
- date
- PassType
- post
- Session
- CreateIntentRequest
- CreatePaymentRequest
- FinalizeStripePaymentRequest
- PaymentRequestCreated
- PaymentRequestStatus
- StrandedCharge
- app/layout.tsx
- sheet.tsx
- spot_label
- _log_unhandled
- settle.ts

## God Nodes (most connected - your core abstractions)
1. `cn()` - 80 edges
2. `_issue_pass_and_payment()` - 55 edges
3. `ensure_spots()` - 48 edges
4. `business_today()` - 46 edges
5. `PassType` - 45 edges
6. `PaymentMethod` - 43 edges
7. `VehicleType` - 34 edges
8. `_get()` - 30 edges
9. `api` - 25 edges
10. `Base` - 24 edges

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

## Communities (121 total, 43 thin omitted)

### Community 0 - "test_reminders_sweep.py"
Cohesion: 0.10
Nodes (33): _already_reminded_today(), cron_trigger(), list_reminders(), monthly_renewal_list(), date, post, Request, Session (+25 more)

### Community 1 - "pass_.py"
Cohesion: 0.33
Nodes (7): IssuePassRequest, LotCheckResult, PassListItem, PassRead, BaseModel, RenewPassRequest, model_validator

### Community 2 - "PassType"
Cohesion: 0.10
Nodes (45): live_status(), date, PassStatus, PassType, PaymentMethod, VehicleType, dashboard_stats(), Session (+37 more)

### Community 3 - "test_lot_check.py"
Cohesion: 0.26
Nodes (13): lot_check(), get, Session, _issue(), Lot check — the flagship feature: the manager walks up to a truck, types its…, A renewed pass writes a second Payment row. Reporting the original one would…, Standing at the truck, the manager needs to know which spot it SHOULD be in —…, test_a_daily_walkup_is_not_a_monthly_customer() (+5 more)

### Community 4 - "routers/auth.py"
Cohesion: 0.10
Nodes (41): AuthStatus, get_current_user(), Session, Admin or manager — the money tier. An attendant's job is the front desk: issue,…, require_admin(), require_manager(), create_access_token(), decode_access_token() (+33 more)

### Community 5 - "payments/page.tsx"
Cohesion: 0.15
Nodes (22): expiryPhrase(), LotCheckInner(), PAYMENT_LABEL, shortDate(), STATUS_STYLE, bucketOf(), currency(), inPeriod() (+14 more)

### Community 6 - "test_morning_report.py"
Cohesion: 0.09
Nodes (39): conversion_leads(), _money(), _monthly_equivalent(), morning_report(), date, Session, The manager's 7am briefing: who to call today, and why. The dashboard already…, What this company effectively spends per month right now. The window is 90… (+31 more)

### Community 7 - "issue/page.tsx"
Cohesion: 0.09
Nodes (24): currency(), MonthlyCustomer, MonthlyCustomersPage(), STATUS_LABEL, IDENTIFIER_FIELD, IssuePassForm(), PASS_TYPES, PAY_CHOICES (+16 more)

### Community 8 - "models/__init__.py"
Cohesion: 0.16
Nodes (13): Alembic environment — wired to the app's own settings and metadata, so there is…, Base, Company, PaymentRequest, A pending card payment a manager hands off to the customer to self-pay. Created…, A singleton row (always id=1) inserted atomically alongside the very first…, SetupLock, One painted spot. Free/occupied is NEVER stored here — it is derived from live… (+5 more)

### Community 9 - "cn"
Cohesion: 0.12
Nodes (24): MethodBadge(), Badge(), badgeVariants, Card(), CardAction(), CardContent(), CardDescription(), CardFooter() (+16 more)

### Community 10 - "passes.py"
Cohesion: 0.22
Nodes (15): cancel_pass(), get_pass(), issue_pass(), list_passes(), _lookup_monthly_rate(), post, Session, The company's established per-month rate, or None if it has no monthly plan on… (+7 more)

### Community 11 - "migrate.py"
Cohesion: 0.24
Nodes (9): _backfill_pass_qr_codes(), `Base.metadata.create_all()` only creates missing *tables* — it never alters an…, Passes issued before the signed-QR system stored their plaintext receipt number…, run_startup_migrations(), _alembic_config(), Schema management at startup — Alembic is the single mechanism. Replaces the…, Bring the schema to head, whatever state the database is in. Three cases: *…, upgrade_database() (+1 more)

### Community 13 - "morning-report/page.tsx"
Cohesion: 0.10
Nodes (24): ACTION_STYLE, AuditLogPage(), fmt(), styleFor(), currency(), GROUPS, MorningReportPage(), telHref() (+16 more)

### Community 16 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 17 - "app/page.tsx"
Cohesion: 0.10
Nodes (19): CompanyProfilePage(), fmtDate(), fmtDateTime(), money(), money2(), currency(), DashboardPage(), LEAD_TIER (+11 more)

### Community 18 - "test_renewal.py"
Cohesion: 0.23
Nodes (14): add_months(), date, apply_renewal(), Validates a proposed renewal and returns (renewal_start, price) WITHOUT…, Applies a validated renewal: extends the pass, records a Payment, and updates…, renewal_quote(), _issue(), Renewal pricing/validation — and the charge-then-fail regression guard. (+6 more)

### Community 19 - "components.json"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 20 - "test_dedup.py"
Cohesion: 0.27
Nodes (9): _find_or_create_vehicle(), Reuse the company's existing vehicle instead of inserting a new row every time…, _issue(), Company + vehicle de-duplication on issue (the freeform-name bug)., test_find_or_create_vehicle_reuses_by_truck_number(), test_issue_dedupes_company_and_vehicle(), test_new_company_name_is_stored_canonical(), Vehicle (+1 more)

### Community 21 - "devDependencies"
Cohesion: 0.10
Nodes (21): eslint, eslint-config-next, devDependencies, eslint, eslint-config-next, playwright, tailwindcss, @tailwindcss/postcss (+13 more)

### Community 22 - "prod service: backend"
Cohesion: 0.14
Nodes (20): CI job: Frontend · typecheck + test + build (Node 20), Non-blocking lint (react-hooks/set-state-in-effect), Nightly Off-Box Backups (14 kept, host bind mount), One-Command Docker Deployment, Service: cron (reminder sweep + nightly pg_dump), Service: frontend (Next.js), Service: nginx (only published port, /api routing), Service: postgres (named volume) (+12 more)

### Community 23 - "payments.py"
Cohesion: 0.26
Nodes (10): generate_receipt_number(), date, create_payment(), list_payments(), post, Session, PaymentCreate, PaymentRead (+2 more)

### Community 24 - "models/company.py"
Cohesion: 0.18
Nodes (9): health(), lifespan(), The lot, painted by query. `expiring` = holder's last day is today or tomorrow…, DashboardStats, BaseModel, BaseModel, SearchResultItem, FastAPI (+1 more)

### Community 25 - "test_security.py"
Cohesion: 0.12
Nodes (17): _issue(), Rate limiting and input validation on the unauthenticated surface. Each test…, A negative price would record a NEGATIVE payment against the drawer., Blocks two things the per-account lockout does NOT: a spray across many…, Public and unauthenticated: it answers "does this company exist, what is its…, An unbounded password field means megabytes fed straight into bcrypt on an…, Authed desk issue — the only way a pass is created now that the customer kiosk…, Unbounded here would flow straight into the database. (+9 more)

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

### Community 32 - "conftest.py"
Cohesion: 0.23
Nodes (11): client(), db(), engine(), _fresh_engine(), fixture, Session, Test fixtures: an isolated in-memory SQLite database per test. The money-path…, The limiters are module-level singletons keyed by client IP, and every… (+3 more)

### Community 33 - "command.tsx"
Cohesion: 0.20
Nodes (13): CommandPalette(), Command(), CommandDialog(), CommandEmpty(), CommandGroup(), CommandInput(), CommandItem(), CommandList() (+5 more)

### Community 34 - "_price_for"
Cohesion: 0.26
Nodes (11): _monthly_rate_for(), _months_between(), _price_for(), Whole calendar months between two dates, rounding UP for any partial overage…, The established PER-MONTH rate — never multiplied by month count. An existing…, Pricing math: partial-month rounding and per-type price., test_daily_price_scales_with_days(), test_monthly_override_only_for_new_company() (+3 more)

### Community 35 - "_get"
Cohesion: 0.08
Nodes (42): create_company(), get_company(), list_companies(), lookup_company(), Company, post, Session, Used by Issue Pass (monthly) to auto-fill an existing company's negotiated… (+34 more)

### Community 36 - "models/payment.py"
Cohesion: 0.18
Nodes (5): Payment, What the payment was for — the vehicle on its pass., Wipe every piece of business data — the last step before handing the system to…, A payment taken at 10:30pm plaza time belongs to that day's revenue. The same…, test_tonights_takings_are_on_tonights_books()

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
Cohesion: 0.19
Nodes (15): AppShell(), isPublicPath(), MobileNav(), SidebarNav(), ThemeToggle(), SheetContent(), SheetTrigger(), clearToken() (+7 more)

### Community 41 - "rate_limit.py"
Cohesion: 0.24
Nodes (6): _client_key(), Request, RateLimiter, Per-client sliding-window rate limiting, as a FastAPI dependency. Deliberately…, Allow `times` requests per `seconds` per client, else 429., Tests only — start from a clean window.

### Community 42 - "test_spot_holding.py"
Cohesion: 0.24
Nodes (13): free_spot_count(), pick_free_spot(), FCFS with a memory: longest-vacant first (NULLS FIRST — a never-used spot is…, _issue(), A spot is held while its pass is live: daily through expiry day, monthly…, test_cancelled_pass_frees_immediately(), test_expired_monthly_holds_through_grace(), test_live_pass_holds_its_spot() (+5 more)

### Community 43 - "Core Principle: The Software Remembers Everything"
Cohesion: 0.22
Nodes (9): Engineering Identity Mandate, AI Development Rules (Plan, Build, Verify, Optimize), Coding Standards, Core Principle: The Software Remembers Everything, Feature Justification Rule, Reusable Claude Skill Folder, Madco Truck Plaza Parking Management System, Manual Processes Replaced (+1 more)

### Community 44 - "test_move_spot.py"
Cohesion: 0.47
Nodes (8): _auth(), _issue(), Cashier override: move a truck to a FREE spot. Race-safe, audited, login-gated., test_move_needs_login(), test_move_onto_occupied_spot_is_rejected(), test_move_to_bad_spot_or_pass_404(), test_move_to_free_spot_repoints_and_frees_old(), test_move_to_same_spot_is_rejected()

### Community 46 - "Monochrome 16x16 Glyph Icon System (#666, evenodd fill)"
Cohesion: 0.48
Nodes (7): Document/File Glyph Icon (16x16, #666), Monochrome 16x16 Glyph Icon System (#666, evenodd fill), Globe / Web Glyph Icon (16x16, #666), create-next-app Default Scaffold Assets, Next.js Wordmark Logo (394x80, black), Vercel Triangle Logo (white, 1155x1000), Browser Window Glyph Icon (16x16, #666)

### Community 47 - "api.ts"
Cohesion: 0.07
Nodes (29): STATE_CLASS, currency(), Look, lookFor(), VerifyPage(), LEGEND, LotGrid(), STATE_CLASS (+21 more)

### Community 49 - "test_company_profile.py"
Cohesion: 0.24
Nodes (12): company_profile(), Everything about one company in one place: totals, trucks, recent passes and…, _find_company(), Company, Match a company by name case-insensitively, ignoring surrounding whitespace —…, _issue(), Company profile aggregation: totals, per-truck rollup, monthly fields., test_profile_404_for_unknown_company() (+4 more)

### Community 50 - "core/spots.py"
Cohesion: 0.17
Nodes (14): _held_spot_ids(), holding_filter(), _live_window_filter(), move_pass_to_spot(), MoveError, Session, Spot inventory. State is DERIVED: a spot is free iff no live pass holds it.…, A spot the system may hand to the NEXT customer: active, not held by a live… (+6 more)

### Community 51 - "Go-Live Checklist"
Cohesion: 0.50
Nodes (4): ALERT_WEBHOOK_URL Error Alerting (1/min rate limit), Go-Live Checklist, purge_demo Script (Wipe Demo Data, Keep Logins), Twilio A2P Activation (No Code Change)

### Community 52 - "clock.py"
Cohesion: 0.18
Nodes (12): business_now(), plaza_tz(), datetime, What day is it *at the plaza*. Two separate bugs live here if you get this…, Wall-clock time at the plaza, naive — stored as-is so `date(paid_at)` in SQL is…, Settings, The plaza's day. Two bugs lived here, and both only showed themselves in the…, test_business_now_is_wall_clock_time_at_the_plaza() (+4 more)

### Community 56 - "ensure_spots"
Cohesion: 0.27
Nodes (10): ensure_spots(), Idempotent: rows exist for 1..capacity, and exactly those are active. Shrinking…, ensure_spots(): the painted lot exists in the database, sized by config., A deployment that predates spots has live passes with spot_id NULL — the grid…, Regression: the session is autoflush=False, so the picker's not-in-held…, test_backfill_gives_each_stray_its_OWN_spot(), test_capacity_grow_reactivates_and_extends(), test_capacity_shrink_deactivates_never_deletes() (+2 more)

### Community 58 - "_issue_pass_and_payment"
Cohesion: 0.22
Nodes (9): _expiration_for(), _issue_pass_and_payment(), Shared by the normal Issue Pass endpoint and the Stripe finalize/webhook…, The invariant the money depends on: the day a payment is recorded under is the…, test_a_payment_is_stamped_with_the_plazas_day(), The zone label rides on every spot-bearing payload — pass, list, verify, lot…, test_pass_read_has_zone_label(), PassType (+1 more)

### Community 61 - "business_today"
Cohesion: 0.16
Nodes (17): business_today(), date, The plaza's current calendar day. Use this everywhere `date.today()` was used,…, Kiritimati (UTC+14) and Niue (UTC-11) are 25 hours apart, so their calendar…, test_the_day_comes_from_the_plazas_timezone_not_the_hosts(), The spot number rides on every pass payload — ticket, list, verify., test_pass_read_carries_spot_number(), _issue() (+9 more)

### Community 76 - "enums.py"
Cohesion: 0.19
Nodes (19): MonthlyCustomerStatus, ReminderStatus, MonthlyCustomer, Reminder, create_monthly_customer(), list_monthly_customers(), MonthlyCustomer, post (+11 more)

### Community 77 - "logging_config.py"
Cohesion: 0.22
Nodes (5): ERROR-level logs become a phone notification, not a line in a file. A truck…, WebhookAlertHandler, configure_logging(), Console + rotating-file logging for the app. Called once at startup. File…, LogRecord

### Community 78 - "Global Constraints"
Cohesion: 0.20
Nodes (9): Global Constraints, Self-review, Task 1: `spot_label` helper + config, Task 2: expose `spot_label` on every spot-bearing payload, Task 3: move-a-truck endpoint, Task 4: `SpotState` label + `spot_label` frontend types; zone grouping helper, Task 5: the `/availability` page — live board + move flow, Task 6: E2E in a real browser + docs (+1 more)

### Community 79 - "Architecture: labels + polling + one move endpoint (engine untouched)"
Cohesion: 0.22
Nodes (8): 1. Zone labels (derived — no migration, no data change), 2. The cashier availability page (`/availability`), 3. Cashier override — move a truck to a free spot, Architecture: labels + polling + one move endpoint (engine untouched), Decisions (settled with the owner, 2026-08-04), Testing, What does NOT change, Zone Availability + Cashier Override — Design

### Community 80 - "routers/insights.py"
Cohesion: 0.31
Nodes (8): get_db(), Session, CallItem, ConversionLead, ConversionLeads, MorningReport, BaseModel, One line of the morning report: a person to call, and the reason to call them.…

### Community 82 - "reminders.py"
Cohesion: 0.19
Nodes (14): log_audit(), Session, AuditLog, AuditAction, list_audit_log(), Session, _do_send(), MonthlyCustomer (+6 more)

### Community 83 - "routers/verify.py"
Cohesion: 0.31
Nodes (9): get, post, Session, The asphalt gap: no sensors, so an expired truck can still sit in a spot the…, report_occupied(), verify_pass(), PassVerifyResult, BaseModel (+1 more)

### Community 86 - "test_spots_endpoint.py"
Cohesion: 0.43
Nodes (5): _auth(), _issue(), One call paints the whole lot. States derived, matching the holding rules., test_overstay_state_and_clear(), test_states_cover_the_lot()

### Community 87 - "input-group.tsx"
Cohesion: 0.24
Nodes (9): InputGroup(), InputGroupAddon(), inputGroupAddonVariants, InputGroupButton(), inputGroupButtonVariants, InputGroupInput(), InputGroupText(), InputGroupTextarea() (+1 more)

### Community 89 - "renew-dialog.tsx"
Cohesion: 0.15
Nodes (23): currency(), PassesPage(), PAY_CHOICES, PayChoice, PassTicket(), METHOD_LABEL, PAY_CHOICES, PayChoice (+15 more)

### Community 92 - "seed_demo.py"
Cohesion: 0.24
Nodes (7): ParkingPass, _issue(), main(), _phone(), Seed realistic demo data into the dev database so every screen populates. Run…, seed(), Base

### Community 93 - "get_logger"
Cohesion: 0.40
Nodes (5): get_logger(), Child of the app logger, named for the calling module., reminder_scheduler_loop(), _run_sweep_once(), Logger

### Community 96 - "schemas/spot.py"
Cohesion: 0.60
Nodes (4): MoveSpotRequest, MoveSpotResult, SpotState, BaseModel

### Community 97 - "sms.py"
Cohesion: 0.47
Nodes (5): is_configured(), Twilio requires E.164 (+15551234567). Customer phones are stored loosely…, Send an SMS via Twilio. Returns True if it went out, False if SMS isn't…, send_sms(), to_e164()

### Community 102 - "revenue-chart.tsx"
Cohesion: 0.83
Nodes (3): currency(), formatDate(), RevenueChart()

### Community 116 - "app/layout.tsx"
Cohesion: 0.24
Nodes (6): inter, jetbrainsMono, metadata, viewport, ThemeProvider(), Toaster()

### Community 117 - "sheet.tsx"
Cohesion: 0.22
Nodes (6): Sheet(), SheetDescription(), SheetFooter(), SheetHeader(), SheetOverlay(), SheetTitle()

### Community 118 - "spot_label"
Cohesion: 0.43
Nodes (6): Display label for a spot: 1 -> 'A1', 26 -> 'B1', 150 -> 'F25'. The integer…, spot_label(), spot_label: the integer number stays the key; this is only how it reads., test_disabled_zoning_is_bare_number(), test_overflow_past_Z_degrades_to_number(), test_zone_labels_at_boundaries()

### Community 119 - "_log_unhandled"
Cohesion: 0.50
Nodes (4): _log_unhandled(), exception_handler, JSONResponse, Request

## Knowledge Gaps
- **159 isolated node(s):** `QUICK_ACTIONS`, `LEAD_TIER`, `VEHICLE_TYPES`, `IDENTIFIER_FIELD`, `PayChoice` (+154 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **43 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_get()` connect `_get` to `test_reminders_sweep.py`, `PassType`, `routers/auth.py`, `test_morning_report.py`, `passes.py`, `enums.py`, `test_company_profile.py`, `reminders.py`, `payments.py`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `business_today()` connect `business_today` to `test_reminders_sweep.py`, `PassType`, `_get`, `test_report_occupied.py`, `ensure_spots`, `test_morning_report.py`, `models/__init__.py`, `test_spot_holding.py`, `routers/insights.py`, `reminders.py`, `clock.py`, `test_spots_endpoint.py`, `payments.py`, `models/company.py`, `_issue_pass_and_payment`, `seed_demo.py`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `_issue_pass_and_payment()` connect `_issue_pass_and_payment` to `_price_for`, `PassType`, `test_lot_check.py`, `test_morning_report.py`, `passes.py`, `test_spot_holding.py`, `test_company_profile.py`, `test_renewal.py`, `test_dedup.py`, `clock.py`, `test_spots_endpoint.py`, `ensure_spots`, `test_report_occupied.py`, `seed_demo.py`, `business_today`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `PassType` (e.g. with `CompanyBase` and `CompanyCreate`) actually correct?**
  _`PassType` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `QUICK_ACTIONS`, `LEAD_TIER`, `VEHICLE_TYPES` to the rest of the system?**
  _159 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_reminders_sweep.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10084033613445378 - nodes in this community are weakly interconnected._
- **Should `PassType` be split into smaller, more focused modules?**
  _Cohesion score 0.09954751131221719 - nodes in this community are weakly interconnected._