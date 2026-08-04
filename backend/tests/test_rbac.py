"""Role tiers, enforced at the API — not just hidden in the sidebar.

Cashier (attendant) = issue passes, see the lot, move a truck. THAT'S IT.
Manager+ = everything the cashier does, plus the money and the accounts.
Admin    = the owner (staff accounts, password resets, the audit trail).

A cashier login must not be able to read the plaza's revenue, browse accounts,
or renew/cancel passes by calling the API directly, no matter what the UI hides.
"""
from datetime import date


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


def test_cashier_can_only_issue_passes_and_manage_spots(client):
    admin = _admin_token(client)
    cashier = _staff_token(client, admin, "attendant", "gate@madcotruckplaza.com")
    H = {"Authorization": f"Bearer {cashier}"}
    today = date.today().isoformat()

    # CAN: issue a pass — the cashier's whole job.
    issue = client.post(
        "/api/passes",
        json={
            "company_name": "Gate Co", "truck_number": "G1", "phone": "313-555-0100",
            "vehicle_type": "truck", "pass_type": "daily", "issue_date": today,
            "payment_method": "cash",
        },
        headers=H,
    )
    assert issue.status_code == 200, issue.text
    pass_id = issue.json()["id"]

    # CAN: see the availability board, and REACH the move endpoint (404 on bad
    # ids proves the gate let them in — a 403 would mean it didn't).
    assert _get(client, "/api/spots", cashier).status_code == 200
    assert client.post("/api/spots/move", json={"pass_id": 999999, "to_number": 1}, headers=H).status_code == 404

    # CANNOT (403, not 401 — they ARE logged in): everything else, including
    # other endpoints inside routers the cashier can partially reach.
    for path in (
        "/api/passes",                 # the LIST — issuing is fine, browsing is not
        "/api/lot-check?q=7834",
        "/api/reminders",
        "/api/monthly-customers",
        "/api/companies",
        "/api/dashboard/stats",
        "/api/payments",
        "/api/reports/summary",
        "/api/insights/morning-report",
        "/api/audit-log",
        "/api/search?q=x",
    ):
        assert _get(client, path, cashier).status_code == 403, path

    # CANNOT: renew, cancel, clear a spot's overstay — manager actions that live
    # in routers the cashier CAN otherwise reach.
    assert client.post(
        f"/api/passes/{pass_id}/renew", json={"end_date": today, "payment_method": "cash"}, headers=H
    ).status_code == 403
    assert client.post(f"/api/passes/{pass_id}/cancel", headers=H).status_code == 403
    assert client.post("/api/spots/1/clear-overstay", headers=H).status_code == 403

    # The public monthly-rate lookup the issue form uses must still work for them.
    assert _get(client, "/api/companies/lookup?name=Gate%20Co", cashier).status_code == 200


def test_manager_does_everything_but_the_owners_domain(client):
    admin = _admin_token(client)
    manager = _staff_token(client, admin, "manager", "shift@madcotruckplaza.com")

    # The cashier's job PLUS the desk work the cashier was fenced out of.
    for path in (
        "/api/passes",
        "/api/lot-check?q=7834",
        "/api/reminders",
        "/api/monthly-customers",
        "/api/companies",
        "/api/spots",
        "/api/dashboard/stats",
        "/api/reports/summary",
        "/api/insights/morning-report",
        "/api/payments",
        "/api/search?q=x",
    ):
        assert _get(client, path, manager).status_code == 200, path

    # The owner's domain: still forbidden.
    assert _get(client, "/api/audit-log", manager).status_code == 403
    assert _get(client, "/api/auth/users", manager).status_code == 403


def test_admin_sees_everything(client):
    admin = _admin_token(client)
    for path in ("/api/dashboard/stats", "/api/payments", "/api/audit-log", "/api/auth/users", "/api/spots"):
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

    assert client.post("/api/auth/login", json={"email": "shift2@madcotruckplaza.com", "password": "staffpass123"}).status_code == 401
    assert client.post("/api/auth/login", json={"email": "shift2@madcotruckplaza.com", "password": "newpass12345"}).status_code == 200
