"""Role tiers, enforced at the API — not just hidden in the sidebar.

Any login = the front desk job (issue, renew, look up).
Manager+ = the money (revenue, payment history, reports, insights).
Admin    = the owner (staff accounts, password resets, the audit trail).

A seasonal hire with an attendant login must not be able to read the plaza's
revenue by calling the API directly, no matter what the UI hides.
"""


def _admin_token(client) -> str:
    r = client.post(
        "/api/auth/register",
        json={"name": "Owner", "email": "owner@madcotruckplaza.com", "password": "ownerpass123"},
    )
    return r.json()["access_token"]


def _staff_token(client, admin_token, role, email) -> str:
    r = client.post(
        "/api/auth/users",
        json={"name": f"{role} user", "email": email, "password": "staffpass123", "role": role},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code in (200, 201), r.text
    login = client.post("/api/auth/login", json={"email": email, "password": "staffpass123"})
    return login.json()["access_token"]


def _get(client, path, token):
    return client.get(path, headers={"Authorization": f"Bearer {token}"})


def test_attendant_can_work_the_desk_but_not_read_the_money(client):
    admin = _admin_token(client)
    attendant = _staff_token(client, admin, "attendant", "gate@madcotruckplaza.com")

    # The job: passes, lot check, reminders — all open.
    assert _get(client, "/api/passes", attendant).status_code == 200
    assert _get(client, "/api/lot-check?q=7834", attendant).status_code == 200
    assert _get(client, "/api/reminders", attendant).status_code == 200

    # The money: forbidden, with a 403 (not a 401 — they ARE logged in).
    for path in (
        "/api/dashboard/stats",
        "/api/payments",
        "/api/reports/summary",
        "/api/insights/morning-report",
        "/api/insights/conversion-leads",
    ):
        assert _get(client, path, attendant).status_code == 403, path

    # The owner's domain: also forbidden.
    assert _get(client, "/api/audit-log", attendant).status_code == 403
    assert _get(client, "/api/auth/users", attendant).status_code == 403


def test_manager_reads_the_money_but_not_the_owners_domain(client):
    admin = _admin_token(client)
    manager = _staff_token(client, admin, "manager", "shift@madcotruckplaza.com")

    assert _get(client, "/api/dashboard/stats", manager).status_code == 200
    assert _get(client, "/api/reports/summary", manager).status_code == 200
    assert _get(client, "/api/insights/morning-report", manager).status_code == 200

    assert _get(client, "/api/audit-log", manager).status_code == 403
    assert _get(client, "/api/auth/users", manager).status_code == 403


def test_admin_sees_everything(client):
    admin = _admin_token(client)
    for path in ("/api/dashboard/stats", "/api/payments", "/api/audit-log", "/api/auth/users"):
        assert _get(client, path, admin).status_code == 200, path


def test_only_admin_resets_passwords(client):
    admin = _admin_token(client)
    manager = _staff_token(client, admin, "manager", "shift2@madcotruckplaza.com")

    users = _get(client, "/api/auth/users", admin).json()
    target = next(u for u in users if u["email"] == "shift2@madcotruckplaza.com")

    denied = client.post(
        f"/api/auth/users/{target['id']}/reset-password",
        json={"new_password": "newpass12345"},
        headers={"Authorization": f"Bearer {manager}"},
    )
    assert denied.status_code == 403

    ok = client.post(
        f"/api/auth/users/{target['id']}/reset-password",
        json={"new_password": "newpass12345"},
        headers={"Authorization": f"Bearer {admin}"},
    )
    assert ok.status_code == 200

    # Old password dead, new one lives.
    assert client.post("/api/auth/login", json={"email": "shift2@madcotruckplaza.com", "password": "staffpass123"}).status_code == 401
    assert client.post("/api/auth/login", json={"email": "shift2@madcotruckplaza.com", "password": "newpass12345"}).status_code == 200
