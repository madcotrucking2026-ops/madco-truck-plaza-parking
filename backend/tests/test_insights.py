"""Conversion-leads insight: which daily/weekly customers to pitch monthly."""

from datetime import date, timedelta

from app.models import Company, MonthlyCustomer
from app.models.enums import MonthlyCustomerStatus, PassType, PaymentMethod, VehicleType
from app.routers.insights import conversion_leads
from app.routers.passes import _issue_pass_and_payment


def _issue_daily(db, company_name, n, when=None):
    when = when or date.today()
    for i in range(n):
        _issue_pass_and_payment(
            db,
            company_name=company_name,
            phone="313-555-0100",
            vehicle_type=VehicleType.truck,
            truck_number=f"T{i}",
            trailer_number=None,
            license_plate=None,
            pass_type=PassType.daily,
            issue_date=when,
            end_date=None,
            price_override=None,
            payment_method=PaymentMethod.cash,
            check_number=None,
        )


def _make_monthly(db, company_name):
    company = Company(name=company_name, phone="313-555-0199")
    db.add(company)
    db.flush()
    db.add(
        MonthlyCustomer(
            company_id=company.id,
            monthly_price=250,
            renewal_date=date.today() + timedelta(days=20),
            status=MonthlyCustomerStatus.truck_parked,
            preferred_payment_method=PaymentMethod.cash,
        )
    )
    db.flush()


def test_leads_tiering_and_exclusions(db):
    _issue_daily(db, "Big Spender", 13)      # 13 * $20 = $260 >= monthly -> hot
    _issue_daily(db, "Frequent Freight", 8)  # 8 visits -> hot
    _issue_daily(db, "Warm Hauler", 5)       # 5 visits -> warm
    _issue_daily(db, "Sometimes Co", 4)      # 4 visits -> cold (>= MIN_VISITS)
    _issue_daily(db, "One Off", 1)           # below MIN_VISITS -> excluded
    _make_monthly(db, "Already Monthly")
    _issue_daily(db, "Already Monthly", 6)   # on a monthly plan -> excluded
    db.commit()

    result = conversion_leads(db)
    assert result.window_days == 90
    by_name = {lead.company_name: lead for lead in result.leads}

    assert set(by_name) == {"Big Spender", "Frequent Freight", "Warm Hauler", "Sometimes Co"}
    assert by_name["Big Spender"].tier == "hot"
    assert by_name["Frequent Freight"].tier == "hot"
    assert by_name["Warm Hauler"].tier == "warm"
    assert by_name["Sometimes Co"].tier == "cold"

    assert by_name["Big Spender"].visits == 13
    assert by_name["Big Spender"].total_spent == 260.0
    assert by_name["Warm Hauler"].suggested_monthly == 250.0

    # Ranked by spend, biggest opportunity first.
    spends = [lead.total_spent for lead in result.leads]
    assert spends == sorted(spends, reverse=True)


def test_high_total_but_few_visits_is_not_hot(db):
    """The bug this guards: a 90-day TOTAL was compared against a MONTHLY price,
    so a company that spent $280 across three months got tagged 'hot' — and the
    owner would pitch a $250/mo plan to someone paying ~$93/mo today."""
    _issue_daily(db, "Occasional Freight", 3)  # 3 visits
    # Push their total over the monthly price without adding visits.
    _issue_pass_and_payment(
        db, company_name="Occasional Freight", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number="BIG", trailer_number=None, license_plate=None, pass_type=PassType.weekly,
        issue_date=date.today(), end_date=None, price_override=None,
        payment_method=PaymentMethod.cash, check_number=None,
    )
    db.commit()

    lead = next(l for l in conversion_leads(db).leads if l.company_name == "Occasional Freight")
    assert lead.total_spent >= 150  # 3 daily ($60) + a weekly ($100)
    # $160 over 90 days is ~$53/month — nowhere near a $250/mo plan.
    assert lead.current_monthly_equivalent < 250
    assert lead.tier == "cold"  # 4 visits, low run-rate


def test_hot_leads_always_rank_above_cold_ones(db):
    """Ranking used to be by raw 90-day spend while tiering was by run-rate, so a
    COLD lead could sort above a HOT one and the owner would call it first."""
    _issue_daily(db, "Regular Runner", 9)  # 9 visits -> hot, but only $180 spent
    # Big total, few visits -> cold. Under the old sort this outranked the hot one.
    _issue_daily(db, "Rare Big Spender", 3)
    for _ in range(3):
        _issue_pass_and_payment(
            db, company_name="Rare Big Spender", phone="313-555-0100", vehicle_type=VehicleType.truck,
            truck_number="BIG", trailer_number=None, license_plate=None, pass_type=PassType.weekly,
            issue_date=date.today(), end_date=None, price_override=None,
            payment_method=PaymentMethod.cash, check_number=None,
        )
    db.commit()

    leads = conversion_leads(db).leads
    by_name = {l.company_name: l for l in leads}
    assert by_name["Regular Runner"].tier == "hot"
    assert by_name["Rare Big Spender"].total_spent > by_name["Regular Runner"].total_spent  # bigger total…
    assert by_name["Rare Big Spender"].tier != "hot"  # …but not a hot lead
    # Hot must come first regardless of the raw total.
    assert leads[0].company_name == "Regular Runner"


def test_no_leads_when_everyone_is_monthly_or_rare(db):
    _make_monthly(db, "Monthly Co")
    _issue_daily(db, "Monthly Co", 9)
    _issue_daily(db, "Barely Here", 2)  # below MIN_VISITS
    db.commit()
    assert conversion_leads(db).leads == []
