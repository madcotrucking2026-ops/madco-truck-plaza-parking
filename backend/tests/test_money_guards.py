"""Money guards: a cashier double-submit never charges twice, and the standalone
payment endpoint (owner/manager only) bounds amounts while allowing owner refunds."""
from datetime import timedelta

from sqlalchemy import func, select

from app.core.clock import business_today
from app.core.config import settings
from app.core.spots import ensure_spots
from app.models import ParkingPass, Payment
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment


def _issue(db, truck="T1"):
    return _issue_pass_and_payment(
        db, company_name="Acme", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number=truck, trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=business_today(), end_date=business_today() + timedelta(days=1),
        price_override=None, payment_method=PaymentMethod.cash, check_number=None,
    )


def test_double_submit_returns_the_same_pass_and_charges_once(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    p1 = _issue(db)
    p2 = _issue(db)  # same truck, same day, moments later -> deduped, not a 2nd charge
    db.commit()
    assert p1.id == p2.id
    assert db.scalar(select(func.count()).select_from(ParkingPass)) == 1
    assert db.scalar(select(func.count()).select_from(Payment)) == 1


def test_different_trucks_are_not_deduped(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    a = _issue(db, "A1")
    b = _issue(db, "B2")
    db.commit()
    assert a.id != b.id
    assert db.scalar(select(func.count()).select_from(ParkingPass)) == 2


def _owner_headers(client):
    r = client.post("/api/auth/register", json={"name": "Owner", "email": "o@x.com", "password": "ownerpass123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_payment_amount_rejects_an_absurd_value(db, client):
    headers = _owner_headers(client)
    r = client.post("/api/payments", json={"amount": 5_000_000, "method": "cash"}, headers=headers)
    assert r.status_code == 422  # a fat-fingered extra zero can't swing revenue


def test_owner_can_record_a_negative_refund(db, client):
    headers = _owner_headers(client)
    r = client.post("/api/payments", json={"amount": -250, "method": "cash"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["amount"] == -250  # a refund the owner records
