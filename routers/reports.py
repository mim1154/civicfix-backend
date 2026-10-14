from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Report, User
from app.schemas import (
    ReportCreate,
    ReportListResponse,
    ReportResponse,
    ReportUpdate,
)
from routers.auth import get_current_user

router = APIRouter(prefix="/api/reports", tags=["Reports"])


def get_accessible_report(report_id: int, current_user: User, db: Session):
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if current_user.role != "admin" and report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You cannot access this report")

    return report


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    data: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = Report(
        user_id=current_user.id,
        title=data.title,
        category=data.category,
        location=data.location,
        description=data.description,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/", response_model=ReportListResponse)
def list_reports(
    q: str | None = None,
    category: str | None = None,
    report_status: str | None = Query(default=None, alias="status"),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Report)

    if current_user.role != "admin":
        query = query.filter(Report.user_id == current_user.id)

    if q:
        search = f"%{q}%"
        conditions = [
            Report.title.ilike(search),
            Report.location.ilike(search),
        ]
        if q.isdigit():
            conditions.append(Report.id == int(q))
        query = query.filter(or_(*conditions))

    if category:
        query = query.filter(Report.category == category)

    if report_status:
        query = query.filter(Report.status == report_status)

    if date_from:
        query = query.filter(Report.created_at >= date_from)

    if date_to:
        query = query.filter(Report.created_at <= date_to)

    total = query.count()

    sort_columns = {
        "created_at": Report.created_at,
        "title": Report.title,
        "status": Report.status,
    }
    if sort_by not in sort_columns:
        raise HTTPException(status_code=400, detail="Invalid sort_by value")
    if sort_order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="sort_order must be asc or desc")

    sort_column = sort_columns[sort_by]
    query = query.order_by(
        sort_column.asc() if sort_order == "asc" else sort_column.desc()
    )

    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_accessible_report(report_id, current_user, db)


@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: int,
    data: ReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = get_accessible_report(report_id, current_user, db)
    changes = data.model_dump(exclude_unset=True)

    if current_user.role != "admin" and "status" in changes:
        raise HTTPException(status_code=403, detail="Only admin can change status")

    for field, value in changes.items():
        if value is not None:
            setattr(report, field, value)

    db.commit()
    db.refresh(report)
    return report


@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = get_accessible_report(report_id, current_user, db)
    db.delete(report)
    db.commit()
    return {"message": "Report deleted successfully"}