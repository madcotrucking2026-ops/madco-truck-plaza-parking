from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.clock import business_today
from app.core.database import get_db
from app.models import Company, ParkingPass, Payment, Vehicle
from app.schemas.reports import (
    CompanyStat,
    PaymentMethodStat,
    ReportsSummary,
    RevenuePoint,
    TruckStat,
)

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/summary", response_model=ReportsSummary)
def reports_summary(db: Session = Depends(get_db)) -> ReportsSummary:
    today = business_today()
    period_start = today - timedelta(days=29)

    rows = db.execute(
        select(func.date(Payment.paid_at), func.sum(Payment.amount))
        .where(func.date(Payment.paid_at) >= period_start.isoformat())
        .group_by(func.date(Payment.paid_at))
    ).all()
    by_day = {str(day): float(total) for day, total in rows}
    revenue_series = [
        RevenuePoint(
            date=(period_start + timedelta(days=i)).isoformat(),
            amount=by_day.get((period_start + timedelta(days=i)).isoformat(), 0.0),
        )
        for i in range(30)
    ]
    revenue_30d = sum(p.amount for p in revenue_series)

    passes_30d = db.scalar(
        select(func.count(ParkingPass.id)).where(ParkingPass.issue_date >= period_start)
    ) or 0
    avg_price = db.scalar(
        select(func.coalesce(func.avg(ParkingPass.price), 0)).where(ParkingPass.issue_date >= period_start)
    ) or 0.0
    active_companies = db.scalar(select(func.count(func.distinct(ParkingPass.company_id)))) or 0

    top_companies_rows = db.execute(
        select(Company.id, Company.name, func.count(ParkingPass.id), func.coalesce(func.sum(ParkingPass.price), 0))
        .join(ParkingPass, ParkingPass.company_id == Company.id)
        .group_by(Company.id)
        .order_by(func.sum(ParkingPass.price).desc())
        .limit(8)
    ).all()
    top_companies = [
        CompanyStat(company_id=cid, company_name=name, visits=visits, total_paid=float(total))
        for cid, name, visits, total in top_companies_rows
    ]

    method_rows = db.execute(
        select(Payment.method, func.count(Payment.id), func.coalesce(func.sum(Payment.amount), 0)).group_by(
            Payment.method
        )
    ).all()
    payment_methods = [
        PaymentMethodStat(method=method.value, count=count, total=float(total))
        for method, count, total in method_rows
    ]

    truck_rows = db.execute(
        select(Vehicle.truck_number, Company.name, func.count(ParkingPass.id))
        .join(ParkingPass, ParkingPass.vehicle_id == Vehicle.id)
        .join(Company, ParkingPass.company_id == Company.id, isouter=True)
        .where(Vehicle.truck_number.is_not(None))
        .group_by(Vehicle.truck_number, Company.name)
        .order_by(func.count(ParkingPass.id).desc())
        .limit(8)
    ).all()
    frequent_trucks = [
        TruckStat(truck_number=truck_number, company_name=company_name, visits=visits)
        for truck_number, company_name, visits in truck_rows
    ]

    return ReportsSummary(
        revenue_series=revenue_series,
        revenue_30d=revenue_30d,
        passes_30d=passes_30d,
        avg_price=avg_price,
        active_companies=active_companies,
        top_companies=top_companies,
        payment_methods=payment_methods,
        frequent_trucks=frequent_trucks,
    )
