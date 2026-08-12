from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.clock import business_today
from app.core.database import get_db
from app.models import Company, ParkingPass, Payment, Vehicle
from app.models.enums import PassStatus
from app.schemas.reports import (
    CompanyStat,
    PaymentMethodStat,
    ReportsSummary,
    RevenuePoint,
    TrendPoint,
    TrendResponse,
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


_BUCKET_COUNTS = {"day": 30, "week": 12, "month": 12, "year": 5}


def _bucket_key(d: date, bucket: str) -> str:
    if bucket == "day":
        return d.isoformat()
    if bucket == "week":
        return (d - timedelta(days=d.weekday())).isoformat()  # that week's Monday
    if bucket == "month":
        return f"{d.year:04d}-{d.month:02d}"
    return f"{d.year:04d}"


def _series_keys(today: date, bucket: str) -> list[str]:
    """Ordered bucket keys to plot, oldest → newest, so gaps fill with zero and
    the line stays continuous."""
    if bucket == "day":
        return [(today - timedelta(days=i)).isoformat() for i in range(29, -1, -1)]
    if bucket == "week":
        monday = today - timedelta(days=today.weekday())
        return [(monday - timedelta(weeks=i)).isoformat() for i in range(11, -1, -1)]
    if bucket == "month":
        keys = []
        for i in range(11, -1, -1):
            m, y = today.month - i, today.year
            while m <= 0:
                m += 12
                y -= 1
            keys.append(f"{y:04d}-{m:02d}")
        return keys
    return [f"{today.year - i:04d}" for i in range(4, -1, -1)]


def _series_start(keys: list[str], bucket: str) -> date:
    first = keys[0]
    if bucket in ("day", "week"):
        return date.fromisoformat(first)
    if bucket == "month":
        return date(int(first[:4]), int(first[5:7]), 1)
    return date(int(first), 1, 1)


@router.get("/trend", response_model=TrendResponse)
def revenue_trend(
    bucket: str = Query("month"),
    metric: str = Query("revenue"),
    db: Session = Depends(get_db),
) -> TrendResponse:
    """Revenue (or pass count) bucketed by day/week/month/year for the trend line.
    Buckets are computed in Python so the same code runs on SQLite and Postgres."""
    if bucket not in _BUCKET_COUNTS:
        bucket = "month"
    if metric not in ("revenue", "passes"):
        metric = "revenue"

    today = business_today()
    keys = _series_keys(today, bucket)
    start = _series_start(keys, bucket)
    totals: dict[str, float] = {k: 0.0 for k in keys}

    if metric == "revenue":
        # Sum every payment (a void nets out via its negative reversal row), by day.
        # Compare on func.date (like reports_summary): the paid_at column is
        # timestamptz on Postgres, and a raw `>= naive datetime` throws there.
        for d, amount in db.execute(
            select(func.date(Payment.paid_at), Payment.amount).where(
                func.date(Payment.paid_at) >= start.isoformat()
            )
        ).all():
            day = d if isinstance(d, date) else date.fromisoformat(str(d))
            key = _bucket_key(day, bucket)
            if key in totals:
                totals[key] += float(amount)
    else:
        # Count passes actually issued — a mistaken-cancelled pass isn't a sale.
        for (issue_date,) in db.execute(
            select(ParkingPass.issue_date).where(
                ParkingPass.issue_date >= start, ParkingPass.status != PassStatus.cancelled
            )
        ).all():
            key = _bucket_key(issue_date, bucket)
            if key in totals:
                totals[key] += 1

    return TrendResponse(
        bucket=bucket,
        metric=metric,
        points=[TrendPoint(label=k, value=totals[k]) for k in keys],
    )
