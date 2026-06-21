from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user, require_hr
from ..models import Employee
from ..schemas import BalanceOut, EmployeeCreate, EmployeeOut, EmployeeUpdate
from ..services.employee_service import create_employee
from .common import balances_for, employee_out, scoped_employees


router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeOut])
def list_employees(db: Session = Depends(get_db), user: Employee = Depends(current_user)):
    return [employee_out(item) for item in scoped_employees(db, user)]


@router.post("", response_model=EmployeeOut)
def add_employee(payload: EmployeeCreate, db: Session = Depends(get_db), user: Employee = Depends(require_hr)):
    employee = create_employee(db, payload, user)
    db.commit()
    db.refresh(employee)
    return employee_out(employee)


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: str, db: Session = Depends(get_db), user: Employee = Depends(current_user)):
    employee = db.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found.")
    allowed_ids = {item.id for item in scoped_employees(db, user)}
    if employee_id not in allowed_ids:
        raise HTTPException(status_code=403, detail="You cannot view that employee.")
    return employee_out(employee)


@router.patch("/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: str, payload: EmployeeUpdate, db: Session = Depends(get_db), user: Employee = Depends(require_hr)):
    employee = db.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(employee, key, value)
    db.commit()
    db.refresh(employee)
    return employee_out(employee)


@router.get("/{employee_id}/balances", response_model=list[BalanceOut])
def get_balances(employee_id: str, db: Session = Depends(get_db), user: Employee = Depends(current_user)):
    allowed_ids = {item.id for item in scoped_employees(db, user)}
    if employee_id not in allowed_ids:
        raise HTTPException(status_code=403, detail="You cannot view those balances.")
    return balances_for(db, employee_id)

