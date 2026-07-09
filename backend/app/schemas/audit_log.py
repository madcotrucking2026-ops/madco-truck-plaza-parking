from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import AuditAction


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action: AuditAction
    entity_type: str
    entity_id: int | None
    summary: str
    employee_name: str | None
    created_at: datetime
