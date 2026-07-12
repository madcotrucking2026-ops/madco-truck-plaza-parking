"""Dashboard occupancy: capacity, available spots, occupancy %."""

from datetime import date

from app.core.config import settings
from app.models.enums import PassStatus, PassType, PaymentMethod, VehicleType
from app.routers.dashboard import dashboard_stats
from app.routers.passes import _issue_pass_and_payment


def _issue_active(db, truck):
    return _issue_pass_and_payment(
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


def test_cancelled_pass_does_not_occupy_a_spot(db, monkeypatch):
    """A cancelled pass keeps its expiration_date, so counting purely on
    `expiration_date >= today` still treats it as a truck sitting on the lot —
    the lot looks fuller than it is and the manager turns away a paying truck."""
    monkeypatch.setattr(settings, "parking_capacity", 10)
    _issue_active(db, "A")
    cancelled = _issue_active(db, "B")
    cancelled.status = PassStatus.cancelled
    db.commit()

    stats = dashboard_stats(db)
    assert stats.occupied_spaces == 1
    assert stats.available_spaces == 9
    assert stats.active_daily_passes == 1
    assert stats.expiring_tomorrow == 1  # the cancelled one must not be chased either


def test_available_never_negative(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 2)
    for t in ("A", "B", "C", "D"):
        _issue_active(db, t)  # 4 occupied vs capacity 2
    db.commit()

    stats = dashboard_stats(db)
    assert stats.available_spaces == 0  # clamped, not negative
    assert stats.occupancy_pct == 200  # honest overflow signal
