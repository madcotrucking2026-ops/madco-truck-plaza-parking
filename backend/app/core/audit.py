from sqlalchemy.orm import Session

from app.models import AuditLog
from app.models.enums import AuditAction


def log_audit(
    db: Session,
    action: AuditAction,
    entity_type: str,
    summary: str,
    entity_id: int | None = None,
    employee_name: str | None = None,
) -> None:
    db.add(
        AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            summary=summary,
            employee_name=employee_name,
        )
    )
