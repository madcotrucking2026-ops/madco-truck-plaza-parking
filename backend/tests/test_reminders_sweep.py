"""The daily renewal-reminder sweep: who gets a text and who's skipped.

SMS isn't configured under test, so _do_send records a Reminder without an
actual send — perfect for asserting the selection logic. auto_reminders_enabled
is forced on per-test."""

from datetime import date, timedelta

import pytest
from sqlalchemy import func, select

from app.core.config import settings
from app.models import Company, MonthlyCustomer, Reminder
from app.models.enums import MonthlyCustomerStatus, PaymentMethod, ReminderStatus
from app.routers.reminders import run_scheduled_reminders


@pytest.fixture
def auto_on(monkeypatch):
    monkeypatch.setattr(settings, "auto_reminders_enabled", True)


def _mc(db, *, days_until, phone="313-555-0100", reminder_status=ReminderStatus.pending,
        status=MonthlyCustomerStatus.truck_parked, name=None):
    name = name or f"Co d{days_until} {phone} {reminder_status.value} {status.value}"
    company = Company(name=name, phone=phone)
    db.add(company)
    db.flush()
    mc = MonthlyCustomer(
        company_id=company.id,
        monthly_price=250,
        renewal_date=date.today() + timedelta(days=days_until),
        status=status,
        reminder_status=reminder_status,
        preferred_payment_method=PaymentMethod.cash,
    )
    db.add(mc)
    db.flush()
    return mc


def _reminder_count(db):
    return db.scalar(select(func.count()).select_from(Reminder))


def test_sweep_targets_only_the_due_windows(db, auto_on):
    for d in (7, 3, 1, 0, -2):  # due: 7/3/1 before, plus due/overdue
        _mc(db, days_until=d)
    for d in (6, 5, 4, 2, 30):  # not due
        _mc(db, days_until=d)

    result = run_scheduled_reminders(db)
    assert result.enabled is True
    assert result.checked == 10
    assert result.sent == 5
    assert _reminder_count(db) == 5


def test_sweep_skips_stopped_inactive_and_no_phone(db, auto_on):
    _mc(db, days_until=0, reminder_status=ReminderStatus.stopped)     # opted out
    _mc(db, days_until=0, status=MonthlyCustomerStatus.inactive)      # inactive
    _mc(db, days_until=0, phone=None)                                 # no phone on file

    result = run_scheduled_reminders(db)
    assert result.sent == 0
    assert result.skipped == 3
    assert _reminder_count(db) == 0


def test_sweep_is_idempotent_within_a_day(db, auto_on):
    _mc(db, days_until=1)
    first = run_scheduled_reminders(db)
    assert first.sent == 1
    second = run_scheduled_reminders(db)  # same day, already reminded
    assert second.sent == 0
    assert second.skipped == 1
    assert _reminder_count(db) == 1  # not doubled


def test_sweep_noops_when_disabled(db, monkeypatch):
    monkeypatch.setattr(settings, "auto_reminders_enabled", False)
    _mc(db, days_until=0)
    result = run_scheduled_reminders(db)
    assert result.enabled is False
    assert result.checked == 0
    assert _reminder_count(db) == 0


def test_renewed_customer_is_not_due(db, auto_on):
    # Renewing pushes renewal_date far out -> auto-stops (no longer in a window).
    _mc(db, days_until=30)
    result = run_scheduled_reminders(db)
    assert result.sent == 0
    assert _reminder_count(db) == 0
