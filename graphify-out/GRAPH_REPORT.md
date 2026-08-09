# Graph Report - .  (2026-08-09)

## Corpus Check
- 210 files · ~75,204 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1372 nodes · 3601 edges · 85 communities (68 shown, 17 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 185 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73
- Community 74
- Community 75
- Community 80
- Community 81
- Community 82
- Community 83

## God Nodes (most connected - your core abstractions)
1. `ensure_spots()` - 80 edges
2. `cn()` - 80 edges
3. `business_today()` - 75 edges
4. `_issue_pass_and_payment()` - 73 edges
5. `PassType` - 65 edges
6. `PaymentMethod` - 56 edges
7. `VehicleType` - 47 edges
8. `PassStatus` - 36 edges
9. `_get()` - 34 edges
10. `business_now()` - 30 edges

## Surprising Connections (you probably didn't know these)
- `Amber Box-Truck Favicon on Forest` --conceptually_related_to--> `Madco Truck Plaza Parking Management System`  [INFERRED]
  frontend/src/app/icon.svg → CLAUDE.md
- `mtpms-backend Web Service` --semantically_similar_to--> `Backend Service (FastAPI, self-migrating)`  [INFERRED] [semantically similar]
  render.yaml → docker-compose.prod.yml
- `Free Hosting Guide (Vercel+Render+Neon)` --semantically_similar_to--> `Docker Self-Hosted Deploy Guide`  [INFERRED] [semantically similar]
  DEPLOY-FREE.md → DEPLOY.md
- `dev service: postgres (port 5432 exposed)` --semantically_similar_to--> `Postgres Service`  [INFERRED] [semantically similar]
  docker-compose.yml → docker-compose.prod.yml
- `Amber Box-Truck Favicon on Forest` --conceptually_related_to--> `Brand Colour Tokens`  [INFERRED]
  frontend/src/app/icon.svg → DESIGN.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **CI quality gates (pytest, tsc, vitest, build, advisory lint)** — _github_workflows_ci_backend_job, _github_workflows_ci_frontend_job, _github_workflows_ci_lint_non_blocking, backend_requirements_dev_test_deps [EXTRACTED 1.00]
- **Derived-state spot dispatch flow (hold → pick → assign → overstay reassign)** — docs_superpowers_specs_2026_07_28_spot_inventory_design_derived_state, docs_superpowers_specs_2026_07_28_spot_inventory_design_holding_predicate, docs_superpowers_specs_2026_07_28_spot_inventory_design_assignment_algorithm, docs_superpowers_specs_2026_07_28_spot_inventory_design_full_lot_never_strand_money, docs_superpowers_specs_2026_07_28_spot_inventory_design_asphalt_gap [EXTRACTED 1.00]
- **Untouched create-next-app public/ asset set (vendor branding, not Madco brand)** — frontend_public_file_document_icon, frontend_public_globe_globe_icon, frontend_public_window_window_icon, frontend_public_next_nextjs_wordmark, frontend_public_vercel_vercel_triangle_logo [INFERRED 0.85]
- **Production Docker Compose Stack (five services + certbot)** — docker_compose_prod_postgres, docker_compose_prod_backend, docker_compose_prod_frontend, docker_compose_prod_nginx, docker_compose_prod_cron, docker_compose_prod_certbot [EXTRACTED 0.95]
- **Free Hosting Path (GitHub + Neon + Render + Vercel)** — deploy_free_github, deploy_free_neon, deploy_free_render, deploy_free_vercel [EXTRACTED 0.95]
- **Zone Availability Feature (labels + board + move + config)** — docs_superpowers_specs_2026_08_04_zone_availability_design_spot_label, docs_superpowers_specs_2026_08_04_zone_availability_design_availability_page, docs_superpowers_specs_2026_08_04_zone_availability_design_move_endpoint, docs_superpowers_specs_2026_08_04_zone_availability_design_spots_per_zone [EXTRACTED 0.85]

## Communities (85 total, 17 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (80): ensure_spots(), free_spot_count(), is_monthly_spot(), monthly_spot_limit(), move_pass_to_spot(), MoveError, pick_free_spot(), Exception (+72 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (75): add_months(), date, Free a monthly truck's reserved spot(s) back to the pool. Called on close-out…, release_reserved_spot(), apply_renewal(), _close_out_price(), _expiration_for(), _find_or_create_vehicle() (+67 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (74): AuthStatus, generate_receipt_number(), date, create_access_token(), hash_password(), verify_password(), health(), Company (+66 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (63): PassStatus, PassType, PaymentMethod, VehicleType, lot_check(), Session, CompanyBase, CompanyCreate (+55 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (55): live_status(), pass_expired(), date, datetime, PassType, Has this pass's paid window ended, at the plaza clock `now`? `now` is the…, Display label for a spot: 1 -> 'A1', 26 -> 'B1', 150 -> 'F25'. The integer…, spot_label() (+47 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (51): business_today(), date, The plaza's current calendar day. Use this everywhere `date.today()` was used,…, _money(), morning_report(), date, Session, The manager's 7am briefing: who to call today, and why. The dashboard already… (+43 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (49): AI Insights / Manager Report, AI Parking Inspector, AI Sales Opportunities, AI Search, Audit Log, Reduce-Manual-Work Build Mission, Company Profiles, Daily Parking Pass (+41 more)

### Community 7 - "Community 7"
Cohesion: 0.10
Nodes (31): ACTION_STYLE, AuditLogPage(), fmt(), styleFor(), LEGEND, STATE_CLASS, currency(), MonthlyCustomer (+23 more)

### Community 8 - "Community 8"
Cohesion: 0.17
Nodes (19): business_now(), plaza_tz(), datetime, What day is it *at the plaza*. Two separate bugs live here if you get this…, Wall-clock time at the plaza, naive — stored as-is so `date(paid_at)` in SQL is…, Base, ReminderStatus, MonthlyCustomer (+11 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (32): AvailabilityPage(), currency(), DashboardPage(), LEAD_TIER, QUICK_ACTIONS, relativeDayISO(), LEGEND, LotGrid() (+24 more)

### Community 10 - "Community 10"
Cohesion: 0.10
Nodes (25): IDENTIFIER_FIELD, PASS_TYPES, PAY_CHOICES, PayChoice, VEHICLE_TYPES, BulkRenewDialog(), PAY_CHOICES, PayChoice (+17 more)

### Community 11 - "Community 11"
Cohesion: 0.18
Nodes (23): expiryPhrase(), LotCheckInner(), PAYMENT_LABEL, shortDate(), STATUS_STYLE, IssuePassForm(), METHOD_LABEL, PAY_CHOICES (+15 more)

### Community 12 - "Community 12"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (25): MethodBadge(), Card(), CardAction(), CardContent(), CardDescription(), CardFooter(), CardHeader(), CardTitle() (+17 more)

### Community 14 - "Community 14"
Cohesion: 0.18
Nodes (14): currency(), PassesPage(), Field(), Dialog(), DialogContent(), DialogDescription(), DialogFooter(), DialogHeader() (+6 more)

### Community 15 - "Community 15"
Cohesion: 0.14
Nodes (17): get_db(), Session, get_current_user(), Session, Admin or manager — the money tier. An attendant's job is the front desk: issue,…, require_admin(), require_manager(), decode_access_token() (+9 more)

### Community 16 - "Community 16"
Cohesion: 0.15
Nodes (17): log_audit(), Session, AuditLog, AuditAction, ParkingPass, list_audit_log(), Session, cancel_pass() (+9 more)

### Community 17 - "Community 17"
Cohesion: 0.10
Nodes (18): ERROR-level logs become a phone notification, not a line in a file. A truck…, WebhookAlertHandler, `Base.metadata.create_all()` only creates missing *tables* — it never alters an…, run_startup_migrations(), configure_logging(), get_logger(), Console + rotating-file logging for the app. Called once at startup. File…, Child of the app logger, named for the calling module. (+10 more)

### Community 18 - "Community 18"
Cohesion: 0.13
Nodes (22): conversion_leads(), _monthly_equivalent(), What this company effectively spends per month right now. The window is 90…, Daily/weekly customers who come often enough that a monthly plan would likely…, _tier(), CallItem, ConversionLead, ConversionLeads (+14 more)

### Community 19 - "Community 19"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 20 - "Community 20"
Cohesion: 0.16
Nodes (17): CommandPalette(), AppShell(), isPublicPath(), MobileNav(), SidebarNav(), download(), request(), clearToken() (+9 more)

### Community 21 - "Community 21"
Cohesion: 0.16
Nodes (18): effective(), load_overrides(), Session, Owner-editable runtime config: parking capacity + default prices. These are…, Current live values — the env default unless a saved override replaced it., Apply saved overrides onto `settings` (called once at startup, so DB values win…, Upsert {key: value} for EDITABLE keys and apply them to `settings`. The caller…, save_overrides() (+10 more)

### Community 22 - "Community 22"
Cohesion: 0.12
Nodes (17): _issue(), Rate limiting and input validation on the unauthenticated surface. Each test…, A negative price would record a NEGATIVE payment against the drawer., Blocks two things the per-account lockout does NOT: a spray across many…, Public and unauthenticated: it answers "does this company exist, what is its…, An unbounded password field means megabytes fed straight into bcrypt on an…, Authed desk issue — the only way a pass is created now that the customer kiosk…, Unbounded here would flow straight into the database. (+9 more)

### Community 23 - "Community 23"
Cohesion: 0.10
Nodes (21): eslint, eslint-config-next, devDependencies, eslint, eslint-config-next, playwright, tailwindcss, @tailwindcss/postcss (+13 more)

### Community 24 - "Community 24"
Cohesion: 0.14
Nodes (16): Per-client sliding-window rate limiting, as a FastAPI dependency. Deliberately…, _issue(), main(), _phone(), Seed realistic demo data into the dev database so every screen populates. Run…, seed(), client(), db() (+8 more)

### Community 25 - "Community 25"
Cohesion: 0.24
Nodes (16): MonthlyCustomerStatus, create_monthly_customer(), list_monthly_customers(), patch, post, Session, update_status(), MonthlyCustomerCreate (+8 more)

### Community 26 - "Community 26"
Cohesion: 0.11
Nodes (19): class-variance-authority, clsx, cmdk, dependencies, class-variance-authority, clsx, cmdk, next-themes (+11 more)

### Community 27 - "Community 27"
Cohesion: 0.14
Nodes (8): Alembic environment — wired to the app's own settings and metadata, so there is…, load_or_create_jwt_secret(), DashboardStats, BaseModel, _owner_headers(), Money guards: a cashier double-submit never charges twice, and the standalone…, test_owner_can_record_a_negative_refund(), test_payment_amount_rejects_an_absurd_value()

### Community 28 - "Community 28"
Cohesion: 0.16
Nodes (13): Payment, What the payment was for — the vehicle on its pass., dashboard_stats(), Session, A payment taken at 10:30pm plaza time belongs to that day's revenue. The same…, test_tonights_takings_are_on_tonights_books(), _issue_active(), Dashboard occupancy: capacity, available spots, occupancy %. (+5 more)

### Community 29 - "Community 29"
Cohesion: 0.20
Nodes (13): _held_spot_ids(), holding_filter(), _live_window_filter(), Spot inventory. State is DERIVED: a spot is free iff no live pass holds it.…, The date/status part of 'this pass occupies the lot': not cancelled, and inside…, Boolean clause: this pass currently HOLDS its spot. Evaluated per-query against…, A spot the system may hand to the NEXT daily/weekly customer: active, not held…, _sellable_filter() (+5 more)

### Community 30 - "Community 30"
Cohesion: 0.20
Nodes (9): ThemeToggle(), Sheet(), SheetContent(), SheetDescription(), SheetFooter(), SheetHeader(), SheetOverlay(), SheetTitle() (+1 more)

### Community 31 - "Community 31"
Cohesion: 0.22
Nodes (8): CompanyProfilePage(), fmtDate(), fmtDateTime(), money(), money2(), InfoTip(), EditCompanyDialog(), CompanyProfile

### Community 32 - "Community 32"
Cohesion: 0.24
Nodes (12): Task 1: Spot model, migration, idempotent seeding, Task 2: Holding predicate + free-spot picker, Task 3: Assign at issue time (sticky monthly, full lot never blocks), Task 4: Kiosk pre-check — refuse checkout when full, Assignment Algorithm (in-transaction, FOR UPDATE SKIP LOCKED), spots Table + parking_passes.spot_id Data Model, Derived State — A Spot Is Free Iff No Live Pass Holds It, Full Lot — Pre-check, But Never Strand Taken Money (+4 more)

### Community 33 - "Community 33"
Cohesion: 0.18
Nodes (11): CI job: Backend · pytest (Python 3.11), Backend dev/test dependency set (pytest, httpx), Stripe SDK (vestigial dependency), Docker Self-Hosted Deploy Guide, Staff-Only, No Stripe Payments, Plaza Timezone Config (America/Detroit), Production Docker Compose Stack, Global Constraints (business_today, Alembic-only, style) (+3 more)

### Community 34 - "Community 34"
Cohesion: 0.42
Nodes (9): Session, reports_summary(), CompanyStat, PaymentMethodStat, BaseModel, ReportsSummary, RevenuePoint, TruckStat (+1 more)

### Community 35 - "Community 35"
Cohesion: 0.20
Nodes (11): Auth Stack (python-jose, passlib, bcrypt<4.1), FastAPI, Uvicorn ASGI Server, Tech Stack, Cross-Service Env Wiring, GitHub Code Hosting, Free Hosting Guide (Vercel+Render+Neon), Render Backend Host (+3 more)

### Community 36 - "Community 36"
Cohesion: 0.33
Nodes (8): _login(), Auth endpoints + route protection (FastAPI TestClient over an in-memory DB)., _register(), test_login_locks_out_after_five_failures(), test_login_success_and_wrong_password(), test_me_requires_a_valid_token(), test_register_returns_token_then_second_is_forbidden(), test_status_flips_after_setup()

### Community 37 - "Community 37"
Cohesion: 0.38
Nodes (10): _admin_token(), Voiding a mistaken payment. Nothing is deleted — a negative reversal entry is…, _record_payment(), _staff_token(), test_a_negative_reversal_cannot_itself_be_voided(), test_a_payment_cannot_be_voided_twice(), test_attendant_cannot_void(), test_void_missing_payment_is_404() (+2 more)

### Community 38 - "Community 38"
Cohesion: 0.27
Nodes (9): bucketOf(), currency(), inPeriod(), METHOD_STYLE, Payment, PaymentsPage(), Period, PERIODS (+1 more)

### Community 39 - "Community 39"
Cohesion: 0.20
Nodes (6): STATUS_STYLE, StatusBadge(), Badge(), badgeVariants, Label(), Separator()

### Community 40 - "Community 40"
Cohesion: 0.24
Nodes (9): InputGroup(), InputGroupAddon(), inputGroupAddonVariants, InputGroupButton(), inputGroupButtonVariants, InputGroupInput(), InputGroupText(), InputGroupTextarea() (+1 more)

### Community 41 - "Community 41"
Cohesion: 0.31
Nodes (9): _admin_token(), fixture, Owner-editable settings: capacity + default prices. Admin-only to change, any…, _restore_settings(), _staff_token(), test_admin_update_persists_and_applies_live(), test_capacity_change_reshapes_the_lot(), test_get_returns_effective_defaults() (+1 more)

### Community 42 - "Community 42"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, start, test (+1 more)

### Community 43 - "Community 43"
Cohesion: 0.24
Nodes (6): inter, jetbrainsMono, metadata, viewport, ThemeProvider(), Toaster()

### Community 44 - "Community 44"
Cohesion: 0.28
Nodes (5): _client_key(), Request, RateLimiter, Allow `times` requests per `seconds` per client, else 429., Tests only — start from a clean window.

### Community 45 - "Community 45"
Cohesion: 0.22
Nodes (9): Alembic Migrations, psycopg Postgres Driver, SQLAlchemy ORM, Alembic Self-Migration at Startup, TLS via Certbot / Let's Encrypt, Backend Service (FastAPI, self-migrating), Certbot TLS Renewal Service, Fixed JWT_SECRET Rationale (+1 more)

### Community 46 - "Community 46"
Cohesion: 0.44
Nodes (8): _admin_token(), _blank_company(), Editing a company after the fact — the fix for a cashier who issued a pass with…, _staff_token(), test_attendant_cannot_edit_a_company(), test_blank_name_is_rejected(), test_manager_renames_a_blank_company(), test_missing_company_is_404()

### Community 47 - "Community 47"
Cohesion: 0.29
Nodes (6): Settings, parametrize, DATABASE_URL normalization — managed Postgres hosts (Neon/Render/Supabase) hand…, test_database_url_is_normalized_for_sqlalchemy(), BaseSettings, field_validator

### Community 48 - "Community 48"
Cohesion: 0.33
Nodes (7): CI job: Frontend · typecheck + test + build (Node 20), Non-blocking lint (react-hooks/set-state-in-effect), Vercel Frontend Host, Frontend Service (Next.js), Next.js Agent Rules Block, frontend/CLAUDE.md → @AGENTS.md include, Frontend README (create-next-app boilerplate)

### Community 49 - "Community 49"
Cohesion: 0.43
Nodes (7): Task 5: report-occupied endpoint (self-reassign + overstay flag), Task 6: GET /api/spots lot state endpoint, Task 7: Spot number on ticket, kiosk, verify page, Task 8: Dashboard lot grid + overstay chip + lot check spot, Task 9: Overstays in the morning report, The Asphalt Gap — Self-Service Overstay Reassign, Spot Surfaces (ticket hero, lot check, dashboard grid, morning report)

### Community 50 - "Community 50"
Cohesion: 0.48
Nodes (7): Document/File Glyph Icon (16x16, #666), Monochrome 16x16 Glyph Icon System (#666, evenodd fill), Globe / Web Glyph Icon (16x16, #666), create-next-app Default Scaffold Assets, Next.js Wordmark Logo (394x80, black), Vercel Triangle Logo (white, 1155x1000), Browser Window Glyph Icon (16x16, #666)

### Community 51 - "Community 51"
Cohesion: 0.53
Nodes (5): _admin_token(), Full-data backup: an admin downloads a ZIP of CSVs (one per record type); every…, _staff_token(), test_admin_downloads_a_zip_of_csvs(), test_export_is_admin_only()

### Community 52 - "Community 52"
Cohesion: 0.33
Nodes (6): Nightly pg_dump Backups, Neon Postgres Database, dev service: postgres (port 5432 exposed), Cron Nightly Backup Service, Postgres Service, Uptime Decision — Single-Box Stack, HA Rejected

### Community 53 - "Community 53"
Cohesion: 0.40
Nodes (5): Tabs(), TabsContent(), TabsList(), tabsListVariants, TabsTrigger()

### Community 54 - "Community 54"
Cohesion: 0.40
Nodes (5): _log_unhandled(), Exception, Request, exception_handler, JSONResponse

### Community 55 - "Community 55"
Cohesion: 0.50
Nodes (4): _admin(), parametrize, The two new desk payment-method labels are accepted end to end., test_new_methods_are_accepted()

### Community 56 - "Community 56"
Cohesion: 0.83
Nodes (3): currency(), formatDate(), RevenueChart()

## Knowledge Gaps
- **156 isolated node(s):** `$schema`, `style`, `rsc`, `tsx`, `config` (+151 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `business_today()` connect `Community 5` to `Community 0`, `Community 1`, `Community 2`, `Community 34`, `Community 4`, `Community 3`, `Community 8`, `Community 15`, `Community 16`, `Community 18`, `Community 24`, `Community 27`, `Community 28`, `Community 29`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `_issue_pass_and_payment()` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 8`, `Community 16`, `Community 18`, `Community 24`, `Community 27`, `Community 28`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `PassType` connect `Community 3` to `Community 0`, `Community 1`, `Community 4`, `Community 5`, `Community 8`, `Community 16`, `Community 18`, `Community 24`, `Community 27`, `Community 28`, `Community 29`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `PassType` (e.g. with `MoveError` and `ParkingPass`) actually correct?**
  _`PassType` has 28 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `style`, `rsc` to the rest of the system?**
  _156 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.050940438871473356 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.052160493827160495 - nodes in this community are weakly interconnected._