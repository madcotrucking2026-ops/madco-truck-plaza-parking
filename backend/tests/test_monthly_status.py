"""Spot-holder status toggle for monthly customers."""

from datetime import date

import pytest
from fastapi import HTTPException

from app.models import Company, MonthlyCustomer
from app.models.enums import MonthlyCustomerStatus, PaymentMethod
from app.routers.monthly_customers import update_status
from app.schemas.monthly_customer import MonthlyCustomerStatusUpdate


def _make_mc(db):
    company = Company(name="Spot Co", phone="313-555-0100")
    db.add(company)
    db.flush()
    mc = MonthlyCustomer(
        company_id=company.id,
        monthly_price=250,
        renewal_date=date.today(),
        status=MonthlyCustomerStatus.truck_parked,
        preferred_payment_method=PaymentMethod.cash,
    )
    db.add(mc)
    db.commit()
    return mc


def test_toggle_spot_status(db):
    mc = _make_mc(db)
    updated = update_status(mc.id, MonthlyCustomerStatusUpdate(status=MonthlyCustomerStatus.holding_spot), db)
    assert updated.status == MonthlyCustomerStatus.holding_spot

    updated = update_status(mc.id, MonthlyCustomerStatusUpdate(status=MonthlyCustomerStatus.away), db)
    assert updated.status == MonthlyCustomerStatus.away


def test_update_status_404(db):
    with pytest.raises(HTTPException) as exc:
        update_status(999999, MonthlyCustomerStatusUpdate(status=MonthlyCustomerStatus.away), db)
    assert exc.value.status_code == 404
