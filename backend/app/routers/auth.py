from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from shared.demo_data import DEMO_USER_BY_EMAIL

from ..database import get_db
from ..deps import current_user
from ..models import Employee
from ..schemas import LoginRequest, LoginResponse, PasswordSetupRequest, PasswordSetupResponse
from ..security import hash_password, validate_password, verify_password
from .common import employee_out


router = APIRouter(prefix="/auth", tags=["auth"])
SETUP_TOKEN_PREFIX = "setup:"


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    email = str(payload.email).strip().lower()
    user = db.query(Employee).filter(Employee.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    if user.password_hash:
        if not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials.")
        return LoginResponse(user=employee_out(user), token=user.id, must_set_password=user.must_set_password)

    demo_account = DEMO_USER_BY_EMAIL.get(email)
    if demo_account and demo_account["user_id"] == user.id and demo_account["password"] == payload.password:
        user.password_hash = hash_password(payload.password)
        user.must_set_password = False
        db.commit()
        db.refresh(user)
        return LoginResponse(user=employee_out(user), token=user.id)

    if user.must_set_password and not payload.password:
        return LoginResponse(user=employee_out(user), token=f"{SETUP_TOKEN_PREFIX}{user.id}", must_set_password=True)

    raise HTTPException(status_code=401, detail="Invalid credentials.")


@router.post("/set-password", response_model=PasswordSetupResponse)
def set_password(
    payload: PasswordSetupRequest,
    x_user_id: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> PasswordSetupResponse:
    if not x_user_id or not x_user_id.startswith(SETUP_TOKEN_PREFIX):
        raise HTTPException(status_code=401, detail="Missing or invalid setup token.")
    user_id = x_user_id.removeprefix(SETUP_TOKEN_PREFIX)
    user = db.get(Employee, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid or inactive user.")
    if user.password_hash and not user.must_set_password:
        raise HTTPException(status_code=409, detail="Password has already been set.")
    try:
        password = validate_password(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    user.password_hash = hash_password(password)
    user.must_set_password = False
    db.commit()
    return PasswordSetupResponse()


@router.get("/me")
def me(user: Employee = Depends(current_user)):
    return employee_out(user)


@router.post("/logout")
def logout() -> dict[str, bool]:
    return {"ok": True}
