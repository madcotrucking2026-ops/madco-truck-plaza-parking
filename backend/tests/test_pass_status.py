from datetime import date, datetime

from app.core.pass_status import live_status, pass_expired
from app.models.enums import PassStatus, PassType


def dt(y, m, d, h=0, mn=0):
    return datetime(y, m, d, h, mn)


# --- daily: expires at NOON on its expiry date ---
def test_daily_valid_the_minute_before_noon():
    assert not pass_expired(PassType.daily, date(2026, 8, 6), dt(2026, 8, 6, 11, 59))


def test_daily_expired_exactly_at_noon():
    assert pass_expired(PassType.daily, date(2026, 8, 6), dt(2026, 8, 6, 12, 0))


def test_daily_expired_after_noon():
    assert pass_expired(PassType.daily, date(2026, 8, 6), dt(2026, 8, 6, 12, 1))


def test_daily_valid_night_before_expiry_day():
    assert not pass_expired(PassType.daily, date(2026, 8, 6), dt(2026, 8, 5, 23, 0))


# --- weekly / monthly: whole-day (expire the day AFTER, at midnight) ---
def test_monthly_valid_all_of_expiry_day():
    assert not pass_expired(PassType.monthly, date(2026, 9, 5), dt(2026, 9, 5, 23, 59))


def test_monthly_expired_next_midnight():
    assert pass_expired(PassType.monthly, date(2026, 9, 5), dt(2026, 9, 6, 0, 0))


def test_weekly_valid_all_of_expiry_day_including_after_noon():
    # weekly is NOT noon — it holds the whole expiry day, unlike daily
    assert not pass_expired(PassType.weekly, date(2026, 8, 12), dt(2026, 8, 12, 18, 0))


def test_weekly_expired_next_day():
    assert pass_expired(PassType.weekly, date(2026, 8, 12), dt(2026, 8, 13, 0, 0))


# --- live_status wrapper ---
def test_live_status_daily_expired_after_noon():
    assert live_status(PassType.daily, date(2026, 8, 6), dt(2026, 8, 6, 13, 0)) == PassStatus.expired


def test_live_status_daily_expiring_soon_before_noon():
    assert live_status(PassType.daily, date(2026, 8, 6), dt(2026, 8, 6, 9, 0)) == PassStatus.expiring_soon


def test_live_status_monthly_active_far_out():
    assert live_status(PassType.monthly, date(2026, 9, 5), dt(2026, 8, 5, 9, 0)) == PassStatus.active


def test_live_status_cancelled_always_wins():
    got = live_status(PassType.daily, date(2026, 8, 6), dt(2026, 8, 6, 13, 0), PassStatus.cancelled)
    assert got == PassStatus.cancelled


def test_list_passes_renders_status_for_a_real_pass(db):
    """Regression: list_passes builds each row's status via live_status. The
    endpoint tests only ever hit it with an empty DB, so the comprehension never
    ran and a stale call signature slipped through. Issue one real pass and
    confirm the endpoint renders a valid status instead of crashing."""
    from app.models.enums import PaymentMethod, VehicleType
    from app.routers.passes import _issue_pass_and_payment, list_passes

    _issue_pass_and_payment(
        db,
        company_name="Regression Co",
        phone="313-555-0000",
        vehicle_type=VehicleType.truck,
        truck_number="REG-1",
        trailer_number=None,
        license_plate=None,
        pass_type=PassType.daily,
        issue_date=date(2026, 8, 5),
        end_date=date(2026, 8, 6),
        price_override=None,
        payment_method=PaymentMethod.cash,
        check_number=None,
    )
    db.commit()

    rows = list_passes(db)
    assert len(rows) == 1
    assert rows[0].status in set(PassStatus)
