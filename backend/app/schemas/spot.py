from datetime import date

from pydantic import BaseModel


class SpotState(BaseModel):
    number: int
    state: str  # free | occupied | expiring | grace | overstay | inactive
    company_name: str | None = None
    truck_number: str | None = None
    pass_id: int | None = None
    expiration_date: date | None = None
