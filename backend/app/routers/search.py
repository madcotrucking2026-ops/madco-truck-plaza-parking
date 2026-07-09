from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Company, Vehicle
from app.schemas.search import SearchResultItem

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=list[SearchResultItem])
def search_everywhere(q: str = Query(..., min_length=1), db: Session = Depends(get_db)) -> list[SearchResultItem]:
    like = f"%{q}%"
    results: list[SearchResultItem] = []

    companies = db.scalars(
        select(Company)
        .where(Company.name.ilike(like) | (Company.phone == q) | (Company.usdot_number == q))
        .limit(5)
    )
    for company in companies:
        results.append(
            SearchResultItem(
                type="company",
                label=company.name,
                sublabel=company.phone,
                query=company.name,
            )
        )

    vehicles = db.scalars(
        select(Vehicle)
        .where(
            Vehicle.truck_number.ilike(like)
            | Vehicle.trailer_number.ilike(like)
            | Vehicle.license_plate.ilike(like)
        )
        .limit(8)
    )
    for vehicle in vehicles:
        identifier = vehicle.truck_number or vehicle.trailer_number or vehicle.license_plate or ""
        results.append(
            SearchResultItem(
                type="vehicle",
                label=identifier,
                sublabel=vehicle.company.name if vehicle.company else None,
                query=identifier,
            )
        )

    return results[:10]
