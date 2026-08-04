from datetime import date

from pydantic import BaseModel


class SpotState(BaseModel):
    number: int
    label: str
    state: str  # free | occupied | expiring | grace | overstay | inactive
    company_name: str | None = None
    truck_number: str | None = None
    pass_id: int | None = None
    expiration_date: date | None = None


class MoveSpotRequest(BaseModel):
    pass_id: int
    to_number: int


class MoveSpotResult(BaseModel):
    pass_id: int
    spot_number: int
    spot_label: str
