from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import log_audit
from app.core.codes import generate_receipt_number
from app.core.database import get_db
from app.models import Payment
from app.models.enums import AuditAction
from app.schemas.payment import PaymentCreate, PaymentRead

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.get("", response_model=list[PaymentRead])
def list_payments(db: Session = Depends(get_db)) -> list[Payment]:
    return list(db.scalars(select(Payment).order_by(Payment.paid_at.desc())))


@router.post("", response_model=PaymentRead)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db)) -> Payment:
    payment = Payment(
        **payload.model_dump(),
        receipt_number=generate_receipt_number("PMT", date.today()),
    )
    db.add(payment)
    db.flush()

    log_audit(
        db,
        AuditAction.created,
        "payment",
        f"Recorded {payload.method.value} payment of ${payload.amount:.2f}",
        entity_id=payment.id,
    )

    db.commit()
    db.refresh(payment)
    return payment
