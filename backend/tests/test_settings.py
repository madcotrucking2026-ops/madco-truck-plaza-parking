"""Owner-editable settings: capacity + default prices. Admin-only to change,
any staff can read (the issue form previews from the live prices), a saved change
persists + applies live, and a capacity change reshapes the painted lot."""
import pytest

from app.core.app_settings import EDITABLE
from app.core.config import settings


@pytest.fixture(autouse=True)
def _restore_settings():
    # The overrides mutate the global `settings` object — snapshot + restore so a
    # change here never leaks into another test.
    saved = {k: getattr(settings, k) for k in EDITABLE}
    yield
    for k, v in saved.items():
        setattr(settings, k, v)


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


def test_get_returns_effective_defaults(client):
    admin = _admin_token(client)
    r = client.get("/api/settings", headers={"Authorization": f"Bearer {admin}"})
    assert r.status_code == 200
    d = r.json()
    assert d == {"parking_capacity": 150, "daily_price": 20.0, "weekly_price": 100.0, "monthly_price": 250.0}


def test_admin_update_persists_and_applies_live(client):
    admin = _admin_token(client)
    H = {"Authorization": f"Bearer {admin}"}
    r = client.put(
        "/api/settings",
        json={"parking_capacity": 200, "daily_price": 25, "weekly_price": 120, "monthly_price": 275},
        headers=H,
    )
    assert r.status_code == 200, r.text
    assert r.json()["daily_price"] == 25.0
    # applied to the live config (so _price_for/ensure_spots see it)...
    assert settings.daily_price == 25.0 and settings.parking_capacity == 200
    # ...and persisted (a fresh GET still shows it)
    assert client.get("/api/settings", headers=H).json()["parking_capacity"] == 200


def test_capacity_change_reshapes_the_lot(client):
    admin = _admin_token(client)
    H = {"Authorization": f"Bearer {admin}"}
    client.put(
        "/api/settings",
        json={"parking_capacity": 12, "daily_price": 20, "weekly_price": 100, "monthly_price": 250},
        headers=H,
    )
    spots = client.get("/api/spots", headers=H).json()
    assert len([s for s in spots if s["state"] != "inactive"]) == 12  # lot repainted to 12


def test_only_admin_changes_settings_but_any_staff_can_read(client):
    admin = _admin_token(client)
    cashier = _staff_token(client, admin, "attendant", "c@x.com")
    manager = _staff_token(client, admin, "manager", "m@x.com")
    body = {"parking_capacity": 100, "daily_price": 20, "weekly_price": 100, "monthly_price": 250}
    assert client.put("/api/settings", json=body, headers={"Authorization": f"Bearer {cashier}"}).status_code == 403
    assert client.put("/api/settings", json=body, headers={"Authorization": f"Bearer {manager}"}).status_code == 403
    assert client.put("/api/settings", json=body, headers={"Authorization": f"Bearer {admin}"}).status_code == 200
    # the cashier CAN read (issue form needs the live prices)
    assert client.get("/api/settings", headers={"Authorization": f"Bearer {cashier}"}).status_code == 200
