from datetime import date

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.stripe_client import is_configured
from app.models import ParkingPass, Payment
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import (
    _expiration_for,
    _issue_pass_and_payment,
    _lookup_monthly_rate,
    _price_for,
    _validate_weekly_span,
)
from app.schemas.pass_ import PassRead
from app.schemas.stripe_payment import (
    CancelIntentRequest,
    CreateIntentRequest,
    CreateIntentResponse,
    FinalizeStripePaymentRequest,
)

router = APIRouter(prefix="/api/payments/stripe", tags=["stripe"])


def _require_configured() -> None:
    if not is_configured():
        raise HTTPException(status_code=503, detail="Card payments aren't set up yet — please pay cash or check inside.")


def _compute_price(db: Session, company_name: str, pass_type: PassType, issue_date: date, end_date: date | None) -> tuple:
    """The single source of truth both create-intent and (as a sanity check
    only, not a trust boundary) finalize use for what a pass SHOULD cost."""
    expiration_date = _expiration_for(pass_type, issue_date, end_date)
    monthly_rate = None
    if pass_type == PassType.monthly:
        monthly_rate = _lookup_monthly_rate(db, company_name)
        if monthly_rate is None:
            raise HTTPException(
                status_code=400,
                detail=f"{company_name} isn't set up for monthly parking yet — please see the front desk.",
            )
    price = _price_for(pass_type, issue_date, expiration_date, None, monthly_rate)
    return expiration_date, price


def _metadata_from_payload(payload: CreateIntentRequest) -> dict:
    """Stripe metadata values must be strings — this is the ONLY record of
    what a customer is actually paying for; finalize/webhook read it back
    instead of trusting anything resubmitted by the client."""
    return {
        "company_name": payload.company_name,
        "phone": payload.phone,
        "vehicle_type": payload.vehicle_type.value,
        "truck_number": payload.truck_number or "",
        "trailer_number": payload.trailer_number or "",
        "license_plate": payload.license_plate or "",
        "pass_type": payload.pass_type.value,
        "issue_date": payload.issue_date.isoformat(),
        "end_date": payload.end_date.isoformat() if payload.end_date else "",
    }


def _finalize_intent(db: Session, intent) -> ParkingPass:
    """Shared by the client-driven /finalize call (fast path, for immediate
    UI feedback) and the Stripe webhook (safety-net path, for when the
    customer's tab dies before /finalize ever gets called). Idempotent and
    race-safe: whichever of the two runs first creates the pass; the other
    just returns the same result.
    """
    if intent.status != "succeeded":
        raise HTTPException(status_code=400, detail="Payment has not completed yet.")

    existing = db.scalar(select(Payment).where(Payment.stripe_payment_intent_id == intent.id))
    if existing is not None:
        return db.get(ParkingPass, existing.parking_pass_id)

    # intent.metadata is a Stripe SDK StripeObject, not a plain dict — it
    # has no .get()/.keys()/.items(), and dict(obj) misfires (falls back to
    # sequence-style integer indexing). `.to_dict()` is the SDK's own
    # supported conversion; do this once so every access below is a normal dict.
    md = intent.metadata.to_dict() if intent.metadata else {}
    if "company_name" not in md or "pass_type" not in md or "issue_date" not in md:
        raise HTTPException(status_code=400, detail="This payment isn't linked to a parking pass request.")

    pass_type = PassType(md["pass_type"])
    issue_date = date.fromisoformat(md["issue_date"])
    end_date = date.fromisoformat(md["end_date"]) if md.get("end_date") else None

    try:
        return _issue_pass_and_payment(
            db,
            company_name=md["company_name"],
            phone=md.get("phone", ""),
            vehicle_type=VehicleType(md.get("vehicle_type") or "truck"),
            truck_number=md.get("truck_number") or None,
            trailer_number=md.get("trailer_number") or None,
            license_plate=md.get("license_plate") or None,
            pass_type=pass_type,
            issue_date=issue_date,
            end_date=end_date,
            price_override=None,
            payment_method=PaymentMethod.credit_card,
            check_number=None,
            stripe_payment_intent_id=intent.id,
            # The amount Stripe actually confirms it charged IS the price —
            # never recompute a possibly-drifted number here.
            price_from_charge=intent.amount_received / 100,
        )
    except IntegrityError:
        # Lost a race against the other finalization path (webhook vs the
        # client's own /finalize call) — the unique constraint on
        # stripe_payment_intent_id caught it; return whatever it created.
        db.rollback()
        existing = db.scalar(select(Payment).where(Payment.stripe_payment_intent_id == intent.id))
        if existing is not None:
            return db.get(ParkingPass, existing.parking_pass_id)
        raise


@router.post("/create-intent", response_model=CreateIntentResponse)
def create_intent(payload: CreateIntentRequest, db: Session = Depends(get_db)) -> CreateIntentResponse:
    _require_configured()
    _validate_weekly_span(payload.pass_type, payload.issue_date, payload.end_date)
    _, price = _compute_price(db, payload.company_name, payload.pass_type, payload.issue_date, payload.end_date)

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(round(float(price) * 100)),
            currency="usd",
            payment_method_types=["card"],
            metadata=_metadata_from_payload(payload),
            idempotency_key=f"create-intent-{payload.client_request_id}",
        )
    except stripe.error.StripeError as exc:
        raise HTTPException(status_code=502, detail=f"Payment setup failed: {exc.user_message or 'please try again.'}") from exc

    return CreateIntentResponse(client_secret=intent.client_secret, payment_intent_id=intent.id, amount=price)


@router.post("/finalize", response_model=PassRead)
def finalize(payload: FinalizeStripePaymentRequest, db: Session = Depends(get_db)):
    _require_configured()
    try:
        intent = stripe.PaymentIntent.retrieve(payload.payment_intent_id)
    except stripe.error.StripeError as exc:
        raise HTTPException(status_code=502, detail="Could not verify payment with Stripe — please try again.") from exc
    return _finalize_intent(db, intent)


@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    """Safety net for the case where a customer's card is charged but their
    tab/network dies before the frontend's own /finalize call ever reaches
    us — Stripe retries this webhook until it gets a 200, so a charge can
    never silently vanish with no local record as long as this is configured.
    Requires STRIPE_WEBHOOK_SECRET (from the Stripe Dashboard's webhook
    endpoint settings) — refuses to run without it rather than skip signature
    verification.
    """
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook not configured.")

    body = await request.body()
    signature = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(body, signature, settings.stripe_webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as exc:
        raise HTTPException(status_code=400, detail="Invalid webhook signature.") from exc

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        md = intent.metadata.to_dict() if intent.metadata else {}
        # This safety-net only owns the kiosk direct-pay intents, which carry the
        # full pass metadata (company_name etc). Payment-request intents finalize
        # via their own client-driven route, and unrelated charges (e.g. a manual
        # Dashboard charge) aren't ours at all — ack and ignore both so Stripe
        # doesn't retry a payment we can't turn into a pass for ~3 days.
        if "company_name" in md:
            _finalize_intent(db, intent)

    return {"received": True}


@router.post("/cancel-intent")
def cancel_intent(payload: CancelIntentRequest) -> dict:
    """Best-effort cleanup when a customer abandons checkout. This endpoint is
    unauthenticated (the kiosk/self-pay pages are public), so it will ONLY cancel
    a PaymentIntent that THIS app created — recognised by our own metadata marker.
    Without that check a leaked pi_ id would let anyone cancel any pending intent."""
    if not is_configured():
        return {"cancelled": False}
    try:
        intent = stripe.PaymentIntent.retrieve(payload.payment_intent_id)
        md = intent.metadata.to_dict() if intent.metadata else {}
        if "company_name" not in md and "payment_request_token" not in md:
            return {"cancelled": False}  # not one of ours — refuse to touch it
        stripe.PaymentIntent.cancel(payload.payment_intent_id)
    except stripe.error.StripeError:
        pass  # already succeeded/canceled/unknown — best-effort cleanup only
    return {"cancelled": True}
