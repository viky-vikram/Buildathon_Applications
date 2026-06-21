from __future__ import annotations

from datetime import date, datetime, time

from shared.demo_data import ACTIVITY, BALANCES, EMPLOYEES, LEAVE_TYPES, LOCK_PERIODS, POLICY, PUBLIC_HOLIDAYS, REQUESTS

from .database import Base, SessionLocal, engine, init_db
from .models import ActivityEvent, Employee, LeaveBalance, LeaveRequest, LeaveType, PolicyDate, PolicySetting, RequestDecision
from .services import excel_records


def seed(reset: bool = True) -> None:
    if reset:
        Base.metadata.drop_all(bind=engine)
    init_db()
    db = SessionLocal()
    try:
        for leave in LEAVE_TYPES:
            db.merge(LeaveType(key=leave["key"], name=leave["name"], cap=leave["cap"], color=leave["color"]))
        for row in EMPLOYEES:
            db.merge(
                Employee(
                    id=row["id"],
                    name=row["name"],
                    email=row["email"].lower(),
                    role=row["role"],
                    title=row["title"],
                    department=row["dept"],
                    manager_id=row["manager_id"],
                    join_date=date.fromisoformat(row["join"]),
                    phone=row["phone"],
                    is_active=True,
                )
            )
        db.flush()
        for employee_id, values in BALANCES.items():
            for leave_type, used in values.items():
                db.add(LeaveBalance(employee_id=employee_id, leave_type=leave_type, used=float(used)))
        for row in REQUESTS:
            db.add(
                LeaveRequest(
                    id=row["id"],
                    employee_id=row["emp_id"],
                    leave_type=row["type"],
                    start_date=date.fromisoformat(row["start"]),
                    end_date=date.fromisoformat(row["end"]),
                    half_day=bool(row["half"]),
                    days=float(row["days"]),
                    status=row["status"],
                    reason=row["reason"],
                    contact=row["contact"],
                    handover=row["handover"],
                    applied_on=date.fromisoformat(row["applied_on"]),
                    decided_by=row["decided_by"],
                    decision_reason=row["decision_reason"],
                )
            )
            if row.get("decided_by"):
                db.add(RequestDecision(request_id=row["id"], actor_id=row["decided_by"], action=row["status"], note=row["decision_reason"]))
        today = date.today()
        for item in PUBLIC_HOLIDAYS:
            db.add(PolicyDate(date=date(today.year, today.month, item["day"]), kind="holiday", label=item["label"], blocks_leave=False))
        for item in LOCK_PERIODS:
            for day_num in range(item["from"], item["to"] + 1):
                db.add(PolicyDate(date=date(today.year, today.month, day_num), kind="locked", label=item["label"], blocks_leave=True))
        for key, value in POLICY.items():
            db.merge(PolicySetting(key=key, value=str(value).lower()))
        for item in ACTIVITY:
            db.add(ActivityEvent(kind=item["kind"], text=item["text"], created_at=datetime.combine(date.fromisoformat(item["when"]), time.min)))
        db.commit()
        excel_records.rebuild_from_db(db)
    finally:
        db.close()


if __name__ == "__main__":
    seed(reset=True)
    print("Seeded data/daybook.sqlite3 and data/daybook_records.xlsx")
