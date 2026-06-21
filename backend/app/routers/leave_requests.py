from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import Employee, LeaveRequest
from ..schemas import DecisionIn, LeaveRequestCreate, LeaveRequestOut
from ..services.leave_workflow import can_view, create_leave_request, decide_request
from .common import enrich_requests, scoped_requests


router = APIRouter(prefix="/leave-requests", tags=["leave requests"])


@router.get("", response_model=list[LeaveRequestOut])
def list_requests(db: Session = Depends(get_db), user: Employee = Depends(current_user)):
    return enrich_requests(db, scoped_requests(db, user))


@router.post("", response_model=LeaveRequestOut)
def create_request(payload: LeaveRequestCreate, db: Session = Depends(get_db), user: Employee = Depends(current_user)):
    request = create_leave_request(db, user, payload)
    db.commit()
    db.refresh(request)
    return enrich_requests(db, [request])[0]


@router.get("/{request_id}", response_model=LeaveRequestOut)
def get_request(request_id: str, db: Session = Depends(get_db), user: Employee = Depends(current_user)):
    request = db.get(LeaveRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Leave request not found.")
    if not can_view(user, request):
        raise HTTPException(status_code=403, detail="You cannot view that request.")
    return enrich_requests(db, [request])[0]


@router.post("/{request_id}/cancel", response_model=LeaveRequestOut)
def cancel_request(request_id: str, payload: DecisionIn | None = None, db: Session = Depends(get_db), user: Employee = Depends(current_user)):
    request = db.get(LeaveRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Leave request not found.")
    request = decide_request(db, request, user, "cancelled", (payload.note if payload else ""))
    db.commit()
    db.refresh(request)
    return enrich_requests(db, [request])[0]


@router.post("/{request_id}/approve", response_model=LeaveRequestOut)
def approve_request(request_id: str, payload: DecisionIn, db: Session = Depends(get_db), user: Employee = Depends(current_user)):
    request = db.get(LeaveRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Leave request not found.")
    request = decide_request(db, request, user, "approved", payload.note)
    db.commit()
    db.refresh(request)
    return enrich_requests(db, [request])[0]


@router.post("/{request_id}/reject", response_model=LeaveRequestOut)
def reject_request(request_id: str, payload: DecisionIn, db: Session = Depends(get_db), user: Employee = Depends(current_user)):
    request = db.get(LeaveRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Leave request not found.")
    request = decide_request(db, request, user, "rejected", payload.note)
    db.commit()
    db.refresh(request)
    return enrich_requests(db, [request])[0]

