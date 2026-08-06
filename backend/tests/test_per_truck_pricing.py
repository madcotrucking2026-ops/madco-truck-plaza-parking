"""Per-truck monthly pricing: each truck of a company is priced on its OWN
(SX Express 1325=$250, 1236=$210, 1397=$200); the company pays the sum, and a
renewal charges each truck at its own rate — there is no single company rate."""
from datetime import timedelta

from app.core.clock import business_today
from app.core.config import settings
from app.core.dates import add_months
from app.core.spots import ensure_spots
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _issue_pass_and_payment, renewal_quote


def _issue(db, truck, price, company="SX Express"):
    return _issue_pass_and_payment(
        db, company_name=company, phone="313-555-0100", vehicle_type=VehicleType.truck,
        truck_number=truck, trailer_number=None, license_plate=None, pass_type=PassType.monthly,
        issue_date=business_today(), end_date=business_today() + timedelta(days=30),
        price_override=price, payment_method=PaymentMethod.cash, check_number=None,
    )


def test_each_truck_keeps_its_own_price_company_pays_the_sum(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 10)
    ensure_spots(db)
    t1 = _issue(db, "1325", 250)  # first truck sets nothing in stone
    t2 = _issue(db, "1236", 210)  # priced on its own — NOT forced to 250
    t3 = _issue(db, "1397", 200)
    db.commit()
    prices = [float(t1.price), float(t2.price), float(t3.price)]
    assert prices == [250, 210, 200]           # each truck its own price
    assert sum(prices) == 660                    # the cashier charges the company $660
    # each truck also holds its own spot (lot organization)
    assert len({t1.spot_id, t2.spot_id, t3.spot_id}) == 3


def test_renewal_charges_the_truck_its_own_rate_not_the_company_rate(db, monkeypatch):
    monkeypatch.setattr(settings, "parking_capacity", 10)
    ensure_spots(db)
    _issue(db, "1325", 250)        # company's first truck is $250
    t2 = _issue(db, "1236", 210)   # this truck is $210
    db.commit()
    # renew truck 1236 one whole month from its old end — must bill 210, not 250
    _, price = renewal_quote(db, t2, add_months(t2.expiration_date, 1), mode="continue")
    assert round(price) == 210
