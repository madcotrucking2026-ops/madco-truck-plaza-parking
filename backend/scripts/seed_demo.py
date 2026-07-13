"""Seed realistic demo data into the dev database so every screen populates.

Run from backend/ with the venv:
    .venv/Scripts/python.exe -m scripts.seed_demo

Additive (re-running adds more). Drives the real _issue_pass_and_payment /
apply_renewal code paths, so payments, monthly customers, the audit log, and
signed QR codes are all produced exactly as in the app — then backdates each
payment to its pass's issue date so the revenue history/chart looks real.
"""

import random
from datetime import datetime, timedelta

from sqlalchemy import func, select

from app.core.clock import business_today
from app.core.database import SessionLocal
from app.models import Payment
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment

random.seed(42)
# The plaza's today, not the host's — seeding from a UTC box in the evening would
# otherwise lay the whole demo history down a day off. See app/core/clock.py.
TODAY = business_today()
_phone_seq = iter(range(100, 999))


def _phone() -> str:
    return f"313-555-0{next(_phone_seq)}"


def _issue(db, *, company, phone, truck, ptype, issue_date, end_date=None, override=None,
           method=PaymentMethod.cash):
    p = _issue_pass_and_payment(
        db, company_name=company, phone=phone, vehicle_type=VehicleType.truck,
        truck_number=truck, trailer_number=None, license_plate=None, pass_type=ptype,
        issue_date=issue_date, end_date=end_date, price_override=override,
        payment_method=method, check_number=None,
    )
    # Backdate the just-created payment so revenue history spans real dates.
    pmt = db.scalar(
        select(Payment).where(Payment.parking_pass_id == p.id).order_by(Payment.id.desc())
    )
    if pmt is not None:
        pmt.paid_at = datetime(issue_date.year, issue_date.month, issue_date.day, 12, 0)
    return p


def seed(db):
    methods = [PaymentMethod.cash, PaymentMethod.credit_card, PaymentMethod.check, PaymentMethod.debit_card]

    # --- Conversion-lead candidates: frequent daily/weekly, NOT monthly ---
    leads = [
        ("Ironhide Freight", PassType.daily, 12),
        ("Copper Line Logistics", PassType.daily, 8),
        ("Delta Yard Carriers", PassType.weekly, 5),
        ("Roadrunner Transit", PassType.daily, 4),
    ]
    for name, ptype, n in leads:
        phone = _phone()
        for i in range(n):
            days_ago = random.randint(1, 88)
            issue_date = TODAY - timedelta(days=days_ago)
            _issue(db, company=name, phone=phone, truck=f"{name[:3].upper()}-{1000 + i}",
                   ptype=ptype, issue_date=issue_date, method=random.choice(methods))

    # --- Monthly customers with staggered renewals (drives reminders + renewals-due) ---
    #   name, trucks, renews_in_days, custom_rate
    monthly = [
        ("ABC Logistics", 3, 7, 800),        # multi-truck, special pricing
        ("Summit Haulers", 1, 3, None),
        ("Great Lakes Freight", 2, 1, None),
        ("Overdue Cartage", 1, -2, None),    # overdue -> daily overdue reminder
        ("Peninsula Movers", 1, 20, None),   # not due yet
    ]
    for name, trucks, renews_in, rate in monthly:
        phone = _phone()
        end = TODAY + timedelta(days=renews_in)
        start = end - timedelta(days=30)
        for t in range(trucks):
            _issue(db, company=name, phone=phone, truck=f"{name[:3].upper()}-{200 + t}",
                   ptype=PassType.monthly, issue_date=start, end_date=end,
                   override=rate if t == 0 else None, method=PaymentMethod.credit_card)

    # --- Needs-attention: passes expiring today / tomorrow ---
    _issue(db, company="Bell City Freight", phone=_phone(), truck="BEL-9001",
           ptype=PassType.daily, issue_date=TODAY - timedelta(days=1), end_date=TODAY)
    _issue(db, company="Ridgeline Haulage", phone=_phone(), truck="RID-9002",
           ptype=PassType.daily, issue_date=TODAY - timedelta(days=1), end_date=TODAY)
    _issue(db, company="Northwind Cartage", phone=_phone(), truck="NOR-9003",
           ptype=PassType.weekly, issue_date=TODAY - timedelta(days=6))  # expires tomorrow

    db.commit()


def main():
    with SessionLocal() as db:
        seed(db)
        from app.models import Company, MonthlyCustomer, ParkingPass
        print("Seeded demo data:")
        for label, model in (("companies", Company), ("monthly customers", MonthlyCustomer),
                             ("passes", ParkingPass), ("payments", Payment)):
            n = db.scalar(select(func.count()).select_from(model))
            print(f"  {label:20s} {n}")


if __name__ == "__main__":
    main()
