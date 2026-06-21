from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import Employee, LeaveRequest
from ..schemas import LeaveRequestOut
from .common import enrich_requests


router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/pending", response_model=list[LeaveRequestOut])
def pending_approvals(db: Session = Depends(get_db), user: Employee = Depends(current_user)):
    if user.role == "hr":
        rows = db.query(LeaveRequest).filter(LeaveRequest.status == "pending").order_by(LeaveRequest.applied_on.desc()).all()
    elif user.role == "manager":
        ids = [item.id for item in db.query(Employee).filter(Employee.manager_id == user.id).all()]
        rows = db.query(LeaveRequest).filter(LeaveRequest.status == "pending", LeaveRequest.employee_id.in_(ids)).order_by(LeaveRequest.applied_on.desc()).all()
    else:
        rows = []
    return enrich_requests(db, rows)

