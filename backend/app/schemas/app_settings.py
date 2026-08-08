from pydantic import BaseModel, Field


class AppSettingsRead(BaseModel):
    parking_capacity: int
    daily_price: float
    weekly_price: float
    monthly_price: float


class AppSettingsUpdate(BaseModel):
    parking_capacity: int = Field(ge=1, le=10_000)
    daily_price: float = Field(ge=0, le=100_000)
    weekly_price: float = Field(ge=0, le=100_000)
    monthly_price: float = Field(ge=0, le=100_000)
