"""The two new desk payment-method labels are accepted end to end."""
import pytest


def _admin(client) -> str:
    r = client.post("/api/auth/register", json={"name": "Owner", "email": "o@x.com", "password": "ownerpass123"})
    return r.json()["access_token"]


@pytest.mark.parametrize("method", ["tender_card", "house_account"])
def test_new_methods_are_accepted(client, method):
    H = {"Authorization": f"Bearer {_admin(client)}"}
    r = client.post("/api/payments", json={"amount": 200, "method": method}, headers=H)
    assert r.status_code == 200, r.text
    assert r.json()["method"] == method
