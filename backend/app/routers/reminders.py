"""Read-only "renewals due" list — which monthly customers renew when. The plaza
went text-free (no SMS), so nothing is sent from here; the same data feeds the
dashboard's "Renewals due soon" card and the morning report."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clock import business_today
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import MonthlyCustomer, Reminder, User
from app.schemas.reminder import ReminderCustomer, RemindersOverview

router = APIRouter(prefix="/api/reminders", tags=["reminders"])


def monthly_renewal_list(db: Session) -> list[ReminderCustomer]:
    """Every monthly customer with how their renewal stands, soonest first. Shared
    with the morning report so "who renews when" is answered in exactly one place."""
    today = business_today()
    customers: list[ReminderCustomer] = []
    for mc in db.scalars(select(MonthlyCustomer).order_by(MonthlyCustomer.renewal_date)):
        last = db.scalar(
            select(Reminder)
            .where(Reminder.monthly_customer_id == mc.id, Reminder.sent_at.is_not(None))
            .order_by(Reminder.sent_at.desc())
        )
        customers.append(
            ReminderCustomer(
                monthly_customer_id=mc.id,
                company_name=mc.company.name if mc.company else "—",
                phone=mc.company.phone if mc.company else None,
                monthly_price=float(mc.monthly_price),
                renewal_date=mc.renewal_date,
                days_until_renewal=(mc.renewal_date - today).days,
                reminder_status=mc.reminder_status.value,
                last_reminder_at=last.sent_at if last else None,
            )
        )
    return customers


@router.get("", response_model=RemindersOverview)
def list_reminders(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> RemindersOverview:
    return RemindersOverview(customers=monthly_renewal_list(db))
