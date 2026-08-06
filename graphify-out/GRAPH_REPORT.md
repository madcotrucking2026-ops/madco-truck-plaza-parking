# Graph Report - madco-truck-plaza-parking  (2026-08-06)

## Corpus Check
- 185 files · ~70,062 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1375 nodes · 3514 edges · 90 communities (72 shown, 18 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 204 edges (avg confidence: 0.65)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7ffd2b0b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- passes.py
- PassType
- MonthlyCustomer
- test_morning_report.py
- routers/auth.py
- renew-dialog.tsx
- _get
- _issue_pass_and_payment
- get_db
- cn
- test_pass_status.py
- WebhookAlertHandler
- reminders.py
- app/page.tsx
- Pass expiry + renewal — design spec (2026-08-05)
- business_today
- compilerOptions
- api.ts
- command.tsx
- components.json
- DESIGN.md — Madco Truck Plaza Parking Management System
- devDependencies
- prod service: backend
- test_renewal.py
- companies.py
- test_security.py
- test_report_occupied.py
- dependencies
- Task 2: Holding predicate + free-spot picker
- Service: backend (self-migrating FastAPI)
- AI Search
- Monthly Reminder System
- bulk-renew-dialog.tsx
- Lot organization + reserved monthly spots — design spec (2026-08-05)
- Payment
- app/layout.tsx
- monthly_spot_limit
- Tech Stack
- test_auth_api.py
- package.json
- mobile-nav.tsx
- payments.py
- ensure_spots
- Core Principle: The Software Remembers Everything
- test_move_spot.py
- test_lot_check.py
- Monochrome 16x16 Glyph Icon System (#666, evenodd fill)
- [token]/page.tsx
- Session
- Spot Surfaces (ticket hero, lot check, dashboard grid, morning report)
- Go-Live Checklist
- routers/reports.py
- next.config.ts
- seed_demo.py
- login/layout.tsx
- test_reserved_spots.py
- verify/[token]/layout.tsx
- swarm_test.py
- payments/page.tsx
- eslint.config.mjs
- lucide-react
- next
- react-dom
- test_dashboard.py
- @stripe/react-stripe-js
- tailwind-merge
- _price_for
- postcss.config.mjs
- RateLimiter
- routers/spots.py
- test_spots_endpoint.py
- Global Constraints
- Architecture: labels + polling + one move endpoint (engine untouched)
- test_cron_endpoint.py
- _log_unhandled
- DashboardStats
- settings/page.tsx
- routers/insights.py
- routers/audit_log.py
- @base-ui/react
- shadcn
- spot_label
- settle.ts

## God Nodes (most connected - your core abstractions)
1. `cn()` - 80 edges
2. `_issue_pass_and_payment()` - 67 edges
3. `PassType` - 65 edges
4. `ensure_spots()` - 63 edges
5. `business_today()` - 60 edges
6. `PaymentMethod` - 54 edges
7. `VehicleType` - 45 edges
8. `PassStatus` - 37 edges
9. `business_now()` - 34 edges
10. `_get()` - 34 edges

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

## Communities (90 total, 18 thin omitted)

### Community 0 - "passes.py"
Cohesion: 0.12
Nodes (31): log_audit(), Session, business_now(), plaza_tz(), datetime, What day is it *at the plaza*. Two separate bugs live here if you get this…, Wall-clock time at the plaza, naive — stored as-is so `date(paid_at)` in SQL is…, Base (+23 more)

### Community 1 - "PassType"
Cohesion: 0.07
Nodes (64): PassStatus, PassType, PaymentMethod, VehicleType, company_profile(), Everything about one company in one place: totals, trucks, recent passes and…, _find_company(), Match a company by name case-insensitively, ignoring surrounding whitespace —… (+56 more)

### Community 2 - "MonthlyCustomer"
Cohesion: 0.22
Nodes (18): MonthlyCustomerStatus, ReminderStatus, MonthlyCustomer, create_monthly_customer(), list_monthly_customers(), MonthlyCustomer, post, Session (+10 more)

### Community 3 - "test_morning_report.py"
Cohesion: 0.17
Nodes (23): _money(), morning_report(), date, Session, The manager's 7am briefing: who to call today, and why. The dashboard already…, _revenue_on(), _daily(), _FakeUser (+15 more)

### Community 4 - "routers/auth.py"
Cohesion: 0.13
Nodes (32): AuthStatus, create_access_token(), hash_password(), verify_password(), EmployeeRole, auth_status(), create_staff_user(), list_users() (+24 more)

### Community 5 - "renew-dialog.tsx"
Cohesion: 0.10
Nodes (37): expiryPhrase(), LotCheckInner(), PAYMENT_LABEL, shortDate(), STATUS_STYLE, IDENTIFIER_FIELD, IssuePassForm(), PASS_TYPES (+29 more)

### Community 6 - "_get"
Cohesion: 0.06
Nodes (55): health(), me(), lookup_company(), Used by Issue Pass (monthly) to auto-fill an existing company's negotiated…, _already_reminded_today(), cron_trigger(), _do_send(), list_reminders() (+47 more)

### Community 7 - "_issue_pass_and_payment"
Cohesion: 0.16
Nodes (18): _close_out_price(), _expiration_for(), issue_pass(), _issue_pass_and_payment(), _monthly_rate_for(), date, PassType, Shared by the normal Issue Pass endpoint and the Stripe finalize/webhook… (+10 more)

### Community 8 - "get_db"
Cohesion: 0.10
Nodes (24): _backfill_pass_qr_codes(), get_db(), Session, `Base.metadata.create_all()` only creates missing *tables* — it never alters an…, Passes issued before the signed-QR system stored their plaintext receipt number…, run_startup_migrations(), _alembic_config(), Schema management at startup — Alembic is the single mechanism. Replaces the… (+16 more)

### Community 9 - "cn"
Cohesion: 0.08
Nodes (43): currency(), MonthlyCustomer, MonthlyCustomersPage(), STATUS_LABEL, AddStaffCard(), Role, ROLES, Badge() (+35 more)

### Community 10 - "test_pass_status.py"
Cohesion: 0.19
Nodes (23): live_status(), pass_expired(), date, datetime, PassType, Has this pass's paid window ended, at the plaza clock `now`? `now` is the…, list_passes(), dt() (+15 more)

### Community 11 - "WebhookAlertHandler"
Cohesion: 0.29
Nodes (3): ERROR-level logs become a phone notification, not a line in a file. A truck…, WebhookAlertHandler, LogRecord

### Community 12 - "reminders.py"
Cohesion: 0.12
Nodes (14): Alembic environment — wired to the app's own settings and metadata, so there is…, Settings, load_or_create_jwt_secret(), configure_logging(), get_logger(), Console + rotating-file logging for the app. Called once at startup. File…, Child of the app logger, named for the calling module., is_configured() (+6 more)

### Community 13 - "app/page.tsx"
Cohesion: 0.12
Nodes (16): CompanyProfilePage(), fmtDate(), fmtDateTime(), money(), money2(), currency(), DashboardPage(), LEAD_TIER (+8 more)

### Community 14 - "Pass expiry + renewal — design spec (2026-08-05)"
Cohesion: 0.14
Nodes (13): Decisions made (flag at sign-off if wrong), Out of scope / risks, Pass expiry + renewal — design spec (2026-08-05), R1 — Daily passes expire at 12:00 PM (noon), plaza time, R2 — A renewal always starts from the old pass's end date (all types), R3 — Late renewal, two modes: **Continue** vs **Close-out**, R4 — Auto pre-fill (owner never calculates), R5 — Daily / weekly renewal (+5 more)

### Community 15 - "business_today"
Cohesion: 0.21
Nodes (14): business_today(), date, The plaza's current calendar day. Use this everywhere `date.today()` was used,…, Kiritimati (UTC+14) and Niue (UTC-11) are 25 hours apart, so their calendar…, test_the_day_comes_from_the_plazas_timezone_not_the_hosts(), _issue(), Assignment is part of issuing a pass — same transaction, no separate step., Sticky: a lapsed monthly who comes back gets the number they always had. (+6 more)

### Community 16 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 17 - "api.ts"
Cohesion: 0.08
Nodes (35): AvailabilityPage(), LEGEND, STATE_CLASS, currency(), GROUPS, MorningReportPage(), telHref(), currency() (+27 more)

### Community 18 - "command.tsx"
Cohesion: 0.20
Nodes (13): CommandPalette(), Command(), CommandDialog(), CommandEmpty(), CommandGroup(), CommandInput(), CommandItem(), CommandList() (+5 more)

### Community 19 - "components.json"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 20 - "DESIGN.md — Madco Truck Plaza Parking Management System"
Cohesion: 0.13
Nodes (14): Accessibility, Brand tokens (light mode `:root`), Colour — the 60-30-10 system, Component conventions, DESIGN.md — Madco Truck Plaza Parking Management System, Guardrails — what this brand never does, Identity, Motion (+6 more)

### Community 21 - "devDependencies"
Cohesion: 0.10
Nodes (21): eslint, eslint-config-next, devDependencies, eslint, eslint-config-next, playwright, tailwindcss, @tailwindcss/postcss (+13 more)

### Community 22 - "prod service: backend"
Cohesion: 0.14
Nodes (20): CI job: Frontend · typecheck + test + build (Node 20), Non-blocking lint (react-hooks/set-state-in-effect), Nightly Off-Box Backups (14 kept, host bind mount), One-Command Docker Deployment, Service: cron (reminder sweep + nightly pg_dump), Service: frontend (Next.js), Service: nginx (only published port, /api routing), Service: postgres (named volume) (+12 more)

### Community 23 - "test_renewal.py"
Cohesion: 0.20
Nodes (19): add_months(), date, apply_renewal(), Validates a proposed renewal and returns (renewal_start, price) WITHOUT…, Applies a validated renewal: extends the pass, records a Payment, and updates…, renewal_quote(), _issue(), Renewal pricing/validation — and the charge-then-fail regression guard. (+11 more)

### Community 24 - "companies.py"
Cohesion: 0.13
Nodes (21): get_current_user(), Session, Admin or manager — the money tier. An attendant's job is the front desk: issue,…, require_admin(), require_manager(), Per-client sliding-window rate limiting, as a FastAPI dependency. Deliberately…, reminder_scheduler_loop(), _run_sweep_once() (+13 more)

### Community 25 - "test_security.py"
Cohesion: 0.12
Nodes (17): _issue(), Rate limiting and input validation on the unauthenticated surface. Each test…, A negative price would record a NEGATIVE payment against the drawer., Blocks two things the per-account lockout does NOT: a spray across many…, Public and unauthenticated: it answers "does this company exist, what is its…, An unbounded password field means megabytes fed straight into bcrypt on an…, Authed desk issue — the only way a pass is created now that the customer kiosk…, Unbounded here would flow straight into the database. (+9 more)

### Community 26 - "test_report_occupied.py"
Cohesion: 0.16
Nodes (16): make_pass_token(), Returns the pass id if the token's signature is valid, else None., _sign(), verify_pass_token(), post, Session, The asphalt gap: no sensors, so an expired truck can still sit in a spot the…, report_occupied() (+8 more)

### Community 27 - "dependencies"
Cohesion: 0.11
Nodes (19): class-variance-authority, clsx, cmdk, dependencies, class-variance-authority, clsx, cmdk, next-themes (+11 more)

### Community 28 - "Task 2: Holding predicate + free-spot picker"
Cohesion: 0.16
Nodes (19): Spot Inventory Is Config (PARKING_CAPACITY / SPOT_GRACE_DAYS), Stripe Webhook + Payment-Method Domain Setup, PARKING_CAPACITY env (default 150), Task 10: E2E proof + DEPLOY.md docs + memory, Task 1: Spot model, migration, idempotent seeding, Task 2: Holding predicate + free-spot picker, Task 3: Assign at issue time (sticky monthly, full lot never blocks), Task 4: Kiosk pre-check — refuse checkout when full (+11 more)

### Community 29 - "Service: backend (self-migrating FastAPI)"
Cohesion: 0.15
Nodes (15): CI job: Backend · pytest (Python 3.11), bcrypt<4.1 pin (passlib 1.7.4 self-test breakage), Backend dev/test dependency set (pytest, httpx), Backend runtime dependency set, Inter (headings and body), JetBrains Mono (numbers), Typography System, Schema = Alembic Only (Self-Upgrading at Startup) (+7 more)

### Community 30 - "AI Search"
Cohesion: 0.21
Nodes (15): Accepted Payment Methods, AI Search, Audit Log, Digitally Stored Customer Agreement, Future Features Roadmap, JWT Auth with Role Based Access, Outstanding Balance, Parking Objects (Vehicle Types) (+7 more)

### Community 31 - "Monthly Reminder System"
Cohesion: 0.24
Nodes (15): AI Insights / Morning Manager Report, AI Sales Opportunities (Hot/Warm/Cold Leads), Celery Background Jobs, Company Profiles, Daily Customer Tracking, Daily Pass ($20, custom day range), Monthly Customers, Monthly Pass ($250 default, overridable) (+7 more)

### Community 32 - "bulk-renew-dialog.tsx"
Cohesion: 0.14
Nodes (20): currency(), PassesPage(), Field(), PAY_CHOICES, PayChoice, Button(), buttonVariants, Dialog() (+12 more)

### Community 33 - "Lot organization + reserved monthly spots — design spec (2026-08-05)"
Cohesion: 0.12
Nodes (15): Behaviour changes by component, Data model + migration, Frontend, Lot organization + reserved monthly spots — design spec (2026-08-05), Open / risks, R1 — Zone split, R2 — Monthly = a reserved spot, theirs for the whole paid period, R3 — Release only on close-out (+7 more)

### Community 34 - "Payment"
Cohesion: 0.29
Nodes (4): Payment, What the payment was for — the vehicle on its pass., A payment taken at 10:30pm plaza time belongs to that day's revenue. The same…, test_tonights_takings_are_on_tonights_books()

### Community 35 - "app/layout.tsx"
Cohesion: 0.24
Nodes (6): inter, jetbrainsMono, metadata, viewport, ThemeProvider(), Toaster()

### Community 36 - "monthly_spot_limit"
Cohesion: 0.42
Nodes (8): is_monthly_spot(), monthly_spot_limit(), Highest spot number in the MONTHLY area (Zone A by default). 0 when the split…, True if this spot number falls in the monthly (reserved) area., The monthly/daily lot split (which spot numbers are the monthly area)., test_monthly_area_is_zone_a_by_default(), test_split_off_when_count_is_zero(), test_two_monthly_zones_extends_the_area()

### Community 37 - "Tech Stack"
Cohesion: 0.17
Nodes (12): Docker Deployment, FastAPI, Next.js, Nginx, PostgreSQL, Shadcn UI, SQLAlchemy, Tailwind CSS (+4 more)

### Community 38 - "test_auth_api.py"
Cohesion: 0.33
Nodes (8): _login(), Auth endpoints + route protection (FastAPI TestClient over an in-memory DB)., _register(), test_login_locks_out_after_five_failures(), test_login_success_and_wrong_password(), test_me_requires_a_valid_token(), test_register_returns_token_then_second_is_forbidden(), test_status_flips_after_setup()

### Community 39 - "package.json"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, start, test (+1 more)

### Community 40 - "mobile-nav.tsx"
Cohesion: 0.13
Nodes (21): AppShell(), isPublicPath(), MobileNav(), SidebarNav(), ThemeToggle(), Sheet(), SheetContent(), SheetDescription() (+13 more)

### Community 41 - "payments.py"
Cohesion: 0.26
Nodes (10): generate_receipt_number(), date, create_payment(), list_payments(), post, Session, PaymentCreate, PaymentRead (+2 more)

### Community 42 - "ensure_spots"
Cohesion: 0.14
Nodes (27): ensure_spots(), free_spot_count(), pick_free_spot(), PassType, Assign a physical spot, reservation- and type-aware. Monthly is per-truck and…, Idempotent: rows exist for 1..capacity, and exactly those are active. Shrinking…, _issue(), A spot is held while its pass is live: daily through expiry day, monthly… (+19 more)

### Community 43 - "Core Principle: The Software Remembers Everything"
Cohesion: 0.22
Nodes (9): Engineering Identity Mandate, AI Development Rules (Plan, Build, Verify, Optimize), Coding Standards, Core Principle: The Software Remembers Everything, Feature Justification Rule, Reusable Claude Skill Folder, Madco Truck Plaza Parking Management System, Manual Processes Replaced (+1 more)

### Community 44 - "test_move_spot.py"
Cohesion: 0.47
Nodes (8): _auth(), _issue(), Cashier override: move a truck to a FREE spot. Race-safe, audited, login-gated., test_move_needs_login(), test_move_onto_occupied_spot_is_rejected(), test_move_to_bad_spot_or_pass_404(), test_move_to_free_spot_repoints_and_frees_old(), test_move_to_same_spot_is_rejected()

### Community 45 - "test_lot_check.py"
Cohesion: 0.26
Nodes (13): lot_check(), Session, _issue(), Lot check — the flagship feature: the manager walks up to a truck, types its…, A renewed pass writes a second Payment row. Reporting the original one would…, Standing at the truck, the manager needs to know which spot it SHOULD be in —…, test_a_daily_walkup_is_not_a_monthly_customer(), test_a_renewal_reports_the_LATEST_payment_not_the_first() (+5 more)

### Community 46 - "Monochrome 16x16 Glyph Icon System (#666, evenodd fill)"
Cohesion: 0.48
Nodes (7): Document/File Glyph Icon (16x16, #666), Monochrome 16x16 Glyph Icon System (#666, evenodd fill), Globe / Web Glyph Icon (16x16, #666), create-next-app Default Scaffold Assets, Next.js Wordmark Logo (394x80, black), Vercel Triangle Logo (white, 1155x1000), Browser Window Glyph Icon (16x16, #666)

### Community 47 - "[token]/page.tsx"
Cohesion: 0.32
Nodes (6): currency(), Look, lookFor(), VerifyPage(), PassVerifyResult, ReassignResult

### Community 48 - "Session"
Cohesion: 0.18
Nodes (12): cancel_pass(), _find_or_create_vehicle(), _lookup_monthly_rate(), post, Session, Reuse the company's existing vehicle instead of inserting a new row every time…, The company's established per-month rate, or None if it has no monthly plan on…, Removes a truck from a monthly plan (or cancels any pass) without deleting its… (+4 more)

### Community 50 - "Spot Surfaces (ticket hero, lot check, dashboard grid, morning report)"
Cohesion: 0.24
Nodes (12): AI Parking Inspector, Brand Colors, Dark Mode and Light Mode, Design Philosophy, Framer Motion, Modern Skeuomorphism UI Style, Color Coded Notifications, Search Everywhere (CTRL + K) (+4 more)

### Community 51 - "Go-Live Checklist"
Cohesion: 0.50
Nodes (4): ALERT_WEBHOOK_URL Error Alerting (1/min rate limit), Go-Live Checklist, purge_demo Script (Wipe Demo Data, Keep Logins), Twilio A2P Activation (No Code Change)

### Community 52 - "routers/reports.py"
Cohesion: 0.41
Nodes (10): Session, reports_summary(), CompanyStat, OutstandingBalance, PaymentMethodStat, BaseModel, ReportsSummary, RevenuePoint (+2 more)

### Community 56 - "seed_demo.py"
Cohesion: 0.53
Nodes (5): _issue(), main(), _phone(), Seed realistic demo data into the dev database so every screen populates. Run…, seed()

### Community 58 - "test_reserved_spots.py"
Cohesion: 0.15
Nodes (23): _live_window_filter(), move_pass_to_spot(), MoveError, Exception, Session, A move the cashier asked for that can't be honored. `status` is the HTTP code…, Cashier override: put a truck in a specific FREE spot. Race-safe against the…, The date/status part of 'this pass occupies the lot': not cancelled, and inside… (+15 more)

### Community 61 - "payments/page.tsx"
Cohesion: 0.10
Nodes (25): ACTION_STYLE, AuditLogPage(), fmt(), styleFor(), bucketOf(), currency(), inPeriod(), METHOD_STYLE (+17 more)

### Community 66 - "test_dashboard.py"
Cohesion: 0.33
Nodes (9): dashboard_stats(), Session, _issue_active(), Dashboard occupancy: capacity, available spots, occupancy %., A cancelled pass keeps its expiration_date, so counting purely on…, test_available_never_negative(), test_cancelled_pass_does_not_occupy_a_spot(), test_capacity_available_and_occupancy() (+1 more)

### Community 69 - "_price_for"
Cohesion: 0.33
Nodes (9): _months_between(), _price_for(), Whole calendar months between two dates, rounding UP for any partial overage…, Pricing math: partial-month rounding and per-type price., test_daily_price_scales_with_days(), test_monthly_override_only_for_new_company(), test_monthly_uses_established_rate_times_months(), test_months_between_rounds_partial_up() (+1 more)

### Community 75 - "RateLimiter"
Cohesion: 0.28
Nodes (5): _client_key(), Request, RateLimiter, Allow `times` requests per `seconds` per client, else 429., Tests only — start from a clean window.

### Community 76 - "routers/spots.py"
Cohesion: 0.52
Nodes (5): The lot, painted by query. `expiring` = holder's last day is today or tomorrow…, MoveSpotRequest, MoveSpotResult, BaseModel, SpotState

### Community 77 - "test_spots_endpoint.py"
Cohesion: 0.43
Nodes (5): _auth(), _issue(), One call paints the whole lot. States derived, matching the holding rules., test_overstay_state_and_clear(), test_states_cover_the_lot()

### Community 78 - "Global Constraints"
Cohesion: 0.20
Nodes (9): Global Constraints, Self-review, Task 1: `spot_label` helper + config, Task 2: expose `spot_label` on every spot-bearing payload, Task 3: move-a-truck endpoint, Task 4: `SpotState` label + `spot_label` frontend types; zone grouping helper, Task 5: the `/availability` page — live board + move flow, Task 6: E2E in a real browser + docs (+1 more)

### Community 79 - "Architecture: labels + polling + one move endpoint (engine untouched)"
Cohesion: 0.22
Nodes (8): 1. Zone labels (derived — no migration, no data change), 2. The cashier availability page (`/availability`), 3. Cashier override — move a truck to a free spot, Architecture: labels + polling + one move endpoint (engine untouched), Decisions (settled with the owner, 2026-08-04), Testing, What does NOT change, Zone Availability + Cashier Override — Design

### Community 81 - "_log_unhandled"
Cohesion: 0.40
Nodes (5): _log_unhandled(), Exception, Request, exception_handler, JSONResponse

### Community 84 - "routers/insights.py"
Cohesion: 0.15
Nodes (22): conversion_leads(), _monthly_equivalent(), What this company effectively spends per month right now. The window is 90…, Daily/weekly customers who come often enough that a monthly plan would likely…, _tier(), CallItem, ConversionLead, ConversionLeads (+14 more)

### Community 118 - "spot_label"
Cohesion: 0.11
Nodes (21): _held_spot_ids(), holding_filter(), Boolean clause: this pass currently HOLDS its spot. Evaluated per-query against…, A spot the system may hand to the NEXT daily/weekly customer: active, not held…, Display label for a spot: 1 -> 'A1', 26 -> 'B1', 150 -> 'F25'. The integer…, _sellable_filter(), spot_label(), clear_overstay() (+13 more)

## Knowledge Gaps
- **194 isolated node(s):** `$schema`, `style`, `rsc`, `tsx`, `config` (+189 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `business_today()` connect `business_today` to `passes.py`, `PassType`, `test_morning_report.py`, `_get`, `_issue_pass_and_payment`, `reminders.py`, `test_renewal.py`, `companies.py`, `test_report_occupied.py`, `payments.py`, `ensure_spots`, `test_move_spot.py`, `routers/reports.py`, `seed_demo.py`, `test_reserved_spots.py`, `test_dashboard.py`, `routers/spots.py`, `test_spots_endpoint.py`, `routers/insights.py`, `spot_label`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `PassType` connect `PassType` to `passes.py`, `test_dashboard.py`, `seed_demo.py`, `test_morning_report.py`, `_price_for`, `test_report_occupied.py`, `test_pass_status.py`, `ensure_spots`, `test_move_spot.py`, `test_lot_check.py`, `test_spots_endpoint.py`, `business_today`, `routers/insights.py`, `test_renewal.py`, `companies.py`, `test_reserved_spots.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Why does `_get()` connect `_get` to `passes.py`, `PassType`, `test_dashboard.py`, `test_morning_report.py`, `routers/auth.py`, `MonthlyCustomer`, `payments.py`, `test_pass_status.py`, `test_lot_check.py`, `Session`, `routers/insights.py`, `routers/reports.py`, `spot_label`, `companies.py`, `test_report_occupied.py`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `PassType` (e.g. with `MoveError` and `ParkingPass`) actually correct?**
  _`PassType` has 29 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `style`, `rsc` to the rest of the system?**
  _194 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `passes.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12401693889897157 - nodes in this community are weakly interconnected._
- **Should `PassType` be split into smaller, more focused modules?**
  _Cohesion score 0.07192982456140351 - nodes in this community are weakly interconnected._