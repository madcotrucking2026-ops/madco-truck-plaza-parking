"""Assignment is part of issuing a pass — same transaction, no separate step."""
from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.core.spots import ensure_spots
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment, apply_renewal


def _issue(db, truck, company=None, ptype=PassType.daily, days=1, price=None):
    return _issue_pass_and_payment(
        db, company_name=company or f"Co {truck}", phone="313-555-0100",
        vehicle_type=VehicleType.truck, truck_number=truck, trailer_number=None,
        license_plate=None, pass_type=ptype, issue_date=business_today(),
        end_date=business_today() + timedelta(days=days), price_override=price,
        payment_method=PaymentMethod.cash, check_number=None,
    )


def test_issue_assigns_a_spot(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    p = _issue(db, "T1")
    db.commit()
    assert p.spot is not None and 1 <= p.spot.number <= 5


def test_two_passes_two_spots(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    a = _issue(db, "T1")
    b = _issue(db, "T2")
    db.commit()
    assert a.spot_id != b.spot_id


def test_renewal_keeps_the_spot(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    p = _issue(db, "T1")
    db.commit()
    before = p.spot_id
    apply_renewal(db, p, business_today() + timedelta(days=3), PaymentMethod.cash)
    db.commit()
    assert p.spot_id == before


def test_returning_monthly_gets_their_old_spot(db, monkeypatch):
    """Sticky: a lapsed monthly who comes back gets the number they always had."""
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    old = _issue(db, "M1", company="Sticky Freight", ptype=PassType.monthly, days=30, price=250)
    db.commit()
    old_spot = old.spot_id
    old.expiration_date = business_today() - timedelta(days=10)  # lapsed past grace
    db.commit()
    new = _issue(db, "M1", company="Sticky Freight", ptype=PassType.monthly, days=30, price=250)
    db.commit()
    assert new.spot_id == old_spot


def test_full_lot_issues_pass_with_no_spot(db, monkeypatch):
    """Money already taken must NEVER fail for lack of a spot — pass issues with
    spot_id NULL and staff resolve it from the dashboard."""
    monkeypatch.setattr(settings, "parking_capacity", 1)
    ensure_spots(db)
    _issue(db, "T1")
    db.commit()
    p2 = _issue(db, "T2")
    db.commit()
    assert p2.spot_id is None
    assert p2.receipt_number  # the pass itself is fully valid
