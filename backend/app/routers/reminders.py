import secrets
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.audit import log_audit
from app.core.clock import business_now, business_today
from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.logging_config import get_logger
from app.core.sms import is_configured as sms_configured
from app.core.sms import send_sms
from app.models import MonthlyCustomer, Reminder, User
from app.models.enums import AuditAction, MonthlyCustomerStatus, ReminderStatus
from app.schemas.reminder import ReminderCustomer, RemindersOverview, SendReminderResult, SweepResult

router = APIRouter(prefix="/api/reminders", tags=["reminders"])
# Mounted WITHOUT the router-level login dependency: its caller is a cron job,
# authenticated by the shared-secret header inside the endpoint itself.
cron_router = APIRouter(prefix="/api/reminders", tags=["reminders"])
log = get_logger(__name__)

# Send a heads-up these many days before renewal, then daily once due/overdue.
REMIND_DAYS_BEFORE = (7, 3, 1)


def _reminder_message(company_name: str, renewal_date: date) -> str:
    pretty_date = f"{renewal_date:%B} {renewal_date.day}, {renewal_date.year}"
    book_url = f"{settings.public_base_url}/book"
    return (
        f"Hi {company_name}, your monthly parking at Madco Truck Plaza renews on {pretty_date}. "
        f"Renew and pay by card here: {book_url} — or stop by the front desk to pay cash or check. Thank you."
    )


def _do_send(db: Session, mc: MonthlyCustomer, employee_name: str | None) -> bool:
    """Build + send (SMS if configured) + record one reminder. Shared by the
    manual 'Send' button and the automatic daily sweep. Returns whether an
    actual text went out (vs. only recorded)."""
    company_name = mc.company.name if mc.company else "—"
    phone = mc.company.phone if mc.company else None
    message = _reminder_message(company_name, mc.renewal_date)

    sent = send_sms(phone, message) if phone else False

    db.add(
        Reminder(
            monthly_customer_id=mc.id,
            scheduled_date=business_today(),
            # Plaza time, because _already_reminded_today() compares this against
            # the plaza's date. Stamped in UTC it disagreed with that date every
            # evening after 8pm — the "did we text them already?" check came back
            # False and the customer got a second text. No spam means no spam.
            sent_at=business_now(),
            status=ReminderStatus.sent,
            message=message,
        )
    )
    mc.reminder_status = ReminderStatus.sent
    log_audit(
        db,
        AuditAction.reminder_sent,
        "monthly_customer",
        f"Reminder {'sent via SMS' if sent else 'recorded (SMS not configured)'} to {company_name}",
        entity_id=mc.id,
        employee_name=employee_name,
    )
    log.info("Reminder for %s: sent=%s phone=%s", company_name, sent, phone)
    return sent


def _reminder_due_today(days_until: int) -> bool:
    return days_until in REMIND_DAYS_BEFORE or days_until <= 0


def _already_reminded_today(db: Session, monthly_customer_id: int, today: date) -> bool:
    return (
        db.scalar(
            select(Reminder.id).where(
                Reminder.monthly_customer_id == monthly_customer_id,
                func.date(Reminder.sent_at) == today.isoformat(),
            )
        )
        is not None
    )


def run_scheduled_reminders(db: Session, *, triggered_by: str = "scheduler") -> SweepResult:
    """The daily sweep: for every monthly customer, text a renewal reminder if
    one is due today (7/3/1 days before, or due/overdue) and one hasn't already
    gone out today. Auto-stops when they renew — renewing pushes renewal_date
    into the future, so they simply stop being 'due'. Opted-out (reminder_status
    stopped) and inactive customers are skipped. Idempotent per day."""
    if not settings.auto_reminders_enabled:
        return SweepResult(enabled=False, checked=0, sent=0, skipped=0)

    today = business_today()
    checked = sent = skipped = 0
    for mc in db.scalars(select(MonthlyCustomer)):
        checked += 1
        if mc.reminder_status == ReminderStatus.stopped or mc.status == MonthlyCustomerStatus.inactive:
            skipped += 1
            continue
        if not _reminder_due_today((mc.renewal_date - today).days):
            continue
        if _already_reminded_today(db, mc.id, today):
            skipped += 1
            continue
        if not (mc.company and mc.company.phone):
            skipped += 1
            continue
        _do_send(db, mc, employee_name=triggered_by)
        sent += 1

    db.commit()
    log.info("Reminder sweep (%s): checked=%s sent=%s skipped=%s", triggered_by, checked, sent, skipped)
    return SweepResult(enabled=True, checked=checked, sent=sent, skipped=skipped)


def monthly_renewal_list(db: Session) -> list[ReminderCustomer]:
    """Every monthly customer with how their renewal stands, soonest first.

    Shared with the morning report — the same question ("who renews when, and have
    we told them?") must never be answered by two different pieces of code that can
    drift apart.
    """
    today = business_today()
    customers: list[ReminderCustomer] = []
    stmt = select(MonthlyCustomer).order_by(MonthlyCustomer.renewal_date)
    for mc in db.scalars(stmt):
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
    customers = monthly_renewal_list(db)
    return RemindersOverview(
        sms_configured=sms_configured(),
        auto_enabled=settings.auto_reminders_enabled,
        customers=customers,
    )


@router.post("/run-now", response_model=SweepResult)
def run_now(db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> SweepResult:
    """Manually trigger the same automatic sweep (also runs on its own daily)."""
    return run_scheduled_reminders(db, triggered_by=_user.name or "manual")


@cron_router.post("/cron", response_model=SweepResult)
def cron_trigger(request: Request, db: Session = Depends(get_db)) -> SweepResult:
    """The external daily trigger — cron, a systemd timer, Task Scheduler.

    The in-process scheduler only sweeps while the app happens to be up; this is
    the belt-and-braces that survives restarts. Authenticated by a shared secret
    header instead of a JWT, because a cron job can't log in and a credential
    that never expires shouldn't be a user account. Refuses (503) when no token
    is configured rather than running unauthenticated. Idempotent per day — the
    sweep already skips anyone reminded today, so cron + in-process scheduler
    firing on the same day cannot double-text a customer.
    """
    if not settings.scheduler_token:
        raise HTTPException(status_code=503, detail="Scheduler token not configured.")
    supplied = request.headers.get("x-scheduler-token", "")
    if not secrets.compare_digest(supplied, settings.scheduler_token):
        raise HTTPException(status_code=403, detail="Bad scheduler token.")
    return run_scheduled_reminders(db, triggered_by="external-cron")


@router.post("/{monthly_customer_id}/send", response_model=SendReminderResult)
def send_reminder(
    monthly_customer_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> SendReminderResult:
    mc = db.get(MonthlyCustomer, monthly_customer_id)
    if mc is None:
        raise HTTPException(status_code=404, detail="Monthly customer not found.")

    message = _reminder_message(mc.company.name if mc.company else "—", mc.renewal_date)
    sent = _do_send(db, mc, employee_name=_user.name)
    db.commit()
    return SendReminderResult(sent=sent, message=message, reminder_status=ReminderStatus.sent.value)
