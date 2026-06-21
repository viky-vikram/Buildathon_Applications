# Development Plan

This document records the current build status and the production-readiness path for the Daybook leave-management app.

## Phase 1: Application Foundation

Status: complete

- FastAPI backend scaffold with health checks, CORS, router registration, and OpenAPI docs.
- Streamlit frontend with the Daybook visual theme and role-aware navigation.
- Shared fixtures and theme constants in `shared/` to avoid duplicated UI and seed data.
- Local development setup through `requirements.txt`, `pyproject.toml`, and `.streamlit/config.toml`.

## Phase 2: Persistence and Records

Status: complete

- SQLite is the source of truth for employees, leave balances, leave requests, decisions, policy dates, activity, and settings.
- Excel record workbook supports append and rebuild flows for HR/admin users.
- Runtime files now live under `var/data/` and are ignored from source control except `.gitkeep`.
- Legacy runtime folders `data/` and `database excel/` were removed from the active project structure.

## Phase 3: Role-Based Leave Workflow

Status: complete

- Employee, manager, and HR/admin demo roles have separate credentials and role-specific dashboards.
- HR/admin users can register employees and managers with initial balances.
- Newly registered employees and managers complete first-login password setup.
- Employees can submit leave, track request status, view balances, cancel pending requests, and review leave history.
- Managers can approve or reject pending leave for their team with required rejection notes.
- HR/admin users can view organisation dashboards, all requests, employees, records, statistics, wallchart, and burnout views.

## Phase 4: UX and Workflow Feedback

Status: complete

- Leave submission shows a floating banner with the applied leave type.
- Manager approval and rejection show floating banners with the relevant leave type and decision.
- Banners use the Daybook theme, fly in from the top-right, and disappear automatically after 5 seconds.
- Local Streamlit runs open directly in the default browser by setting `server.headless = false`.
- Login hero pointers now reflect employee registration, leave status tracking, and secure SQLite/Excel records.

## Phase 5: QA and Documentation

Status: complete

- Backend API and Streamlit E2E regression coverage lives in `tests/`.
- Deployment and QA notes are maintained in `docs/DEPLOYMENT_QA.md`.
- Workflow chart PDF lives in `docs/Daybook_Leave_Management_Workflow.pdf`.
- Project structure is documented in this roadmap and the README.

## Production Follow-Ups

Status: recommended next work

- Replace demo token auth with signed session tokens or an identity provider.
- Add database migrations with Alembic before schema changes become frequent.
- Add CI that runs linting, unit tests, and Streamlit smoke tests.
- Add a managed deployment profile for FastAPI, Streamlit, SQLite replacement storage, and durable Excel/report exports.
- Add audit-log review screens and export filters for HR/admin users.
