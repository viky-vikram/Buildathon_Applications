# Daybook Leave Management

Daybook is a FastAPI and Streamlit leave-management application for employees, managers, and HR/admin users. It supports role-based dashboards, leave booking, manager approvals, employee registration, leave-balance tracking, wallcharts, analytics, SQLite persistence, and Excel record handoff.

The current build is a production-style demo: the UI labels it as `Demo version`, demo accounts are seeded locally, and all reads/writes go through the FastAPI backend.

## What The App Does

- Employees can sign in, book leave, track approval status, cancel pending requests, view balances, and review leave history.
- Managers can view pending approval requests directly on `My Dashboard` and in the `Approvals` page.
- Managers can approve or reject leave requests, with rejection reasons required by the API.
- HR/admin users can register employees or managers, initialize leave balances, view all requests, monitor wallcharts and statistics, and rebuild Excel records.
- New employees and managers created by HR complete a first-login password setup before normal sign-in.
- Leave submission, approval, rejection, password setup, and admin actions show floating banners that disappear after 5 seconds.
- Activity is shown only in the sidebar `Notifications` expander.

## Architecture

- `backend/app`: FastAPI application, authentication, role permissions, SQLAlchemy models, Pydantic schemas, routers, workflow services, and seed logic.
- `frontend`: Streamlit UI and API client.
- `shared`: shared demo data, leave type constants, role labels, and theme CSS.
- `var/data`: generated runtime SQLite database and Excel workbook.
- `docs`: deployment notes, roadmap, build-plan PDF, screenshots notes, and workflow chart PDF.
- `tests`: backend API and Streamlit E2E regression tests.

```text
backend/
  app/
    main.py                 # FastAPI app, CORS, health, router registration
    database.py             # SQLite engine/session setup
    models.py               # SQLAlchemy ORM models
    schemas.py              # Pydantic API schemas
    deps.py                 # Current-user and role dependencies
    security.py             # Password hashing and verification
    seed.py                 # Demo seed/reset command
    routers/                # Auth, employees, leave, approvals, balances, calendar, analytics, records
    services/               # Leave workflow, policy, employee creation, Excel records
frontend/
  api_client.py             # Central Streamlit API helper
  streamlit_app.py          # API-backed Streamlit application
shared/
  demo_data.py              # Demo users, seed fixtures, labels, leave types
  theme.py                  # Streamlit theme and toast banner CSS
var/
  data/                     # Runtime SQLite and Excel files, ignored except .gitkeep
  logs/                     # Local logs, ignored except .gitkeep
docs/
  Daybook_Leave_Management_Workflow.pdf
  DEPLOYMENT_QA.md
  ROADMAP.md
tests/
  test_backend_api.py
  test_streamlit_e2e.py
```

## Roles And Screens

| Role | Main Capabilities |
| --- | --- |
| Employee | My Dashboard, Book Leave, My Leave History, My Details |
| Manager | Employee screens plus Approvals, Wallchart, Burnout Board, Team Statistics |
| HR/Admin | Overview, Wallchart, All Requests, Burnout Board, Statistics, Employees, Records, and personal leave screens |

## Login And Demo Accounts

The login form opens blank by default. Use these demo credentials manually, or use the role shortcut buttons on the login page.

```text
Employee:  maya.lin@acme.co / employee-demo
Manager:   david.okafor@acme.co / manager-demo
HR/Admin:  grace.hall@acme.co / hr-demo
```

New employees and managers created from the HR `Employees` screen can sign in with their work email and a blank password once. They are then prompted to create a password.

## Leave Workflow

1. Employee signs in and submits a leave request with leave type, dates, half-day option, reason, contact details, and handover notes.
2. FastAPI validates working days, locked policy dates, available leave balance, and permissions.
3. The request is stored in SQLite as pending and mirrored to the Excel workbook.
4. The manager sees pending team requests on `My Dashboard` and `Approvals`.
5. The manager approves or rejects the request.
6. The decision is recorded in SQLite and Excel with actor, note, status, and activity history.
7. The employee can track status in dashboard/history views.
8. Activity appears in sidebar `Notifications`.

See the workflow PDF:

```text
docs/Daybook_Leave_Management_Workflow.pdf
```

## Storage

Seed/reset creates:

```text
var/data/daybook.sqlite3
var/data/daybook_records.xlsx
```

SQLite is the source of truth. Excel is an operational record workbook for handoff and audit review. API writes append rows for employees, balances, leave requests, decisions, policy dates, and activity events. HR/admin users can rebuild the workbook from SQLite from the `Records` screen or through the records API.

The old `data/` and `database excel/` runtime locations were removed from the active structure. Runtime files now live under `var/data/` and are ignored from source control except `.gitkeep`.

## Run Locally

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m backend.app.seed
uvicorn backend.app.main:app --reload --port 8000
```

Open a second terminal in the same activated environment:

```powershell
streamlit run frontend/streamlit_app.py
```

Streamlit is configured to open directly in your default browser because `.streamlit/config.toml` sets:

```toml
[server]
headless = false
```

If the browser does not open automatically, visit:

```text
http://localhost:8501
```

The frontend expects the API at `http://127.0.0.1:8000`. Override with:

```powershell
$env:DAYBOOK_API_BASE_URL="http://127.0.0.1:8000"
```

For deployed frontends, set allowed API origins:

```powershell
$env:DAYBOOK_CORS_ORIGINS="https://your-streamlit-app.example"
```

## API

FastAPI docs are available after starting the backend:

```text
http://127.0.0.1:8000/docs
```

Core endpoints:

- `POST /auth/login`
- `POST /auth/set-password`
- `GET /auth/me`
- `POST /auth/logout`
- `GET /employees`
- `POST /employees`
- `GET /employees/{id}`
- `PATCH /employees/{id}`
- `GET /employees/{id}/balances`
- `GET /leave-requests`
- `POST /leave-requests`
- `GET /leave-requests/{id}`
- `POST /leave-requests/{id}/cancel`
- `GET /approvals/pending`
- `POST /leave-requests/{id}/approve`
- `POST /leave-requests/{id}/reject`
- `GET /calendar/wallchart`
- `GET /calendar/policy-dates`
- `POST /calendar/policy-dates`
- `GET /analytics/dashboard`
- `GET /analytics/team`
- `GET /analytics/org`
- `GET /analytics/burnout`
- `GET /records/excel/status`
- `POST /records/excel/rebuild`

## Tests

Run the regression suite:

```powershell
python -m unittest discover -s tests
```

Useful quick compile check:

```powershell
python -m compileall backend frontend shared tests
```

If dependencies are missing, tests may skip with an install hint.

## Documentation

- `docs/ROADMAP.md`: current development plan and recommended production follow-ups.
- `docs/DEPLOYMENT_QA.md`: local run, storage, and QA checklist.
- `docs/Daybook_Leave_Management_Workflow.pdf`: aligned production workflow chart.
- `docs/build-plan/Daybook_Leave_Management_Build_Plan.pdf`: original build-plan artifact.

## Current Completed Features

- FastAPI backend with routers, CORS, health check, OpenAPI docs, role dependencies, and SQLite persistence.
- SQLAlchemy models for employees, leave types, balances, leave requests, request decisions, policy dates, activity events, and settings.
- Demo seed/reset with employee, manager, and HR/admin users.
- Role-based Streamlit navigation and dashboards.
- Blank login form with demo shortcut buttons.
- First-login password setup for HR-created employees and managers.
- Employee leave booking, history, details, balances, and pending cancellation.
- Manager dashboard and approval queue using the same pending approvals source.
- Approval and rejection decisions with leave-type-specific success banners.
- HR/admin employee and manager registration with opening balances.
- HR/admin records status and Excel rebuild.
- Wallchart, burnout board, team statistics, organisation overview, and all-request filters.
- Sidebar notifications for activity history.
- Runtime storage standardized under `var/data/`.
- Browser auto-open for Streamlit local runs.

## Production Follow-Ups

- Replace demo token auth with signed session tokens or a managed identity provider.
- Add Alembic migrations for database schema changes.
- Add CI for linting, unit tests, API tests, and Streamlit smoke tests.
- Move from local SQLite to a managed database for multi-user deployment.
- Move Excel export/rebuild output to durable object storage or a controlled reporting location.
- Add richer audit-log filtering and export controls for HR/admin users.
