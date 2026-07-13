"""The 7am briefing: who to call today, in the order money is at risk.

The ORDER is the whole feature. A report that lists a warm sales lead above a
renewal that's a week overdue is a report that costs the owner money, so the
ranking is pinned here.
"""

from datetime import timedelta

from app.core.clock import business_today
from app.models import Company, MonthlyCustomer
from app.models.enums import MonthlyCustomerStatus, PassType, PaymentMethod, VehicleType
from app.routers.insights import morning_report
from app.routers.passes import _issue_pass_and_payment


class _FakeUser:
    id = 1


def _monthly(db, name, renews_in_days, price=250):
    company = Company(name=name, phone="313-555-0100")
    db.add(company)
    db.flush()
    db.add(
        MonthlyCustomer(
            company_id=company.id,
            monthly_price=price,
            renewal_date=business_today() + timedelta(days=renews_in_days),
            status=MonthlyCustomerStatus.truck_parked,
            preferred_payment_method=PaymentMethod.cash,
        )
    )
    db.flush()
    return company


def _daily(db, company, truck, n=1, expires_today=False):
    today = business_today()
    for i in range(n):
        _issue_pass_and_payment(
            db,
            company_name=company,
            phone="313-555-0111",
            vehicle_type=VehicleType.truck,
            truck_number=f"{truck}{i}",
            trailer_number=None,
            license_plate=None,
            pass_type=PassType.daily,
            # A daily pass issued yesterday runs out today.
            issue_date=today - timedelta(days=1) if expires_today else today,
            end_date=today if expires_today else None,
            price_override=None,
            payment_method=PaymentMethod.cash,
            check_number=None,
        )


def test_overdue_renewal_outranks_everything_else(db):
    _monthly(db, "Late Freight", renews_in_days=-6)          # money already owed
    _monthly(db, "Due Today Cartage", renews_in_days=0)      # money due now
    _daily(db, "Expiring Haulage", "EXP", expires_today=True)  # money leaving the lot
    _daily(db, "Regular Runner", "REG", n=9)                 # a hot lead
    db.commit()

    report = morning_report(db=db, _user=_FakeUser())
    by_company = [c.company_name for c in report.calls]

    assert by_company[0] == "Late Freight", "an overdue renewal must be the first call of the day"
    assert report.calls[0].priority == "now"
    assert "6 days overdue" in report.calls[0].reason

    # The sales lead is worth a call, but never before money already owed.
    lead_index = by_company.index("Regular Runner")
    assert lead_index == len(report.calls) - 1
    assert report.calls[lead_index].priority == "worth_a_call"


def test_a_renewal_far_off_is_not_this_mornings_problem(db):
    _monthly(db, "Not Yet Co", renews_in_days=20)
    db.commit()

    report = morning_report(db=db, _user=_FakeUser())

    assert report.calls == []
    assert report.all_clear is True


def test_an_expiring_pass_names_the_truck(db):
    _daily(db, "Expiring Haulage", "7834", expires_today=True)
    db.commit()

    call = next(c for c in morning_report(db=db, _user=_FakeUser()).calls if c.kind == "pass_expiring")

    assert "7834" in call.reason  # the owner needs to know WHICH truck to go find
    assert call.pass_id is not None  # and be able to renew it without hunting for it
    assert call.priority == "today"


def test_a_lead_who_would_pay_MORE_is_told_so(db):
    """Caught on real data: the report said "8 visits, spending $53/mo — offer the
    $250/mo plan". That pitch asks the driver to pay 5x what he pays today. Nikhil
    would make the call, get a flat no, and after a few of those stop reading this
    page. If the plan costs them more, the report says so."""
    _daily(db, "Occasional Regular", "OCC", n=8)  # 8 visits x $20 = $160 over 90d = ~$53/mo
    db.commit()

    lead = next(c for c in morning_report(db=db, _user=_FakeUser()).calls if c.kind == "lead")

    assert "MORE" in lead.reason, "must not imply a saving that isn't there"
    assert "SAVES" not in lead.reason
    assert "unlimited parking" in lead.reason  # the honest angle to sell on


def test_a_lead_who_would_SAVE_is_ranked_above_one_who_would_not(db):
    """The customer who already outspends the plan closes himself — call him first."""
    # 8 weekly passes = $800 over 90 days = ~$267/mo, above the $250 plan.
    for i in range(8):
        _issue_pass_and_payment(
            db, company_name="Big Spender Freight", phone="313-555-0100", vehicle_type=VehicleType.truck,
            truck_number=f"BIGX{i}", trailer_number=None, license_plate=None, pass_type=PassType.weekly,
            issue_date=business_today(), end_date=None, price_override=None,
            payment_method=PaymentMethod.cash, check_number=None,
        )
    _daily(db, "Frequent Cheapskate", "CHP", n=9)  # 9 x $20 = $180 over 90d = $60/mo
    db.commit()

    leads = [c for c in morning_report(db=db, _user=_FakeUser()).calls if c.kind == "lead"]
    by_name = {c.company_name: c for c in leads}

    assert "SAVES" in by_name["Big Spender Freight"].reason
    assert "MORE" in by_name["Frequent Cheapskate"].reason
    # The easy yes comes first.
    assert leads[0].company_name == "Big Spender Freight"


def test_only_hot_leads_make_the_report(db):
    """A morning report padded with lukewarm maybes is a report nobody reads."""
    _daily(db, "Regular Runner", "REG", n=9)  # hot: 9 visits
    _daily(db, "Sometimes Co", "SOM", n=4)    # cold: on the radar, not worth a call
    db.commit()

    leads = [c.company_name for c in morning_report(db=db, _user=_FakeUser()).calls if c.kind == "lead"]

    assert leads == ["Regular Runner"]


def test_money_and_lot_are_reported_for_the_plazas_day(db):
    _daily(db, "Cash Today Co", "CSH", n=2)  # 2 x $20 taken today
    db.commit()

    report = morning_report(db=db, _user=_FakeUser())

    assert report.generated_for == business_today()
    assert report.todays_revenue == 40.0
    assert report.occupied_spaces == 2
    assert report.available_spaces == report.capacity - 2
