from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_hr
from ..models import Employee
from ..schemas import ExcelStatus
from ..services import excel_records


router = APIRouter(prefix="/records", tags=["records"])


@router.get("/excel/status", response_model=ExcelStatus)
def excel_status(_user: Employee = Depends(require_hr)):
    return excel_records.status()


@router.post("/excel/rebuild", response_model=ExcelStatus)
def excel_rebuild(db: Session = Depends(get_db), _user: Employee = Depends(require_hr)):
    return excel_records.rebuild_from_db(db)

