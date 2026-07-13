from datetime import date

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


class CallItem(BaseModel):
    """One line of the morning report: a person to call, and the reason to call them.

    Deliberately NOT a statistic. The dashboard already has numbers; what the owner
    lacks at 7am is a list he can work down with a phone in his hand.
    """

    priority: str  # "now" | "today" | "worth_a_call"
    kind: str  # "renewal_overdue" | "renewal_due" | "pass_expiring" | "lead"
    company_id: int | None
    company_name: str
    phone: str | None
    reason: str  # plain English, ready to read aloud
    amount: float | None  # what's on the table, if anything
    monthly_customer_id: int | None = None  # set when a reminder can be texted
    pass_id: int | None = None  # set when the pass can be renewed in one click


class MorningReport(BaseModel):
    generated_for: date

    # Money
    yesterday_revenue: float
    todays_revenue: float
    month_to_date_revenue: float

    # Lot
    occupied_spaces: int
    available_spaces: int
    capacity: int

    calls: list[CallItem]
    # True when there is genuinely nothing to do — said plainly, rather than
    # padding the page with things that don't need the owner's attention.
    all_clear: bool
