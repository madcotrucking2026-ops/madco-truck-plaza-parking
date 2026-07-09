from datetime import date

from pydantic import BaseModel

from app.models.enums import PassStatus, PassType


class PassVerifyResult(BaseModel):
    # `valid` is False for a bad/forged/tampered token — the guard sees a clear
    # "not a valid pass" instead of any pass details.
    valid: bool
    status: PassStatus | None = None
    company_name: str | None = None
    truck_number: str | None = None
    trailer_number: str | None = None
    license_plate: str | None = None
    pass_type: PassType | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    price: float | None = None
    receipt_number: str | None = None
