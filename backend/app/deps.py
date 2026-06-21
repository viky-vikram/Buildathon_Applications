from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db
from .models import Employee


def current_user(x_user_id: str | None = Header(default=None), db: Session = Depends(get_db)) -> Employee:
    if not x_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-User-Id header.")
    user = db.get(Employee, x_user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or inactive user.")
    return user


def require_hr(user: Employee = Depends(current_user)) -> Employee:
    if user.role != "hr":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only HR/admin can perform this action.")
    return user

