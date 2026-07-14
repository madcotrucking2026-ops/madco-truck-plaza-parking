from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import User
from app.models.enums import EmployeeRole

# auto_error=False so a missing header raises our own 401 (with a clear
# message) instead of FastAPI's generic one.
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=401,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise unauthorized

    try:
        user = db.get(User, int(user_id))
    except (TypeError, ValueError):
        # Only reachable with a forged/corrupt token — a malformed `sub`
        # claim should still just be "not authenticated", not a 500.
        raise unauthorized from None

    if user is None or not user.is_active:
        raise unauthorized

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != EmployeeRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required.")
    return current_user


def require_manager(current_user: User = Depends(get_current_user)) -> User:
    """Admin or manager — the money tier.

    An attendant's job is the front desk: issue, renew, look up, remind. Revenue
    totals, payment history, reports and the audit trail are the owner's business,
    not something every seasonal hire with a login can browse.
    """
    if current_user.role not in (EmployeeRole.admin, EmployeeRole.manager):
        raise HTTPException(status_code=403, detail="Manager access required.")
    return current_user
