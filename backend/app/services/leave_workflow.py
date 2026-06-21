from __future__ import annotations

from datetime import date

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import ActivityEvent, Employee, LeaveRequest, RequestDecision
from . import excel_records
from .leave_policy import available_days, working_days


def next_request_id(db: Session) -> str:
    count = db.query(func.count(LeaveRequest.id)).scalar() or 0
    cursor = int(count) + 1
    while db.get(LeaveRequest, f"r{cursor}"):
        cursor += 1
    return f"r{cursor}"


def can_view(user: Employee, request: LeaveRequest) -> bool:
    return request.employee_id == user.id or request.employee.manager_id == user.id or user.role == "hr"


def can_decide(user: Employee, request: LeaveRequest, hr_can_approve: bool = False) -> bool:
    return request.status == "pending" and (request.employee.manager_id == user.id or (hr_can_approve and user.role == "hr"))


def create_activity(db: Session, kind: str, text: str, actor_id: str | None = None) -> ActivityEvent:
    event = ActivityEvent(kind=kind, text=text, actor_id=actor_id)
    db.add(event)
    db.flush()
    excel_records.append_record("ActivityEvents", "create", excel_records.activity_payload(event), actor_id)
    return event


def create_leave_request(db: Session, user: Employee, payload) -> LeaveRequest:
    end_date = payload.start_date if payload.half_day else (payload.end_date or payload.start_date)
    days, _has_holiday, has_locked = working_days(db, payload.start_date, end_date, payload.half_day)
    if days <= 0:
        raise HTTPException(status_code=422, detail="The selected date range has no working leave days.")
    if has_locked:
        raise HTTPException(status_code=422, detail="Locked company dates cannot be requested.")
    available = available_days(db, user.id, payload.leave_type)
    if available is not None and days > available:
        raise HTTPException(status_code=422, detail=f"Insufficient balance. {days:g} requested, {available:g} available.")
    request = LeaveRequest(
        id=next_request_id(db),
        employee_id=user.id,
        leave_type=payload.leave_type,
        start_date=payload.start_date,
        end_date=end_date,
        half_day=payload.half_day,
        days=days,
        status="pending",
        reason=payload.reason.strip(),
        contact=payload.contact.strip(),
        handover=payload.handover.strip(),
        applied_on=date.today(),
    )
    db.add(request)
    db.flush()
    create_activity(db, "request", f"{user.name} requested {request.leave_type} leave", user.id)
    excel_records.append_record("LeaveRequests", "create", excel_records.request_payload(request), user.id)
    return request


def decide_request(db: Session, request: LeaveRequest, actor: Employee, action: str, note: str = "") -> LeaveRequest:
    if action not in {"approved", "rejected", "cancelled"}:
        raise HTTPException(status_code=422, detail="Unsupported decision action.")
    if action == "cancelled":
        if request.employee_id != actor.id or request.status != "pending":
            raise HTTPException(status_code=403, detail="Only the owner can cancel a pending request.")
    elif not can_decide(actor, request):
        raise HTTPException(status_code=403, detail=f"You cannot {action} this request.")
    if request.status != "pending":
        raise HTTPException(status_code=422, detail=f"Cannot change a {request.status} request.")
    if action == "rejected" and not note.strip():
        raise HTTPException(status_code=422, detail="A rejection reason is required.")
    request.status = action
    request.decided_by = actor.id
    request.decision_reason = note.strip()
    decision = RequestDecision(request_id=request.id, actor_id=actor.id, action=action, note=note.strip())
    db.add(decision)
    db.flush()
    create_activity(db, action, f"{actor.name} {action} {request.employee.name}'s leave", actor.id)
    excel_records.append_record("LeaveRequests", action, excel_records.request_payload(request), actor.id)
    excel_records.append_record("Decisions", action, excel_records.decision_payload(decision), actor.id)
    return request

