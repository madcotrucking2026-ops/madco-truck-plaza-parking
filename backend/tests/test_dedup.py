"""Company + vehicle de-duplication on issue (the freeform-name bug)."""

from datetime import date

from sqlalchemy import func, select

from app.models import Company, ParkingPass, Vehicle
from app.models.enums import PassType, PaymentMethod, VehicleType
from app.routers.passes import _find_company, _find_or_create_vehicle, _issue_pass_and_payment


def _issue(db, *, company_name, truck_number, pass_type=PassType.daily, **kw):
    return _issue_pass_and_payment(
        db,
        company_name=company_name,
        phone=kw.get("phone", "555"),
        vehicle_type=VehicleType.truck,
        truck_number=truck_number,
        trailer_number=kw.get("trailer_number"),
        license_plate=kw.get("license_plate"),
        pass_type=pass_type,
        issue_date=kw.get("issue_date", date(2026, 7, 1)),
        end_date=kw.get("end_date"),
        price_override=kw.get("price_override"),
        payment_method=PaymentMethod.cash,
        check_number=None,
        stripe_payment_intent_id=kw.get("stripe_payment_intent_id"),
        price_from_charge=kw.get("price_from_charge"),
    )


def test_find_company_ignores_case_and_whitespace(db):
    db.add(Company(name="ABC Trucking", phone="555"))
    db.commit()
    assert _find_company(db, "  abc  trucking ").name == "ABC Trucking"
    assert _find_company(db, "ABC TRUCKING").name == "ABC Trucking"
    assert _find_company(db, "different co") is None


def test_find_or_create_vehicle_reuses_by_truck_number(db):
    company = Company(name="Hauler Co", phone="555")
    db.add(company)
    db.flush()
    v1 = _find_or_create_vehicle(db, company.id, VehicleType.truck, "7834", "T1", None)
    v2 = _find_or_create_vehicle(db, company.id, VehicleType.truck, " 7834 ", "T2", None)  # messy, same truck
    v3 = _find_or_create_vehicle(db, company.id, VehicleType.truck, "9999", None, None)  # different truck
    assert v2.id == v1.id  # reused
    assert v3.id != v1.id  # new


def test_issue_dedupes_company_and_vehicle(db):
    # Manager sets up the company (canonical), then two messy kiosk issues for
    # the same returning truck must not fork the profile.
    db.add(Company(name="ABC Trucking", phone="555"))
    db.commit()
    _issue(db, company_name="  abc TRUCKING ", truck_number="7834", issue_date=date(2026, 7, 1))
    _issue(db, company_name="ABC  Trucking", truck_number=" 7834 ", issue_date=date(2026, 7, 2))

    assert len(db.scalars(select(Company)).all()) == 1
    assert len(db.scalars(select(Vehicle)).all()) == 1
    assert len(db.scalars(select(ParkingPass)).all()) == 2


def test_new_company_name_is_stored_canonical(db):
    _issue(db, company_name="  Bell  City   Freight ", truck_number="1")
    name = db.scalar(select(Company.name))
    assert name == "Bell City Freight"  # collapsed whitespace, trimmed
