"""A weekly pass can carry a custom per-week rate (some customers negotiate one),
and a pass can be issued with no vehicle identifier at all."""
from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment


def _issue_weekly(db, truck, price):
    return _issue_pass_and_payment(
        db, company_name=f"Wk {truck}", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number=truck, trailer_number=None, license_plate=None, pass_type=PassType.weekly,
        issue_date=business_today(), end_date=business_today() + timedelta(days=7),
        price_override=price, payment_method=PaymentMethod.cash, check_number=None,
    )


def test_weekly_custom_price_is_honored(db):
    p = _issue_weekly(db, "W1", 75)
    db.commit()
    assert float(p.price) == 75.0


def test_weekly_defaults_when_no_override(db):
    p = _issue_weekly(db, "W2", None)
    db.commit()
    assert float(p.price) == float(settings.weekly_price)


def test_pass_with_no_identifier_is_allowed(db):
    p = _issue_pass_and_payment(
        db, company_name="No ID Co", phone="313-555-0100", vehicle_type=VehicleType.car,
        truck_number=None, trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=business_today(), end_date=business_today() + timedelta(days=1),
        price_override=None, payment_method=PaymentMethod.cash, check_number=None,
    )
    db.commit()
    assert p.id is not None
