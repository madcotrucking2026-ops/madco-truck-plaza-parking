from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import AuditLog
from app.schemas.audit_log import AuditLogRead

router = APIRouter(prefix="/api/audit-log", tags=["audit-log"])


@router.get("", response_model=list[AuditLogRead])
def list_audit_log(limit: int = Query(100, le=500), db: Session = Depends(get_db)) -> list[AuditLog]:
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    return list(db.scalars(stmt))
