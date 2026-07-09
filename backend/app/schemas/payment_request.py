from datetime import date
from typing import Literal

from pydantic import BaseModel

from app.models.enums import PassType, VehicleType


class PaymentRequestIssueDetails(BaseModel):
    """Everything needed to issue a NEW pass once the customer pays."""

    company_name: str
    truck_number: str | None = None
    trailer_number: str | None = None
    license_plate: str | None = None
    phone: str
    vehicle_type: VehicleType
    pass_type: PassType
    issue_date: date
    end_date: date | None = None
    price: float | None = None  # only for bootstrapping a brand-new monthly company rate


class PaymentRequestRenewDetails(BaseModel):
    pass_id: int
    end_date: date


class CreatePaymentRequest(BaseModel):
    kind: Literal["issue", "renew"]
    issue: PaymentRequestIssueDetails | None = None
    renew: PaymentRequestRenewDetails | None = None


class PaymentRequestCreated(BaseModel):
    token: str
    pay_url: str
    amount: float
    summary: str
    status: str


class PaymentRequestStatus(BaseModel):
    status: str  # pending | paid | cancelled
    kind: str
    amount: float
    summary: str
    receipt_number: str | None = None  # populated once paid
