from __future__ import annotations

from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import LeaveBalance, LeaveRequest, LeaveType, PolicyDate


def iter_dates(start: date, end: date):
    cursor = start
    while cursor <= end:
        yield cursor
        cursor += timedelta(days=1)


def is_holiday(db: Session, day: date) -> bool:
    return db.query(PolicyDate).filter(PolicyDate.date == day, PolicyDate.kind == "holiday").first() is not None


def is_locked(db: Session, day: date) -> bool:
    return db.query(PolicyDate).filter(PolicyDate.date == day, PolicyDate.blocks_leave.is_(True)).first() is not None


def working_days(db: Session, start: date, end: date, half_day: bool) -> tuple[float, bool, bool]:
    if end < start:
        raise HTTPException(status_code=422, detail="End date cannot be before start date.")
    if half_day:
        return 0.5, is_holiday(db, start), is_locked(db, start)
    days = 0.0
    has_holiday = False
    has_locked = False
    for item in iter_dates(start, end):
        holiday = is_holiday(db, item)
        locked = is_locked(db, item)
        has_holiday = has_holiday or holiday
        has_locked = has_locked or locked
        if item.weekday() < 5 and not holiday:
            days += 1
    return days, has_holiday, has_locked


def overlaps(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    return a_start <= b_end and b_start <= a_end


def committed_days(db: Session, employee_id: str, leave_type: str, today: date | None = None) -> float:
    today = today or date.today()
    balance = (
        db.query(LeaveBalance)
        .filter(LeaveBalance.employee_id == employee_id, LeaveBalance.leave_type == leave_type)
        .first()
    )
    used = balance.used if balance else 0.0
    future = (
        db.query(func.coalesce(func.sum(LeaveRequest.days), 0.0))
        .filter(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.leave_type == leave_type,
            LeaveRequest.status.notin_(["rejected", "cancelled"]),
            LeaveRequest.end_date >= today,
        )
        .scalar()
        or 0.0
    )
    return float(used + future)


def available_days(db: Session, employee_id: str, leave_type: str, today: date | None = None) -> float | None:
    leave = db.get(LeaveType, leave_type)
    if not leave:
        raise HTTPException(status_code=422, detail="Unknown leave type.")
    if leave.cap is None:
        return None
    return max(0.0, leave.cap - committed_days(db, employee_id, leave_type, today))


def approved_clashes(db: Session, employee_id: str, start: date, end: date, scope_ids: list[str]) -> list[str]:
    if not scope_ids:
        return []
    rows = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.status == "approved",
            LeaveRequest.employee_id != employee_id,
            LeaveRequest.employee_id.in_(scope_ids),
            LeaveRequest.start_date <= end,
            LeaveRequest.end_date >= start,
        )
        .all()
    )
    return [row.employee.name for row in rows]

