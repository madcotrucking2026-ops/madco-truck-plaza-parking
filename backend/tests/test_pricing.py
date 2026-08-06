"""Pricing math: partial-month rounding and per-type price."""

from datetime import date

from app.core.config import settings
from app.models.enums import PassType
from app.routers.passes import _months_between, _price_for


def test_months_between_rounds_partial_up():
    # A full calendar month is 1; one day past a full month starts a new month.
    assert _months_between(date(2026, 7, 5), date(2026, 8, 5)) == 1
    assert _months_between(date(2026, 7, 5), date(2026, 9, 5)) == 2
    assert _months_between(date(2026, 7, 5), date(2026, 8, 6)) == 2  # one day over -> 2
    assert _months_between(date(2026, 7, 5), date(2026, 7, 20)) == 1  # partial -> min 1
    assert _months_between(date(2026, 7, 5), date(2026, 7, 5)) == 1  # never below 1


def test_daily_price_scales_with_days():
    d = settings.daily_price
    assert _price_for(PassType.daily, date(2026, 7, 1), date(2026, 7, 2), None) == d * 1
    assert _price_for(PassType.daily, date(2026, 7, 1), date(2026, 7, 4), None) == d * 3


def test_weekly_price_is_flat():
    assert _price_for(PassType.weekly, date(2026, 7, 1), date(2026, 7, 8), None) == settings.weekly_price


def test_monthly_uses_established_rate_times_months():
    # An existing company rate wins and is multiplied by the month span.
    price = _price_for(PassType.monthly, date(2026, 7, 1), date(2026, 9, 1), None, existing_monthly_price=900)
    assert price == 900 * 2


def test_monthly_price_is_per_truck_override_always_wins():
    # Each truck is priced on its own — a typed price always wins, even when the
    # company already has another truck on a different rate (SX Express: one truck
    # $250, the next $210). No single company rate is forced onto every truck.
    price = _price_for(PassType.monthly, date(2026, 7, 1), date(2026, 8, 1), override=210, existing_monthly_price=250)
    assert price == 210
    # No price typed for this truck -> fall back to the company's on-file rate.
    price = _price_for(PassType.monthly, date(2026, 7, 1), date(2026, 8, 1), override=None, existing_monthly_price=250)
    assert price == 250
    # Brand-new company, price typed -> that price seeds the truck.
    price = _price_for(PassType.monthly, date(2026, 7, 1), date(2026, 8, 1), override=400, existing_monthly_price=None)
    assert price == 400
