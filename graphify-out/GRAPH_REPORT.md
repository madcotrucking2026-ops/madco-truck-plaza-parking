# Graph Report - madco-truck-plaza-parking  (2026-08-04)

## Corpus Check
- 188 files · ~68,941 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1368 nodes · 3485 edges · 97 communities (69 shown, 28 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 175 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `32a52ac5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- reminders.py
- passes.py
- test_spot_assignment.py
- test_lot_check.py
- routers/auth.py
- issue/page.tsx
- test_morning_report.py
- test_spot_label.py
- api.ts
- cn
- create_payment_request
- User
- PassType
- api
- test_stranded_charges.py
- renew-dialog.tsx
- compilerOptions
- app/page.tsx
- monthly-customers/page.tsx
- components.json
- issue_stranded_pass
- devDependencies
- prod service: backend
- payments.py
- main.py
- test_security.py
- test_report_occupied.py
- dependencies
- Task 2: Holding predicate + free-spot picker
- Service: backend (self-migrating FastAPI)
- AI Search
- Monthly Reminder System
- seed_demo.py
- test_webhook_payment_request.py
- _issue_pass_and_payment
- routers/reports.py
- MonthlyCustomer
- Tech Stack
- test_auth_api.py
- package.json
- app/layout.tsx
- RateLimiter
- ensure_spots
- Core Principle: The Software Remembers Everything
- revenue-chart.tsx
- Monochrome 16x16 Glyph Icon System (#666, evenodd fill)
- test_reminders_sweep.py
- test_cron_endpoint.py
- stripe_payments.py
- routers/spots.py
- Go-Live Checklist
- ParkingPass
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
- payments/page.tsx
- Global Constraints
- Architecture: labels + polling + one move endpoint (engine untouched)
- test_insights.py
- WebhookAlertHandler
- _log_unhandled
- routers/verify.py
- routers/insights.py
- _compute_price
- _FakeMeta
- SpotState
- date
- Session
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
3. `business_today()` - 52 edges
4. `PassType` - 51 edges
5. `ensure_spots()` - 46 edges
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

## Communities (97 total, 28 thin omitted)

### Community 0 - "reminders.py"
Cohesion: 0.10
Nodes (32): is_configured(), Twilio requires E.164 (+15551234567). Customer phones are stored loosely…, Send an SMS via Twilio. Returns True if it went out, False if SMS isn't…, send_sms(), to_e164(), _already_reminded_today(), cron_trigger(), _do_send() (+24 more)

### Community 1 - "passes.py"
Cohesion: 0.17
Nodes (18): cancel_pass(), get_pass(), issue_pass(), list_passes(), get, post, Session, Removes a truck from a monthly plan (or cancels any pass) without deleting its… (+10 more)

### Community 2 - "test_spot_assignment.py"
Cohesion: 0.31
Nodes (9): _issue(), Assignment is part of issuing a pass — same transaction, no separate step., Sticky: a lapsed monthly who comes back gets the number they always had., Money already taken must NEVER fail for lack of a spot — pass issues with…, test_full_lot_issues_pass_with_no_spot(), test_issue_assigns_a_spot(), test_renewal_keeps_the_spot(), test_returning_monthly_gets_their_old_spot() (+1 more)

### Community 3 - "test_lot_check.py"
Cohesion: 0.12
Nodes (27): add_months(), date, lot_check(), get, Session, apply_renewal(), Validates a proposed renewal and returns (renewal_start, price) WITHOUT…, Applies a validated renewal: extends the pass, records a Payment, and updates… (+19 more)

### Community 4 - "routers/auth.py"
Cohesion: 0.09
Nodes (44): AuthStatus, create_access_token(), hash_password(), verify_password(), health(), EmployeeRole, auth_status(), create_staff_user() (+36 more)

### Community 5 - "issue/page.tsx"
Cohesion: 0.09
Nodes (41): BookPage(), PASS_TYPES, PayWay, expiryPhrase(), LotCheckInner(), PAYMENT_LABEL, shortDate(), STATUS_STYLE (+33 more)

### Community 6 - "test_morning_report.py"
Cohesion: 0.23
Nodes (19): morning_report(), The manager's 7am briefing: who to call today, and why. The dashboard already…, _daily(), _FakeUser, _monthly(), The 7am briefing: who to call today, in the order money is at risk. The ORDER…, Caught on real data: the report said "8 visits, spending $53/mo — offer the…, The customer who already outspends the plan closes himself — call him first. (+11 more)

### Community 7 - "test_spot_label.py"
Cohesion: 0.43
Nodes (6): Display label for a spot: 1 -> 'A1', 26 -> 'B1', 150 -> 'F25'. The integer…, spot_label(), spot_label: the integer number stays the key; this is only how it reads., test_disabled_zoning_is_bare_number(), test_overflow_past_Z_degrades_to_number(), test_zone_labels_at_boundaries()

### Community 8 - "api.ts"
Cohesion: 0.07
Nodes (38): ACTION_STYLE, AuditLogPage(), fmt(), styleFor(), currency(), GROUPS, MorningReportPage(), telHref() (+30 more)

### Community 9 - "cn"
Cohesion: 0.09
Nodes (37): Badge(), badgeVariants, Card(), CardAction(), CardContent(), CardDescription(), CardFooter(), CardHeader() (+29 more)

### Community 10 - "create_payment_request"
Cohesion: 0.19
Nodes (16): create_intent(), create_payment_request(), finalize(), finalize_request(), get_payment_request(), _get_request(), CreateIntentResponse, post (+8 more)

### Community 11 - "User"
Cohesion: 0.17
Nodes (16): get_current_user(), Session, Admin or manager — the money tier. An attendant's job is the front desk: issue,…, require_admin(), require_manager(), decode_access_token(), Company, User (+8 more)

### Community 12 - "PassType"
Cohesion: 0.07
Nodes (60): live_status(), date, PassStatus, PassType, PaymentMethod, company_profile(), lookup_company(), Everything about one company in one place: totals, trucks, recent passes and… (+52 more)

### Community 13 - "api"
Cohesion: 0.09
Nodes (32): CommandPalette(), Field(), AppShell(), isPublicPath(), MobileNav(), SidebarNav(), ThemeToggle(), Button() (+24 more)

### Community 14 - "test_stranded_charges.py"
Cohesion: 0.22
Nodes (24): Cards Stripe accepted that produced no pass here — money taken, nothing given.…, stranded_charges(), _configured(), _FakeCharge, _FakeUser, _intent(), _listing(), The stranded-charge detector: cards Stripe accepted that produced no pass. This… (+16 more)

### Community 15 - "renew-dialog.tsx"
Cohesion: 0.15
Nodes (19): currency(), PassesPage(), PAY_CHOICES, PayChoice, PassTicket(), PAY_CHOICES, PayChoice, Dialog() (+11 more)

### Community 16 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 17 - "app/page.tsx"
Cohesion: 0.09
Nodes (21): CompanyProfilePage(), fmtDate(), fmtDateTime(), money(), money2(), currency(), DashboardPage(), LEAD_TIER (+13 more)

### Community 18 - "monthly-customers/page.tsx"
Cohesion: 0.13
Nodes (18): currency(), MonthlyCustomer, MonthlyCustomersPage(), STATUS_LABEL, ComingSoon(), AddStaffCard(), Role, ROLES (+10 more)

### Community 19 - "components.json"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 20 - "issue_stranded_pass"
Cohesion: 0.13
Nodes (20): is_configured(), cancel_intent(), create_intent(), finalize(), issue_stranded_pass(), _metadata_from_payload(), _ours(), CreateIntentResponse (+12 more)

### Community 21 - "devDependencies"
Cohesion: 0.10
Nodes (21): eslint, eslint-config-next, devDependencies, eslint, eslint-config-next, playwright, tailwindcss, @tailwindcss/postcss (+13 more)

### Community 22 - "prod service: backend"
Cohesion: 0.14
Nodes (20): CI job: Frontend · typecheck + test + build (Node 20), Non-blocking lint (react-hooks/set-state-in-effect), Nightly Off-Box Backups (14 kept, host bind mount), One-Command Docker Deployment, Service: cron (reminder sweep + nightly pg_dump), Service: frontend (Next.js), Service: nginx (only published port, /api routing), Service: postgres (named volume) (+12 more)

### Community 23 - "payments.py"
Cohesion: 0.17
Nodes (15): log_audit(), Session, generate_receipt_number(), date, AuditLog, AuditAction, list_audit_log(), Session (+7 more)

### Community 24 - "main.py"
Cohesion: 0.11
Nodes (19): _backfill_pass_qr_codes(), `Base.metadata.create_all()` only creates missing *tables* — it never alters an…, Passes issued before the signed-QR system stored their plaintext receipt number…, run_startup_migrations(), get_logger(), Child of the app logger, named for the calling module., _alembic_config(), Schema management at startup — Alembic is the single mechanism. Replaces the… (+11 more)

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
Cohesion: 0.14
Nodes (18): get_db(), Session, _issue(), main(), _phone(), Seed realistic demo data into the dev database so every screen populates. Run…, seed(), client() (+10 more)

### Community 33 - "test_webhook_payment_request.py"
Cohesion: 0.26
Nodes (14): _finalize_payment_request(), Webhook safety net for pay-link payments. Imported lazily to keep the router…, _FakeIntent, _pending_request(), The webhook safety net for manager-created pay links. The bug this guards: the…, Customer pays, phone dies. Stripe's webhook must still produce the pass., Both paths race on a good connection. Second one must return the same pass, not…, If Stripe charged something other than the quote, no retry will ever fix it.… (+6 more)

### Community 34 - "_issue_pass_and_payment"
Cohesion: 0.14
Nodes (22): _expiration_for(), _find_or_create_vehicle(), _issue_pass_and_payment(), _monthly_rate_for(), _months_between(), _price_for(), Reuse the company's existing vehicle instead of inserting a new row every time…, Shared by the normal Issue Pass endpoint and the Stripe finalize/webhook… (+14 more)

### Community 35 - "routers/reports.py"
Cohesion: 0.41
Nodes (10): Session, reports_summary(), CompanyStat, OutstandingBalance, PaymentMethodStat, BaseModel, ReportsSummary, RevenuePoint (+2 more)

### Community 36 - "MonthlyCustomer"
Cohesion: 0.22
Nodes (18): MonthlyCustomerStatus, ReminderStatus, MonthlyCustomer, create_monthly_customer(), list_monthly_customers(), MonthlyCustomer, post, Session (+10 more)

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
Cohesion: 0.11
Nodes (35): ensure_spots(), free_spot_count(), _held_spot_ids(), holding_filter(), _live_window_filter(), pick_free_spot(), Spot inventory. State is DERIVED: a spot is free iff no live pass holds it.…, A spot the system may hand to the NEXT customer: active, not held by a live… (+27 more)

### Community 43 - "Core Principle: The Software Remembers Everything"
Cohesion: 0.22
Nodes (9): Engineering Identity Mandate, AI Development Rules (Plan, Build, Verify, Optimize), Coding Standards, Core Principle: The Software Remembers Everything, Feature Justification Rule, Reusable Claude Skill Folder, Madco Truck Plaza Parking Management System, Manual Processes Replaced (+1 more)

### Community 44 - "revenue-chart.tsx"
Cohesion: 0.83
Nodes (3): currency(), formatDate(), RevenueChart()

### Community 46 - "Monochrome 16x16 Glyph Icon System (#666, evenodd fill)"
Cohesion: 0.48
Nodes (7): Document/File Glyph Icon (16x16, #666), Monochrome 16x16 Glyph Icon System (#666, evenodd fill), Globe / Web Glyph Icon (16x16, #666), create-next-app Default Scaffold Assets, Next.js Wordmark Logo (394x80, black), Vercel Triangle Logo (white, 1155x1000), Browser Window Glyph Icon (16x16, #666)

### Community 47 - "test_reminders_sweep.py"
Cohesion: 0.35
Nodes (12): The daily sweep: for every monthly customer, text a renewal reminder if one is…, run_scheduled_reminders(), auto_on(), _mc(), fixture, The daily renewal-reminder sweep: who gets a text and who's skipped. SMS isn't…, _reminder_count(), test_renewed_customer_is_not_due() (+4 more)

### Community 49 - "stripe_payments.py"
Cohesion: 0.31
Nodes (11): VehicleType, Was this charge given back? A refunded card is not stranded money — the…, _refunded(), CancelIntentRequest, CreateIntentRequest, CreateIntentResponse, FinalizeStripePaymentRequest, BaseModel (+3 more)

### Community 50 - "routers/spots.py"
Cohesion: 0.21
Nodes (9): clear_overstay(), lot_state(), get, post, Session, The lot, painted by query. `expiring` = holder's last day is today or tomorrow…, Staff dealt with the squatter — put the spot back to normal., BaseModel (+1 more)

### Community 51 - "Go-Live Checklist"
Cohesion: 0.50
Nodes (4): ALERT_WEBHOOK_URL Error Alerting (1/min rate limit), Go-Live Checklist, purge_demo Script (Wipe Demo Data, Keep Logins), Twilio A2P Activation (No Code Change)

### Community 52 - "ParkingPass"
Cohesion: 0.27
Nodes (10): ParkingPass, _finalize_intent(), Shared by the client-driven /finalize call (fast path, for immediate UI…, _md(), Stripe finalize core (_finalize_intent) — the path that turns a confirmed…, test_finalize_is_idempotent(), test_finalize_issues_pass_from_metadata(), test_finalize_rejects_intent_without_pass_metadata() (+2 more)

### Community 61 - "business_today"
Cohesion: 0.10
Nodes (29): business_now(), business_today(), plaza_tz(), date, datetime, What day is it *at the plaza*. Two separate bugs live here if you get this…, Wall-clock time at the plaza, naive — stored as-is so `date(paid_at)` in SQL is…, The plaza's current calendar day. Use this everywhere `date.today()` was used,… (+21 more)

### Community 76 - "models/__init__.py"
Cohesion: 0.11
Nodes (17): Alembic environment — wired to the app's own settings and metadata, so there is…, Base, Payment, What the payment was for — the vehicle on its pass., PaymentRequest, A pending card payment a manager hands off to the customer to self-pay. Created…, Reminder, A singleton row (always id=1) inserted atomically alongside the very first… (+9 more)

### Community 77 - "payments/page.tsx"
Cohesion: 0.24
Nodes (10): bucketOf(), currency(), inPeriod(), METHOD_STYLE, MethodBadge(), Payment, PaymentsPage(), Period (+2 more)

### Community 78 - "Global Constraints"
Cohesion: 0.20
Nodes (9): Global Constraints, Self-review, Task 1: `spot_label` helper + config, Task 2: expose `spot_label` on every spot-bearing payload, Task 3: move-a-truck endpoint, Task 4: `SpotState` label + `spot_label` frontend types; zone grouping helper, Task 5: the `/availability` page — live board + move flow, Task 6: E2E in a real browser + docs (+1 more)

### Community 79 - "Architecture: labels + polling + one move endpoint (engine untouched)"
Cohesion: 0.22
Nodes (8): 1. Zone labels (derived — no migration, no data change), 2. The cashier availability page (`/availability`), 3. Cashier override — move a truck to a free spot, Architecture: labels + polling + one move endpoint (engine untouched), Decisions (settled with the owner, 2026-08-04), Testing, What does NOT change, Zone Availability + Cashier Override — Design

### Community 80 - "test_insights.py"
Cohesion: 0.15
Nodes (19): conversion_leads(), _monthly_equivalent(), date, Session, What this company effectively spends per month right now. The window is 90…, Daily/weekly customers who come often enough that a monthly plan would likely…, _revenue_on(), _tier() (+11 more)

### Community 81 - "WebhookAlertHandler"
Cohesion: 0.22
Nodes (5): ERROR-level logs become a phone notification, not a line in a file. A truck…, WebhookAlertHandler, configure_logging(), Console + rotating-file logging for the app. Called once at startup. File…, LogRecord

### Community 82 - "_log_unhandled"
Cohesion: 0.40
Nodes (5): _log_unhandled(), Request, Exception, exception_handler, JSONResponse

### Community 83 - "routers/verify.py"
Cohesion: 0.31
Nodes (9): get, post, Session, The asphalt gap: no sensors, so an expired truck can still sit in a spot the…, report_occupied(), verify_pass(), PassVerifyResult, BaseModel (+1 more)

### Community 84 - "routers/insights.py"
Cohesion: 0.42
Nodes (7): _money(), CallItem, ConversionLead, ConversionLeads, MorningReport, BaseModel, One line of the morning report: a person to call, and the reason to call them.…

### Community 85 - "_compute_price"
Cohesion: 0.33
Nodes (6): _lookup_monthly_rate(), The company's established per-month rate, or None if it has no monthly plan on…, _compute_price(), date, PassType, The single source of truth both create-intent and (as a sanity check only, not…

## Knowledge Gaps
- **155 isolated node(s):** `Task 1: `spot_label` helper + config`, `Task 2: expose `spot_label` on every spot-bearing payload`, `Task 3: move-a-truck endpoint`, `Task 4: `SpotState` label + `spot_label` frontend types; zone grouping helper`, `Task 5: the `/availability` page — live board + move flow` (+150 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_issue_pass_and_payment()` connect `_issue_pass_and_payment` to `seed_demo.py`, `passes.py`, `test_spot_assignment.py`, `test_lot_check.py`, `test_morning_report.py`, `create_payment_request`, `ensure_spots`, `PassType`, `models/__init__.py`, `test_insights.py`, `stripe_payments.py`, `ParkingPass`, `test_report_occupied.py`, `business_today`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Why does `_get()` connect `routers/auth.py` to `reminders.py`, `routers/reports.py`, `MonthlyCustomer`, `test_morning_report.py`, `create_payment_request`, `User`, `PassType`, `test_stranded_charges.py`, `test_insights.py`, `ParkingPass`, `issue_stranded_pass`, `payments.py`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Why does `business_today()` connect `business_today` to `reminders.py`, `seed_demo.py`, `test_spot_assignment.py`, `routers/reports.py`, `test_morning_report.py`, `ensure_spots`, `User`, `PassType`, `models/__init__.py`, `test_reminders_sweep.py`, `test_insights.py`, `routers/insights.py`, `payments.py`, `test_report_occupied.py`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `PassType` (e.g. with `CompanyBase` and `CompanyCreate`) actually correct?**
  _`PassType` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Task 1: `spot_label` helper + config`, `Task 2: expose `spot_label` on every spot-bearing payload`, `Task 3: move-a-truck endpoint` to the rest of the system?**
  _155 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `reminders.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10252100840336134 - nodes in this community are weakly interconnected._
- **Should `test_lot_check.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11954022988505747 - nodes in this community are weakly interconnected._