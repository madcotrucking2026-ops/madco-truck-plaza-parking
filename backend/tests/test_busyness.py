"""The Dashboard busyness view: how busy the lot is by day of week and hour of
day. The owner's real question is "what days / what times", not revenue."""
from datetime import timedelta

from app.core.clock import business_today


def _admin(client) -> dict:
    r = client.post("/api/auth/register", json={"name": "O", "email": "o@x.com", "password": "ownerpass123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _issue(client, H, issue_date, truck):
    return client.post(
        "/api/passes",
        json={
            "company_name": "Busy Co", "truck_number": truck, "phone": "313-555-0199",
            "vehicle_type": "truck", "pass_type": "daily",
            "issue_date": issue_date.isoformat(),
            "end_date": (issue_date + timedelta(days=5)).isoformat(),
            "price": 20, "payment_method": "cash",
        },
        headers=H,
    )


def test_busyness_empty_when_no_passes(client):
    H = _admin(client)
    r = client.get("/api/reports/busyness", headers=H)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] == 0
    assert len(body["by_weekday"]) == 7
    assert len(body["by_hour"]) == 24


def test_busyness_counts_and_peaks_by_weekday(client):
    H = _admin(client)
    today = business_today()
    friday = today - timedelta(days=(today.weekday() - 4) % 7)  # most recent Friday
    monday = today - timedelta(days=(today.weekday() - 0) % 7)  # most recent Monday
    for i in range(3):
        assert _issue(client, H, friday, f"F{i}").status_code < 300
    assert _issue(client, H, monday, "M0").status_code < 300

    body = client.get("/api/reports/busyness", headers=H).json()
    assert body["total"] == 4
    by = {b["label"]: b["value"] for b in body["by_weekday"]}
    assert by["Fri"] == 3
    assert by["Mon"] == 1
    # Every counted pass lands in exactly one hour bucket too.
    assert sum(b["value"] for b in body["by_hour"]) == 4


def test_busyness_excludes_cancelled(client):
    H = _admin(client)
    today = business_today()
    friday = today - timedelta(days=(today.weekday() - 4) % 7)
    pid = _issue(client, H, friday, "C0").json()["id"]
    assert client.post(f"/api/passes/{pid}/cancel", json={}, headers=H).status_code == 200
    body = client.get("/api/reports/busyness", headers=H).json()
    assert body["total"] == 0
