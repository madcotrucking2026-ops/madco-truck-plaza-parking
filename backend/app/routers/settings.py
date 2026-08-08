"""Owner-editable settings: parking capacity + default daily/weekly/monthly
prices. Any signed-in staff can READ them (the issue form previews a charge from
the live prices); only an admin can CHANGE them."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.app_settings import effective, save_overrides
from app.core.audit import log_audit
from app.core.database import get_db
from app.core.deps import require_admin
from app.core.spots import ensure_spots
from app.models.enums import AuditAction
from app.schemas.app_settings import AppSettingsRead, AppSettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=AppSettingsRead)
def get_settings() -> AppSettingsRead:
    return AppSettingsRead(**effective())


@router.put("", response_model=AppSettingsRead, dependencies=[Depends(require_admin)])
def update_settings(payload: AppSettingsUpdate, db: Session = Depends(get_db)) -> AppSettingsRead:
    before = effective()
    save_overrides(db, payload.model_dump())
    if payload.parking_capacity != before["parking_capacity"]:
        # Reshape the painted lot to the new size. ensure_spots is idempotent and
        # never deletes a spot — it activates rows up to capacity and deactivates
        # any above it (history preserved).
        ensure_spots(db)
    log_audit(
        db,
        AuditAction.edited,
        "settings",
        f"Settings updated — capacity {before['parking_capacity']}→{payload.parking_capacity}, "
        f"daily ${payload.daily_price:.0f}, weekly ${payload.weekly_price:.0f}, "
        f"monthly ${payload.monthly_price:.0f}",
        entity_id=None,
    )
    db.commit()
    return AppSettingsRead(**effective())
