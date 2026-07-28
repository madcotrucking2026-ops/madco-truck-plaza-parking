"""ensure_spots(): the painted lot exists in the database, sized by config."""
from sqlalchemy import func, select

from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.core.spots import ensure_spots
from app.models import Spot
from app.models.enums import PassStatus, PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment


def test_seeds_capacity_spots_once(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 300)
    ensure_spots(db)
    ensure_spots(db)  # idempotent — second run adds nothing
    assert db.scalar(select(func.count()).select_from(Spot)) == 300
    assert db.scalar(select(func.min(Spot.number))) == 1
    assert db.scalar(select(func.max(Spot.number))) == 300


def test_capacity_shrink_deactivates_never_deletes(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 300)
    ensure_spots(db)
    monkeypatch.setattr(settings, "parking_capacity", 280)
    ensure_spots(db)
    assert db.scalar(select(func.count()).select_from(Spot)) == 300  # history kept
    assert db.scalar(select(func.count()).select_from(Spot).where(Spot.active)) == 280


def test_capacity_grow_reactivates_and_extends(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 10)
    ensure_spots(db)
    monkeypatch.setattr(settings, "parking_capacity", 12)
    ensure_spots(db)
    assert db.scalar(select(func.count()).select_from(Spot).where(Spot.active)) == 12


def test_startup_backfills_spots_for_live_legacy_passes(db, monkeypatch):
    """A deployment that predates spots has live passes with spot_id NULL — the
    grid would show a green empty lot while trucks sit on it. Startup assigns
    them spots once; afterwards a NULL spot is a genuine anomaly (full-lot race)."""
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    live = _issue_pass_and_payment(
        db, company_name="Legacy Freight", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number="LEG1", trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=business_today(), end_date=business_today() + timedelta(days=2),
        price_override=None, payment_method=PaymentMethod.cash, check_number=None,
    )
    expired = _issue_pass_and_payment(
        db, company_name="Old News Freight", phone="313-555-0101", vehicle_type=VehicleType.truck,
        truck_number="OLD1", trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=business_today() - timedelta(days=9), end_date=business_today() - timedelta(days=8),
        price_override=None, payment_method=PaymentMethod.cash, check_number=None,
    )
    live.spot_id = None      # simulate pre-spot-era rows
    expired.spot_id = None
    db.commit()

    ensure_spots(db)

    db.expire_all()
    assert live.spot_id is not None, "live legacy pass must be given a spot"
    assert expired.spot_id is None, "expired history stays untouched"


def test_backfill_gives_each_stray_its_OWN_spot(db, monkeypatch):
    """Regression: the session is autoflush=False, so the picker's not-in-held
    subquery couldn't see assignments made earlier in the same backfill loop —
    every legacy pass landed on the SAME spot (found live: 10 passes on spot 1)."""
    monkeypatch.setattr(settings, "parking_capacity", 5)
    ensure_spots(db)
    strays = []
    for i in range(3):
        parking_pass = _issue_pass_and_payment(
            db, company_name=f"Stray {i}", phone="313-555-0100", vehicle_type=VehicleType.truck,
            truck_number=f"STR{i}", trailer_number=None, license_plate=None, pass_type=PassType.daily,
            issue_date=business_today(), end_date=business_today() + timedelta(days=2),
            price_override=None, payment_method=PaymentMethod.cash, check_number=None,
        )
        parking_pass.spot_id = None
        strays.append(parking_pass)
    db.commit()

    ensure_spots(db)

    db.expire_all()
    assigned = [p.spot_id for p in strays]
    assert None not in assigned
    assert len(set(assigned)) == 3, f"each stray needs its OWN spot, got {assigned}"
