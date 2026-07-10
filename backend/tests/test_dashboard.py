"""Dashboard occupancy: capacity, available spots, occupancy %."""

from datetime import date

from app.core.config import settings
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.dashboard import dashboard_stats
from app.routers.passes import _issue_pass_and_payment


def _issue_active(db, truck):
    _issue_pass_and_payment(
        db, company_name="Lot Co", phone="555", vehicle_type=VehicleType.truck,
        truck_number=truck, trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=date.today(), end_date=None, price_override=None,
        payment_method=PaymentMethod.cash, check_number=None,
    )


def test_capacity_available_and_occupancy(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 10)
    for t in ("A", "B", "C"):
        _issue_active(db, t)  # daily, issued today -> occupies a spot
    db.commit()

    stats = dashboard_stats(db)
    assert stats.capacity == 10
    assert stats.occupied_spaces == 3
    assert stats.available_spaces == 7
    assert stats.occupancy_pct == 30


def test_available_never_negative(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 2)
    for t in ("A", "B", "C", "D"):
        _issue_active(db, t)  # 4 occupied vs capacity 2
    db.commit()

    stats = dashboard_stats(db)
    assert stats.available_spaces == 0  # clamped, not negative
    assert stats.occupancy_pct == 200  # honest overflow signal
