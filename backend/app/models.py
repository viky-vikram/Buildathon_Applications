from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(120), default="")
    department: Mapped[str] = mapped_column(String(80), nullable=False)
    manager_id: Mapped[str | None] = mapped_column(String(32), ForeignKey("employees.id"), nullable=True)
    join_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone: Mapped[str] = mapped_column(String(50), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    password_hash: Mapped[str] = mapped_column(String(240), default="")
    must_set_password: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    manager: Mapped["Employee | None"] = relationship(remote_side=[id])
    balances: Mapped[list["LeaveBalance"]] = relationship(back_populates="employee", cascade="all, delete-orphan")
    requests: Mapped[list["LeaveRequest"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan",
        foreign_keys="LeaveRequest.employee_id",
    )


class LeaveType(Base):
    __tablename__ = "leave_types"

    key: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    cap: Mapped[float | None] = mapped_column(Float, nullable=True)
    color: Mapped[str] = mapped_column(String(20), nullable=False)


class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    __table_args__ = (UniqueConstraint("employee_id", "leave_type", name="uq_balance_employee_type"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[str] = mapped_column(String(32), ForeignKey("employees.id"), nullable=False)
    leave_type: Mapped[str] = mapped_column(String(40), ForeignKey("leave_types.key"), nullable=False)
    used: Mapped[float] = mapped_column(Float, default=0)

    employee: Mapped[Employee] = relationship(back_populates="balances")


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(32), ForeignKey("employees.id"), index=True, nullable=False)
    leave_type: Mapped[str] = mapped_column(String(40), ForeignKey("leave_types.key"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    half_day: Mapped[bool] = mapped_column(Boolean, default=False)
    days: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    reason: Mapped[str] = mapped_column(Text, default="")
    contact: Mapped[str] = mapped_column(String(160), default="")
    handover: Mapped[str] = mapped_column(Text, default="")
    applied_on: Mapped[date] = mapped_column(Date, nullable=False)
    decided_by: Mapped[str | None] = mapped_column(String(32), ForeignKey("employees.id"), nullable=True)
    decision_reason: Mapped[str] = mapped_column(Text, default="")

    employee: Mapped[Employee] = relationship(back_populates="requests", foreign_keys=[employee_id])


class RequestDecision(Base):
    __tablename__ = "request_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(32), ForeignKey("leave_requests.id"), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(32), ForeignKey("employees.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(24), nullable=False)
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class PolicyDate(Base):
    __tablename__ = "policy_dates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(24), nullable=False)
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    blocks_leave: Mapped[bool] = mapped_column(Boolean, default=False)


class ActivityEvent(Base):
    __tablename__ = "activity_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(40), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(32), ForeignKey("employees.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, index=True)


class PolicySetting(Base):
    __tablename__ = "policy_settings"

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[str] = mapped_column(String(200), nullable=False)
