"""What day is it *at the plaza*.

Two separate bugs live here if you get this wrong, and both cost money:

1. `date.today()` is the SERVER's date. Today that server is a laptop in Michigan
   and it happens to be right. On any cloud VM — which runs UTC — "today" would
   silently become UTC's today, so from 8pm Michigan time onward the system would
   roll over to tomorrow: passes would expire early and revenue would land on the
   wrong day. The plaza's day must not depend on where the app is hosted.

2. Payment.paid_at defaulted to the database's now() — UTC — while the dashboard
   bucketed revenue with the server's LOCAL today. In Michigan (UTC-4/-5) that
   means a payment taken after 8pm was stamped with tomorrow's date and dropped
   straight out of "Today's Revenue". Evening is a truck stop's busy time.

So: one clock, pinned to the plaza's timezone, used for every business-day
decision and for the timestamps we later bucket by day.
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.core.config import settings


def plaza_tz() -> ZoneInfo:
    return ZoneInfo(settings.timezone)


def business_now() -> datetime:
    """Wall-clock time at the plaza, naive — stored as-is so `date(paid_at)` in SQL
    is the plaza's calendar day without any timezone gymnastics per database."""
    return datetime.now(plaza_tz()).replace(tzinfo=None)


def business_today() -> date:
    """The plaza's current calendar day. Use this everywhere `date.today()` was
    used, so the answer never depends on the host's timezone."""
    return business_now().date()
