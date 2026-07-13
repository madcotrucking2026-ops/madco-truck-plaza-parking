"""The plaza's day.

Two bugs lived here, and both only showed themselves in the evening — which is a
truck stop's busy time, and the reason they went unnoticed:

  * Payment.paid_at was stamped by the database in UTC while revenue was bucketed
    by the server's LOCAL date. After 8pm Michigan time those disagree, so the
    evening's takings dropped off "Today's Revenue" and reappeared tomorrow.
  * "Today" came from date.today() — the SERVER's date. On a cloud VM (always UTC)
    the plaza's day would roll over at 8pm: passes expiring early, revenue on the
    wrong day, reminders re-sending.
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select

from app.core.clock import business_now, business_today
from app.core.config import settings
from app.models import Payment
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.dashboard import dashboard_stats
from app.routers.passes import _issue_pass_and_payment


def test_the_day_comes_from_the_plazas_timezone_not_the_hosts(monkeypatch):
    """Kiritimati (UTC+14) and Niue (UTC-11) are 25 hours apart, so their calendar
    dates NEVER agree. If the clock were reading the host's timezone instead of the
    configured one, both would return the same day and this would fail."""
    monkeypatch.setattr(settings, "timezone", "Pacific/Kiritimati")
    far_east = business_today()
    monkeypatch.setattr(settings, "timezone", "Pacific/Niue")
    far_west = business_today()

    assert far_east != far_west


def test_business_now_is_wall_clock_time_at_the_plaza(monkeypatch):
    monkeypatch.setattr(settings, "timezone", "America/Detroit")
    expected = datetime.now(ZoneInfo("America/Detroit")).replace(tzinfo=None)

    assert abs((business_now() - expected).total_seconds()) < 5


def test_a_payment_is_stamped_with_the_plazas_day(db):
    """The invariant the money depends on: the day a payment is recorded under is
    the day the plaza was actually open. Stamped in UTC, a 9pm payment was filed
    under tomorrow."""
    _issue_pass_and_payment(
        db,
        company_name="Night Shift Hauling",
        phone="313-555-0111",
        vehicle_type=VehicleType.truck,
        truck_number="2200",
        trailer_number=None,
        license_plate=None,
        pass_type=PassType.daily,
        issue_date=business_today(),
        end_date=None,
        price_override=None,
        payment_method=PaymentMethod.cash,
        check_number=None,
    )
    db.commit()

    payment = db.scalar(select(Payment))
    assert payment.paid_at.date() == business_today()


def test_every_business_timestamp_is_stamped_in_plaza_time(db):
    """Not just payments. The Activity Log showed a 9pm action as happening at
    00:13 the NEXT DAY, because the database stamped it in UTC. Anything the
    manager reads a time off must agree with the clock on the wall."""
    from app.core.audit import log_audit
    from app.models import AuditLog, Company, Vehicle
    from app.models.enums import AuditAction

    db.add(Company(name="Timestamp Freight", phone="313-555-0122"))
    db.add(Vehicle(truck_number="TS01", vehicle_type=VehicleType.truck))
    log_audit(db, AuditAction.search_performed, "lot_check", 'Searched "TS01"')
    db.commit()

    for row in (db.scalar(select(AuditLog)), db.scalar(select(Company)), db.scalar(select(Vehicle))):
        assert row.created_at.date() == business_today(), f"{type(row).__name__} is not on the plaza's day"


def test_tonights_takings_are_on_tonights_books(db, monkeypatch):
    """A payment taken at 10:30pm plaza time belongs to that day's revenue. The same
    instant is already tomorrow in UTC, which is exactly how it used to go missing."""
    business_day = date(2026, 7, 12)
    monkeypatch.setattr("app.routers.dashboard.business_today", lambda: business_day)

    db.add(
        Payment(
            amount=20,
            method=PaymentMethod.cash,
            paid_at=datetime(2026, 7, 12, 22, 30),  # 10:30pm at the plaza
        )
    )
    db.commit()

    assert dashboard_stats(db).todays_revenue == 20.0
