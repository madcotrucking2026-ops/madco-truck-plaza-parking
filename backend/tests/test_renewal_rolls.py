"""Renewal rolls the pass to the CURRENT period: issue_date becomes the old end,
so the ticket shows the span just paid for (7/4→8/4 renewed to 9/4 reads 8/4→9/4),
and price ÷ term stays the true per-month rate on every future renewal."""
from app.core.clock import business_today
from app.core.dates import add_months
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment, apply_renewal


def _issue_monthly(db, start, end, price):
    return _issue_pass_and_payment(
        db, company_name="Roll Co", phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number="RL1", trailer_number=None, license_plate=None, pass_type=PassType.monthly,
        issue_date=start, end_date=end, price_override=price, payment_method=PaymentMethod.cash, check_number=None,
    )


def test_renewal_rolls_to_the_current_period(db):
    start = business_today()
    end = add_months(start, 1)
    p = _issue_monthly(db, start, end, 150)
    db.commit()

    new_end = add_months(end, 1)
    apply_renewal(db, p, new_end, PaymentMethod.cash, mode="continue")
    db.commit()
    db.refresh(p)
    assert p.issue_date == end            # period start rolled forward to the old end
    assert p.expiration_date == new_end   # extended to the new end
    assert float(p.price) == 150.0        # one month at the truck's own rate


def test_second_renewal_keeps_the_rate(db):
    """The old bug: price ÷ months(original_issue → expiration) diluted the rate,
    so a $150 truck computed $75 on its next renewal. Rolling the period fixes it."""
    start = business_today()
    end = add_months(start, 1)
    p = _issue_monthly(db, start, end, 150)
    db.commit()
    end2 = add_months(end, 1)
    apply_renewal(db, p, end2, PaymentMethod.cash, mode="continue")
    db.commit()
    end3 = add_months(end2, 1)
    apply_renewal(db, p, end3, PaymentMethod.cash, mode="continue")
    db.commit()
    db.refresh(p)
    assert p.issue_date == end2
    assert float(p.price) == 150.0  # still $150/mo, not halved to $75
