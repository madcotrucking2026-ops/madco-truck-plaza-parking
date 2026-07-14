from datetime import UTC, date, datetime, timedelta

import stripe
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import require_manager
from app.core.logging_config import get_logger
from app.core.rate_limit import checkout_limiter
from app.core.stripe_client import is_configured
from app.models import ParkingPass, Payment, PaymentRequest, User
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
    StrandedCharge,
)

router = APIRouter(prefix="/api/payments/stripe", tags=["stripe"])
log = get_logger(__name__)


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


@router.post(
    "/create-intent",
    response_model=CreateIntentResponse,
    # Public + unauthenticated, and every call mints a real PaymentIntent on the
    # plaza's Stripe account. Throttle it.
    dependencies=[Depends(checkout_limiter)],
)
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


@router.post("/finalize", response_model=PassRead, dependencies=[Depends(checkout_limiter)])
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

        if "company_name" in md:
            # Kiosk direct-pay: the intent carries the full pass metadata.
            _finalize_intent(db, intent)

        elif "payment_request_token" in md:
            # A manager-created pay link. This branch used to be missing: the
            # event was acked and dropped, so a customer whose phone died after
            # paying left us holding their money with no pass issued and the
            # request stuck on "pending", with nothing to reconcile it.
            _finalize_payment_request(db, md["payment_request_token"], intent)

        # Anything else (e.g. a charge created by hand in the Stripe Dashboard)
        # isn't ours — ack it so Stripe stops retrying for ~3 days.

    return {"received": True}


def _finalize_payment_request(db: Session, token: str, intent) -> None:
    """Webhook safety net for pay-link payments. Imported lazily to keep the
    router import graph acyclic."""
    from app.routers.payment_requests import finalize_request

    req = db.scalar(select(PaymentRequest).where(PaymentRequest.token == token))
    if req is None:
        log.warning("Webhook: no payment request for token=%s intent=%s", token, intent.id)
        return  # nothing to reconcile; ack so Stripe stops retrying

    try:
        finalize_request(db, req, intent)
    except HTTPException as exc:
        # A permanent problem (e.g. the charged amount doesn't match the quote).
        # Retrying will never fix it, so log loudly and ack rather than let Stripe
        # hammer us for three days — but this is money taken with no pass, and it
        # needs a human.
        db.rollback()
        log.error(
            "Webhook could NOT finalize a paid request — money taken, no pass. "
            "token=%s intent=%s reason=%s",
            token, intent.id, exc.detail,
        )


def _refunded(intent) -> bool:
    """Was this charge given back? A refunded card is not stranded money — the
    customer is square with us, so it must not sit on the dashboard forever
    demanding a pass that nobody is owed."""
    charge = getattr(intent, "latest_charge", None)
    if charge is None or isinstance(charge, str):  # not expanded — assume not refunded
        return False
    if getattr(charge, "refunded", False):
        return True
    refunded = getattr(charge, "amount_refunded", 0) or 0
    return refunded >= (intent.amount_received or 0)


def _ours(md: dict) -> bool:
    """Was this charge created by this app? (A charge made by hand in the Stripe
    Dashboard is not ours to reconcile, and must never be reported as stranded.)"""
    return "company_name" in md or "payment_request_token" in md


@router.get("/stranded", response_model=list[StrandedCharge])
def stranded_charges(
    days: int = Query(default=7, ge=1, le=90),
    db: Session = Depends(get_db),
    _user: User = Depends(require_manager),
) -> list[StrandedCharge]:
    """Cards Stripe accepted that produced no pass here — money taken, nothing given.

    The webhook and the browser retries mean this list should always be empty. It
    exists because "should" isn't good enough where money is concerned: if the
    webhook secret is missing in production, or a charge lands while the app is
    down for longer than Stripe retries, the ONLY trace today is a log line nobody
    reads. This turns that into something the manager actually sees.
    """
    if not is_configured():
        return []

    since = int((datetime.now(tz=UTC) - timedelta(days=days)).timestamp())
    stranded: list[StrandedCharge] = []

    listing = stripe.PaymentIntent.list(created={"gte": since}, limit=100, expand=["data.latest_charge"])
    for intent in listing.auto_paging_iter():
        if intent.status != "succeeded":
            continue
        md = intent.metadata.to_dict() if intent.metadata else {}
        if not _ours(md):
            continue
        if db.scalar(select(Payment).where(Payment.stripe_payment_intent_id == intent.id)) is not None:
            continue  # reconciled — this charge has its pass
        if _refunded(intent):
            continue  # the customer got their money back; nothing is owed to them

        company = md.get("company_name")
        vehicle = md.get("truck_number") or md.get("trailer_number") or md.get("license_plate") or None
        reason = "No pass was issued for this charge."
        if token := md.get("payment_request_token"):
            req = db.scalar(select(PaymentRequest).where(PaymentRequest.token == token))
            if req is not None:
                company = req.summary
                if abs(intent.amount_received / 100 - float(req.amount)) > 0.01:
                    reason = (
                        f"Charged ${intent.amount_received / 100:.2f} but the request was "
                        f"for ${float(req.amount):.2f} — needs a human before a pass is issued."
                    )

        stranded.append(
            StrandedCharge(
                payment_intent_id=intent.id,
                amount=intent.amount_received / 100,
                charged_at=datetime.fromtimestamp(intent.created, tz=UTC),
                company_name=company,
                vehicle=vehicle,
                reason=reason,
            )
        )

    if stranded:
        log.error("%d charge(s) have no pass — customers paid and got nothing.", len(stranded))
    return stranded


@router.post("/stranded/{payment_intent_id}/issue", response_model=PassRead)
def issue_stranded_pass(
    payment_intent_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(require_manager),
):
    """One-click repair for a stranded charge: issue the pass the customer paid for.

    Runs the same finalize path the webhook would have — so it re-reads the pass
    details from Stripe's own record of what was bought, never from the caller.
    """
    _require_configured()
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    except stripe.error.StripeError as exc:
        raise HTTPException(status_code=502, detail="Could not reach Stripe — please try again.") from exc

    md = intent.metadata.to_dict() if intent.metadata else {}
    if not _ours(md):
        raise HTTPException(status_code=400, detail="That charge wasn't created by this system.")

    if token := md.get("payment_request_token"):
        from app.routers.payment_requests import finalize_request  # lazy: keeps the router graph acyclic

        req = db.scalar(select(PaymentRequest).where(PaymentRequest.token == token))
        if req is None:
            raise HTTPException(status_code=404, detail="The payment request for this charge is gone.")
        parking_pass = finalize_request(db, req, intent)
    else:
        parking_pass = _finalize_intent(db, intent)

    log.info("Stranded charge repaired by hand: intent=%s pass_id=%s", intent.id, parking_pass.id)
    return parking_pass


@router.post("/cancel-intent", dependencies=[Depends(checkout_limiter)])
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
