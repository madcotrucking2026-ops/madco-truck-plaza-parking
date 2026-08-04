"""Rate limiting and input validation on the unauthenticated surface.

Each test names the attack it blocks, not just the status code it expects.
"""

from datetime import date, timedelta

EMAIL = "admin@madcotruckplaza.com"
PASSWORD = "supersecret1"


def _register(client):
    return client.post("/api/auth/register", json={"name": "Admin", "email": EMAIL, "password": PASSWORD})


# --------------------------------------------------------------------------
# Rate limiting
# --------------------------------------------------------------------------


def test_login_is_rate_limited(client):
    """Blocks two things the per-account lockout does NOT: a spray across many
    accounts (4 tries each never trips a 5-strike lockout), and locking the
    owner out of his own account on demand by failing on his email."""
    _register(client)
    codes = [
        client.post("/api/auth/login", json={"email": f"u{i}@example-fleet.com", "password": "nope1234"}).status_code
        for i in range(12)
    ]
    assert 429 in codes, "login accepted 12 attempts from one IP without throttling"
    first_429 = codes.index(429)
    assert first_429 >= 10, f"throttled too early (at attempt {first_429 + 1})"


def test_rate_limited_response_says_when_to_retry(client):
    for _ in range(11):
        r = client.post("/api/auth/login", json={"email": "a@example-fleet.com", "password": "nope1234"})
    assert r.status_code == 429
    assert r.headers.get("Retry-After")  # a client can back off correctly


def test_company_lookup_is_rate_limited(client):
    """Public and unauthenticated: it answers "does this company exist, what is
    its negotiated monthly rate, and which trucks park under it". Throttled so a
    wordlist can't enumerate the customer book."""
    codes = [client.get("/api/companies/lookup?name=acme").status_code for _ in range(35)]
    assert 429 in codes


# --------------------------------------------------------------------------
# Input validation — all of this is reachable WITHOUT a login
# --------------------------------------------------------------------------


def test_giant_password_is_rejected_before_hashing(client):
    """An unbounded password field means megabytes fed straight into bcrypt on
    an endpoint that needs no auth."""
    r = client.post("/api/auth/login", json={"email": EMAIL, "password": "x" * 100_000})
    assert r.status_code == 422


def test_malformed_email_is_rejected(client):
    r = client.post("/api/auth/register", json={"name": "A", "email": "not-an-email", "password": PASSWORD})
    assert r.status_code == 422


def test_short_password_is_rejected(client):
    r = client.post("/api/auth/register", json={"name": "A", "email": EMAIL, "password": "short"})
    assert r.status_code == 422


def _issue(client, **over):
    """Authed desk issue — the only way a pass is created now that the customer
    kiosk is retired. Same IssuePassRequest bounds the kiosk used to enforce."""
    _register(client)
    token = client.post("/api/auth/login", json={"email": EMAIL, "password": PASSWORD}).json()["access_token"]
    body = {
        "company_name": "Acme Trucking", "truck_number": "T1", "phone": "313-555-0100",
        "vehicle_type": "truck", "pass_type": "daily", "issue_date": date.today().isoformat(),
        "payment_method": "cash",
    }
    body.update(over)
    return client.post("/api/passes", headers={"Authorization": f"Bearer {token}"}, json=body)


def test_oversized_company_name_is_rejected_on_issue(client):
    """Unbounded here would flow straight into the database."""
    assert _issue(client, company_name="A" * 5000).status_code == 422


def test_backwards_date_range_is_rejected(client):
    today = date.today()
    assert _issue(client, issue_date=today.isoformat(), end_date=(today - timedelta(days=5)).isoformat()).status_code == 422


def test_absurd_pass_span_is_rejected(client):
    """A crafted end_date decades out turns into an absurd computed price."""
    today = date.today()
    assert _issue(client, end_date=(today + timedelta(days=4000)).isoformat()).status_code == 422


def test_negative_price_is_rejected_on_issue(client):
    """A negative price would record a NEGATIVE payment against the drawer."""
    _register(client)
    token = client.post("/api/auth/login", json={"email": EMAIL, "password": PASSWORD}).json()["access_token"]
    r = client.post(
        "/api/passes",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_name": "Acme",
            "truck_number": "T1",
            "phone": "313-555-0100",
            "vehicle_type": "truck",
            "pass_type": "monthly",
            "price": -500,
            "issue_date": date.today().isoformat(),
            "payment_method": "cash",
        },
    )
    assert r.status_code == 422
