from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shared.demo_data import DEMO_USER_BY_EMAIL

from ..database import get_db
from ..deps import current_user
from ..models import Employee
from ..schemas import LoginRequest, LoginResponse
from .common import employee_out


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    account = DEMO_USER_BY_EMAIL.get(str(payload.email).lower())
    if not account or account["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Invalid demo credentials.")
    user = db.get(Employee, account["user_id"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Demo account is not linked to an active employee.")
    return LoginResponse(user=employee_out(user), token=user.id)


@router.get("/me")
def me(user: Employee = Depends(current_user)):
    return employee_out(user)


@router.post("/logout")
def logout() -> dict[str, bool]:
    return {"ok": True}
