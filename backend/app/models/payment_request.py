from datetime import datetime

from sqlalchemy import DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PaymentRequest(Base):
    """A pending card payment a manager hands off to the customer to self-pay.
    Created (status=pending) when a manager picks 'Card — customer pays' on
    Issue Pass or Renew; the customer opens /pay/{token} on their phone, pays
    by card (Stripe), and only then is the pass actually issued/renewed and the
    row flipped to paid. Cash/check never create one of these — they're taken
    at the desk and recorded instantly."""

    __tablename__ = "payment_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    kind: Mapped[str] = mapped_column(String(16))  # "issue" | "renew"
    payload_json: Mapped[str] = mapped_column(Text)  # details needed to issue/renew on payment
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    summary: Mapped[str] = mapped_column(String(255))  # human-readable, shown to the customer

    status: Mapped[str] = mapped_column(String(16), default="pending")  # "pending" | "paid" | "cancelled"
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String(255))
    parking_pass_id: Mapped[int | None] = mapped_column(Integer)  # set once paid

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
