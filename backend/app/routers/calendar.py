from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user, require_hr
from ..models import Employee, PolicyDate
from ..schemas import PolicyDateCreate, PolicyDateOut
from ..services import excel_records
from .common import employee_out, enrich_requests, scoped_employees, scoped_requests


router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/wallchart")
def wallchart(db: Session = Depends(get_db), user: Employee = Depends(current_user)):
    return {
        "employees": [employee_out(item).model_dump() for item in scoped_employees(db, user)],
        "requests": [item.model_dump() for item in enrich_requests(db, scoped_requests(db, user))],
        "policy_dates": [PolicyDateOut.model_validate(item).model_dump() for item in db.query(PolicyDate).all()],
    }


@router.get("/policy-dates", response_model=list[PolicyDateOut])
def policy_dates(db: Session = Depends(get_db), _user: Employee = Depends(current_user)):
    return db.query(PolicyDate).order_by(PolicyDate.date).all()


@router.post("/policy-dates", response_model=PolicyDateOut)
def add_policy_date(payload: PolicyDateCreate, db: Session = Depends(get_db), user: Employee = Depends(require_hr)):
    item = PolicyDate(**payload.model_dump())
    db.add(item)
    db.flush()
    excel_records.append_record("PolicyDates", "create", excel_records.policy_payload(item), user.id)
    db.commit()
    db.refresh(item)
    return item
