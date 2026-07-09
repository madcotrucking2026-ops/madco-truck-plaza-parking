from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import PassStatus, PassType, PaymentMethod, VehicleType


class IssuePassRequest(BaseModel):
    company_name: str
    truck_number: str | None = None
    trailer_number: str | None = None
    license_plate: str | None = None
    phone: str
    vehicle_type: VehicleType

    pass_type: PassType
    price: float | None = None
    """Only meaningful when setting a monthly rate for a brand-new company —
    ignored for daily/weekly (always computed) and for existing monthly
    customers (their established rate is looked up automatically)."""
    issue_date: date
    end_date: date | None = None

    payment_method: PaymentMethod
    check_number: str | None = None


class RenewPassRequest(BaseModel):
    end_date: date
    payment_method: PaymentMethod
    check_number: str | None = None


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


class PassListItem(BaseModel):
    id: int
    pass_type: PassType
    status: PassStatus
    price: float
    issue_date: date
    expiration_date: date
    receipt_number: str | None
    qr_code: str | None
    company_name: str | None
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
