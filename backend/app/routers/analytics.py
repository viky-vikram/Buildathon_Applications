from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import Employee, LeaveRequest
from ..schemas import DashboardOut
from .common import balances_for, employee_out, enrich_requests, recent_activity, scoped_employees, scoped_requests


router = APIRouter(prefix="/analytics", tags=["analytics"])


def metrics_for(requests: list[LeaveRequest], employee_count: int) -> dict:
    approved = [item for item in requests if item.status == "approved"]
    rejected = [item for item in requests if item.status == "rejected"]
    decided = len(approved) + len(rejected)
    today = date.today()
    return {
        "employees": employee_count,
        "total_requests": len(requests),
        "pending": sum(1 for item in requests if item.status == "pending"),
        "approved": len(approved),
        "approval_rate": round(len(approved) / decided * 100) if decided else 0,
        "days_taken": sum(item.days for item in approved),
        "on_leave_today": sum(1 for item in approved if item.start_date <= today <= item.end_date),
    }


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db), user: Employee = Depends(current_user)):
    employees = scoped_employees(db, user)
    requests = scoped_requests(db, user)
    return DashboardOut(
        user=employee_out(user),
        balances=balances_for(db, user.id),
        requests=enrich_requests(db, requests),
        employees=[employee_out(item) for item in employees],
        activity=recent_activity(db),
        metrics=metrics_for(requests, len(employees)),
    )


@router.get("/team")
def team(db: Session = Depends(get_db), user: Employee = Depends(current_user)):
    ids = [item.id for item in db.query(Employee).filter(Employee.manager_id == user.id).all()]
    rows = db.query(LeaveRequest).filter(LeaveRequest.employee_id.in_(ids)).all() if ids else []
    return {"metrics": metrics_for(rows, len(ids)), "requests": [item.model_dump() for item in enrich_requests(db, rows)]}


@router.get("/org")
def org(db: Session = Depends(get_db), _user: Employee = Depends(current_user)):
    employees = db.query(Employee).all()
    rows = db.query(LeaveRequest).all()
    return {"metrics": metrics_for(rows, len(employees)), "requests": [item.model_dump() for item in enrich_requests(db, rows)]}


@router.get("/burnout")
def burnout(db: Session = Depends(get_db), user: Employee = Depends(current_user)):
    employees = scoped_employees(db, user)
    rows = []
    today = date.today()
    for employee in employees:
        last = (
            db.query(LeaveRequest)
            .filter(LeaveRequest.employee_id == employee.id, LeaveRequest.status == "approved")
            .order_by(LeaveRequest.end_date.desc())
            .first()
        )
        days = None if not last else max(0, (today - last.end_date).days)
        if days is None or days >= 45:
            rows.append({"employee": employee.name, "department": employee.department, "signal": "No leave taken yet" if days is None else f"{days} days since leave"})
    return {"rows": rows}

