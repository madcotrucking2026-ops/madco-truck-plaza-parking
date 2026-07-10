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


def test_renewal_quote_rejects_end_date_not_after_start(db):
    today = date.today()
    p = _issue(db, pass_type=PassType.daily, issue_date=today - timedelta(days=10))  # lapsed
    with pytest.raises(HTTPException):
        renewal_quote(db, p, today)  # not after the rebased "renew from today" floor
    with pytest.raises(HTTPException):
        renewal_quote(db, p, today - timedelta(days=1))


def test_renewal_quote_rebases_from_today_for_lapsed_pass(db):
    today = date.today()
    p = _issue(db, pass_type=PassType.daily, issue_date=today - timedelta(days=10))
    start, price = renewal_quote(db, p, today + timedelta(days=3))
    assert start == today  # not the stale expiration in the past
    assert price == settings.daily_price * 3


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
