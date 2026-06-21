from __future__ import annotations

from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import ActivityEvent, Employee, LeaveBalance, LeaveRequest, LeaveType
from ..schemas import ActivityOut, BalanceOut, EmployeeOut, LeaveRequestOut


def employee_out(item: Employee) -> EmployeeOut:
    return EmployeeOut(
        id=item.id,
        name=item.name,
        email=item.email,
        role=item.role,
        title=item.title,
        department=item.department,
        manager_id=item.manager_id,
        manager_name=item.manager.name if item.manager else None,
        join_date=item.join_date,
        phone=item.phone,
        is_active=item.is_active,
    )


def request_out(item: LeaveRequest) -> LeaveRequestOut:
    leave_type = item.leave_type
    leave_name = leave_type
    return LeaveRequestOut(
        id=item.id,
        employee_id=item.employee_id,
        employee_name=item.employee.name,
        employee_email=item.employee.email,
        department=item.employee.department,
        leave_type=leave_type,
        leave_type_name=getattr(item, "leave_type_name", None) or leave_name.title(),
        start_date=item.start_date,
        end_date=item.end_date,
        half_day=item.half_day,
        days=item.days,
        status=item.status,
        reason=item.reason,
        contact=item.contact,
        handover=item.handover,
        applied_on=item.applied_on,
        decided_by=item.decided_by,
        decided_by_name=item.decided_by,
        decision_reason=item.decision_reason,
    )


def enrich_requests(db: Session, requests: list[LeaveRequest]) -> list[LeaveRequestOut]:
    leave_names = {item.key: item.name for item in db.query(LeaveType).all()}
    employee_names = {item.id: item.name for item in db.query(Employee).all()}
    rows = []
    for request in requests:
        row = request_out(request)
        row.leave_type_name = leave_names.get(request.leave_type, request.leave_type.title())
        row.decided_by_name = employee_names.get(request.decided_by) if request.decided_by else None
        rows.append(row)
    return rows


def scoped_employees(db: Session, user: Employee) -> list[Employee]:
    if user.role == "hr":
        return db.query(Employee).order_by(Employee.name).all()
    if user.role == "manager":
        return db.query(Employee).filter((Employee.manager_id == user.id) | (Employee.id == user.id)).order_by(Employee.name).all()
    return [user]


def scoped_requests(db: Session, user: Employee) -> list[LeaveRequest]:
    if user.role == "hr":
        return db.query(LeaveRequest).join(Employee).order_by(LeaveRequest.applied_on.desc(), LeaveRequest.id.desc()).all()
    if user.role == "manager":
        ids = [item.id for item in db.query(Employee).filter(Employee.manager_id == user.id).all()] + [user.id]
        return db.query(LeaveRequest).filter(LeaveRequest.employee_id.in_(ids)).order_by(LeaveRequest.applied_on.desc(), LeaveRequest.id.desc()).all()
    return db.query(LeaveRequest).filter(LeaveRequest.employee_id == user.id).order_by(LeaveRequest.applied_on.desc(), LeaveRequest.id.desc()).all()


def balances_for(db: Session, employee_id: str) -> list[BalanceOut]:
    today = date.today()
    leave_types = {item.key: item for item in db.query(LeaveType).all()}
    rows = []
    for balance in db.query(LeaveBalance).filter(LeaveBalance.employee_id == employee_id).order_by(LeaveBalance.leave_type).all():
        leave = leave_types[balance.leave_type]
        pending = db.query(func.coalesce(func.sum(LeaveRequest.days), 0.0)).filter(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.leave_type == balance.leave_type,
            LeaveRequest.status == "pending",
        ).scalar() or 0.0
        approved_future = db.query(func.coalesce(func.sum(LeaveRequest.days), 0.0)).filter(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.leave_type == balance.leave_type,
            LeaveRequest.status == "approved",
            LeaveRequest.end_date >= today,
        ).scalar() or 0.0
        available = None if leave.cap is None else max(0.0, leave.cap - balance.used - pending - approved_future)
        rows.append(
            BalanceOut(
                leave_type=balance.leave_type,
                name=leave.name,
                cap=leave.cap,
                used=balance.used,
                pending=float(pending),
                approved_future=float(approved_future),
                available=available,
            )
        )
    return rows


def recent_activity(db: Session, limit: int = 12) -> list[ActivityOut]:
    events = db.query(ActivityEvent).order_by(ActivityEvent.created_at.desc()).limit(limit).all()
    return [ActivityOut(kind=item.kind, text=item.text, created_at=item.created_at) for item in events]

