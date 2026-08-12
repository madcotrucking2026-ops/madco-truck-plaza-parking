"""Manager/owner corrects a pass's dates or price (audit-logged). The cashier
cannot — editing a pass is a money/records correction, not front-desk work."""
from datetime import timedelta

from app.core.clock import business_today
from app.core.dates import add_months


def _admin(client) -> dict:
    r = client.post("/api/auth/register", json={"name": "O", "email": "o@x.com", "password": "ownerpass123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _cashier(client, admin) -> dict:
    client.post(
        "/api/auth/users",
        json={"name": "gate", "email": "g@x.com", "password": "staffpass123", "role": "attendant"},
        headers=admin,
    )
    tok = client.post("/api/auth/login", json={"email": "g@x.com", "password": "staffpass123"}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def _issue_monthly(client, H, start, end):
    return client.post(
        "/api/passes",
        json={
            "company_name": "Edit Co", "truck_number": "E1", "phone": "313-555-0100",
            "vehicle_type": "truck", "pass_type": "monthly",
            "issue_date": start.isoformat(), "end_date": end.isoformat(),
            "price": 150, "payment_method": "cash",
        },
        headers=H,
    )


def test_manager_edits_dates_and_price(client):
    H = _admin(client)
    today = business_today()
    pid = _issue_monthly(client, H, today, add_months(today, 1)).json()["id"]
    new_end = add_months(today, 2)
    r = client.patch(f"/api/passes/{pid}", json={"end_date": new_end.isoformat(), "price": 300}, headers=H)
    assert r.status_code == 200, r.text
    assert r.json()["expiration_date"] == new_end.isoformat()
    assert r.json()["price"] == 300.0


def test_edit_rejects_expiration_before_issue(client):
    H = _admin(client)
    today = business_today()
    pid = _issue_monthly(client, H, today, add_months(today, 1)).json()["id"]
    r = client.patch(f"/api/passes/{pid}", json={"end_date": (today - timedelta(days=5)).isoformat()}, headers=H)
    assert r.status_code == 400


def test_cashier_cannot_edit(client):
    admin = _admin(client)
    today = business_today()
    pid = _issue_monthly(client, admin, today, add_months(today, 1)).json()["id"]
    cashier = _cashier(client, admin)
    r = client.patch(f"/api/passes/{pid}", json={"price": 999}, headers=cashier)
    assert r.status_code == 403
