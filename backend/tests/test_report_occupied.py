"""Customer finds a squatter in their assigned spot: one tap moves them and
flags the spot for staff. Public, HMAC-token-authed — works at 3am."""
from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.core.pass_token import make_pass_token
from app.core.spots import ensure_spots
from app.models import Spot
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment


def _issue(db, truck):
    return _issue_pass_and_payment(
        db, company_name=f"Co {truck}", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number=truck, trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=business_today(), end_date=business_today() + timedelta(days=1),
        price_override=None, payment_method=PaymentMethod.cash, check_number=None,
    )


def test_reassigns_and_flags_old_spot(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 3)
    ensure_spots(db)
    p = _issue(db, "T1")
    db.commit()
    old_spot_id = p.spot_id

    r = client.post(f"/api/verify/{make_pass_token(p.id)}/report-occupied")
    assert r.status_code == 200

    db.expire_all()
    assert p.spot_id != old_spot_id
    old = db.get(Spot, old_spot_id)
    assert old.overstay_reported is True
    assert old.last_vacated_at is not None  # back of the assignment queue
    assert r.json()["spot_number"] == p.spot.number


def test_full_lot_says_see_the_desk(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 1)
    ensure_spots(db)
    p = _issue(db, "T1")
    db.commit()
    r = client.post(f"/api/verify/{make_pass_token(p.id)}/report-occupied")
    assert r.status_code == 409


def test_forged_token_is_404(db, client):
    assert client.post("/api/verify/not-a-token/report-occupied").status_code == 404


def test_verify_page_shows_the_spot(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 3)
    ensure_spots(db)
    p = _issue(db, "T1")
    db.commit()
    r = client.get(f"/api/verify/{make_pass_token(p.id)}")
    assert r.json()["spot_number"] == p.spot.number
