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


def test_profile_404_for_unknown_company(db):
    with pytest.raises(HTTPException) as exc:
        company_profile(999999, db)
    assert exc.value.status_code == 404
