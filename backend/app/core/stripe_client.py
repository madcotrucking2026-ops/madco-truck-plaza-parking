import stripe

from app.core.config import settings

stripe.api_key = settings.stripe_secret_key


def is_configured() -> bool:
    return bool(settings.stripe_secret_key)
