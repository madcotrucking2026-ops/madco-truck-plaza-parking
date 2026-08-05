"""A spot is held while its pass is live: daily through expiry day, monthly
through expiry + grace, cancelled never. Assignment prefers longest-vacant."""
from datetime import timedelta

from app.core.clock import business_now, business_today
from app.core.config import settings
from app.core.spots import ensure_spots, free_spot_count, pick_free_spot
from app.models import Spot
from app.models.enums import PassStatus, PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment


def _issue(db, truck, ptype=PassType.daily, days=1, price=None):
    return _issue_pass_and_payment(
        db, company_name=f"Co {truck}", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number=truck, trailer_number=None, license_plate=None, pass_type=ptype,
        issue_date=business_today(), end_date=business_today() + timedelta(days=days),
        price_override=price, payment_method=PaymentMethod.cash, check_number=None,
    )


def test_live_pass_holds_its_spot(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 2)
    ensure_spots(db)
    _issue(db, "T1")
    db.commit()
    assert free_spot_count(db) == 1


def test_cancelled_pass_frees_immediately(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 1)
    ensure_spots(db)
    p = _issue(db, "T1")
    db.commit()
    p.status = PassStatus.cancelled
    db.commit()
    assert free_spot_count(db) == 1


def test_expired_monthly_holds_through_grace(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 1)
    monkeypatch.setattr(settings, "spot_grace_days", 3)
    ensure_spots(db)
    p = _issue(db, "T1", ptype=PassType.monthly, days=30, price=250)
    db.commit()
    p.expiration_date = business_today() - timedelta(days=2)  # 2 days overdue
    db.commit()
    assert free_spot_count(db) == 0  # inside grace: still theirs
    p.expiration_date = business_today() - timedelta(days=4)  # 4 days overdue
    db.commit()
    assert free_spot_count(db) == 1  # grace over: back in the pool


def test_picker_prefers_longest_vacant(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 3)
    ensure_spots(db)
    spots = {s.number: s for s in db.query(Spot)}
    spots[1].last_vacated_at = business_now()                      # just vacated
    spots[2].last_vacated_at = business_now() - timedelta(days=9)  # long vacant
    db.commit()                                                    # 3: never occupied
    assert pick_free_spot(db).number == 3   # NULLS FIRST wins
    spots[3].last_vacated_at = business_now()
    db.commit()
    assert pick_free_spot(db).number == 2   # then oldest vacancy


def test_picker_honors_preference_when_free(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 3)
    ensure_spots(db)
    preferred = db.query(Spot).filter_by(number=2).one()
    assert pick_free_spot(db, prefer_spot_id=preferred.id).number == 2


def test_picker_ignores_inactive_spots(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 2)
    ensure_spots(db)
    db.query(Spot).filter_by(number=1).one().active = False
    db.commit()
    assert pick_free_spot(db).number == 2


def test_daily_spot_holds_before_noon_frees_at_noon(db, monkeypatch):
    from datetime import datetime

    import app.core.spots as spots_mod

    monkeypatch.setattr(settings, "parking_capacity", 1)
    ensure_spots(db)
    p = _issue(db, "D1", ptype=PassType.daily, days=1)
    db.commit()
    exp = p.expiration_date  # a daily pass is good until NOON on this date

    monkeypatch.setattr(spots_mod, "business_now", lambda: datetime(exp.year, exp.month, exp.day, 11, 0))
    assert free_spot_count(db) == 0  # before noon: truck still parked

    monkeypatch.setattr(spots_mod, "business_now", lambda: datetime(exp.year, exp.month, exp.day, 12, 0))
    assert free_spot_count(db) == 1  # noon: spot freed for the afternoon


def test_weekly_spot_not_freed_at_noon(db, monkeypatch):
    from datetime import datetime, timedelta as _td

    import app.core.spots as spots_mod

    monkeypatch.setattr(settings, "parking_capacity", 1)
    ensure_spots(db)
    p = _issue(db, "W1", ptype=PassType.weekly, days=7)
    db.commit()
    exp = p.expiration_date

    monkeypatch.setattr(spots_mod, "business_now", lambda: datetime(exp.year, exp.month, exp.day, 15, 0))
    assert free_spot_count(db) == 0  # afternoon of expiry day: weekly still holds (not noon)

    nxt = exp + _td(days=1)
    monkeypatch.setattr(spots_mod, "business_now", lambda: datetime(nxt.year, nxt.month, nxt.day, 1, 0))
    assert free_spot_count(db) == 1  # next day: released at midnight
