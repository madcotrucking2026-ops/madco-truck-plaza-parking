# Deploying MTPMS

The entire system runs from one command on any machine with Docker (a $10/mo
VPS, a mini-PC in the office, a cloud VM). Nothing else to install.

## First deployment

```bash
git clone <this repo> && cd madco-truck-plaza-parking
cp .env.prod.example .env.prod
# Fill in .env.prod:
#   python -c "import secrets; print(secrets.token_hex(32))"   # JWT_SECRET
#   python -c "import secrets; print(secrets.token_hex(16))"   # POSTGRES_PASSWORD, SCHEDULER_TOKEN
#   PUBLIC_BASE_URL = the address customers will use
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

Open the site → it asks to create the admin account (one-time; further
registrations are locked). Then Settings → Add a Staff Login for everyone else.

What you get:
- **postgres** — the database, on a named volume
- **backend** — FastAPI; runs its own Alembic migrations at every start
- **frontend** — Next.js
- **nginx** — the ONLY published port (80); routes `/api` → backend, rest → frontend
- **cron** — daily reminder sweep + nightly `pg_dump` into `./backups/` (14 kept)

## Go-live checklist (in order)

1. **Domain + HTTPS** — point DNS at the box, then (still in HTTP mode — the
   HTTP config already answers Let's Encrypt's challenge):

   ```bash
   # one-shot: obtain the first certificate
   docker compose -f docker-compose.prod.yml --env-file .env.prod run --rm certbot \
     certonly --webroot -w /var/www/certbot --cert-name mtpms \
     -d park.madcotruckplaza.com --email you@example.com --agree-tos --no-eff-email

   # flip to TLS: in .env.prod set
   #   NGINX_CONF=nginx-tls.conf
   #   PUBLIC_BASE_URL=https://park.madcotruckplaza.com
   docker compose -f docker-compose.prod.yml --env-file .env.prod --profile tls up -d --build
   ```

   `--cert-name mtpms` pins the certificate path `nginx-tls.conf` expects — no
   config editing. The `tls` profile starts the renewal daemon (checks twice a
   day; certbot renews when <30 days remain) and nginx reloads itself every 6h
   to pick renewed certs up. The rebuild is required because the frontend bakes
   `PUBLIC_BASE_URL` into the browser bundle. HTTPS is REQUIRED for live Stripe
   and for Apple/Google Pay.
2. **Live Stripe keys** in `.env.prod` (after Stripe business verification).
3. **Stripe webhook** — Dashboard → Developers → Webhooks → add
   `https://<domain>/api/payments/stripe/webhook`, event
   `payment_intent.succeeded`; copy the `whsec_…` into `STRIPE_WEBHOOK_SECRET`.
   The backend WARNS at startup while this is missing — that warning must be
   gone before real cards are charged.
4. **Stripe payment-method domain** — Dashboard → Settings → Payment method
   domains → add the domain → Verify (enables Apple/Google Pay).
5. **Twilio** — creds into `.env.prod`; texts start delivering the moment the
   A2P campaign shows Approved. No code change.
6. **Alerting** — put a Slack/Discord/ntfy webhook in `ALERT_WEBHOOK_URL`;
   every application ERROR pings it (rate-limited to 1/min).
7. **Wipe the demo data** —
   `docker compose -f docker-compose.prod.yml exec backend python -m scripts.purge_demo --yes`
   (keeps logins, empties the books).

## Day-2 operations

| Task | Command |
|---|---|
| Update the app | `git pull && docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build` |
| Logs | `docker compose -f docker-compose.prod.yml logs -f backend` |
| Backup NOW | `docker compose -f docker-compose.prod.yml exec cron sh -c 'pg_dump -h postgres -U mtpms mtpms | gzip > /backups/manual-$(date +%Y%m%d).sql.gz'` |
| Restore | `gunzip -c backups/<file>.sql.gz \| docker compose -f docker-compose.prod.yml exec -T postgres psql -U mtpms mtpms` (into a FRESH volume) |
| Owner forgot password | `docker compose -f docker-compose.prod.yml exec backend python -m scripts.reset_password <email>` |
| Staff forgot password | Settings → Staff Logins → Reset password (admin only) |

Backups land in `./backups/` on the host. **Copy them somewhere off the box**
(external drive, cloud storage) — a backup on the same disk as the database
only survives mistakes, not hardware.

## Architecture notes (for whoever maintains this)

- **One backend worker, on purpose.** Rate limiting and the reminder scheduler
  are in-process. One uvicorn worker handles a truck stop's traffic with ease;
  before scaling out, move rate limiting to nginx/Redis.
- **Spot inventory is config.** `PARKING_CAPACITY` sizes the painted lot (spot
  rows are added/deactivated idempotently at startup — a 300-spot client is an
  env var, not code). `SPOT_GRACE_DAYS` (default 3) is how long a lapsed monthly
  keeps their number before it returns to the pool. Free/occupied is DERIVED
  from live passes — there is no status column and no midnight job to fail.
- **The plaza's timezone is config** (`TIMEZONE`, default America/Detroit).
  Every "today" — revenue, expiry, reminders — is computed in it, never the
  host's. On Postgres the session timezone is pinned to it too.
- **Schema = Alembic only.** New change → new revision:
  `docker compose exec backend alembic revision --autogenerate -m "..."`.
  The backend upgrades itself to head at startup; pre-Alembic databases are
  detected and stamped once.
- **Roles**: attendant = front desk (passes, lot check, reminders);
  manager = + money (dashboard, payments, reports, insights);
  admin = + staff accounts and the audit log. Enforced at the API, mirrored in
  the sidebar.
