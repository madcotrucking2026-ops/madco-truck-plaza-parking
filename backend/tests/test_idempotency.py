"""A single Stripe PaymentIntent can never mint two passes."""

from datetime import date

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.models import ParkingPass, Payment
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment


def _issue_with_intent(db, intent_id):
    return _issue_pass_and_payment(
        db,
        company_name="Hauler Co",
        phone="555",
        vehicle_type=VehicleType.truck,
        truck_number="7834",
        trailer_number=None,
        license_plate=None,
        pass_type=PassType.daily,
        issue_date=date(2026, 7, 1),
        end_date=None,
        price_override=None,
        payment_method=PaymentMethod.credit_card,
        check_number=None,
        stripe_payment_intent_id=intent_id,
        price_from_charge=20.0,
    )


def test_duplicate_payment_intent_is_rejected(db):
    _issue_with_intent(db, "pi_test_123")
    # The unique constraint on payments.stripe_payment_intent_id is the guard the
    # finalize endpoints rely on to stay idempotent under a race.
    with pytest.raises(IntegrityError):
        _issue_with_intent(db, "pi_test_123")
    db.rollback()

    # Exactly one payment/pass exists for that intent.
    count = db.scalar(select(func.count()).select_from(Payment).where(Payment.stripe_payment_intent_id == "pi_test_123"))
    assert count == 1
    assert db.scalar(select(func.count()).select_from(ParkingPass)) == 1


def test_price_from_charge_is_used_verbatim(db):
    # The charged amount is the price of record — never a recomputed number.
    p = _issue_with_intent(db, "pi_test_456")
    assert float(p.price) == 20.0
    payment = db.scalar(select(Payment).where(Payment.stripe_payment_intent_id == "pi_test_456"))
    assert float(payment.amount) == 20.0
