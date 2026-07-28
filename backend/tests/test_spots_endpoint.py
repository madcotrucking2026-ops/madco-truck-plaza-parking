"""One call paints the whole lot. States derived, matching the holding rules."""
from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.core.spots import ensure_spots
from app.models import Spot
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment


def _auth(client):
    r = client.post(
        "/api/auth/register",
        json={"name": "Owner", "email": "o@x.com", "password": "ownerpass123"},
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _issue(db, truck, ptype=PassType.daily, days=1, price=None):
    return _issue_pass_and_payment(
        db, company_name=f"Co {truck}", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number=truck, trailer_number=None, license_plate=None, pass_type=ptype,
        issue_date=business_today(), end_date=business_today() + timedelta(days=days),
        price_override=price, payment_method=PaymentMethod.cash, check_number=None,
    )


def test_states_cover_the_lot(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 4)
    monkeypatch.setattr(settings, "spot_grace_days", 3)
    ensure_spots(db)
    headers = _auth(client)

    occupied = _issue(db, "T1", days=5)  # comfortably live
    expiring = _issue(db, "T2", days=1)  # expires tomorrow
    monthly = _issue(db, "T3", ptype=PassType.monthly, days=30, price=250)
    db.commit()
    monthly.expiration_date = business_today() - timedelta(days=1)  # in grace
    db.commit()

    spots = {s["number"]: s for s in client.get("/api/spots", headers=headers).json()}
    assert spots[occupied.spot.number]["state"] == "occupied"
    assert spots[occupied.spot.number]["truck_number"] == "T1"
    assert spots[expiring.spot.number]["state"] == "expiring"
    assert spots[monthly.spot.number]["state"] == "grace"
    free = [s for s in spots.values() if s["state"] == "free"]
    assert len(free) == 1 and free[0]["company_name"] is None


def test_overstay_state_and_clear(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 2)
    ensure_spots(db)
    headers = _auth(client)
    spot = db.query(Spot).filter_by(number=1).one()
    spot.overstay_reported = True
    db.commit()

    spots = {s["number"]: s for s in client.get("/api/spots", headers=headers).json()}
    assert spots[1]["state"] == "overstay"

    assert client.post("/api/spots/1/clear-overstay", headers=headers).status_code == 200
    db.expire_all()
    assert spot.overstay_reported is False


def test_lot_state_needs_a_login(client):
    assert client.get("/api/spots").status_code == 401
