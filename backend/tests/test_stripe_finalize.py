"""Stripe finalize core (_finalize_intent) — the path that turns a confirmed
charge into a pass. Driven with a fake intent object so no SDK/network is
touched; exercises metadata parsing, idempotency, price-from-charge, and guards."""

import pytest
from fastapi import HTTPException
from sqlalchemy import func, select

from app.models import ParkingPass, Payment
from app.routers.stripe_payments import _finalize_intent


class _FakeMeta:
    """Mimics stripe's StripeObject metadata: only .to_dict() is supported
    (the SDK's .get()/dict() misbehave — the reason the code uses to_dict())."""

    def __init__(self, data: dict):
        self._data = dict(data)

    def to_dict(self) -> dict:
        return dict(self._data)


class _FakeIntent:
    def __init__(self, id, status, amount_received, metadata):
        self.id = id
        self.status = status
        self.amount_received = amount_received
        self.metadata = _FakeMeta(metadata)


def _md(**over):
    base = {
        "company_name": "Test Co",
        "phone": "555",
        "vehicle_type": "truck",
        "truck_number": "7834",
        "trailer_number": "",
        "license_plate": "",
        "pass_type": "daily",
        "issue_date": "2026-07-01",
        "end_date": "",
    }
    base.update(over)
    return base


def test_finalize_issues_pass_from_metadata(db):
    intent = _FakeIntent("pi_ok", "succeeded", 2000, _md())
    p = _finalize_intent(db, intent)
    assert float(p.price) == 20.0  # amount_received / 100 is the price of record
    payment = db.scalar(select(Payment).where(Payment.stripe_payment_intent_id == "pi_ok"))
    assert payment is not None and float(payment.amount) == 20.0
    assert p.company.name == "Test Co"


def test_finalize_is_idempotent(db):
    intent = _FakeIntent("pi_dup", "succeeded", 2000, _md())
    first = _finalize_intent(db, intent)
    again = _finalize_intent(db, intent)  # same intent replayed (webhook + client)
    assert again.id == first.id
    assert db.scalar(select(func.count()).select_from(Payment)) == 1
    assert db.scalar(select(func.count()).select_from(ParkingPass)) == 1


def test_finalize_rejects_unconfirmed_charge(db):
    intent = _FakeIntent("pi_pending", "requires_payment_method", 0, _md())
    with pytest.raises(HTTPException) as exc:
        _finalize_intent(db, intent)
    assert exc.value.status_code == 400


def test_finalize_rejects_intent_without_pass_metadata(db):
    md = _md()
    del md["company_name"]  # e.g. an unrelated dashboard charge
    intent = _FakeIntent("pi_foreign", "succeeded", 2000, md)
    with pytest.raises(HTTPException) as exc:
        _finalize_intent(db, intent)
    assert exc.value.status_code == 400
