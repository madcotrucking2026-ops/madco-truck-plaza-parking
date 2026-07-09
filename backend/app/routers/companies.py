from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Company, MonthlyCustomer, ParkingPass, User, Vehicle
from app.models.enums import PassType
from app.schemas.company import CompanyCreate, CompanyLookupResult, CompanyMonthlyTruck, CompanyRead

router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.get("", response_model=list[CompanyRead])
def list_companies(
    q: str | None = None, db: Session = Depends(get_db), _user: User = Depends(get_current_user)
) -> list[Company]:
    stmt = select(Company)
    if q:
        stmt = stmt.where(Company.name.ilike(f"%{q}%"))
    return list(db.scalars(stmt.order_by(Company.name)))


@router.post("", response_model=CompanyRead)
def create_company(
    payload: CompanyCreate, db: Session = Depends(get_db), _user: User = Depends(get_current_user)
) -> Company:
    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/lookup", response_model=CompanyLookupResult)
def lookup_company(name: str, db: Session = Depends(get_db)) -> CompanyLookupResult:
    """Used by Issue Pass (monthly) to auto-fill an existing company's negotiated
    monthly rate and show which trucks are already parking under it."""
    company = db.scalar(select(Company).where(func.lower(Company.name) == name.strip().lower()))
    if company is None:
        return CompanyLookupResult(found=False)

    monthly_customer = db.scalar(select(MonthlyCustomer).where(MonthlyCustomer.company_id == company.id))

    trucks_stmt = (
        select(ParkingPass)
        .join(Vehicle, ParkingPass.vehicle_id == Vehicle.id)
        .where(ParkingPass.company_id == company.id, ParkingPass.pass_type == PassType.monthly)
        .order_by(ParkingPass.issue_date.desc())
    )
    seen: set[str] = set()
    trucks: list[CompanyMonthlyTruck] = []
    for p in db.scalars(trucks_stmt):
        key = p.vehicle.truck_number or p.vehicle.license_plate or str(p.vehicle_id)
        if key in seen:
            continue
        seen.add(key)
        trucks.append(
            CompanyMonthlyTruck(
                truck_number=p.vehicle.truck_number,
                license_plate=p.vehicle.license_plate,
                price=p.price,
                expiration_date=p.expiration_date,
            )
        )

    return CompanyLookupResult(
        found=True,
        company_id=company.id,
        monthly_price=monthly_customer.monthly_price if monthly_customer else None,
        trucks=trucks,
    )


@router.get("/{company_id}", response_model=CompanyRead)
def get_company(
    company_id: int, db: Session = Depends(get_db), _user: User = Depends(get_current_user)
) -> Company:
    company = db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
