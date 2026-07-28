from datetime import date

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
    """Only meaningful when setting a monthly rate for a brand-new company —
    ignored for daily/weekly (always computed) and for existing monthly
    customers (their established rate is looked up automatically)."""
    issue_date: date
    end_date: date | None = None

    payment_method: PaymentMethod
    check_number: str | None = Field(default=None, max_length=IDENT_MAX)

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


class PassRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pass_type: PassType
    status: PassStatus
    price: float
    issue_date: date
    expiration_date: date
    receipt_number: str | None
    qr_code: str | None
    barcode: str | None
    spot_number: int | None = None


class PassListItem(BaseModel):
    id: int
    pass_type: PassType
    status: PassStatus
    price: float
    issue_date: date
    expiration_date: date
    receipt_number: str | None
    qr_code: str | None
    spot_number: int | None = None
    company_name: str | None
    company_id: int | None = None
    truck_number: str | None
    trailer_number: str | None
    license_plate: str | None


class LotCheckResult(BaseModel):
    found: bool
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
