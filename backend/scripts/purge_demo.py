"""Wipe every piece of business data — the last step before handing the system
to the client with a clean book.

Deletes: passes, payments, payment requests, companies, vehicles, monthly
customers, reminders, audit log.
Keeps:   user accounts (logins survive the handover) and the schema.

Refuses to run without --yes, and says exactly what it is about to destroy
first. There is deliberately no partial mode: half-purged books are worse than
either state.

    .venv/Scripts/python.exe -m scripts.purge_demo --yes
    docker compose exec backend python -m scripts.purge_demo --yes
"""

import sys

from sqlalchemy import delete, func, select

from app.core.database import SessionLocal
from app.models import (
    AuditLog,
    Company,
    MonthlyCustomer,
    ParkingPass,
    Payment,
    PaymentRequest,
    Reminder,
    User,
    Vehicle,
)

# Children before parents, so foreign keys never block the wipe.
PURGE_ORDER = [
    ("payments", Payment),
    ("payment requests", PaymentRequest),
    ("reminders", Reminder),
    ("parking passes", ParkingPass),
    ("monthly customers", MonthlyCustomer),
    ("vehicles", Vehicle),
    ("companies", Company),
    ("audit log entries", AuditLog),
]


def main() -> int:
    db = SessionLocal()

    counts = [(label, db.scalar(select(func.count()).select_from(model))) for label, model in PURGE_ORDER]
    total = sum(n for _, n in counts)
    users = db.scalar(select(func.count()).select_from(User))

    print("This will PERMANENTLY delete:")
    for label, n in counts:
        print(f"  {n:>6}  {label}")
    print(f"and keep {users} user account(s). There is no undo.")

    if "--yes" not in sys.argv:
        print("\nDry run — nothing deleted. Re-run with --yes to actually purge.")
        return 0
    if total == 0:
        print("\nNothing to purge.")
        return 0

    for label, model in PURGE_ORDER:
        db.execute(delete(model))
    db.commit()
    print(f"\nPurged {total} row(s). The books are empty; logins are untouched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
