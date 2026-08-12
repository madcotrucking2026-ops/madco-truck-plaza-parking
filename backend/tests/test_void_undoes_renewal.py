"""Voiding a RENEWAL payment undoes the renewal — the pass rolls back to the
state that payment recorded (its pre-renewal dates + price). Voiding the money
alone isn't enough: a mistaken renewal must revert the dates too."""
from app.core.clock import business_today
from app.core.dates import add_months


def _admin(client) -> dict:
    r = client.post("/api/auth/register", json={"name": "O", "email": "o@x.com", "password": "ownerpass123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_voiding_a_renewal_rolls_the_pass_back(client):
    H = _admin(client)
    today = business_today()
    end = add_months(today, 1)          # original month: today -> +1mo
    new_end = add_months(end, 1)        # renewed to +2mo

    issue = client.post(
        "/api/passes",
        json={
            "company_name": "Undo Co", "truck_number": "U1", "phone": "313-555-0100",
            "vehicle_type": "truck", "pass_type": "monthly",
            "issue_date": today.isoformat(), "end_date": end.isoformat(),
            "price": 150, "payment_method": "cash",
        },
        headers=H,
    )
    assert issue.status_code == 200, issue.text
    pid = issue.json()["id"]

    # Renew — rolls to the current period (end -> new_end).
    r = client.post(
        f"/api/passes/{pid}/renew",
        json={"end_date": new_end.isoformat(), "payment_method": "cash"},
        headers=H,
    )
    assert r.status_code == 200, r.text
    assert r.json()["issue_date"] == end.isoformat()
    assert r.json()["expiration_date"] == new_end.isoformat()

    # The renewal payment = the newest positive payment for this truck.
    pays = [p for p in client.get("/api/payments", headers=H).json() if p["truck_number"] == "U1"]
    renewal = max((p for p in pays if p["amount"] > 0), key=lambda p: p["id"])

    # Void it — the pass rolls back to BEFORE the renewal.
    v = client.post(f"/api/payments/{renewal['id']}/void", headers=H)
    assert v.status_code == 200, v.text

    after = client.get(f"/api/passes/{pid}", headers=H).json()
    assert after["issue_date"] == today.isoformat()        # back to the original start
    assert after["expiration_date"] == end.isoformat()     # back to the original end
    assert after["price"] == 150.0
