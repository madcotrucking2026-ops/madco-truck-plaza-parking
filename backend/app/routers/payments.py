from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import log_audit
from app.core.clock import business_today
from app.core.codes import generate_receipt_number
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Payment, User
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
        receipt_number=generate_receipt_number("PMT", business_today()),
    )
    db.add(payment)
    db.flush()

    # A negative amount is an owner-issued refund — say so plainly in the trail.
    if payload.amount < 0:
        summary = f"Refund of ${abs(payload.amount):.2f} ({payload.method.value})"
    else:
        summary = f"Recorded {payload.method.value} payment of ${payload.amount:.2f}"
    log_audit(db, AuditAction.created, "payment", summary, entity_id=payment.id)

    db.commit()
    db.refresh(payment)
    return payment


@router.post("/{payment_id}/void", response_model=PaymentRead)
def void_payment(
    payment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Payment:
    """Void a payment recorded by mistake (cashier error, wrong company). Nothing
    is deleted — a negative reversal entry is recorded against the same pass, so
    revenue nets to zero while both the original and the correction stay on the
    books. A real, no-refund cancellation should NOT be voided (the money is
    earned); this is only for money that was never actually owed."""
    original = db.get(Payment, payment_id)
    if original is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    if float(original.amount) <= 0:
        raise HTTPException(status_code=400, detail="Only a positive payment can be voided.")
    already_voided = db.scalar(select(Payment.id).where(Payment.reversal_of_payment_id == payment_id))
    if already_voided is not None:
        raise HTTPException(status_code=400, detail="This payment was already voided.")

    reversal = Payment(
        parking_pass_id=original.parking_pass_id,
        monthly_customer_id=original.monthly_customer_id,
        amount=-float(original.amount),
        method=original.method,
        reversal_of_payment_id=original.id,
        employee_name=user.name,
        receipt_number=generate_receipt_number("VOID", business_today()),
        notes=f"Void of {original.receipt_number or f'payment #{original.id}'} — recorded in error",
    )
    db.add(reversal)
    db.flush()
    log_audit(
        db,
        AuditAction.cancelled,
        "payment",
        f"Voided payment #{original.id} (${float(original.amount):.2f}) — reversal #{reversal.id} recorded",
        entity_id=original.id,
        employee_name=user.name,
    )
    db.commit()
    db.refresh(reversal)
    return reversal
