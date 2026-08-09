"""Voiding a mistaken payment. Nothing is deleted — a negative reversal entry is
recorded, so revenue nets to zero while both rows stay on the books. This is the
cure for a cashier error (wrong/blank company, double entry), NOT a real
no-refund cancellation where the money is genuinely earned."""


def _admin_token(client) -> str:
    r = client.post("/api/auth/register", json={"name": "Owner", "email": "o@x.com", "password": "ownerpass123"})
    return r.json()["access_token"]


def _staff_token(client, admin, role, email) -> str:
    client.post(
        "/api/auth/users",
        json={"name": f"{role} u", "email": email, "password": "staffpass123", "role": role},
        headers={"Authorization": f"Bearer {admin}"},
    )
    return client.post("/api/auth/login", json={"email": email, "password": "staffpass123"}).json()["access_token"]


def _record_payment(client, H, amount=200.0) -> int:
    r = client.post("/api/payments", json={"amount": amount, "method": "cash"}, headers=H)
    assert r.status_code == 200, r.text
    return r.json()["id"]


def _todays_revenue(client, H) -> float:
    return client.get("/api/dashboard/stats", headers=H).json()["todays_revenue"]


def test_void_records_a_reversal_and_nets_revenue_to_zero(client):
    admin = _admin_token(client)
    H = {"Authorization": f"Bearer {admin}"}
    pid = _record_payment(client, H, 200)
    assert _todays_revenue(client, H) == 200.0

    r = client.post(f"/api/payments/{pid}/void", headers=H)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["amount"] == -200.0
    assert body["reversal_of_payment_id"] == pid
    # Both rows remain, and revenue nets to zero.
    assert _todays_revenue(client, H) == 0.0


def test_a_payment_cannot_be_voided_twice(client):
    admin = _admin_token(client)
    H = {"Authorization": f"Bearer {admin}"}
    pid = _record_payment(client, H, 150)
    assert client.post(f"/api/payments/{pid}/void", headers=H).status_code == 200
    assert client.post(f"/api/payments/{pid}/void", headers=H).status_code == 400


def test_a_negative_reversal_cannot_itself_be_voided(client):
    admin = _admin_token(client)
    H = {"Authorization": f"Bearer {admin}"}
    pid = _record_payment(client, H, 100)
    reversal_id = client.post(f"/api/payments/{pid}/void", headers=H).json()["id"]
    assert client.post(f"/api/payments/{reversal_id}/void", headers=H).status_code == 400


def test_void_missing_payment_is_404(client):
    admin = _admin_token(client)
    H = {"Authorization": f"Bearer {admin}"}
    assert client.post("/api/payments/999999/void", headers=H).status_code == 404


def test_attendant_cannot_void(client):
    admin = _admin_token(client)
    H = {"Authorization": f"Bearer {admin}"}
    pid = _record_payment(client, H, 200)
    cashier = _staff_token(client, admin, "attendant", "c@x.com")
    r = client.post(f"/api/payments/{pid}/void", headers={"Authorization": f"Bearer {cashier}"})
    assert r.status_code == 403
