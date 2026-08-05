"""Renewal pricing/validation — and the charge-then-fail regression guard."""

from datetime import date, timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.core.config import settings
from app.core.dates import add_months
from app.models import MonthlyCustomer
from app.models.enums import PassStatus, PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment, apply_renewal, renewal_quote


def _issue(db, *, pass_type, issue_date, end_date=None):
    return _issue_pass_and_payment(
        db,
        company_name="Hauler Co",
        phone="555",
        vehicle_type=VehicleType.truck,
        truck_number="7834",
        trailer_number=None,
        license_plate=None,
        pass_type=pass_type,
        issue_date=issue_date,
        end_date=end_date,
        price_override=None,
        payment_method=PaymentMethod.cash,
        check_number=None,
    )


def test_renewal_quote_rejects_end_date_not_after_old_end(db):
    today = date.today()
    p = _issue(db, pass_type=PassType.daily, issue_date=today - timedelta(days=10))  # lapsed
    old_end = p.expiration_date
    # The new end must be AFTER the old end date — a renewal continues from there.
    with pytest.raises(HTTPException):
        renewal_quote(db, p, old_end)
    with pytest.raises(HTTPException):
        renewal_quote(db, p, old_end - timedelta(days=1))


def test_renewal_quote_continues_from_old_end_when_paid_late(db):
    # Client rule: a late-paying customer's renewal starts from the old end date,
    # never from today — no free gap, they pay from where they left off.
    today = date.today()
    p = _issue(db, pass_type=PassType.daily, issue_date=today - timedelta(days=10))
    old_end = p.expiration_date  # in the past — the pass already lapsed
    new_end = today + timedelta(days=3)
    start, price = renewal_quote(db, p, new_end)
    assert start == old_end  # continues from where it ended, NOT from today
    assert price == settings.daily_price * (new_end - old_end).days


def test_apply_renewal_with_stripe_charge_skips_revalidation(db):
    """The bug we fixed: a weekly self-pay renewal's span check is re-run at
    finalize AFTER the card was charged. If the 'renew from today' floor shifted,
    the span is no longer 7 and it 400s post-charge. When a real charge amount is
    supplied, apply_renewal must trust it and NOT re-validate."""
    today = date.today()
    p = _issue(db, pass_type=PassType.weekly, issue_date=today - timedelta(days=10))  # lapsed weekly
    bad_end = today + timedelta(days=5)  # span from today is 5, not 7

    # Cash/check path (no charge) still validates and rejects the bad span.
    with pytest.raises(HTTPException):
        apply_renewal(db, p, bad_end, PaymentMethod.cash)

    # Stripe path (already charged) trusts the amount and goes through.
    renewed = apply_renewal(db, p, bad_end, PaymentMethod.credit_card, price_from_charge=137.0)
    assert float(renewed.price) == 137.0
    assert renewed.expiration_date == bad_end
    assert renewed.status == PassStatus.active


def test_monthly_renewal_advances_customer_and_prices_by_rate(db):
    today = date.today()
    p = _issue(db, pass_type=PassType.monthly, issue_date=today)
    new_end = add_months(p.expiration_date, 1)
    renewed = apply_renewal(db, p, new_end, PaymentMethod.cash)

    assert float(renewed.price) == float(settings.monthly_price)  # one month at the established rate
    mc = db.scalar(select(MonthlyCustomer).where(MonthlyCustomer.company_id == p.company_id))
    assert mc is not None
    assert mc.renewal_date == new_end


def test_continue_monthly_catches_up_whole_months(db):
    # Late & continuing: Aug 8 old end, renew to Oct 8 = 2 whole months.
    p = _issue(db, pass_type=PassType.monthly, issue_date=date(2026, 7, 8))
    p.expiration_date = date(2026, 8, 8)
    db.commit()
    _, price = renewal_quote(db, p, date(2026, 10, 8), mode="continue")
    assert price == settings.monthly_price * 2


def test_close_out_monthly_whole_months_plus_leftover_days(db):
    # Client's example: Jul 8 -> Aug 8 monthly, leaves Sep 11.
    # Aug 8 -> Sep 11 = 1 whole month + 3 leftover days at the daily rate.
    p = _issue(db, pass_type=PassType.monthly, issue_date=date(2026, 7, 8))
    p.expiration_date = date(2026, 8, 8)
    db.commit()
    start, price = renewal_quote(db, p, date(2026, 9, 11), mode="close_out")
    assert start == date(2026, 8, 8)
    assert price == settings.monthly_price + 3 * settings.daily_price


def test_close_out_leftover_is_capped_at_one_period(db):
    # Leaves Sep 5 — before the Sep 8 anniversary, so 0 whole months + 28 leftover
    # days. 28*daily would exceed a month, so it caps at one month's rate.
    p = _issue(db, pass_type=PassType.monthly, issue_date=date(2026, 7, 8))
    p.expiration_date = date(2026, 8, 8)
    db.commit()
    _, price = renewal_quote(db, p, date(2026, 9, 5), mode="close_out")
    assert price == settings.monthly_price  # capped, never more than continuing


def test_close_out_daily_bills_days_used(db):
    p = _issue(db, pass_type=PassType.daily, issue_date=date(2026, 8, 5))
    p.expiration_date = date(2026, 8, 6)
    db.commit()
    _, price = renewal_quote(db, p, date(2026, 8, 9), mode="close_out")
    assert price == settings.daily_price * 3  # Aug 6 -> Aug 9 = 3 days


def test_close_out_marks_monthly_customer_inactive_and_stops_reminders(db):
    from app.models.enums import MonthlyCustomerStatus, ReminderStatus

    p = _issue(db, pass_type=PassType.monthly, issue_date=date(2026, 7, 8))
    p.expiration_date = date(2026, 8, 8)
    db.commit()
    apply_renewal(db, p, date(2026, 9, 11), PaymentMethod.cash, mode="close_out")
    mc = db.scalar(select(MonthlyCustomer).where(MonthlyCustomer.company_id == p.company_id))
    assert mc.status == MonthlyCustomerStatus.inactive
    assert mc.reminder_status == ReminderStatus.stopped
