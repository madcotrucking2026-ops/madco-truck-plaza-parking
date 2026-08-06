"""Pool rules the 110-customer swarm exposed as missing.

1. An overstay-flagged spot has a REPORTED SQUATTER on it — selling it to the
   next arrival sends them straight into the same blocked spot the last customer
   just escaped. Flagged spots leave the pool until staff clear them.
2. After locking a candidate, the picker re-verifies it against a FRESH
   statement. On Postgres, a concurrent transaction whose snapshot predates a
   just-committed assignment can lock the released row and resell it (the
   assignment never writes the spot row, so the engine's row-recheck sees no
   change). The re-verify closes that window; under SQLite it is simply a
   cheap second read. Found live: spots 51/54/110/119 each sold twice.
"""
from datetime import timedelta

from app.core.clock import business_now, business_today
from app.core.config import settings
from app.core.spots import ensure_spots, free_spot_count, pick_free_spot
from app.models import Spot
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment


def test_overstay_flagged_spot_is_not_sellable(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 2)
    ensure_spots(db)
    flagged = db.query(Spot).filter_by(number=1).one()
    flagged.overstay_reported = True
    flagged.overstay_reported_at = business_now()
    db.commit()

    assert free_spot_count(db) == 1
    assert pick_free_spot(db, PassType.daily, None).number == 2
    # Even as an explicit monthly preference — a squatter is a squatter.
    assert pick_free_spot(db, PassType.daily, None, prefer_spot_id=flagged.id).number == 2


def test_clearing_the_flag_returns_the_spot_to_the_pool(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 1)
    ensure_spots(db)
    spot = db.query(Spot).filter_by(number=1).one()
    spot.overstay_reported = True
    db.commit()
    assert free_spot_count(db) == 0

    spot.overstay_reported = False
    db.commit()
    assert free_spot_count(db) == 1


def test_flagged_spots_never_assigned_at_issue(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 2)
    ensure_spots(db)
    db.query(Spot).filter_by(number=1).one().overstay_reported = True
    db.commit()

    p = _issue_pass_and_payment(
        db, company_name="Clean Co", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number="C1", trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=business_today(), end_date=business_today() + timedelta(days=1),
        price_override=None, payment_method=PaymentMethod.cash, check_number=None,
    )
    db.commit()
    assert p.spot.number == 2
