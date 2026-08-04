"""Cashier override: move a truck to a FREE spot. Race-safe, audited, login-gated."""
from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.core.spots import ensure_spots
from app.models import Spot
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment


def _auth(client):
    client.post("/api/auth/register", json={"name": "O", "email": "o@x.com", "password": "ownerpass123"})
    t = client.post("/api/auth/login", json={"email": "o@x.com", "password": "ownerpass123"}).json()["access_token"]
    return {"Authorization": f"Bearer {t}"}


def _issue(db, truck):
    return _issue_pass_and_payment(
        db, company_name=f"Co {truck}", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number=truck, trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=business_today(), end_date=business_today() + timedelta(days=1),
        price_override=None, payment_method=PaymentMethod.cash, check_number=None)


def test_move_to_free_spot_repoints_and_frees_old(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 10)
    ensure_spots(db)
    H = _auth(client)
    p = _issue(db, "T1")
    db.commit()
    old = p.spot_id
    target = db.query(Spot).filter(Spot.id != old).first().number
    r = client.post("/api/spots/move", json={"pass_id": p.id, "to_number": target}, headers=H)
    assert r.status_code == 200, r.text
    assert r.json()["spot_number"] == target
    db.expire_all()
    assert p.spot.number == target
    assert db.get(Spot, old).last_vacated_at is not None


def test_move_onto_occupied_spot_is_rejected(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 10)
    ensure_spots(db)
    H = _auth(client)
    a = _issue(db, "A")
    b = _issue(db, "B")
    db.commit()
    r = client.post("/api/spots/move", json={"pass_id": a.id, "to_number": b.spot.number}, headers=H)
    assert r.status_code in (400, 409)


def test_move_to_same_spot_is_rejected(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    H = _auth(client)
    p = _issue(db, "T1")
    db.commit()
    r = client.post("/api/spots/move", json={"pass_id": p.id, "to_number": p.spot.number}, headers=H)
    assert r.status_code == 400


def test_move_needs_login(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    p = _issue(db, "T1")
    db.commit()
    assert client.post("/api/spots/move", json={"pass_id": p.id, "to_number": 3}).status_code == 401


def test_move_to_bad_spot_or_pass_404(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    H = _auth(client)
    p = _issue(db, "T1")
    db.commit()
    assert client.post("/api/spots/move", json={"pass_id": 99999, "to_number": 2}, headers=H).status_code == 404
    assert client.post("/api/spots/move", json={"pass_id": p.id, "to_number": 9999}, headers=H).status_code == 404
