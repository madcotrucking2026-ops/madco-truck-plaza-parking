"""Full-data backup: an admin downloads a ZIP of CSVs (one per record type);
every other role is refused. The point is a copy the owner keeps off-platform."""
import io
import zipfile


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


def test_admin_downloads_a_zip_of_csvs(client):
    admin = _admin_token(client)
    r = client.get("/api/export", headers={"Authorization": f"Bearer {admin}"})
    assert r.status_code == 200, r.text
    assert r.headers["content-type"] == "application/zip"
    assert "attachment" in r.headers["content-disposition"]

    archive = zipfile.ZipFile(io.BytesIO(r.content))
    names = set(archive.namelist())
    assert {
        "companies.csv",
        "vehicles.csv",
        "monthly_customers.csv",
        "parking_passes.csv",
        "payments.csv",
        "README.txt",
    } <= names
    # Even an empty table ships its header row, so a restore knows the columns.
    header = archive.read("companies.csv").decode().splitlines()[0]
    assert "id" in header.split(",")


def test_export_is_admin_only(client):
    admin = _admin_token(client)
    for role, email in (("attendant", "c@x.com"), ("manager", "m@x.com")):
        token = _staff_token(client, admin, role, email)
        r = client.get("/api/export", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 403, role
