"""The monthly/daily lot split (which spot numbers are the monthly area)."""

from app.core.config import settings
from app.core.spots import is_monthly_spot, monthly_spot_limit


def test_monthly_area_is_zone_a_by_default(monkeypatch):
    monkeypatch.setattr(settings, "spots_per_zone", 25)
    monkeypatch.setattr(settings, "monthly_zone_count", 1)
    assert monthly_spot_limit() == 25
    assert is_monthly_spot(1)
    assert is_monthly_spot(25)
    assert not is_monthly_spot(26)  # Zone B onward = daily/weekly pool
    assert not is_monthly_spot(0)


def test_two_monthly_zones_extends_the_area(monkeypatch):
    monkeypatch.setattr(settings, "spots_per_zone", 25)
    monkeypatch.setattr(settings, "monthly_zone_count", 2)
    assert monthly_spot_limit() == 50
    assert is_monthly_spot(50)
    assert not is_monthly_spot(51)


def test_split_off_when_count_is_zero(monkeypatch):
    monkeypatch.setattr(settings, "monthly_zone_count", 0)
    assert monthly_spot_limit() == 0
    assert not is_monthly_spot(1)  # nothing is monthly-reserved; all pooled
