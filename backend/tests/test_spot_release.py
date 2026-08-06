"""A monthly truck's reserved spot is released back to the pool ONLY on
close-out (the truck is leaving for good) — never by the pass merely expiring —
and existing monthlies are backfilled a reservation at startup (Task 3)."""
from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.core.spots import ensure_spots, free_spot_count, release_reserved_spot
from app.models import Spot
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment, apply_renewal


def _issue_monthly(db, truck):
    return _issue_pass_and_payment(
        db, company_name=f"Co {truck}", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number=truck, trailer_number=None, license_plate=None, pass_type=PassType.monthly,
        issue_date=business_today(), end_date=business_today() + timedelta(days=30),
        price_override=250, payment_method=PaymentMethod.cash, check_number=None,
    )


def test_release_helper_frees_the_reservation(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 2)
    ensure_spots(db)
    p = _issue_monthly(db, "M1")
    db.commit()
    assert p.spot.reserved_vehicle_id == p.vehicle_id  # reserved on issue
    release_reserved_spot(db, p.vehicle_id)
    db.commit()
    assert db.get(Spot, p.spot_id).reserved_vehicle_id is None  # back in the pool


def test_close_out_releases_the_reserved_spot(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 2)
    ensure_spots(db)
    p = _issue_monthly(db, "M1")
    db.commit()
    vid = p.vehicle_id
    assert db.get(Spot, p.spot_id).reserved_vehicle_id == vid
    # the truck is leaving for good — close out (any end date after the old end)
    apply_renewal(db, p, business_today() + timedelta(days=35), PaymentMethod.cash, mode="close_out")
    db.commit()
    assert db.get(Spot, p.spot_id).reserved_vehicle_id is None  # released to the pool


def test_continue_renewal_keeps_the_reservation(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 2)
    ensure_spots(db)
    p = _issue_monthly(db, "M1")
    db.commit()
    vid = p.vehicle_id
    # a continuing customer keeps their fixed spot — expiry/renewal never releases it
    apply_renewal(db, p, business_today() + timedelta(days=60), PaymentMethod.cash, mode="continue")
    db.commit()
    assert db.get(Spot, p.spot_id).reserved_vehicle_id == vid  # still theirs


def test_startup_backfill_reserves_existing_monthly_spot(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 2)
    ensure_spots(db)
    p = _issue_monthly(db, "M1")
    db.commit()
    vid = p.vehicle_id
    # simulate legacy data that predates the feature: a live monthly holding a
    # spot with no reservation stamped yet.
    db.get(Spot, p.spot_id).reserved_vehicle_id = None
    db.commit()
    ensure_spots(db)  # startup backfill
    assert db.get(Spot, p.spot_id).reserved_vehicle_id == vid  # reservation restored


def test_backfill_leaves_daily_spots_pooled(db, monkeypatch):
    """A daily pass holding a spot must NOT get a reservation from the backfill —
    only monthlies own their spot."""
    monkeypatch.setattr(settings, "parking_capacity", 2)
    ensure_spots(db)
    p = _issue_pass_and_payment(
        db, company_name="Daily Co", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number="D1", trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=business_today(), end_date=business_today() + timedelta(days=1),
        price_override=20, payment_method=PaymentMethod.cash, check_number=None,
    )
    db.commit()
    ensure_spots(db)
    assert db.get(Spot, p.spot_id).reserved_vehicle_id is None  # daily stays pooled
