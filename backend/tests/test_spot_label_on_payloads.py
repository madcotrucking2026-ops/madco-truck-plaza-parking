"""The zone label rides on every spot-bearing payload — pass, list, verify, lot state."""
from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.core.spots import ensure_spots
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment
from app.schemas.pass_ import PassRead


def test_pass_read_has_zone_label(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 150)
    monkeypatch.setattr(settings, "spots_per_zone", 25)
    ensure_spots(db)
    p = _issue_pass_and_payment(
        db, company_name="Co", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number="T1", trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=business_today(), end_date=business_today() + timedelta(days=1),
        price_override=None, payment_method=PaymentMethod.cash, check_number=None,
    )
    db.commit()
    out = PassRead.model_validate(p)
    assert out.spot_number is not None
    assert out.spot_label and out.spot_label[0] in "ABCDEF"


def test_spots_endpoint_labels_by_zone(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 150)
    monkeypatch.setattr(settings, "spots_per_zone", 25)
    ensure_spots(db)
    client.post("/api/auth/register", json={"name": "O", "email": "o@x.com", "password": "ownerpass123"})
    tok = client.post("/api/auth/login", json={"email": "o@x.com", "password": "ownerpass123"}).json()["access_token"]
    spots = client.get("/api/spots", headers={"Authorization": f"Bearer {tok}"}).json()
    by_num = {s["number"]: s for s in spots}
    assert by_num[1]["label"] == "A1"
    assert by_num[150]["label"] == "F25"
