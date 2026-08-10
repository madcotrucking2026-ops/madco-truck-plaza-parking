"""Yearly pass: a 12-month term at a custom flat annual price, with a reserved
spot in the monthly zone (released on cancel/close-out like a monthly)."""
from app.core.clock import business_today
from app.core.config import settings
from app.core.dates import add_months
from app.core.spots import ensure_spots, monthly_spot_limit
from app.models import Spot
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment, cancel_pass


def _issue_yearly(db, truck, price):
    return _issue_pass_and_payment(
        db, company_name=f"Yr {truck}", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number=truck, trailer_number=None, license_plate=None, pass_type=PassType.yearly,
        issue_date=business_today(), end_date=None,
        price_override=price, payment_method=PaymentMethod.cash, check_number=None,
    )


def test_yearly_custom_price_and_12_month_term(db):
    p = _issue_yearly(db, "Y1", 1800)
    db.commit()
    assert float(p.price) == 1800.0
    assert p.expiration_date == add_months(business_today(), 12)


def test_yearly_defaults_to_config_price(db):
    p = _issue_yearly(db, "Y3", None)
    db.commit()
    assert float(p.price) == float(settings.yearly_price)


def test_yearly_gets_a_reserved_monthly_zone_spot(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 3)
    monkeypatch.setattr(settings, "spots_per_zone", 25)
    monkeypatch.setattr(settings, "monthly_zone_count", 1)  # Zone A = spots 1..25
    ensure_spots(db)
    p = _issue_yearly(db, "Y2", 1800)
    db.commit()
    assert p.spot_id is not None
    spot = db.get(Spot, p.spot_id)
    assert spot.reserved_vehicle_id == p.vehicle_id
    assert spot.number <= monthly_spot_limit()  # in the monthly (reserved) zone


def test_cancel_frees_a_yearly_reserved_spot(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 3)
    ensure_spots(db)
    p = _issue_yearly(db, "Y4", 1800)
    db.commit()
    sid = p.spot_id
    cancel_pass(p.id, db=db)
    db.commit()
    assert db.get(Spot, sid).reserved_vehicle_id is None
