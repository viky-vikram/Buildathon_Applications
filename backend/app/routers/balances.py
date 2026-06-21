from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import Employee
from ..schemas import BalanceOut
from .common import balances_for


router = APIRouter(prefix="/balances", tags=["balances"])


@router.get("/me", response_model=list[BalanceOut])
def my_balances(db: Session = Depends(get_db), user: Employee = Depends(current_user)):
    return balances_for(db, user.id)

