from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    email: str
    password: str


class PasswordSetupRequest(BaseModel):
    password: str


class PasswordSetupResponse(BaseModel):
    ok: bool = True


class EmployeeBase(BaseModel):
    name: str
    email: str
    role: str = Field(pattern="^(employee|manager|hr)$")
    title: str = ""
    department: str
    manager_id: str | None = None
    join_date: date
    phone: str = ""
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    role: str = Field(pattern="^(employee|manager)$")
    balances: dict[str, float] = Field(default_factory=dict)


class EmployeeUpdate(BaseModel):
    name: str | None = None
    title: str | None = None
    department: str | None = None
    manager_id: str | None = None
    phone: str | None = None
    is_active: bool | None = None


class EmployeeOut(EmployeeBase):
    id: str
    manager_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BalanceOut(BaseModel):
    leave_type: str
    name: str
    cap: float | None
    used: float
    pending: float
    approved_future: float
    available: float | None


class LeaveRequestCreate(BaseModel):
    leave_type: str
    start_date: date
    end_date: date | None = None
    half_day: bool = False
    reason: str = ""
    contact: str = ""
    handover: str = ""


class LeaveRequestOut(BaseModel):
    id: str
    employee_id: str
    employee_name: str
    employee_email: str
    department: str
    leave_type: str
    leave_type_name: str
    start_date: date
    end_date: date
    half_day: bool
    days: float
    status: str
    reason: str
    contact: str
    handover: str
    applied_on: date
    decided_by: str | None = None
    decided_by_name: str | None = None
    decision_reason: str = ""


class DecisionIn(BaseModel):
    note: str = ""


class RejectIn(BaseModel):
    reason: str


class PolicyDateCreate(BaseModel):
    date: date
    kind: str = Field(pattern="^(holiday|locked)$")
    label: str
    blocks_leave: bool = False


class PolicyDateOut(PolicyDateCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ActivityOut(BaseModel):
    kind: str
    text: str
    created_at: datetime


class LoginResponse(BaseModel):
    user: EmployeeOut
    token: str
    must_set_password: bool = False


class ExcelStatus(BaseModel):
    path: str
    exists: bool
    sheets: dict[str, int]
    last_error: str | None = None


class DashboardOut(BaseModel):
    user: EmployeeOut
    balances: list[BalanceOut]
    requests: list[LeaveRequestOut]
    employees: list[EmployeeOut]
    activity: list[ActivityOut]
    metrics: dict[str, Any]
