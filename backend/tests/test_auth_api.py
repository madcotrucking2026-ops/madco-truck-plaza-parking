"""Auth endpoints + route protection (FastAPI TestClient over an in-memory DB)."""

EMAIL = "admin@madcotruckplaza.com"
PASSWORD = "supersecret1"


def _register(client, name="Admin", email=EMAIL, password=PASSWORD):
    return client.post("/api/auth/register", json={"name": name, "email": email, "password": password})


def _login(client, email=EMAIL, password=PASSWORD):
    return client.post("/api/auth/login", json={"email": email, "password": password})


def test_status_flips_after_setup(client):
    assert client.get("/api/auth/status").json()["needs_setup"] is True
    _register(client)
    assert client.get("/api/auth/status").json()["needs_setup"] is False


def test_register_returns_token_then_second_is_forbidden(client):
    r = _register(client)
    assert r.status_code == 200
    assert r.json()["access_token"]
    # SetupLock makes bootstrap one-shot — a second register is refused.
    r2 = _register(client, email="other@madcotruckplaza.com")
    assert r2.status_code == 403


def test_login_success_and_wrong_password(client):
    _register(client)
    assert _login(client).status_code == 200
    bad = _login(client, password="wrongpass")
    assert bad.status_code == 401


def test_login_locks_out_after_five_failures(client):
    _register(client)
    for _ in range(5):
        assert _login(client, password="wrongpass").status_code == 401
    # Sixth attempt with the CORRECT password is still refused — account locked.
    locked = _login(client)
    assert locked.status_code == 401
    assert "Too many failed attempts" in locked.json()["detail"]


def test_me_requires_a_valid_token(client):
    _register(client)
    assert client.get("/api/auth/me").status_code in (401, 403)  # no token
    token = _login(client).json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == EMAIL


def test_protected_routes_reject_anonymous(client):
    # The manager API is guarded — no token, no data.
    for path in ("/api/passes", "/api/dashboard/stats", "/api/reminders"):
        assert client.get(path).status_code in (401, 403), path


def test_public_status_endpoint_is_open(client):
    # Auth status is deliberately public (the login page reads it pre-auth).
    assert client.get("/api/auth/status").status_code == 200
