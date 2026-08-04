# Graph Report - madco-truck-plaza-parking  (2026-08-04)

## Corpus Check
- 189 files · ~69,551 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1390 nodes · 3540 edges · 95 communities (65 shown, 30 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 174 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `914da0d1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- reminders.py
- passes.py
- _issue_pass_and_payment
- lot_check
- register
- issue/page.tsx
- test_morning_report.py
- dashboard_stats
- payments/page.tsx
- cn
- create_payment_request
- User
- enums.py
- api.ts
- test_stranded_charges.py
- renew-dialog.tsx
- compilerOptions
- app/page.tsx
- monthly-customers/page.tsx
- components.json
- routers/auth.py
- devDependencies
- prod service: backend
- create_payment
- payment_requests.py
- test_security.py
- test_report_occupied.py
- dependencies
- Task 2: Holding predicate + free-spot picker
- Service: backend (self-migrating FastAPI)
- AI Search
- Monthly Reminder System
- conftest.py
- _get
- _price_for
- routers/reports.py
- test_monthly_status.py
- Tech Stack
- test_auth_api.py
- package.json
- app/layout.tsx
- RateLimiter
- ensure_spots
- Core Principle: The Software Remembers Everything
- test_move_spot.py
- Monochrome 16x16 Glyph Icon System (#666, evenodd fill)
- verify/[token]/page.tsx
- test_cron_endpoint.py
- stripe_payments.py
- core/spots.py
- Go-Live Checklist
- test_spots_endpoint.py
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
- LotCheckResult
- models/__init__.py
- search_everywhere
- Global Constraints
- Architecture: labels + polling + one move endpoint (engine untouched)
- conversion_leads
- get
- post
- routers/verify.py
- BaseModel
- Session
- SpotState
- date
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

## Communities (95 total, 30 thin omitted)

### Community 0 - "reminders.py"
Cohesion: 0.06
Nodes (54): ERROR-level logs become a phone notification, not a line in a file. A truck…, WebhookAlertHandler, configure_logging(), get_logger(), Console + rotating-file logging for the app. Called once at startup. File…, Child of the app logger, named for the calling module., reminder_scheduler_loop(), _run_sweep_once() (+46 more)

### Community 1 - "passes.py"
Cohesion: 0.08
Nodes (40): add_months(), date, ParkingPass, apply_renewal(), cancel_pass(), _expiration_for(), get_pass(), issue_pass() (+32 more)

### Community 2 - "_issue_pass_and_payment"
Cohesion: 0.08
Nodes (37): company_profile(), Everything about one company in one place: totals, trucks, recent passes and…, _find_company(), _find_or_create_vehicle(), _issue_pass_and_payment(), Reuse the company's existing vehicle instead of inserting a new row every time…, Shared by the normal Issue Pass endpoint and the Stripe finalize/webhook…, Match a company by name case-insensitively, ignoring surrounding whitespace —… (+29 more)

### Community 3 - "lot_check"
Cohesion: 0.23
Nodes (12): lot_check(), get, Session, _issue(), A renewed pass writes a second Payment row. Reporting the original one would…, Standing at the truck, the manager needs to know which spot it SHOULD be in —…, test_a_daily_walkup_is_not_a_monthly_customer(), test_a_renewal_reports_the_LATEST_payment_not_the_first() (+4 more)

### Community 4 - "register"
Cohesion: 0.14
Nodes (20): AuthStatus, create_access_token(), hash_password(), verify_password(), auth_status(), create_staff_user(), list_users(), login() (+12 more)

### Community 5 - "issue/page.tsx"
Cohesion: 0.08
Nodes (44): BookPage(), PASS_TYPES, PayWay, expiryPhrase(), LotCheckInner(), PAYMENT_LABEL, shortDate(), STATUS_STYLE (+36 more)

### Community 6 - "test_morning_report.py"
Cohesion: 0.17
Nodes (23): _money(), morning_report(), date, Session, The manager's 7am briefing: who to call today, and why. The dashboard already…, _revenue_on(), _daily(), _FakeUser (+15 more)

### Community 7 - "dashboard_stats"
Cohesion: 0.15
Nodes (12): Payment, What the payment was for — the vehicle on its pass., dashboard_stats(), Session, A payment taken at 10:30pm plaza time belongs to that day's revenue. The same…, test_tonights_takings_are_on_tonights_books(), _issue_active(), A cancelled pass keeps its expiration_date, so counting purely on… (+4 more)

### Community 8 - "payments/page.tsx"
Cohesion: 0.07
Nodes (36): ACTION_STYLE, AuditLogPage(), fmt(), styleFor(), currency(), GROUPS, MorningReportPage(), telHref() (+28 more)

### Community 9 - "cn"
Cohesion: 0.06
Nodes (52): StatCard(), MobileNav(), SidebarNav(), Badge(), badgeVariants, Card(), CardAction(), CardContent() (+44 more)

### Community 10 - "create_payment_request"
Cohesion: 0.22
Nodes (14): create_intent(), create_payment_request(), finalize(), get_payment_request(), _get_request(), CreateIntentResponse, post, Session (+6 more)

### Community 11 - "User"
Cohesion: 0.25
Nodes (11): Company, User, me(), create_company(), get_company(), list_companies(), lookup_company(), post (+3 more)

### Community 12 - "enums.py"
Cohesion: 0.17
Nodes (25): live_status(), date, PassStatus, PassType, PaymentMethod, CompanyBase, CompanyCreate, CompanyLookupResult (+17 more)

### Community 13 - "api.ts"
Cohesion: 0.11
Nodes (24): CommandPalette(), LEGEND, LotGrid(), STATE_CLASS, AppShell(), isPublicPath(), ThemeToggle(), api (+16 more)

### Community 14 - "test_stranded_charges.py"
Cohesion: 0.06
Nodes (73): cancel_intent(), _compute_price(), create_intent(), finalize(), _finalize_intent(), _finalize_payment_request(), issue_stranded_pass(), _metadata_from_payload() (+65 more)

### Community 15 - "renew-dialog.tsx"
Cohesion: 0.15
Nodes (22): currency(), PassesPage(), Field(), PAY_CHOICES, PayChoice, PAY_CHOICES, PayChoice, Button() (+14 more)

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

### Community 20 - "routers/auth.py"
Cohesion: 0.37
Nodes (12): EmployeeRole, AuthStatus, CreateStaffUserRequest, LoginRequest, BaseModel, Bootstrap-only — creates the very first user account. Rejected once any user…, Admin-only — adds an additional staff login after initial setup., Admin-only. There is no email infrastructure at a truck stop and none is… (+4 more)

### Community 21 - "devDependencies"
Cohesion: 0.10
Nodes (21): eslint, eslint-config-next, devDependencies, eslint, eslint-config-next, playwright, tailwindcss, @tailwindcss/postcss (+13 more)

### Community 22 - "prod service: backend"
Cohesion: 0.14
Nodes (20): CI job: Frontend · typecheck + test + build (Node 20), Non-blocking lint (react-hooks/set-state-in-effect), Nightly Off-Box Backups (14 kept, host bind mount), One-Command Docker Deployment, Service: cron (reminder sweep + nightly pg_dump), Service: frontend (Next.js), Service: nginx (only published port, /api routing), Service: postgres (named volume) (+12 more)

### Community 23 - "create_payment"
Cohesion: 0.29
Nodes (7): generate_receipt_number(), date, create_payment(), list_payments(), post, Session, Payment

### Community 24 - "payment_requests.py"
Cohesion: 0.09
Nodes (24): Alembic environment — wired to the app's own settings and metadata, so there is…, Settings, get_db(), Session, get_current_user(), Session, Admin or manager — the money tier. An attendant's job is the front desk: issue,…, require_admin() (+16 more)

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

### Community 32 - "conftest.py"
Cohesion: 0.12
Nodes (20): _backfill_pass_qr_codes(), `Base.metadata.create_all()` only creates missing *tables* — it never alters an…, Passes issued before the signed-QR system stored their plaintext receipt number…, run_startup_migrations(), _alembic_config(), Schema management at startup — Alembic is the single mechanism. Replaces the…, Bring the schema to head, whatever state the database is in. Three cases: *…, upgrade_database() (+12 more)

### Community 33 - "_get"
Cohesion: 0.44
Nodes (9): health(), _admin_token(), _get(), Role tiers, enforced at the API — not just hidden in the sidebar. Any login =…, _staff_token(), test_admin_sees_everything(), test_attendant_can_work_the_desk_but_not_read_the_money(), test_manager_reads_the_money_but_not_the_owners_domain() (+1 more)

### Community 34 - "_price_for"
Cohesion: 0.26
Nodes (11): _monthly_rate_for(), _months_between(), _price_for(), Whole calendar months between two dates, rounding UP for any partial overage…, The established PER-MONTH rate — never multiplied by month count. An existing…, Pricing math: partial-month rounding and per-type price., test_daily_price_scales_with_days(), test_monthly_override_only_for_new_company() (+3 more)

### Community 35 - "routers/reports.py"
Cohesion: 0.41
Nodes (10): Session, reports_summary(), CompanyStat, OutstandingBalance, PaymentMethodStat, BaseModel, ReportsSummary, RevenuePoint (+2 more)

### Community 36 - "test_monthly_status.py"
Cohesion: 0.24
Nodes (16): MonthlyCustomerStatus, create_monthly_customer(), list_monthly_customers(), MonthlyCustomer, post, Session, update_status(), MonthlyCustomerCreate (+8 more)

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

### Community 42 - "ensure_spots"
Cohesion: 0.13
Nodes (28): ensure_spots(), free_spot_count(), pick_free_spot(), Session, FCFS with a memory: longest-vacant first (NULLS FIRST — a never-used spot is…, Idempotent: rows exist for 1..capacity, and exactly those are active. Shrinking…, _issue(), Sticky: a lapsed monthly who comes back gets the number they always had. (+20 more)

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
Cohesion: 0.20
Nodes (18): VehicleType, finalize_request(), Turn a confirmed charge into the pass this request was for. Shared by TWO…, CreatePaymentRequest, PaymentRequestCreated, PaymentRequestIssueDetails, PaymentRequestRenewDetails, PaymentRequestStatus (+10 more)

### Community 50 - "core/spots.py"
Cohesion: 0.08
Nodes (37): _held_spot_ids(), holding_filter(), _live_window_filter(), move_pass_to_spot(), MoveError, Spot inventory. State is DERIVED: a spot is free iff no live pass holds it.…, A spot the system may hand to the NEXT customer: active, not held by a live…, A move the cashier asked for that can't be honored. `status` is the HTTP code… (+29 more)

### Community 51 - "Go-Live Checklist"
Cohesion: 0.50
Nodes (4): ALERT_WEBHOOK_URL Error Alerting (1/min rate limit), Go-Live Checklist, purge_demo Script (Wipe Demo Data, Keep Logins), Twilio A2P Activation (No Code Change)

### Community 52 - "test_spots_endpoint.py"
Cohesion: 0.43
Nodes (5): _auth(), _issue(), One call paints the whole lot. States derived, matching the holding rules., test_overstay_state_and_clear(), test_states_cover_the_lot()

### Community 61 - "business_today"
Cohesion: 0.15
Nodes (15): business_today(), date, The plaza's current calendar day. Use this everywhere `date.today()` was used,…, Kiritimati (UTC+14) and Niue (UTC-11) are 25 hours apart, so their calendar…, test_the_day_comes_from_the_plazas_timezone_not_the_hosts(), _fill_the_lot(), A pay-link for a NEW pass needs a spot; a renewal already holds one and must…, test_kiosk_refuses_when_full() (+7 more)

### Community 76 - "models/__init__.py"
Cohesion: 0.12
Nodes (27): log_audit(), Session, business_now(), plaza_tz(), datetime, What day is it *at the plaza*. Two separate bugs live here if you get this…, Wall-clock time at the plaza, naive — stored as-is so `date(paid_at)` in SQL is…, Base (+19 more)

### Community 77 - "search_everywhere"
Cohesion: 0.67
Nodes (3): Session, search_everywhere(), SearchResultItem

### Community 78 - "Global Constraints"
Cohesion: 0.20
Nodes (9): Global Constraints, Self-review, Task 1: `spot_label` helper + config, Task 2: expose `spot_label` on every spot-bearing payload, Task 3: move-a-truck endpoint, Task 4: `SpotState` label + `spot_label` frontend types; zone grouping helper, Task 5: the `/availability` page — live board + move flow, Task 6: E2E in a real browser + docs (+1 more)

### Community 79 - "Architecture: labels + polling + one move endpoint (engine untouched)"
Cohesion: 0.22
Nodes (8): 1. Zone labels (derived — no migration, no data change), 2. The cashier availability page (`/availability`), 3. Cashier override — move a truck to a free spot, Architecture: labels + polling + one move endpoint (engine untouched), Decisions (settled with the owner, 2026-08-04), Testing, What does NOT change, Zone Availability + Cashier Override — Design

### Community 80 - "conversion_leads"
Cohesion: 0.12
Nodes (20): conversion_leads(), _monthly_equivalent(), What this company effectively spends per month right now. The window is 90…, Daily/weekly customers who come often enough that a monthly plan would likely…, _tier(), CallItem, ConversionLead, ConversionLeads (+12 more)

### Community 83 - "routers/verify.py"
Cohesion: 0.31
Nodes (9): get, post, Session, The asphalt gap: no sensors, so an expired truck can still sit in a spot the…, report_occupied(), verify_pass(), PassVerifyResult, BaseModel (+1 more)

## Knowledge Gaps
- **155 isolated node(s):** `Task 1: `spot_label` helper + config`, `Task 2: expose `spot_label` on every spot-bearing payload`, `Task 3: move-a-truck endpoint`, `Task 4: `SpotState` label + `spot_label` frontend types; zone grouping helper`, `Task 5: the `/availability` page — live board + move flow` (+150 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_issue_pass_and_payment()` connect `_issue_pass_and_payment` to `passes.py`, `_price_for`, `lot_check`, `test_morning_report.py`, `dashboard_stats`, `ensure_spots`, `models/__init__.py`, `enums.py`, `test_stranded_charges.py`, `conversion_leads`, `stripe_payments.py`, `test_spots_endpoint.py`, `payment_requests.py`, `test_report_occupied.py`, `business_today`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `_get()` connect `_get` to `reminders.py`, `_issue_pass_and_payment`, `routers/reports.py`, `register`, `test_monthly_status.py`, `test_morning_report.py`, `dashboard_stats`, `create_payment_request`, `User`, `search_everywhere`, `test_stranded_charges.py`, `conversion_leads`, `stripe_payments.py`, `create_payment`, `payment_requests.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Why does `business_today()` connect `business_today` to `reminders.py`, `passes.py`, `_issue_pass_and_payment`, `routers/reports.py`, `test_morning_report.py`, `dashboard_stats`, `ensure_spots`, `models/__init__.py`, `enums.py`, `conversion_leads`, `test_spots_endpoint.py`, `create_payment`, `payment_requests.py`, `test_report_occupied.py`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `PassType` (e.g. with `CompanyBase` and `CompanyCreate`) actually correct?**
  _`PassType` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Task 1: `spot_label` helper + config`, `Task 2: expose `spot_label` on every spot-bearing payload`, `Task 3: move-a-truck endpoint` to the rest of the system?**
  _155 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `reminders.py` be split into smaller, more focused modules?**
  _Cohesion score 0.060515873015873016 - nodes in this community are weakly interconnected._
- **Should `passes.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0792156862745098 - nodes in this community are weakly interconnected._