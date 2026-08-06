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
    for truck, n in (("T1", 2), ("T2", 1)):
        for _ in range(n):
            _issue(db, company="Freight Co", truck=truck)  # daily, issued today -> active
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
