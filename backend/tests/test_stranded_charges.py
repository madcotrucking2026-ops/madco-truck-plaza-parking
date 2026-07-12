"""The stranded-charge detector: cards Stripe accepted that produced no pass.

This list should always be empty. The tests exist to make sure that when it ISN'T
empty, we say so — and that we never cry wolf over a charge that's perfectly fine
or that was never ours to begin with.
"""

import json
from datetime import date, datetime

import pytest
import stripe
from fastapi import HTTPException

from app.models import ParkingPass, PaymentRequest
from app.routers.stripe_payments import (
    _finalize_intent,
    issue_stranded_pass,
    stranded_charges,
)
from tests.test_stripe_finalize import _FakeIntent, _md


class _FakeUser:
    id = 1


def _listing(monkeypatch, intents):
    """Stand in for stripe.PaymentIntent.list(...).auto_paging_iter()."""

    class _Page:
        def auto_paging_iter(self):
            return iter(intents)

    monkeypatch.setattr(stripe.PaymentIntent, "list", lambda **kw: _Page())


def _configured(monkeypatch):
    monkeypatch.setattr("app.routers.stripe_payments.is_configured", lambda: True)


def _intent(id, md, amount=2000, status="succeeded"):
    intent = _FakeIntent(id, status, amount, md)
    intent.created = int(datetime(2026, 7, 12).timestamp())
    return intent


def test_a_charge_with_no_pass_is_reported(db, monkeypatch):
    _configured(monkeypatch)
    _listing(monkeypatch, [_intent("pi_orphan", _md(truck_number="7834"))])

    result = stranded_charges(days=7, db=db, _user=_FakeUser())

    assert len(result) == 1
    assert result[0].payment_intent_id == "pi_orphan"
    assert result[0].amount == 20.0
    assert result[0].company_name == "Test Co"
    assert result[0].vehicle == "7834"


def test_a_charge_that_produced_a_pass_is_not_reported(db, monkeypatch):
    _configured(monkeypatch)
    intent = _intent("pi_good", _md())
    _finalize_intent(db, intent)  # the normal path ran; the customer has their pass
    db.commit()
    _listing(monkeypatch, [intent])

    assert stranded_charges(days=7, db=db, _user=_FakeUser()) == []


def test_a_charge_we_did_not_create_is_never_reported(db, monkeypatch):
    """A charge someone made by hand in the Stripe Dashboard has no pass here and
    never will. Reporting it as 'money taken, no pass' would be a false alarm that
    trains the manager to ignore this list — which is how the real one gets missed."""
    _configured(monkeypatch)
    _listing(monkeypatch, [_intent("pi_dashboard", {"note": "manual charge"})])

    assert stranded_charges(days=7, db=db, _user=_FakeUser()) == []


def test_an_unpaid_intent_is_not_reported(db, monkeypatch):
    """Abandoned checkouts are not stranded money — nobody was charged."""
    _configured(monkeypatch)
    _listing(monkeypatch, [_intent("pi_abandoned", _md(), amount=0, status="requires_payment_method")])

    assert stranded_charges(days=7, db=db, _user=_FakeUser()) == []


class _FakeCharge:
    def __init__(self, refunded=False, amount_refunded=0):
        self.refunded = refunded
        self.amount_refunded = amount_refunded


def test_a_refunded_charge_is_not_stranded(db, monkeypatch):
    """Money that went back to the customer isn't owed a pass. Without this the
    charge would sit on the dashboard forever, demanding a pass nobody wants —
    and a permanent false alarm is how the real alert gets ignored."""
    _configured(monkeypatch)
    intent = _intent("pi_refunded", _md())
    intent.latest_charge = _FakeCharge(refunded=True, amount_refunded=2000)
    _listing(monkeypatch, [intent])

    assert stranded_charges(days=7, db=db, _user=_FakeUser()) == []


def test_a_partially_refunded_charge_is_still_stranded(db, monkeypatch):
    """Half the money back is still money held with no pass behind it."""
    _configured(monkeypatch)
    intent = _intent("pi_partial", _md())
    intent.latest_charge = _FakeCharge(refunded=False, amount_refunded=500)  # $5 of $20
    _listing(monkeypatch, [intent])

    assert len(stranded_charges(days=7, db=db, _user=_FakeUser())) == 1


def test_an_amount_mismatch_says_it_needs_a_human(db, monkeypatch):
    """The one case a click must NOT auto-fix: Stripe charged something other than
    what we quoted. Issuing a pass would paper over a real discrepancy."""
    _configured(monkeypatch)
    db.add(
        PaymentRequest(
            token="tok_mismatch",
            kind="issue",
            amount=250.0,
            status="pending",
            summary="Mismatch Freight · Monthly",
            payload_json=json.dumps({"company_name": "Mismatch Freight", "pass_type": "monthly",
                                     "issue_date": date.today().isoformat(), "vehicle_type": "truck"}),
        )
    )
    db.commit()
    _listing(monkeypatch, [_intent("pi_mismatch", {"payment_request_token": "tok_mismatch"}, amount=2000)])

    result = stranded_charges(days=7, db=db, _user=_FakeUser())

    assert len(result) == 1
    assert "needs a human" in result[0].reason
    assert "$20.00" in result[0].reason and "$250.00" in result[0].reason


def test_one_click_issues_the_pass_the_customer_paid_for(db, monkeypatch):
    _configured(monkeypatch)
    intent = _intent("pi_repair", _md(truck_number="9001"))
    monkeypatch.setattr(stripe.PaymentIntent, "retrieve", lambda pid: intent)

    parking_pass = issue_stranded_pass("pi_repair", db=db, _user=_FakeUser())

    assert float(parking_pass.price) == 20.0
    assert db.get(ParkingPass, parking_pass.id) is not None
    # And it now drops off the stranded list.
    _listing(monkeypatch, [intent])
    assert stranded_charges(days=7, db=db, _user=_FakeUser()) == []


def test_one_click_refuses_a_charge_that_is_not_ours(db, monkeypatch):
    _configured(monkeypatch)
    intent = _intent("pi_foreign", {"note": "manual charge"})
    monkeypatch.setattr(stripe.PaymentIntent, "retrieve", lambda pid: intent)

    with pytest.raises(HTTPException) as exc:
        issue_stranded_pass("pi_foreign", db=db, _user=_FakeUser())
    assert exc.value.status_code == 400
