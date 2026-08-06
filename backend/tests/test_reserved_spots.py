"""Reserved monthly spots (lot-organization Task 2).

A monthly pass is per-truck (vehicle) and OWNS a fixed spot: it is auto-assigned
the lowest free spot in the monthly area, reserved to that truck, and held even
while the truck is out on a run. Daily/weekly are pooled in the daily area and
can NEVER land on a reserved spot — empty or not. Monthly overflows into the
daily area when the monthly zone is full, reserving there too.
"""
from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.core.spots import (
    MoveError,
    ensure_spots,
    free_spot_count,
    monthly_spot_limit,
    move_pass_to_spot,
)
from app.models import Spot
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment

import pytest


def _issue(db, truck, company=None, ptype=PassType.daily, days=1, price=None):
    return _issue_pass_and_payment(
        db, company_name=company or f"Co {truck}", phone="313-555-0100",
        vehicle_type=VehicleType.truck, truck_number=truck, trailer_number=None,
        license_plate=None, pass_type=ptype, issue_date=business_today(),
        end_date=business_today() + timedelta(days=days), price_override=price,
        payment_method=PaymentMethod.cash, check_number=None,
    )


def _zoned(monkeypatch, *, per_zone, monthly_zones, capacity):
    """Split the lot: `monthly_zones` leading zones of `per_zone` spots are the
    monthly (reserved) area, the rest is the daily pool."""
    monkeypatch.setattr(settings, "spots_per_zone", per_zone)
    monkeypatch.setattr(settings, "monthly_zone_count", monthly_zones)
    monkeypatch.setattr(settings, "parking_capacity", capacity)


def _spot_of(db, parking_pass) -> Spot:
    return db.get(Spot, parking_pass.spot_id)


def test_monthly_auto_assigns_lowest_free_monthly_spot_and_reserves_it(db, monkeypatch):
    _zoned(monkeypatch, per_zone=5, monthly_zones=1, capacity=10)  # monthly 1..5, daily 6..10
    ensure_spots(db)
    p = _issue(db, "M1", ptype=PassType.monthly, days=30, price=250)
    db.commit()
    assert p.spot is not None
    assert p.spot.number == 1  # lowest free monthly spot
    assert p.spot.reserved_vehicle_id == p.vehicle_id  # reserved to that truck


def test_second_monthly_truck_gets_the_next_spot(db, monkeypatch):
    _zoned(monkeypatch, per_zone=5, monthly_zones=1, capacity=10)
    ensure_spots(db)
    a = _issue(db, "M1", ptype=PassType.monthly, days=30, price=250)
    b = _issue(db, "M2", ptype=PassType.monthly, days=30, price=250)
    db.commit()
    assert a.spot.number == 1
    assert b.spot.number == 2
    assert a.spot.reserved_vehicle_id == a.vehicle_id
    assert b.spot.reserved_vehicle_id == b.vehicle_id


def test_reissue_reuses_the_same_reserved_spot_even_after_lapse(db, monkeypatch):
    """Renewals never move: a lapsed monthly who comes back gets THEIR spot, and
    the reservation holds through the lapse (released only on close-out, Task 3)."""
    _zoned(monkeypatch, per_zone=5, monthly_zones=1, capacity=10)
    ensure_spots(db)
    first = _issue(db, "M1", company="Sticky Freight", ptype=PassType.monthly, days=30, price=250)
    db.commit()
    reserved = first.spot_id
    # Lapse well past grace — the reservation, not a live pass, holds the spot.
    first.expiration_date = business_today() - timedelta(days=30)
    db.commit()
    again = _issue(db, "M1", company="Sticky Freight", ptype=PassType.monthly, days=30, price=250)
    db.commit()
    assert again.spot_id == reserved
    assert _spot_of(db, again).number == 1


def test_daily_never_lands_on_a_reserved_spot(db, monkeypatch):
    """Reserve spot 1 to a monthly truck that is OUT (no live pass). A daily pass
    must skip it and take a daily-area spot, and free_spot_count must not count
    the reserved-empty spot."""
    _zoned(monkeypatch, per_zone=5, monthly_zones=1, capacity=10)  # monthly 1..5, daily 6..10
    ensure_spots(db)
    m = _issue(db, "M1", ptype=PassType.monthly, days=30, price=250)
    db.commit()
    assert m.spot.number == 1 and m.spot.reserved_vehicle_id == m.vehicle_id
    # Truck leaves and the pass lapses: only the reservation still holds the spot.
    m.expiration_date = business_today() - timedelta(days=30)
    db.commit()

    # 10 spots, spot 1 reserved-empty -> 9 sellable (the reservation excludes it).
    assert free_spot_count(db) == 9

    d = _issue(db, "D1", ptype=PassType.daily, days=1)
    db.commit()
    assert d.spot is not None
    assert d.spot.number != 1
    assert d.spot.number > monthly_spot_limit()  # daily area only


def test_monthly_overflows_into_the_daily_area_when_its_zone_is_full(db, monkeypatch):
    _zoned(monkeypatch, per_zone=2, monthly_zones=1, capacity=5)  # monthly 1..2, daily 3..5
    ensure_spots(db)
    a = _issue(db, "M1", ptype=PassType.monthly, days=30, price=250)
    b = _issue(db, "M2", ptype=PassType.monthly, days=30, price=250)
    db.commit()
    assert a.spot.number == 1 and b.spot.number == 2  # monthly zone now full
    c = _issue(db, "M3", ptype=PassType.monthly, days=30, price=250)
    db.commit()
    assert c.spot is not None
    assert c.spot.number == 3  # lowest free DAILY spot
    assert c.spot.number > monthly_spot_limit()
    assert c.spot.reserved_vehicle_id == c.vehicle_id  # overflow still reserves


def test_daily_and_weekly_only_pick_daily_area_spots(db, monkeypatch):
    _zoned(monkeypatch, per_zone=3, monthly_zones=1, capacity=6)  # monthly 1..3, daily 4..6
    ensure_spots(db)
    d = _issue(db, "D1", ptype=PassType.daily, days=1)
    w = _issue(db, "W1", ptype=PassType.weekly, days=7)
    db.commit()
    assert d.spot.number > monthly_spot_limit()
    assert w.spot.number > monthly_spot_limit()
    assert d.spot_id != w.spot_id


def test_move_onto_another_trucks_reserved_spot_is_rejected(db, monkeypatch):
    _zoned(monkeypatch, per_zone=5, monthly_zones=1, capacity=10)
    ensure_spots(db)
    m = _issue(db, "M1", ptype=PassType.monthly, days=30, price=250)  # reserves spot 1
    d = _issue(db, "D1", ptype=PassType.daily, days=1)                # daily-area spot
    db.commit()
    with pytest.raises(MoveError) as exc:
        move_pass_to_spot(db, d.id, m.spot.number)  # spot 1 belongs to M1
    assert exc.value.status == 400
    assert "reserved for another truck" in exc.value.detail


def test_monthly_move_carries_the_reservation_and_clears_the_old_spot(db, monkeypatch):
    _zoned(monkeypatch, per_zone=5, monthly_zones=1, capacity=10)
    ensure_spots(db)
    m = _issue(db, "M1", ptype=PassType.monthly, days=30, price=250)
    db.commit()
    old_spot_id = m.spot_id
    assert db.get(Spot, old_spot_id).number == 1
    target_number = 2  # a free spot the cashier moves them onto

    move_pass_to_spot(db, m.id, target_number)
    db.expire_all()

    moved = db.get(type(m), m.id)
    target = db.query(Spot).filter_by(number=target_number).one()
    assert moved.spot_id == target.id
    assert target.reserved_vehicle_id == moved.vehicle_id  # reservation followed
    assert db.get(Spot, old_spot_id).reserved_vehicle_id is None  # old spot released
