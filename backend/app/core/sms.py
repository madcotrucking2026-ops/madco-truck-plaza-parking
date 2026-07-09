import re

from app.core.config import settings
from app.core.logging_config import get_logger

log = get_logger(__name__)


def is_configured() -> bool:
    return bool(settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_from_number)


def to_e164(phone: str | None) -> str | None:
    """Twilio requires E.164 (+15551234567). Customer phones are stored loosely
    ('313-555-0100', '3135550100'); normalize a US 10- or 11-digit number.
    Returns None if it can't be made into a plausible number."""
    if not phone:
        return None
    if phone.strip().startswith("+"):
        return phone.strip()
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return None


def send_sms(to_number: str, body: str) -> bool:
    """Send an SMS via Twilio. Returns True if it went out, False if SMS isn't
    configured or the number is unusable (the caller still records the reminder
    either way). Never raises to the request path — a texting failure must not
    break the app flow."""
    if not is_configured():
        return False
    to = to_e164(to_number)
    if to is None:
        log.warning("Skipping SMS — unusable phone number: %r", to_number)
        return False
    try:
        from twilio.rest import Client

        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        # Prefer the registered A2P Messaging Service; fall back to the raw
        # from-number if no service SID is configured.
        if settings.twilio_messaging_service_sid:
            client.messages.create(
                to=to, messaging_service_sid=settings.twilio_messaging_service_sid, body=body
            )
        else:
            client.messages.create(to=to, from_=settings.twilio_from_number, body=body)
        log.info("Sent reminder SMS to %s", to)
        return True
    except Exception:  # noqa: BLE001 — texting must never crash the request
        log.exception("Failed to send reminder SMS to %s", to)
        return False
