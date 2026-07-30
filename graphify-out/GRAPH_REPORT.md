# Graph Report - .  (2026-07-30)

## Corpus Check
- 194 files · ~66,200 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1325 nodes · 3589 edges · 75 communities (57 shown, 18 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 201 edges (avg confidence: 0.65)
- Token cost: 75,450 input · 0 output

## Community Hubs (Navigation)
- SMS & Monthly Customer Records
- Stripe Webhook & Stranded Charges
- Plaza Clock & Spot Inventory Core
- Pass Issue, Pricing & Renewal
- Auth, RBAC & Request Dependencies
- Kiosk Booking & Lot Check Pages
- Insights, Morning Report & Leads
- Logging, Alerts & Startup Migrations
- Audit, Companies & Report Pages
- Shadcn UI Primitives
- Payment Requests & Company Lookup
- Alembic Env, Clock & ORM Models
- Enums, Company Schemas & Routes
- App Shell, Nav & API Client
- Stripe Client & Payment Intents
- Passes Page, Ticket & Renew Dialogs
- TypeScript Config
- Dashboard & Company Profile Pages
- Monthly Customers & Settings Pages
- Shadcn Component Registry
- Lot Grid, Theme Toggle & Buttons
- Frontend Dev Dependencies
- Docker Services, Nginx & Backups
- Audit Log & Receipt Numbers
- Config, JWT Secret & Dashboard Tests
- Security & Rate-Limit Tests
- Pass Status, QR Tokens & Rate Limit
- Frontend Runtime Dependencies
- Spot Inventory Spec & Task Plan
- Backend Deploy, Timezone & Typography
- Product Spec: Passes, Spots & Search
- Product Spec: Pricing & Reminders
- Test Fixtures & DB Session
- Payment Model & Dashboard Stats
- Price Calculation & Pricing Tests
- Reports Summary & Schemas
- Design System & Lot UI Tasks
- Tech Stack & Framework Choices
- Auth API Tests
- Frontend Package Scripts
- Root Layout, Fonts & Theme Provider
- In-Memory Rate Limiter
- Company Profile Aggregation
- Project Charter & Coding Standards
- Public Pass Verify Page
- Lot State Endpoint Tests
- Next.js Scaffold Assets
- Demo Data Seeding
- Cron Reminder Endpoint Tests
- Payment Idempotency Tests
- Global Search
- Go-Live Checklist & Alerting
- Revenue Chart
- Next Config & CSP
- Kiosk Booking Layout
- Login Layout
- Pay Link Layout
- Verify Page Layout
- Load Swarm Test Script
- Timezone Boundary Test
- ESLint Config
- Lucide Icons
- Next.js Package
- React DOM Package
- Sonner Toasts
- Stripe React SDK
- Tailwind Merge
- Tailwind Animate CSS
- PostCSS Config

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

## Communities (75 total, 18 thin omitted)

### Community 0 - "SMS & Monthly Customer Records"
Cohesion: 0.06
Nodes (62): is_configured(), Twilio requires E.164 (+15551234567). Customer phones are stored loosely…, Send an SMS via Twilio. Returns True if it went out, False if SMS isn't…, send_sms(), to_e164(), MonthlyCustomerStatus, ReminderStatus, MonthlyCustomer (+54 more)

### Community 1 - "Stripe Webhook & Stranded Charges"
Cohesion: 0.07
Nodes (58): _finalize_intent(), _finalize_payment_request(), issue_stranded_pass(), _ours(), Request, Session, Safety net for the case where a customer's card is charged but their…, Webhook safety net for pay-link payments. Imported lazily to keep the router… (+50 more)

### Community 2 - "Plaza Clock & Spot Inventory Core"
Cohesion: 0.08
Nodes (51): business_today(), date, The plaza's current calendar day. Use this everywhere `date.today()` was used,…, ensure_spots(), free_spot_count(), _held_spot_ids(), _live_window_filter(), pick_free_spot() (+43 more)

### Community 3 - "Pass Issue, Pricing & Renewal"
Cohesion: 0.08
Nodes (49): add_months(), date, ParkingPass, apply_renewal(), cancel_pass(), _expiration_for(), _find_company(), _find_or_create_vehicle() (+41 more)

### Community 4 - "Auth, RBAC & Request Dependencies"
Cohesion: 0.09
Nodes (47): AuthStatus, get_current_user(), Session, Admin or manager — the money tier. An attendant's job is the front desk: issue,…, require_admin(), require_manager(), create_access_token(), decode_access_token() (+39 more)

### Community 5 - "Kiosk Booking & Lot Check Pages"
Cohesion: 0.10
Nodes (39): BookPage(), PASS_TYPES, PayWay, expiryPhrase(), LotCheckInner(), PAYMENT_LABEL, shortDate(), STATUS_STYLE (+31 more)

### Community 6 - "Insights, Morning Report & Leads"
Cohesion: 0.09
Nodes (45): conversion_leads(), _money(), _monthly_equivalent(), morning_report(), date, Session, The manager's 7am briefing: who to call today, and why. The dashboard already…, What this company effectively spends per month right now. The window is 90… (+37 more)

### Community 7 - "Logging, Alerts & Startup Migrations"
Cohesion: 0.06
Nodes (37): ERROR-level logs become a phone notification, not a line in a file. A truck…, WebhookAlertHandler, _backfill_pass_qr_codes(), `Base.metadata.create_all()` only creates missing *tables* — it never alters an…, Passes issued before the signed-QR system stored their plaintext receipt number…, run_startup_migrations(), configure_logging(), get_logger() (+29 more)

### Community 8 - "Audit, Companies & Report Pages"
Cohesion: 0.07
Nodes (35): ACTION_STYLE, AuditLogPage(), fmt(), styleFor(), currency(), GROUPS, MorningReportPage(), telHref() (+27 more)

### Community 9 - "Shadcn UI Primitives"
Cohesion: 0.10
Nodes (36): Badge(), badgeVariants, Card(), CardAction(), CardContent(), CardDescription(), CardFooter(), CardHeader() (+28 more)

### Community 10 - "Payment Requests & Company Lookup"
Cohesion: 0.08
Nodes (44): PaymentRequest, A pending card payment a manager hands off to the customer to self-pay. Created…, lookup_company(), Used by Issue Pass (monthly) to auto-fill an existing company's negotiated…, lot_check(), Session, create_intent(), create_payment_request() (+36 more)

### Community 11 - "Alembic Env, Clock & ORM Models"
Cohesion: 0.15
Nodes (18): Alembic environment — wired to the app's own settings and metadata, so there is…, business_now(), plaza_tz(), datetime, What day is it *at the plaza*. Two separate bugs live here if you get this…, Wall-clock time at the plaza, naive — stored as-is so `date(paid_at)` in SQL is…, Base, Reminder (+10 more)

### Community 12 - "Enums, Company Schemas & Routes"
Cohesion: 0.19
Nodes (29): PassStatus, PassType, PaymentMethod, CompanyBase, CompanyCreate, CompanyLookupResult, CompanyMonthlyTruck, CompanyProfile (+21 more)

### Community 13 - "App Shell, Nav & API Client"
Cohesion: 0.10
Nodes (29): CommandPalette(), AppShell(), isPublicPath(), MobileNav(), SidebarNav(), api, AuthStatus, ConversionLead (+21 more)

### Community 14 - "Stripe Client & Payment Intents"
Cohesion: 0.13
Nodes (29): is_configured(), VehicleType, _require_configured(), cancel_intent(), create_intent(), finalize(), _metadata_from_payload(), CreateIntentResponse (+21 more)

### Community 15 - "Passes Page, Ticket & Renew Dialogs"
Cohesion: 0.14
Nodes (21): currency(), PassesPage(), Field(), PAY_CHOICES, PayChoice, vehicleOf(), PassTicket(), PAY_CHOICES (+13 more)

### Community 16 - "TypeScript Config"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 17 - "Dashboard & Company Profile Pages"
Cohesion: 0.11
Nodes (17): CompanyProfilePage(), fmtDate(), fmtDateTime(), money(), money2(), currency(), DashboardPage(), LEAD_TIER (+9 more)

### Community 18 - "Monthly Customers & Settings Pages"
Cohesion: 0.13
Nodes (18): currency(), MonthlyCustomer, MonthlyCustomersPage(), STATUS_LABEL, ComingSoon(), AddStaffCard(), Role, ROLES (+10 more)

### Community 19 - "Shadcn Component Registry"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 20 - "Lot Grid, Theme Toggle & Buttons"
Cohesion: 0.14
Nodes (15): LEGEND, LotGrid(), STATE_CLASS, ThemeToggle(), Button(), buttonVariants, Sheet(), SheetContent() (+7 more)

### Community 21 - "Frontend Dev Dependencies"
Cohesion: 0.10
Nodes (21): eslint, eslint-config-next, devDependencies, eslint, eslint-config-next, playwright, tailwindcss, @tailwindcss/postcss (+13 more)

### Community 22 - "Docker Services, Nginx & Backups"
Cohesion: 0.14
Nodes (20): CI job: Frontend · typecheck + test + build (Node 20), Non-blocking lint (react-hooks/set-state-in-effect), Nightly Off-Box Backups (14 kept, host bind mount), One-Command Docker Deployment, Service: cron (reminder sweep + nightly pg_dump), Service: frontend (Next.js), Service: nginx (only published port, /api routing), Service: postgres (named volume) (+12 more)

### Community 23 - "Audit Log & Receipt Numbers"
Cohesion: 0.17
Nodes (15): log_audit(), Session, generate_receipt_number(), date, AuditLog, AuditAction, list_audit_log(), Session (+7 more)

### Community 24 - "Config, JWT Secret & Dashboard Tests"
Cohesion: 0.15
Nodes (15): Settings, load_or_create_jwt_secret(), make_pass_token(), _issue_active(), Dashboard occupancy: capacity, available spots, occupancy %., A cancelled pass keeps its expiration_date, so counting purely on…, test_available_never_negative(), test_cancelled_pass_does_not_occupy_a_spot() (+7 more)

### Community 25 - "Security & Rate-Limit Tests"
Cohesion: 0.13
Nodes (16): _intent_body(), Rate limiting and input validation on the unauthenticated surface. Each test…, A crafted end_date decades out turns into an absurd computed price., A negative price would record a NEGATIVE payment against the drawer., Blocks two things the per-account lockout does NOT: a spray across many…, Public and unauthenticated: it answers "does this company exist, what is its…, An unbounded password field means megabytes fed straight into bcrypt on an…, Unbounded here would flow into Stripe metadata and the database. (+8 more)

### Community 26 - "Pass Status, QR Tokens & Rate Limit"
Cohesion: 0.16
Nodes (14): live_status(), date, Returns the pass id if the token's signature is valid, else None., _sign(), verify_pass_token(), Per-client sliding-window rate limiting, as a FastAPI dependency. Deliberately…, post, Session (+6 more)

### Community 27 - "Frontend Runtime Dependencies"
Cohesion: 0.11
Nodes (19): @base-ui/react, class-variance-authority, clsx, cmdk, dependencies, @base-ui/react, class-variance-authority, clsx (+11 more)

### Community 28 - "Spot Inventory Spec & Task Plan"
Cohesion: 0.16
Nodes (19): Spot Inventory Is Config (PARKING_CAPACITY / SPOT_GRACE_DAYS), Stripe Webhook + Payment-Method Domain Setup, PARKING_CAPACITY env (default 150), Task 10: E2E proof + DEPLOY.md docs + memory, Task 1: Spot model, migration, idempotent seeding, Task 2: Holding predicate + free-spot picker, Task 3: Assign at issue time (sticky monthly, full lot never blocks), Task 4: Kiosk pre-check — refuse checkout when full (+11 more)

### Community 29 - "Backend Deploy, Timezone & Typography"
Cohesion: 0.15
Nodes (15): CI job: Backend · pytest (Python 3.11), bcrypt<4.1 pin (passlib 1.7.4 self-test breakage), Backend dev/test dependency set (pytest, httpx), Backend runtime dependency set, Inter (headings and body), JetBrains Mono (numbers), Typography System, Schema = Alembic Only (Self-Upgrading at Startup) (+7 more)

### Community 30 - "Product Spec: Passes, Spots & Search"
Cohesion: 0.21
Nodes (15): Accepted Payment Methods, AI Search, Audit Log, Digitally Stored Customer Agreement, Future Features Roadmap, JWT Auth with Role Based Access, Outstanding Balance, Parking Objects (Vehicle Types) (+7 more)

### Community 31 - "Product Spec: Pricing & Reminders"
Cohesion: 0.24
Nodes (15): AI Insights / Morning Manager Report, AI Sales Opportunities (Hot/Warm/Cold Leads), Celery Background Jobs, Company Profiles, Daily Customer Tracking, Daily Pass ($20, custom day range), Monthly Customers, Monthly Pass ($250 default, overridable) (+7 more)

### Community 32 - "Test Fixtures & DB Session"
Cohesion: 0.20
Nodes (13): get_db(), Session, client(), db(), engine(), _fresh_engine(), fixture, Session (+5 more)

### Community 33 - "Payment Model & Dashboard Stats"
Cohesion: 0.15
Nodes (9): Payment, What the payment was for — the vehicle on its pass., dashboard_stats(), Session, DashboardStats, BaseModel, A payment taken at 10:30pm plaza time belongs to that day's revenue. The same…, test_tonights_takings_are_on_tonights_books() (+1 more)

### Community 34 - "Price Calculation & Pricing Tests"
Cohesion: 0.21
Nodes (13): _months_between(), _price_for(), Whole calendar months between two dates, rounding UP for any partial overage…, _compute_price(), date, PassType, The single source of truth both create-intent and (as a sanity check only, not…, Pricing math: partial-month rounding and per-type price. (+5 more)

### Community 35 - "Reports Summary & Schemas"
Cohesion: 0.41
Nodes (10): Session, reports_summary(), CompanyStat, OutstandingBalance, PaymentMethodStat, BaseModel, ReportsSummary, RevenuePoint (+2 more)

### Community 36 - "Design System & Lot UI Tasks"
Cohesion: 0.24
Nodes (12): AI Parking Inspector, Brand Colors, Dark Mode and Light Mode, Design Philosophy, Framer Motion, Modern Skeuomorphism UI Style, Color Coded Notifications, Search Everywhere (CTRL + K) (+4 more)

### Community 37 - "Tech Stack & Framework Choices"
Cohesion: 0.17
Nodes (12): Docker Deployment, FastAPI, Next.js, Nginx, PostgreSQL, Shadcn UI, SQLAlchemy, Tailwind CSS (+4 more)

### Community 38 - "Auth API Tests"
Cohesion: 0.33
Nodes (8): _login(), Auth endpoints + route protection (FastAPI TestClient over an in-memory DB)., _register(), test_login_locks_out_after_five_failures(), test_login_success_and_wrong_password(), test_me_requires_a_valid_token(), test_register_returns_token_then_second_is_forbidden(), test_status_flips_after_setup()

### Community 39 - "Frontend Package Scripts"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, start, test (+1 more)

### Community 40 - "Root Layout, Fonts & Theme Provider"
Cohesion: 0.24
Nodes (6): inter, jetbrainsMono, metadata, viewport, ThemeProvider(), Toaster()

### Community 41 - "In-Memory Rate Limiter"
Cohesion: 0.28
Nodes (5): _client_key(), Request, RateLimiter, Allow `times` requests per `seconds` per client, else 429., Tests only — start from a clean window.

### Community 42 - "Company Profile Aggregation"
Cohesion: 0.36
Nodes (8): company_profile(), Everything about one company in one place: totals, trucks, recent passes and…, _issue(), Company profile aggregation: totals, per-truck rollup, monthly fields., test_profile_404_for_unknown_company(), test_profile_aggregates_visits_trucks_and_spend(), test_profile_monthly_fields(), CompanyProfile

### Community 43 - "Project Charter & Coding Standards"
Cohesion: 0.22
Nodes (9): Engineering Identity Mandate, AI Development Rules (Plan, Build, Verify, Optimize), Coding Standards, Core Principle: The Software Remembers Everything, Feature Justification Rule, Reusable Claude Skill Folder, Madco Truck Plaza Parking Management System, Manual Processes Replaced (+1 more)

### Community 44 - "Public Pass Verify Page"
Cohesion: 0.32
Nodes (6): currency(), Look, lookFor(), VerifyPage(), PassVerifyResult, ReassignResult

### Community 45 - "Lot State Endpoint Tests"
Cohesion: 0.43
Nodes (5): _auth(), _issue(), One call paints the whole lot. States derived, matching the holding rules., test_overstay_state_and_clear(), test_states_cover_the_lot()

### Community 46 - "Next.js Scaffold Assets"
Cohesion: 0.48
Nodes (7): Document/File Glyph Icon (16x16, #666), Monochrome 16x16 Glyph Icon System (#666, evenodd fill), Globe / Web Glyph Icon (16x16, #666), create-next-app Default Scaffold Assets, Next.js Wordmark Logo (394x80, black), Vercel Triangle Logo (white, 1155x1000), Browser Window Glyph Icon (16x16, #666)

### Community 47 - "Demo Data Seeding"
Cohesion: 0.53
Nodes (5): _issue(), main(), _phone(), Seed realistic demo data into the dev database so every screen populates. Run…, seed()

### Community 49 - "Payment Idempotency Tests"
Cohesion: 0.60
Nodes (4): _issue_with_intent(), A single Stripe PaymentIntent can never mint two passes., test_duplicate_payment_intent_is_rejected(), test_price_from_charge_is_used_verbatim()

### Community 51 - "Go-Live Checklist & Alerting"
Cohesion: 0.50
Nodes (4): ALERT_WEBHOOK_URL Error Alerting (1/min rate limit), Go-Live Checklist, purge_demo Script (Wipe Demo Data, Keep Logins), Twilio A2P Activation (No Code Change)

### Community 52 - "Revenue Chart"
Cohesion: 0.83
Nodes (3): currency(), formatDate(), RevenueChart()

## Knowledge Gaps
- **142 isolated node(s):** `$schema`, `style`, `rsc`, `tsx`, `config` (+137 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `business_today()` connect `Plaza Clock & Spot Inventory Core` to `SMS & Monthly Customer Records`, `Payment Model & Dashboard Stats`, `Pass Issue, Pricing & Renewal`, `Reports Summary & Schemas`, `Insights, Morning Report & Leads`, `Logging, Alerts & Startup Migrations`, `Company Profile Aggregation`, `Alembic Env, Clock & ORM Models`, `Enums, Company Schemas & Routes`, `Payment Requests & Company Lookup`, `Lot State Endpoint Tests`, `Demo Data Seeding`, `Audit Log & Receipt Numbers`, `Config, JWT Secret & Dashboard Tests`, `Pass Status, QR Tokens & Rate Limit`, `Timezone Boundary Test`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `_get()` connect `Payment Requests & Company Lookup` to `SMS & Monthly Customer Records`, `Payment Model & Dashboard Stats`, `Stripe Webhook & Stranded Charges`, `Pass Issue, Pricing & Renewal`, `Auth, RBAC & Request Dependencies`, `Reports Summary & Schemas`, `Insights, Morning Report & Leads`, `Logging, Alerts & Startup Migrations`, `Company Profile Aggregation`, `Audit Log & Receipt Numbers`, `Pass Status, QR Tokens & Rate Limit`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `_issue_pass_and_payment()` connect `Pass Issue, Pricing & Renewal` to `SMS & Monthly Customer Records`, `Payment Model & Dashboard Stats`, `Plaza Clock & Spot Inventory Core`, `Price Calculation & Pricing Tests`, `Auth, RBAC & Request Dependencies`, `Stripe Webhook & Stranded Charges`, `Insights, Morning Report & Leads`, `Payment Requests & Company Lookup`, `Alembic Env, Clock & ORM Models`, `Company Profile Aggregation`, `Enums, Company Schemas & Routes`, `Stripe Client & Payment Intents`, `Demo Data Seeding`, `Lot State Endpoint Tests`, `Payment Idempotency Tests`, `Audit Log & Receipt Numbers`, `Config, JWT Secret & Dashboard Tests`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `PassType` (e.g. with `ParkingPass` and `CompanyBase`) actually correct?**
  _`PassType` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `PaymentMethod` (e.g. with `MonthlyCustomer` and `Payment`) actually correct?**
  _`PaymentMethod` has 22 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `style`, `rsc` to the rest of the system?**
  _142 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `SMS & Monthly Customer Records` be split into smaller, more focused modules?**
  _Cohesion score 0.06459627329192547 - nodes in this community are weakly interconnected._