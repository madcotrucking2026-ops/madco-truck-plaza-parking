from pydantic import BaseModel


class ConversionLead(BaseModel):
    company_id: int
    company_name: str
    phone: str | None
    visits: int  # daily + weekly passes in the window
    total_spent: float
    suggested_monthly: float  # what a monthly plan would cost them
    tier: str  # "hot" | "warm" | "cold"


class ConversionLeads(BaseModel):
    window_days: int
    leads: list[ConversionLead]
