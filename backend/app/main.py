from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import analytics, approvals, auth, balances, calendar, employees, leave_requests, records
from .services.excel_records import ensure_workbook


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    ensure_workbook()
    yield


app = FastAPI(title="Daybook Leave Management API", version="1.0.0", lifespan=lifespan)


def cors_origins() -> list[str]:
    raw = os.environ.get("DAYBOOK_CORS_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(leave_requests.router)
app.include_router(approvals.router)
app.include_router(balances.router)
app.include_router(calendar.router)
app.include_router(analytics.router)
app.include_router(records.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "daybook-api"}
