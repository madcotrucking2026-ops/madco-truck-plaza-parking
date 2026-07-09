from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# A precomputed hash of a fixed, non-secret string — verified against on
# login when no matching email exists, so the bcrypt comparison always runs
# and takes the same time either way. Without this, "no such user" returns
# near-instantly (short-circuits before ever calling verify_password) while
# "wrong password for a real account" takes bcrypt's full ~100-300ms, letting
# an attacker distinguish valid emails from invalid ones purely by timing.
DUMMY_PASSWORD_HASH = pwd_context.hash("not-a-real-password-timing-safety-only")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload.get("sub")
    except jwt.JWTError:
        return None
