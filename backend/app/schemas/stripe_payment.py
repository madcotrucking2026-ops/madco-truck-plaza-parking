from datetime import date

from pydantic import BaseModel

from app.models.enums import PassType, VehicleType


class CreateIntentRequest(BaseModel):
    # A stable id the frontend generates once per checkout attempt (not
    # regenerated on every render/retry) — forwarded to Stripe as an
    # idempotency key so a double-click or network retry can never mint two
    # separate PaymentIntents for the same attempt.
    client_request_id: str
    company_name: str
    truck_number: str | None = None
    trailer_number: str | None = None
    license_plate: str | None = None
    phone: str
    vehicle_type: VehicleType
    pass_type: PassType
    issue_date: date
    end_date: date | None = None


class CreateIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: float


class FinalizeStripePaymentRequest(BaseModel):
    # Deliberately just the intent id — every pass detail (company, truck,
    # dates, etc.) is read back from the PaymentIntent's own Stripe metadata,
    # recorded server-side at create-intent time. A client can no longer
    # submit different pass details than what was actually priced and paid for.
    payment_intent_id: str


class CancelIntentRequest(BaseModel):
    payment_intent_id: str
