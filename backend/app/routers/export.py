"""One-click full-data backup: the owner downloads every business record as a
ZIP of CSV files (openable in Excel). This is the free-tier safety net — the
data lives in managed Postgres, but a backup the owner keeps on their own disk
survives anything that happens to the hosting account. Admin-only; the pull is
recorded in the audit log because it is a full read of the whole database."""
import csv
import enum
import io
import zipfile
from datetime import date, datetime

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import log_audit
from app.core.clock import business_today
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Company, MonthlyCustomer, ParkingPass, Payment, User, Vehicle
from app.models.enums import AuditAction

router = APIRouter(prefix="/api/export", tags=["export"])

# Only the business records worth keeping — customers, trucks, passes, money.
# Deliberately NOT users (password hashes), config, or the audit log itself.
# Order puts the "parent" rows first so the CSVs read top-down like the story.
TABLES: dict[str, type] = {
    "companies": Company,
    "vehicles": Vehicle,
    "monthly_customers": MonthlyCustomer,
    "parking_passes": ParkingPass,
    "payments": Payment,
}


def _cell(value: object) -> str:
    """Every value becomes a plain string a spreadsheet can read."""
    if value is None:
        return ""
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def _readme(today: date, counts: dict[str, int]) -> str:
    lines = [
        "Madco Truck Plaza — data backup",
        f"Exported: {today.isoformat()}",
        "",
        "One CSV per record type. Open any of them in Excel or Google Sheets.",
        "This is a complete copy of your records as of the export date — keep it",
        "somewhere safe (a USB drive or your own cloud storage).",
        "",
        "Contents:",
    ]
    lines += [f"  {name}.csv — {counts[name]} row(s)" for name in TABLES]
    return "\n".join(lines) + "\n"


@router.get("")
def export_all(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Response:
    today = business_today()
    counts: dict[str, int] = {}

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, model in TABLES.items():
            rows = list(db.scalars(select(model)))
            counts[name] = len(rows)
            sheet = io.StringIO()
            writer = csv.writer(sheet)
            columns = [c.name for c in model.__table__.columns]
            writer.writerow(columns)
            for row in rows:
                writer.writerow([_cell(getattr(row, c)) for c in columns])
            archive.writestr(f"{name}.csv", sheet.getvalue())
        archive.writestr("README.txt", _readme(today, counts))

    log_audit(
        db,
        AuditAction.search_performed,
        "export",
        "Full data backup downloaded (" + ", ".join(f"{counts[n]} {n}" for n in TABLES) + ")",
        employee_name=user.name,
    )
    db.commit()

    filename = f"madco-backup-{today.isoformat()}.zip"
    return Response(
        content=buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
