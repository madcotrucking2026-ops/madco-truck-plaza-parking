import hashlib
import hmac

from app.core.config import settings

# Signed, tamper-proof token embedded in each pass's QR code. The QR encodes a
# verify URL ending in `<pass_id>.<signature>`; a guard scanning it hits the
# public verify endpoint, which re-derives the signature and refuses anything
# that doesn't match. Because the HMAC key is the per-install secret, nobody
# can fabricate a valid token for an arbitrary pass id — a printed fake pass
# with a made-up code fails signature verification instead of resolving.

_SIG_LEN = 32  # hex chars of the truncated HMAC-SHA256 (128 bits) kept in the token


def _sign(pass_id: int) -> str:
    return hmac.new(settings.jwt_secret.encode(), str(pass_id).encode(), hashlib.sha256).hexdigest()[:_SIG_LEN]


def make_pass_token(pass_id: int) -> str:
    return f"{pass_id}.{_sign(pass_id)}"


def verify_pass_token(token: str) -> int | None:
    """Returns the pass id if the token's signature is valid, else None."""
    if not token or "." not in token:
        return None
    pid_str, _, sig = token.rpartition(".")
    try:
        pass_id = int(pid_str)
    except ValueError:
        return None
    if hmac.compare_digest(sig, _sign(pass_id)):  # constant-time compare
        return pass_id
    return None
