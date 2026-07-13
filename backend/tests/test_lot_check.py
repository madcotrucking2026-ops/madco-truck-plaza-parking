"""Lot check — the flagship feature: the manager walks up to a truck, types its
number, and gets the whole story in one second. What that story must contain is
"did this one pay, and how" — otherwise he walks back to the office to find out."""

from datetime import date, timedelta

from sqlalchemy import select

from app.models import MonthlyCustomer
from app.models.enums import PassStatus, PassType, PaymentMethod, VehicleType
from app.routers.lot_check import lot_check
from app.routers.passes import _issue_pass_and_payment


def _issue(
    db,
    truck,
    method=PaymentMethod.cash,
    pass_type=PassType.daily,
    company="Roadway Freight",
    days=None,
    price=None,
):
    end = date.today() + timedelta(days=days) if days else None
    return _issue_pass_and_payment(
        db,
        company_name=company,
        phone="313-555-0100",
        vehicle_type=VehicleType.truck,
        truck_number=truck,
        trailer_number=None,
        license_plate=None,
        pass_type=pass_type,
        issue_date=date.today(),
        end_date=end,
        price_override=price,
        payment_method=method,
        check_number=None,
    )


def test_shows_how_the_truck_paid(db):
    _issue(db, "7834", method=PaymentMethod.cash)
    db.commit()

    result = lot_check(q="7834", db=db)

    assert result.found is True
    # A daily pass bought today runs out tomorrow, so it reads as expiring_soon,
    # not active — that's the honest answer, and the manager wants that warning.
    assert result.status == PassStatus.expiring_soon
    assert result.amount_paid == 20.0
    assert result.payment_method == PaymentMethod.cash
    assert result.paid_at == date.today()
    assert result.company_name == "Roadway Freight"


def test_a_renewal_reports_the_LATEST_payment_not_the_first(db):
    """A renewed pass writes a second Payment row. Reporting the original one would
    tell the manager the truck paid days ago for a pass it has since re-bought."""
    from app.routers.passes import apply_renewal

    parking_pass = _issue(db, "9001", method=PaymentMethod.cash)
    db.commit()
    apply_renewal(db, parking_pass, date.today() + timedelta(days=3), PaymentMethod.credit_card)
    db.commit()

    result = lot_check(q="9001", db=db)

    assert result.payment_method == PaymentMethod.credit_card  # the renewal, not the cash
    assert result.expiration_date == date.today() + timedelta(days=3)


def test_flags_a_monthly_customer(db):
    # Issuing a monthly pass for a new company is what establishes it as a monthly
    # customer (and its rate) — go through that real path, not a hand-built row.
    _issue(db, "5150", company="ABC Logistics", pass_type=PassType.monthly, days=30, price=250)
    db.commit()

    result = lot_check(q="5150", db=db)

    assert result.is_monthly_customer is True
    assert result.pass_type == PassType.monthly
    assert db.scalar(select(MonthlyCustomer.monthly_price)) == 250


def test_a_daily_walkup_is_not_a_monthly_customer(db):
    _issue(db, "3300", company="One Off Hauling")
    db.commit()

    assert lot_check(q="3300", db=db).is_monthly_customer is False


def test_unknown_truck_is_simply_not_found(db):
    assert lot_check(q="0000", db=db).found is False
