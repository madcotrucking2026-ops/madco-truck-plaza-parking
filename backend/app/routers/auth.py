from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.core.logging_config import get_logger
from app.core.rate_limit import login_limiter, register_limiter
from app.core.security import DUMMY_PASSWORD_HASH, create_access_token, hash_password, verify_password
from app.models import SetupLock, User
from app.models.enums import EmployeeRole
from app.schemas.auth import (
    AuthStatus,
    CreateStaffUserRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserRead,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
log = get_logger(__name__)

MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def _utcnow() -> datetime:
    # Naive UTC on purpose — SQLite (this app's dev/default DB) doesn't
    # reliably round-trip tzinfo through DateTime(timezone=True), so a value
    # written as timezone-aware can come back naive on read, and comparing
    # aware-vs-naive raises TypeError. Keeping both sides of every
    # locked_until comparison naive UTC sidesteps that entirely.
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.get("/status", response_model=AuthStatus)
def auth_status(db: Session = Depends(get_db)) -> AuthStatus:
    return AuthStatus(needs_setup=db.get(SetupLock, 1) is None)


@router.post("/register", response_model=TokenResponse, dependencies=[Depends(register_limiter)])
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Bootstrap only — creates the very first account (as admin). The
    SetupLock insert is what makes this race-safe: its fixed primary key
    (id=1) means only one concurrent caller can ever succeed — a second,
    near-simultaneous request hits an IntegrityError here and never reaches
    account creation, rather than both racing past a plain existence check."""
    try:
        db.add(SetupLock(id=1))
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=403, detail="Setup has already been completed — please sign in instead.")

    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=EmployeeRole.admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(subject=str(user.id)), user=UserRead.model_validate(user))


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(login_limiter)])
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    invalid = HTTPException(status_code=401, detail="Invalid email or password")

    if user is not None and user.locked_until is not None and user.locked_until > _utcnow():
        raise HTTPException(status_code=401, detail="Too many failed attempts — please try again in a few minutes.")

    # Always run a bcrypt comparison, even when no such user exists, against
    # a fixed dummy hash — otherwise "no such email" short-circuits before
    # ever hashing and returns far faster than "wrong password for a real
    # account," letting response timing reveal which emails have accounts.
    password_ok = verify_password(payload.password, user.hashed_password if user is not None else DUMMY_PASSWORD_HASH)

    if user is None or not user.is_active or not password_ok:
        if user is not None:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
                user.locked_until = _utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
                log.warning("Account locked after %s failed logins: %s", user.failed_login_attempts, payload.email)
            db.commit()
        log.info("Failed login attempt for %s", payload.email)
        raise invalid

    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    log.info("Login OK: %s (id=%s)", user.email, user.id)
    return TokenResponse(access_token=create_access_token(subject=str(user.id)), user=UserRead.model_validate(user))


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/users", response_model=UserRead, status_code=201)
def create_staff_user(
    payload: CreateStaffUserRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> User:
    """Admin-only — adds a login for another employee, after initial setup."""
    if db.scalar(select(User).where(User.email == payload.email)) is not None:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
