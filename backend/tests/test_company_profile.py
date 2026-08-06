"""Company profile aggregation: totals, per-truck rollup, monthly fields."""

from datetime import date, timedelta

import pytest
from fastapi import HTTPException

from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.companies import company_profile
from app.routers.passes import _find_company, _issue_pass_and_payment


def _issue(db, *, company, truck, ptype=PassType.daily, issue_date=None, end_date=None):
    return _issue_pass_and_payment(
        db,
        company_name=company,
        phone="313-555-0100",
        vehicle_type=VehicleType.truck,
        truck_number=truck,
        trailer_number=None,
        license_plate=None,
        pass_type=ptype,
        issue_date=issue_date or date.today(),
        end_date=end_date,
        price_override=None,
        payment_method=PaymentMethod.cash,
        check_number=None,
    )


def test_profile_aggregates_visits_trucks_and_spend(db):
    # T1 visits on two DIFFERENT days (a real repeat visit is a new day; the
    # double-submit guard folds same-truck, same-day re-issues into one), T2 once.
    _issue(db, company="Freight Co", truck="T1", issue_date=date.today())
    _issue(db, company="Freight Co", truck="T1", issue_date=date.today() - timedelta(days=1))
    _issue(db, company="Freight Co", truck="T2", issue_date=date.today())
    db.commit()
    cid = _find_company(db, "Freight Co").id

    prof = company_profile(cid, db)
    assert prof.total_visits == 3
    assert prof.total_spent == 60.0  # 3 daily * $20
    assert prof.active_passes == 3
    assert len(prof.trucks) == 2  # T1 reused (dedup), T2 new
    assert {t.truck_number: t.visits for t in prof.trucks} == {"T1": 2, "T2": 1}
    assert prof.is_monthly is False
    assert prof.loyalty_score == 3 * 4 + 3 * 10  # visits*4 + active*10
    assert len(prof.recent_passes) == 3
    assert len(prof.recent_payments) == 3


def test_profile_monthly_fields(db):
    today = date.today()
    _issue(db, company="Monthly Co", truck="M1", ptype=PassType.monthly,
           issue_date=today, end_date=today + timedelta(days=30))
    db.commit()
    cid = _find_company(db, "Monthly Co").id

    prof = company_profile(cid, db)
    assert prof.is_monthly is True
    assert prof.monthly_price == 250.0
    assert prof.renewal_date == today + timedelta(days=30)


def test_profile_shows_each_monthly_trucks_reserved_spot(db, monkeypatch):
    from app.core.config import settings
    from app.core.spots import ensure_spots, spot_label

    monkeypatch.setattr(settings, "parking_capacity", 4)
    ensure_spots(db)
    today = date.today()
    p1 = _issue(db, company="Reserved Co", truck="M1", ptype=PassType.monthly,
                issue_date=today, end_date=today + timedelta(days=30))
    p2 = _issue(db, company="Reserved Co", truck="M2", ptype=PassType.monthly,
                issue_date=today, end_date=today + timedelta(days=30))
    db.commit()
    cid = _find_company(db, "Reserved Co").id

    prof = company_profile(cid, db)
    spots = {t.truck_number: t.reserved_spot for t in prof.trucks}
    assert spots["M1"] == spot_label(p1.spot.number)  # each truck's fixed spot label
    assert spots["M2"] == spot_label(p2.spot.number)
    assert spots["M1"] != spots["M2"]  # and they're different spots


def test_profile_shows_per_truck_price_and_company_monthly_total(db, monkeypatch):
    """Each monthly truck shows ITS OWN rate and the profile totals them — what
    the cashier collects from the company (SX Express: 250 + 210 + 200 = 660)."""
    from app.core.config import settings
    from app.core.spots import ensure_spots
    from app.routers.passes import _issue_pass_and_payment

    monkeypatch.setattr(settings, "parking_capacity", 10)
    ensure_spots(db)
    for truck, price in (("1325", 250), ("1236", 210), ("1397", 200)):
        _issue_pass_and_payment(
            db, company_name="SX Express", phone="313-555-0100", vehicle_type=VehicleType.truck,
            truck_number=truck, trailer_number=None, license_plate=None, pass_type=PassType.monthly,
            issue_date=date.today(), end_date=date.today() + timedelta(days=30),
            price_override=price, payment_method=PaymentMethod.cash, check_number=None,
        )
    db.commit()
    cid = _find_company(db, "SX Express").id

    prof = company_profile(cid, db)
    assert {t.truck_number: t.monthly_price for t in prof.trucks} == {"1325": 250, "1236": 210, "1397": 200}
    assert prof.monthly_total == 660  # cashier charges the company the sum


def test_profile_daily_truck_has_no_reserved_spot(db, monkeypatch):
    from app.core.config import settings
    from app.core.spots import ensure_spots

    monkeypatch.setattr(settings, "parking_capacity", 4)
    ensure_spots(db)
    _issue(db, company="Daily Co", truck="D1", ptype=PassType.daily)
    db.commit()
    cid = _find_company(db, "Daily Co").id

    prof = company_profile(cid, db)
    assert prof.trucks[0].reserved_spot is None  # daily trucks are never reserved a spot


def test_profile_404_for_unknown_company(db):
    with pytest.raises(HTTPException) as exc:
        company_profile(999999, db)
    assert exc.value.status_code == 404
