from pydantic import BaseModel


class ConversionLead(BaseModel):
    company_id: int
    company_name: str
    phone: str | None
    visits: int  # daily + weekly passes in the window
    total_spent: float
    # total_spent normalised to a per-month run-rate, so it can honestly be
    # compared against suggested_monthly (the window is 90 days, not a month).
    current_monthly_equivalent: float
    suggested_monthly: float  # what a monthly plan would cost them
    tier: str  # "hot" | "warm" | "cold"


class ConversionLeads(BaseModel):
    window_days: int
    leads: list[ConversionLead]
