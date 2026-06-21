# Build Roadmap

This document records the prototype-to-production path. The current production tree is the FastAPI backend, Streamlit frontend, shared fixtures/theme package, and backend API tests.

## Phase 1: Clean Baseline

Status: complete

- Build the first Streamlit prototype.
- Keep the static HTML prototype only until the API-backed app is complete.
- Move generated build-plan assets into `docs/build-plan/`.
- Move local runtime logs into `var/logs/`.
- Add project README and Streamlit configuration.

## Phase 2: Modular Application Structure

Status: complete

- Extract mock employees, balances, requests, leave types, and policy constants into shared fixtures.
- Extract date, balance, permission, workflow, and reporting helpers.
- Move injected CSS into a shared theme module.
- Keep the Streamlit entry point small.
- Add a small test suite for the extracted business logic.

## Phase 3: Persistence

Status: complete

- Add a local JSON storage layer for employees, balances, requests, activity, and next request IDs.
- Seed demo data from structured fixtures.
- Keep session state as the UI working copy, not the source of truth.
- Add storage tests with isolated temporary state files.

## Phase 4: Production-Style Demo

Status: complete

- Replace prototype password handling with role-aware demo users.
- Add exportable reports for leave requests and balances.
- Add screenshots, deployment instructions, and final QA notes.

Implementation notes:

- `shared/demo_data.py` defines employee, manager, and HR/admin demo accounts with separate passwords.
- `backend/app` owns API authentication, workflow, reporting, and persistence.
- `frontend/streamlit_app.py` exposes the API-backed Daybook screens.
- `docs/DEPLOYMENT_QA.md` captures deployment steps and final QA checks.
