from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from app.models.enums import PassType, VehicleType

# This request comes from the PUBLIC kiosk — no login. Every field is attacker
# controlled, so every field is bounded. Unbounded strings here would flow
# straight into Stripe metadata and into the database.
NAME_MAX = 255
IDENT_MAX = 64
PHONE_MAX = 32
# Two years. Nobody prepays truck parking further out, and without a cap a
# crafted end_date turns into an absurd price (and an absurd Stripe charge).
MAX_PASS_DAYS = 730


class CreateIntentRequest(BaseModel):
    # A stable id the frontend generates once per checkout attempt (not
    # regenerated on every render/retry) — forwarded to Stripe as an
    # idempotency key so a double-click or network retry can never mint two
    # separate PaymentIntents for the same attempt.
    client_request_id: str = Field(min_length=1, max_length=IDENT_MAX)
    company_name: str = Field(min_length=1, max_length=NAME_MAX)
    truck_number: str | None = Field(default=None, max_length=IDENT_MAX)
    trailer_number: str | None = Field(default=None, max_length=IDENT_MAX)
    license_plate: str | None = Field(default=None, max_length=IDENT_MAX)
    phone: str = Field(min_length=1, max_length=PHONE_MAX)
    vehicle_type: VehicleType
    pass_type: PassType
    issue_date: date
    end_date: date | None = None

    @model_validator(mode="after")
    def _sane_span(self):
        if self.end_date is not None:
            if self.end_date <= self.issue_date:
                raise ValueError("end_date must be after issue_date")
            if (self.end_date - self.issue_date).days > MAX_PASS_DAYS:
                raise ValueError(f"A pass cannot run longer than {MAX_PASS_DAYS} days")
        return self


class CreateIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: float


class FinalizeStripePaymentRequest(BaseModel):
    # Deliberately just the intent id — every pass detail (company, truck,
    # dates, etc.) is read back from the PaymentIntent's own Stripe metadata,
    # recorded server-side at create-intent time. A client can no longer
    # submit different pass details than what was actually priced and paid for.
    payment_intent_id: str = Field(min_length=1, max_length=IDENT_MAX)


class CancelIntentRequest(BaseModel):
    payment_intent_id: str = Field(min_length=1, max_length=IDENT_MAX)


class StrandedCharge(BaseModel):
    """A card Stripe says we charged, for which no pass exists in our system.

    This should always be an empty list. If it isn't, a real customer paid real
    money and got nothing — so it is stated in exactly those terms, with enough
    detail to find the truck and fix it in one click.
    """

    payment_intent_id: str
    amount: float
    charged_at: datetime
    company_name: str | None
    vehicle: str | None
    reason: str
