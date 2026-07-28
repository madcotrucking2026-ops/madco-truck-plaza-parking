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
