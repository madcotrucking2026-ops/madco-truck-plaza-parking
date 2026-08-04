"""spot_label: the integer number stays the key; this is only how it reads."""
from app.core.config import settings
from app.core.spots import spot_label


def test_zone_labels_at_boundaries(monkeypatch):
    monkeypatch.setattr(settings, "spots_per_zone", 25)
    assert spot_label(1) == "A1"
    assert spot_label(25) == "A25"
    assert spot_label(26) == "B1"
    assert spot_label(150) == "F25"


def test_disabled_zoning_is_bare_number(monkeypatch):
    monkeypatch.setattr(settings, "spots_per_zone", 0)
    assert spot_label(39) == "39"


def test_overflow_past_Z_degrades_to_number(monkeypatch):
    # per-zone of 1 puts spot 27 in the 27th zone (index 26 > 'Z') — no letter, bare.
    monkeypatch.setattr(settings, "spots_per_zone", 1)
    assert spot_label(27) == "27"
    assert spot_label(1) == "A1"
