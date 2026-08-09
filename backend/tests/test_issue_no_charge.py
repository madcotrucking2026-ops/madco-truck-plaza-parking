"""Onboarding an already-paid customer must NOT inflate this month's revenue.
Issuing with record_payment=False registers the pass without a payment; a
backdated paid_on stamps a recorded payment on its real (past) day."""
from datetime import timedelta

from app.core.clock import business_today


def _admin(client) -> dict:
    r = client.post("/api/auth/register", json={"name": "Owner", "email": "o@x.com", "password": "ownerpass123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _todays_revenue(client, H) -> float:
    return client.get("/api/dashboard/stats", headers=H).json()["todays_revenue"]


def _issue(client, H, **over):
    body = {
        "company_name": "ACME",
        "phone": "5551212",
        "vehicle_type": "truck",
        "truck_number": "T1",
        "pass_type": "daily",
        "issue_date": business_today().isoformat(),
        "payment_method": "cash",
    }
    body.update(over)
    return client.post("/api/passes", json=body, headers=H)


def test_no_charge_issue_registers_pass_but_no_revenue(client):
    H = _admin(client)
    r = _issue(client, H, record_payment=False)
    assert r.status_code == 200, r.text
    assert _todays_revenue(client, H) == 0.0
    assert len(client.get("/api/passes", headers=H).json()) == 1  # the pass IS registered


def test_normal_issue_records_revenue(client):
    H = _admin(client)
    r = _issue(client, H)
    assert r.status_code == 200, r.text
    assert _todays_revenue(client, H) == r.json()["price"]


def test_backdated_payment_stays_out_of_todays_revenue(client):
    H = _admin(client)
    yesterday = (business_today() - timedelta(days=1)).isoformat()
    r = _issue(client, H, paid_on=yesterday)
    assert r.status_code == 200, r.text
    assert _todays_revenue(client, H) == 0.0  # recorded, but dated yesterday


def test_future_payment_date_is_rejected(client):
    H = _admin(client)
    future = (business_today() + timedelta(days=1)).isoformat()
    assert _issue(client, H, paid_on=future).status_code == 400
