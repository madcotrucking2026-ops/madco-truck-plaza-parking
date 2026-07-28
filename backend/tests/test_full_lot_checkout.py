"""Never take a card for a spot that doesn't exist. Pre-check at intent time."""
from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.core.spots import ensure_spots
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment


def _fill_the_lot(db):
    _issue_pass_and_payment(
        db, company_name="Filler", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number="F1", trailer_number=None, license_plate=None, pass_type=PassType.daily,
        issue_date=business_today(), end_date=business_today() + timedelta(days=1),
        price_override=None, payment_method=PaymentMethod.cash, check_number=None,
    )
    db.commit()


def test_kiosk_refuses_when_full(db, client, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 1)
    monkeypatch.setattr("app.routers.stripe_payments.is_configured", lambda: True)
    ensure_spots(db)
    _fill_the_lot(db)

    r = client.post("/api/payments/stripe/create-intent", json={
        "client_request_id": "abc123", "company_name": "Latecomer", "phone": "313-555-0101",
        "vehicle_type": "truck", "truck_number": "L1", "pass_type": "daily",
        "issue_date": business_today().isoformat(),
    })
    assert r.status_code == 409
    assert "full" in r.json()["detail"].lower()


def test_pay_link_refuses_new_pass_when_full_but_allows_renewal(db, client, monkeypatch):
    """A pay-link for a NEW pass needs a spot; a renewal already holds one and
    must never be blocked — refusing a renewal would push a paying customer
    into lapsing."""
    import json
    from app.models import ParkingPass, PaymentRequest

    monkeypatch.setattr(settings, "parking_capacity", 1)
    monkeypatch.setattr("app.routers.payment_requests.is_configured", lambda: True)
    ensure_spots(db)
    _fill_the_lot(db)
    held_pass = db.query(ParkingPass).first()

    issue_req = PaymentRequest(
        token="tok_full_issue", kind="issue", amount=20.0, status="pending",
        summary="New pass while full",
        payload_json=json.dumps({"company_name": "Latecomer", "pass_type": "daily"}),
    )
    renew_req = PaymentRequest(
        token="tok_full_renew", kind="renew", amount=20.0, status="pending",
        summary="Renewal while full",
        payload_json=json.dumps({"pass_id": held_pass.id, "end_date": business_today().isoformat()}),
    )
    db.add_all([issue_req, renew_req])
    db.commit()

    r = client.post("/api/payment-requests/tok_full_issue/create-intent")
    assert r.status_code == 409
    assert "full" in r.json()["detail"].lower()

    # Renewal reaches Stripe (fails 502 on the fake key path or succeeds in test
    # mode — either way it is NOT the 409 full-lot refusal).
    r2 = client.post("/api/payment-requests/tok_full_renew/create-intent")
    assert r2.status_code != 409
