from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
EXCEL_DIR = ROOT_DIR / "database excel"
DEFAULT_DB_PATH = DATA_DIR / "daybook.sqlite3"
DEFAULT_EXCEL_PATH = EXCEL_DIR / "daybook_records.xlsx"


def database_url() -> str:
    override = os.environ.get("DAYBOOK_DATABASE_URL")
    if override:
        return override
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"


class Base(DeclarativeBase):
    pass


engine = create_engine(database_url(), connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from . import models  # noqa: F401

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    EXCEL_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
