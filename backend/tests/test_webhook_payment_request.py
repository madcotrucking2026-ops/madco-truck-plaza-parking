"""The webhook safety net for manager-created pay links.

The bug this guards: the webhook only finalized KIOSK intents (the ones carrying
`company_name` in metadata). A pay-link intent carries `payment_request_token`
instead, so it was acked and dropped — a customer whose phone died right after
their card cleared left us holding their money with no pass issued and the
request stuck on "pending", and nothing would ever reconcile it.
"""

import json
from datetime import date

import stripe
from sqlalchemy import func, select

from app.core.config import settings
from app.models import ParkingPass, Payment, PaymentRequest
from app.routers.stripe_payments import _finalize_payment_request
from tests.test_stripe_finalize import _FakeIntent


def _pending_request(db, token="tok_abc", amount=20.0):
    req = PaymentRequest(
        token=token,
        kind="issue",
        amount=amount,
        status="pending",
        summary="Daily pass — Truck 7834",
        payload_json=json.dumps(
            {
                "company_name": "Roadside Freight",
                "phone": "313-555-0142",
                "vehicle_type": "truck",
                "truck_number": "7834",
                "pass_type": "daily",
                "issue_date": date.today().isoformat(),
            }
        ),
    )
    db.add(req)
    db.commit()
    return req


def test_webhook_issues_the_pass_when_the_customer_never_calls_finalize(db):
    """Customer pays, phone dies. Stripe's webhook must still produce the pass."""
    req = _pending_request(db)
    intent = _FakeIntent("pi_link", "succeeded", 2000, {"payment_request_token": req.token})

    _finalize_payment_request(db, req.token, intent)

    db.refresh(req)
    assert req.status == "paid"
    assert req.parking_pass_id is not None
    parking_pass = db.get(ParkingPass, req.parking_pass_id)
    assert float(parking_pass.price) == 20.0  # what Stripe confirms it charged
    assert parking_pass.company.name == "Roadside Freight"
    payment = db.scalar(select(Payment).where(Payment.stripe_payment_intent_id == "pi_link"))
    assert payment is not None and float(payment.amount) == 20.0


def test_webhook_and_customer_finalize_do_not_double_charge(db):
    """Both paths race on a good connection. Second one must return the same pass,
    not issue a second one or record a second payment."""
    req = _pending_request(db, token="tok_race")
    intent = _FakeIntent("pi_race", "succeeded", 2000, {"payment_request_token": req.token})

    _finalize_payment_request(db, req.token, intent)
    _finalize_payment_request(db, req.token, intent)  # webhook redelivery

    assert db.scalar(select(func.count()).select_from(ParkingPass)) == 1
    assert db.scalar(select(func.count()).select_from(Payment)) == 1


def test_webhook_acks_an_amount_mismatch_instead_of_looping_forever(db):
    """If Stripe charged something other than the quote, no retry will ever fix
    it. Ack (so Stripe stops hammering us for 3 days), leave the request pending,
    and leave a loud log line for a human — do NOT issue a pass at the wrong price."""
    req = _pending_request(db, token="tok_bad", amount=250.0)
    intent = _FakeIntent("pi_bad", "succeeded", 2000, {"payment_request_token": req.token})  # $20 != $250

    _finalize_payment_request(db, req.token, intent)  # must not raise

    db.refresh(req)
    assert req.status == "pending"
    assert db.scalar(select(func.count()).select_from(ParkingPass)) == 0


def test_webhook_ignores_a_token_we_do_not_know(db):
    intent = _FakeIntent("pi_ghost", "succeeded", 2000, {"payment_request_token": "nope"})
    _finalize_payment_request(db, "nope", intent)  # must not raise
    assert db.scalar(select(func.count()).select_from(ParkingPass)) == 0


def test_webhook_endpoint_routes_a_pay_link_event_to_the_safety_net(db, client, monkeypatch):
    """The actual bug lived in the webhook's DISPATCH, not in the helper above: the
    handler only recognised intents carrying `company_name`, so a pay-link event
    fell through to a bare 200 and the charge was silently dropped. Drive the real
    endpoint (signature verification stubbed — that part is Stripe's, and it's
    covered by the fact the handler 503s when no secret is configured)."""
    req = _pending_request(db, token="tok_routed")
    intent = _FakeIntent("pi_routed", "succeeded", 2000, {"payment_request_token": req.token})

    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_test")
    monkeypatch.setattr(
        stripe.Webhook,
        "construct_event",
        lambda body, sig, secret: {"type": "payment_intent.succeeded", "data": {"object": intent}},
    )

    resp = client.post("/api/payments/stripe/webhook", content=b"{}", headers={"stripe-signature": "t=1,v1=x"})
    assert resp.status_code == 200

    db.refresh(req)
    assert req.status == "paid", "pay-link event was acked but never turned into a pass"
    assert db.get(ParkingPass, req.parking_pass_id) is not None
