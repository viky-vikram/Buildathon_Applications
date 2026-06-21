from __future__ import annotations

from datetime import date

LEAVE_TYPES = [
    {"key": "annual", "name": "Annual", "cap": 24, "color": "#2F6A4F"},
    {"key": "sick", "name": "Sick", "cap": 12, "color": "#9C3A2E"},
    {"key": "casual", "name": "Casual", "cap": 7, "color": "#3E6E94"},
    {"key": "earned", "name": "Earned", "cap": 15, "color": "#7A5A9E"},
    {"key": "maternity", "name": "Maternity / Paternity", "cap": 90, "color": "#B05A86"},
    {"key": "unpaid", "name": "Unpaid", "cap": None, "color": "#8A8170"},
]
LT = {item["key"]: item for item in LEAVE_TYPES}
DEPARTMENTS = ["Engineering", "Sales", "People"]
ROLE_LABEL = {"employee": "Employee", "manager": "Manager", "hr": "HR / Admin"}
MOCK_PASSWORD = "prototype"
POLICY = {
    "hr_can_approve": False,
    "locked_dates_block": True,
    "allow_employee_cancel_approved": False,
}


TODAY = date.today()
PUBLIC_HOLIDAYS = [{"day": 17, "label": "Public holiday"}]
LOCK_PERIODS = [{"from": 21, "to": 22, "label": "All-hands locked period"}]


EMPLOYEES = [
    {
        "id": "e1",
        "name": "Maya Lin",
        "role": "employee",
        "dept": "Engineering",
        "manager_id": "e5",
        "title": "Software Engineer",
        "join": "2022-03-14",
        "email": "maya.lin@acme.co",
        "phone": "+1 415 555 0142",
    },
    {
        "id": "e2",
        "name": "Sam Reyes",
        "role": "employee",
        "dept": "Engineering",
        "manager_id": "e5",
        "title": "QA Engineer",
        "join": "2023-07-01",
        "email": "sam.reyes@acme.co",
        "phone": "+1 415 555 0188",
    },
    {
        "id": "e3",
        "name": "Priya Nair",
        "role": "employee",
        "dept": "Sales",
        "manager_id": "e6",
        "title": "Account Executive",
        "join": "2021-11-09",
        "email": "priya.nair@acme.co",
        "phone": "+1 415 555 0119",
    },
    {
        "id": "e4",
        "name": "Tom Becker",
        "role": "employee",
        "dept": "Sales",
        "manager_id": "e6",
        "title": "Sales Development Rep",
        "join": "2024-02-20",
        "email": "tom.becker@acme.co",
        "phone": "+1 415 555 0166",
    },
    {
        "id": "e5",
        "name": "David Okafor",
        "role": "manager",
        "dept": "Engineering",
        "manager_id": "e7",
        "title": "Engineering Manager",
        "join": "2019-05-30",
        "email": "david.okafor@acme.co",
        "phone": "+1 415 555 0101",
    },
    {
        "id": "e6",
        "name": "Elena Petrov",
        "role": "manager",
        "dept": "Sales",
        "manager_id": "e7",
        "title": "Sales Manager",
        "join": "2020-01-13",
        "email": "elena.petrov@acme.co",
        "phone": "+1 415 555 0102",
    },
    {
        "id": "e7",
        "name": "Grace Hall",
        "role": "hr",
        "dept": "People",
        "manager_id": None,
        "title": "HR Business Partner",
        "join": "2018-09-02",
        "email": "grace.hall@acme.co",
        "phone": "+1 415 555 0100",
    },
]


DEMO_USERS = [
    {
        "user_id": "e1",
        "label": "Employee",
        "email": "maya.lin@acme.co",
        "password": "employee-demo",
        "summary": "Request leave, see balances, and review personal history.",
    },
    {
        "user_id": "e5",
        "label": "Manager",
        "email": "david.okafor@acme.co",
        "password": "manager-demo",
        "summary": "Approve direct reports, inspect clashes, and export team reports.",
    },
    {
        "user_id": "e7",
        "label": "HR / Admin",
        "email": "grace.hall@acme.co",
        "password": "hr-demo",
        "summary": "Review company-wide leave, balances, employees, and exports.",
    },
]

DEMO_USER_BY_EMAIL = {item["email"].lower(): item for item in DEMO_USERS}
DEMO_USER_BY_ID = {item["user_id"]: item for item in DEMO_USERS}


BALANCES = {
    "e1": {"annual": 9, "sick": 3, "casual": 2, "earned": 5, "maternity": 0, "unpaid": 0},
    "e2": {"annual": 14, "sick": 1, "casual": 4, "earned": 2, "maternity": 0, "unpaid": 1},
    "e3": {"annual": 6, "sick": 5, "casual": 1, "earned": 8, "maternity": 0, "unpaid": 0},
    "e4": {"annual": 3, "sick": 0, "casual": 0, "earned": 1, "maternity": 0, "unpaid": 0},
    "e5": {"annual": 11, "sick": 2, "casual": 3, "earned": 6, "maternity": 0, "unpaid": 0},
    "e6": {"annual": 8, "sick": 4, "casual": 2, "earned": 4, "maternity": 0, "unpaid": 0},
    "e7": {"annual": 5, "sick": 1, "casual": 1, "earned": 3, "maternity": 0, "unpaid": 0},
}


def month_day(day: int, month_offset: int = 0) -> str:
    base_month = TODAY.month + month_offset
    year = TODAY.year + (base_month - 1) // 12
    month = (base_month - 1) % 12 + 1
    return date(year, month, day).isoformat()


REQUESTS = [
    {
        "id": "r1",
        "emp_id": "e1",
        "type": "annual",
        "start": month_day(8),
        "end": month_day(12),
        "half": False,
        "days": 5,
        "status": "approved",
        "reason": "Family trip",
        "contact": "+1 415 555 0142",
        "handover": "Sam covers PR reviews",
        "applied_on": month_day(1),
        "decided_by": "e5",
        "decision_reason": "",
    },
    {
        "id": "r2",
        "emp_id": "e1",
        "type": "sick",
        "start": month_day(2),
        "end": month_day(2),
        "half": False,
        "days": 1,
        "status": "approved",
        "reason": "Flu",
        "contact": "",
        "handover": "",
        "applied_on": month_day(1),
        "decided_by": "e5",
        "decision_reason": "",
    },
    {
        "id": "r3",
        "emp_id": "e2",
        "type": "casual",
        "start": month_day(15),
        "end": month_day(15),
        "half": True,
        "days": 0.5,
        "status": "pending",
        "reason": "DMV appointment",
        "contact": "",
        "handover": "",
        "applied_on": month_day(10),
        "decided_by": None,
        "decision_reason": "",
    },
    {
        "id": "r4",
        "emp_id": "e2",
        "type": "annual",
        "start": month_day(22),
        "end": month_day(26),
        "half": False,
        "days": 5,
        "status": "pending",
        "reason": "Wedding",
        "contact": "+1 415 555 0188",
        "handover": "Maya on call",
        "applied_on": month_day(11),
        "decided_by": None,
        "decision_reason": "",
    },
    {
        "id": "r5",
        "emp_id": "e3",
        "type": "earned",
        "start": month_day(18),
        "end": month_day(20),
        "half": False,
        "days": 3,
        "status": "pending",
        "reason": "Personal",
        "contact": "",
        "handover": "Tom covers pipeline",
        "applied_on": month_day(9),
        "decided_by": None,
        "decision_reason": "",
    },
    {
        "id": "r6",
        "emp_id": "e3",
        "type": "annual",
        "start": month_day(5, -1),
        "end": month_day(9, -1),
        "half": False,
        "days": 5,
        "status": "rejected",
        "reason": "Holiday",
        "contact": "",
        "handover": "",
        "applied_on": month_day(2, -1),
        "decided_by": "e6",
        "decision_reason": "Quarter-end close. Please reschedule after the 10th.",
    },
    {
        "id": "r7",
        "emp_id": "e4",
        "type": "sick",
        "start": month_day(14),
        "end": month_day(14),
        "half": False,
        "days": 1,
        "status": "approved",
        "reason": "Migraine",
        "contact": "",
        "handover": "",
        "applied_on": month_day(13),
        "decided_by": "e6",
        "decision_reason": "",
    },
    {
        "id": "r8",
        "emp_id": "e4",
        "type": "casual",
        "start": month_day(28),
        "end": month_day(28),
        "half": False,
        "days": 1,
        "status": "cancelled",
        "reason": "Errand",
        "contact": "",
        "handover": "",
        "applied_on": month_day(12),
        "decided_by": None,
        "decision_reason": "",
    },
    {
        "id": "r9",
        "emp_id": "e1",
        "type": "earned",
        "start": month_day(3, 1),
        "end": month_day(4, 1),
        "half": False,
        "days": 2,
        "status": "pending",
        "reason": "Course",
        "contact": "",
        "handover": "",
        "applied_on": month_day(14),
        "decided_by": None,
        "decision_reason": "",
    },
    {
        "id": "r10",
        "emp_id": "e5",
        "type": "annual",
        "start": month_day(24),
        "end": month_day(25),
        "half": False,
        "days": 2,
        "status": "approved",
        "reason": "Long weekend",
        "contact": "",
        "handover": "Elena covers escalations",
        "applied_on": month_day(7),
        "decided_by": "e7",
        "decision_reason": "",
    },
]


ACTIVITY = [
    {"kind": "request", "text": "Sam Reyes requested Annual leave", "when": month_day(11)},
    {"kind": "request", "text": "Priya Nair requested Earned leave", "when": month_day(9)},
    {"kind": "approved", "text": "David Okafor approved Maya Lin's leave", "when": month_day(1)},
    {"kind": "rejected", "text": "Elena Petrov declined Priya Nair's request", "when": month_day(2, -1)},
]

