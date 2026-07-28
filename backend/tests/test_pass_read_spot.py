"""The spot number rides on every pass payload — ticket, list, verify."""
from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.core.spots import ensure_spots
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment
from app.schemas.pass_ import PassRead


def test_pass_read_carries_spot_number(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    p = _issue_pass_and_payment(
        db, company_name="Co", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number="T1", trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=business_today(), end_date=business_today() + timedelta(days=1),
        price_override=None, payment_method=PaymentMethod.cash, check_number=None,
    )
    db.commit()
    assert PassRead.model_validate(p).spot_number == p.spot.number
