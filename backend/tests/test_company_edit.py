"""Editing a company after the fact — the fix for a cashier who issued a pass
with the company name left blank. Renaming the company corrects it everywhere,
since passes link to the company by id. Manager-only."""


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


def _blank_company(client, admin) -> int:
    # Simulate the bug: a company created with a blank name.
    r = client.post("/api/companies", json={"name": "   "}, headers={"Authorization": f"Bearer {admin}"})
    assert r.status_code == 200, r.text
    return r.json()["id"]


def test_manager_renames_a_blank_company(client):
    admin = _admin_token(client)
    H = {"Authorization": f"Bearer {admin}"}
    cid = _blank_company(client, admin)

    r = client.patch(f"/api/companies/{cid}", json={"name": "  ABC   Logistics ", "phone": "555-1212"}, headers=H)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["name"] == "ABC Logistics"  # whitespace collapsed
    assert body["phone"] == "555-1212"
    # persisted
    assert client.get(f"/api/companies/{cid}", headers=H).json()["name"] == "ABC Logistics"


def test_blank_name_is_rejected(client):
    admin = _admin_token(client)
    H = {"Authorization": f"Bearer {admin}"}
    cid = _blank_company(client, admin)
    assert client.patch(f"/api/companies/{cid}", json={"name": "   "}, headers=H).status_code == 400


def test_missing_company_is_404(client):
    admin = _admin_token(client)
    H = {"Authorization": f"Bearer {admin}"}
    assert client.patch("/api/companies/999999", json={"name": "X"}, headers=H).status_code == 404


def test_attendant_cannot_edit_a_company(client):
    admin = _admin_token(client)
    cid = _blank_company(client, admin)
    cashier = _staff_token(client, admin, "attendant", "c@x.com")
    r = client.patch(f"/api/companies/{cid}", json={"name": "Nope"}, headers={"Authorization": f"Bearer {cashier}"})
    assert r.status_code == 403
