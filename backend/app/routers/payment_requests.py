import json
import secrets
from datetime import date

import stripe
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.logging_config import get_logger
from app.core.rate_limit import checkout_limiter, lookup_limiter
from app.core.stripe_client import is_configured
from app.models import ParkingPass, Payment, PaymentRequest, User
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import (
    _expiration_for,
    _issue_pass_and_payment,
    _lookup_monthly_rate,
    _price_for,
    _validate_weekly_span,
    apply_renewal,
    renewal_quote,
)
from app.schemas.pass_ import PassRead
from app.schemas.payment_request import (
    CreatePaymentRequest,
    PaymentRequestCreated,
    PaymentRequestStatus,
)
from app.schemas.stripe_payment import CreateIntentResponse

router = APIRouter(prefix="/api/payment-requests", tags=["payment-requests"])
log = get_logger(__name__)


def _require_configured() -> None:
    if not is_configured():
        raise HTTPException(status_code=503, detail="Card payments aren't set up yet.")


def _vehicle_label(truck: str | None, trailer: str | None, plate: str | None) -> str:
    return truck or trailer or plate or "—"


# ---- manager-only: create a pending payment the customer will self-pay ----


@router.post("", response_model=PaymentRequestCreated)
def create_payment_request(
    payload: CreatePaymentRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> PaymentRequestCreated:
    _require_configured()

    if payload.kind == "issue":
        d = payload.issue
        if d is None:
            raise HTTPException(status_code=400, detail="Missing issue details.")
        _validate_weekly_span(d.pass_type, d.issue_date, d.end_date)
        expiration = _expiration_for(d.pass_type, d.issue_date, d.end_date)
        existing_rate = _lookup_monthly_rate(db, d.company_name)
        amount = _price_for(d.pass_type, d.issue_date, expiration, d.price, existing_rate)
        summary = f"{d.company_name} · {_vehicle_label(d.truck_number, d.trailer_number, d.license_plate)} · {d.pass_type.value.title()} pass"
        stored = d.model_dump(mode="json")
    else:
        r = payload.renew
        if r is None:
            raise HTTPException(status_code=400, detail="Missing renew details.")
        parking_pass = db.get(ParkingPass, r.pass_id)
        if parking_pass is None:
            raise HTTPException(status_code=404, detail="Pass not found.")
        _, amount = renewal_quote(db, parking_pass, r.end_date)  # validates too
        truck = _vehicle_label(parking_pass.vehicle.truck_number, parking_pass.vehicle.trailer_number, parking_pass.vehicle.license_plate)
        company = parking_pass.company.name if parking_pass.company else "—"
        summary = f"{company} · {truck} · Renew {parking_pass.pass_type.value} to {r.end_date.isoformat()}"
        stored = r.model_dump(mode="json")

    token = secrets.token_urlsafe(16)
    req = PaymentRequest(
        token=token,
        kind=payload.kind,
        payload_json=json.dumps(stored),
        amount=amount,
        summary=summary,
        status="pending",
    )
    db.add(req)
    db.commit()

    return PaymentRequestCreated(
        token=token,
        pay_url=f"{settings.public_base_url}/pay/{token}",
        amount=float(amount),
        summary=summary,
        status="pending",
    )


# ---- public: the customer's self-pay flow + the manager's status poll ----


def _get_request(db: Session, token: str) -> PaymentRequest:
    req = db.scalar(select(PaymentRequest).where(PaymentRequest.token == token))
    if req is None:
        raise HTTPException(status_code=404, detail="Payment request not found.")
    return req


# The checkout limiter (10/min) guards endpoints that MINT Stripe objects. This one
# is a cheap read, and a customer whose finalize failed polls it while waiting for
# the webhook to land — throttling that at 10/min would cut the recovery short.
@router.get("/{token}", response_model=PaymentRequestStatus, dependencies=[Depends(lookup_limiter)])
def get_payment_request(token: str, db: Session = Depends(get_db)) -> PaymentRequestStatus:
    req = _get_request(db, token)
    receipt = None
    if req.status == "paid" and req.parking_pass_id is not None:
        pass_ = db.get(ParkingPass, req.parking_pass_id)
        receipt = pass_.receipt_number if pass_ else None
    return PaymentRequestStatus(
        status=req.status, kind=req.kind, amount=float(req.amount), summary=req.summary, receipt_number=receipt
    )


@router.post(
    "/{token}/create-intent",
    response_model=CreateIntentResponse,
    dependencies=[Depends(checkout_limiter)],
)
def create_intent(token: str, db: Session = Depends(get_db)) -> CreateIntentResponse:
    _require_configured()
    req = _get_request(db, token)
    if req.status == "paid":
        raise HTTPException(status_code=409, detail="This has already been paid.")

    try:
        intent = stripe.PaymentIntent.create(
            amount=round(float(req.amount) * 100),
            currency="usd",
            payment_method_types=["card"],
            metadata={"payment_request_token": token},
            idempotency_key=f"payreq-{token}",
        )
    except stripe.error.StripeError as exc:
        raise HTTPException(status_code=502, detail=f"Payment setup failed: {exc.user_message or 'please try again.'}") from exc

    # Persist the intent id now so finalize can retrieve it directly (Stripe's
    # metadata search has indexing lag and is unreliable right after payment).
    req.stripe_payment_intent_id = intent.id
    db.commit()

    return CreateIntentResponse(client_secret=intent.client_secret, payment_intent_id=intent.id, amount=float(req.amount))


def finalize_request(db: Session, req: PaymentRequest, intent) -> ParkingPass:
    """Turn a confirmed charge into the pass this request was for.

    Shared by TWO callers, on purpose:
      * the customer's own /finalize call — the fast path, for instant feedback;
      * the Stripe webhook — the safety net, for when their phone dies or drops
        signal after the card is charged but before that call ever lands.

    Without the second caller a customer pays, loses connection, and we are left
    holding their money with no pass issued and the request stuck on "pending".
    Idempotent: whichever path gets here first creates the pass, the other one
    returns the same pass.
    """
    if req.status == "paid" and req.parking_pass_id is not None:
        return db.get(ParkingPass, req.parking_pass_id)

    if intent.status != "succeeded":
        raise HTTPException(status_code=400, detail="Payment has not completed yet.")

    charged = intent.amount_received / 100
    if abs(charged - float(req.amount)) > 0.01:
        raise HTTPException(status_code=400, detail="Charged amount doesn't match — please see the front desk.")

    data = json.loads(req.payload_json)
    try:
        if req.kind == "issue":
            parking_pass = _issue_pass_and_payment(
                db,
                company_name=data["company_name"],
                phone=data.get("phone", ""),
                vehicle_type=VehicleType(data.get("vehicle_type") or "truck"),
                truck_number=data.get("truck_number") or None,
                trailer_number=data.get("trailer_number") or None,
                license_plate=data.get("license_plate") or None,
                pass_type=PassType(data["pass_type"]),
                issue_date=date.fromisoformat(data["issue_date"]),
                end_date=date.fromisoformat(data["end_date"]) if data.get("end_date") else None,
                price_override=data.get("price"),
                payment_method=PaymentMethod.credit_card,
                check_number=None,
                stripe_payment_intent_id=intent.id,
                price_from_charge=charged,
            )
        else:
            parking_pass = db.get(ParkingPass, data["pass_id"])
            if parking_pass is None:
                raise HTTPException(status_code=404, detail="Pass not found.")
            parking_pass = apply_renewal(
                db,
                parking_pass,
                date.fromisoformat(data["end_date"]),
                PaymentMethod.credit_card,
                stripe_payment_intent_id=intent.id,
                price_from_charge=charged,
            )
    except IntegrityError:
        # A concurrent finalize already consumed this intent — reload & return.
        db.rollback()
        existing = db.scalar(select(Payment).where(Payment.stripe_payment_intent_id == intent.id))
        if existing is not None:
            req.status = "paid"
            req.parking_pass_id = existing.parking_pass_id
            req.stripe_payment_intent_id = intent.id
            db.commit()
            return db.get(ParkingPass, existing.parking_pass_id)
        raise

    req.status = "paid"
    req.parking_pass_id = parking_pass.id
    req.stripe_payment_intent_id = intent.id
    db.commit()
    log.info(
        "Card payment finalized: token=%s kind=%s $%.2f pass_id=%s intent=%s",
        req.token, req.kind, charged, parking_pass.id, intent.id,
    )
    return parking_pass


@router.post("/{token}/finalize", response_model=PassRead, dependencies=[Depends(checkout_limiter)])
def finalize(token: str, db: Session = Depends(get_db)):
    """The customer's own call, right after their card clears. The Stripe webhook
    calls finalize_request() too, as the safety net if this one never arrives."""
    _require_configured()
    req = _get_request(db, token)

    if req.status == "paid" and req.parking_pass_id is not None:
        return db.get(ParkingPass, req.parking_pass_id)

    if not req.stripe_payment_intent_id:
        raise HTTPException(status_code=400, detail="Payment hasn't started yet.")

    intent = stripe.PaymentIntent.retrieve(req.stripe_payment_intent_id)
    return finalize_request(db, req, intent)
