"""The revenue/passes trend line — bucketed by day/week/month/year."""
from app.core.clock import business_today


def _admin(client) -> dict:
    r = client.post("/api/auth/register", json={"name": "O", "email": "o@x.com", "password": "ownerpass123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _issue_daily(client, H):
    return client.post(
        "/api/passes",
        json={
            "company_name": "Trend Co", "truck_number": "TR1", "phone": "313-555-0100",
            "vehicle_type": "truck", "pass_type": "daily",
            "issue_date": business_today().isoformat(), "payment_method": "cash",
        },
        headers=H,
    )


def test_bucket_point_counts(client):
    H = _admin(client)
    for bucket, n in (("day", 30), ("week", 12), ("month", 12), ("year", 5)):
        b = client.get(f"/api/reports/trend?bucket={bucket}&metric=revenue", headers=H).json()
        assert b["bucket"] == bucket
        assert len(b["points"]) == n


def test_today_revenue_and_passes_land_in_the_last_bucket(client):
    H = _admin(client)
    price = _issue_daily(client, H).json()["price"]
    rev = client.get("/api/reports/trend?bucket=day&metric=revenue", headers=H).json()
    assert rev["points"][-1]["value"] == price  # today's revenue is the newest point
    cnt = client.get("/api/reports/trend?bucket=day&metric=passes", headers=H).json()
    assert cnt["points"][-1]["value"] == 1


def test_invalid_params_fall_back_to_month_revenue(client):
    H = _admin(client)
    b = client.get("/api/reports/trend?bucket=nope&metric=huh", headers=H).json()
    assert b["bucket"] == "month" and b["metric"] == "revenue" and len(b["points"]) == 12
