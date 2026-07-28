"""ensure_spots(): the painted lot exists in the database, sized by config."""
from sqlalchemy import func, select

from app.core.config import settings
from app.core.spots import ensure_spots
from app.models import Spot


def test_seeds_capacity_spots_once(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 300)
    ensure_spots(db)
    ensure_spots(db)  # idempotent — second run adds nothing
    assert db.scalar(select(func.count()).select_from(Spot)) == 300
    assert db.scalar(select(func.min(Spot.number))) == 1
    assert db.scalar(select(func.max(Spot.number))) == 300


def test_capacity_shrink_deactivates_never_deletes(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 300)
    ensure_spots(db)
    monkeypatch.setattr(settings, "parking_capacity", 280)
    ensure_spots(db)
    assert db.scalar(select(func.count()).select_from(Spot)) == 300  # history kept
    assert db.scalar(select(func.count()).select_from(Spot).where(Spot.active)) == 280


def test_capacity_grow_reactivates_and_extends(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 10)
    ensure_spots(db)
    monkeypatch.setattr(settings, "parking_capacity", 12)
    ensure_spots(db)
    assert db.scalar(select(func.count()).select_from(Spot).where(Spot.active)) == 12
