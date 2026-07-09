from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import MonthlyCustomer
from app.schemas.monthly_customer import (
    MonthlyCustomerCreate,
    MonthlyCustomerRead,
    MonthlyCustomerStatusUpdate,
)

router = APIRouter(prefix="/api/monthly-customers", tags=["monthly-customers"])


@router.get("", response_model=list[MonthlyCustomerRead])
def list_monthly_customers(db: Session = Depends(get_db)) -> list[MonthlyCustomer]:
    return list(db.scalars(select(MonthlyCustomer)))


@router.post("", response_model=MonthlyCustomerRead)
def create_monthly_customer(
    payload: MonthlyCustomerCreate, db: Session = Depends(get_db)
) -> MonthlyCustomer:
    monthly_customer = MonthlyCustomer(**payload.model_dump())
    db.add(monthly_customer)
    db.commit()
    db.refresh(monthly_customer)
    return monthly_customer


@router.patch("/{monthly_customer_id}/status", response_model=MonthlyCustomerRead)
def update_status(
    monthly_customer_id: int, payload: MonthlyCustomerStatusUpdate, db: Session = Depends(get_db)
) -> MonthlyCustomer:
    monthly_customer = db.get(MonthlyCustomer, monthly_customer_id)
    if monthly_customer is None:
        raise HTTPException(status_code=404, detail="Monthly customer not found")
    monthly_customer.status = payload.status
    db.commit()
    db.refresh(monthly_customer)
    return monthly_customer
