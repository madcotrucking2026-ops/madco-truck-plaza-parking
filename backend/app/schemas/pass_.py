from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import PassStatus, PassType, PaymentMethod, VehicleType

NAME_MAX = 255
IDENT_MAX = 64
PHONE_MAX = 32
# Two years — nobody prepays truck parking further out, and an uncapped span
# turns into an absurd price.
MAX_PASS_DAYS = 730
# A price is never negative (that would record a negative payment) and never
# six figures for a parking pass.
PRICE_MAX = 100_000


class IssuePassRequest(BaseModel):
    company_name: str = Field(min_length=1, max_length=NAME_MAX)
    truck_number: str | None = Field(default=None, max_length=IDENT_MAX)
    trailer_number: str | None = Field(default=None, max_length=IDENT_MAX)
    license_plate: str | None = Field(default=None, max_length=IDENT_MAX)
    phone: str = Field(min_length=1, max_length=PHONE_MAX)
    vehicle_type: VehicleType

    pass_type: PassType
    price: float | None = Field(default=None, ge=0, le=PRICE_MAX)
    """A custom per-period rate the cashier types. Monthly: this truck's own
    per-month rate. Weekly: a negotiated per-week rate. Ignored for daily (always
    computed). For an existing monthly customer it overrides the looked-up rate."""
    issue_date: date
    end_date: date | None = None

    payment_method: PaymentMethod
    check_number: str | None = Field(default=None, max_length=IDENT_MAX)

    # False when onboarding a customer who already paid outside the system: the
    # pass + customer are registered but NO payment is recorded, so back-entry
    # doesn't inflate this month's revenue. Default True = normal desk sale.
    record_payment: bool = True
    # Backdate a recorded payment to the day it was actually taken (a real prior
    # receipt). Ignored when record_payment is False; must not be in the future.
    paid_on: date | None = None

    @model_validator(mode="after")
    def _sane_span(self):
        if self.end_date is not None:
            if self.end_date <= self.issue_date:
                raise ValueError("end_date must be after issue_date")
            if (self.end_date - self.issue_date).days > MAX_PASS_DAYS:
                raise ValueError(f"A pass cannot run longer than {MAX_PASS_DAYS} days")
        return self


class RenewPassRequest(BaseModel):
    end_date: date
    payment_method: PaymentMethod
    check_number: str | None = Field(default=None, max_length=IDENT_MAX)
    # "continue" keeps the plan going (whole periods forward); "close_out" settles
    # a departing customer for the time used and closes the account.
    mode: Literal["continue", "close_out"] = "continue"


class PassRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pass_type: PassType
    status: PassStatus
    price: float
    issue_date: date
    expiration_date: date
    receipt_number: str | None
    barcode: str | None
    spot_number: int | None = None
    spot_label: str | None = None


class PassListItem(BaseModel):
    id: int
    pass_type: PassType
    status: PassStatus
    price: float
    issue_date: date
    expiration_date: date
    receipt_number: str | None
    spot_number: int | None = None
    spot_label: str | None = None
    company_name: str | None
    company_id: int | None = None
    truck_number: str | None
    trailer_number: str | None
    license_plate: str | None


class LotCheckResult(BaseModel):
    found: bool
    # The pass id — lets the front desk renew / close out the truck right from the
    # lookup (the cashier's path to any pass, since they have no full passes list).
    pass_id: int | None = None
    status: PassStatus | None = None
    company_name: str | None = None
    phone: str | None = None
    truck_number: str | None = None
    trailer_number: str | None = None
    license_plate: str | None = None
    pass_type: PassType | None = None
    expiration_date: date | None = None
    notes: str | None = None

    # Standing in front of the truck, the manager's question is "did this one pay,
    # and how?" — answering it here is what saves a walk back to the office.
    amount_paid: float | None = None
    payment_method: PaymentMethod | None = None
    paid_at: date | None = None
    is_monthly_customer: bool = False
    spot_number: int | None = None
    spot_label: str | None = None
