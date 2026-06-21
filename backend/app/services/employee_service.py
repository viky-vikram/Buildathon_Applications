from __future__ import annotations

from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models import ActivityEvent, Employee, LeaveBalance, LeaveType
from . import excel_records


def next_employee_id(db: Session) -> str:
    nums = []
    for (emp_id,) in db.query(Employee.id).all():
        if emp_id.startswith("e") and emp_id[1:].isdigit():
            nums.append(int(emp_id[1:]))
    return f"e{max(nums, default=0) + 1}"


def validate_employee_payload(db: Session, payload) -> None:
    if "@" not in payload.email:
        raise HTTPException(status_code=422, detail="Work email must be a valid email address.")
    if db.query(Employee).filter(Employee.email == str(payload.email).lower()).first():
        raise HTTPException(status_code=409, detail="An employee with that work email already exists.")
    if payload.join_date > date.today():
        raise HTTPException(status_code=422, detail="Join date cannot be in the future.")
    if payload.role in {"employee", "manager"}:
        if not payload.manager_id:
            raise HTTPException(status_code=422, detail="A manager is required for employee and manager records.")
        manager = db.get(Employee, payload.manager_id)
        if not manager or manager.role not in {"manager", "hr"}:
            raise HTTPException(status_code=422, detail="Manager must reference an active manager or HR employee.")
    for leave_type, value in payload.balances.items():
        if value < 0:
            raise HTTPException(status_code=422, detail="Leave balances cannot be negative.")
        if not db.get(LeaveType, leave_type):
            raise HTTPException(status_code=422, detail=f"Unknown leave type: {leave_type}.")


def create_employee(db: Session, payload, actor: Employee) -> Employee:
    validate_employee_payload(db, payload)
    employee = Employee(
        id=next_employee_id(db),
        name=payload.name.strip(),
        email=str(payload.email).lower(),
        role=payload.role,
        title=payload.title.strip(),
        department=payload.department.strip(),
        manager_id=payload.manager_id,
        join_date=payload.join_date,
        phone=payload.phone.strip(),
        is_active=payload.is_active,
    )
    db.add(employee)
    db.flush()
    for leave in db.query(LeaveType).all():
        balance = LeaveBalance(employee_id=employee.id, leave_type=leave.key, used=float(payload.balances.get(leave.key, 0)))
        db.add(balance)
        db.flush()
        excel_records.append_record("Balances", "create", excel_records.balance_payload(balance), actor.id)
    event = ActivityEvent(kind="employee", text=f"{actor.name} added {employee.name}", actor_id=actor.id)
    db.add(event)
    db.flush()
    excel_records.append_record("Employees", "create", excel_records.employee_payload(employee), actor.id)
    excel_records.append_record("ActivityEvents", "create", excel_records.activity_payload(event), actor.id)
    return employee
