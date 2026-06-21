from __future__ import annotations

import os
from typing import Any

import requests


API_BASE_URL = os.environ.get("DAYBOOK_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


class ApiError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class DaybookApi:
    def __init__(self, token: str | None = None, base_url: str = API_BASE_URL):
        self.token = token
        self.base_url = base_url

    def headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["X-User-Id"] = self.token
        return headers

    def request(self, method: str, path: str, **kwargs) -> Any:
        try:
            response = requests.request(method, f"{self.base_url}{path}", headers=self.headers(), timeout=8, **kwargs)
        except requests.RequestException as exc:
            raise ApiError(f"Cannot reach Daybook API at {self.base_url}. Start the FastAPI server first.") from exc
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            if isinstance(detail, list):
                detail = "; ".join(str(item.get("msg", item)) for item in detail)
            raise ApiError(str(detail), response.status_code)
        if not response.content:
            return None
        return response.json()

    def get(self, path: str) -> Any:
        return self.request("GET", path)

    def post(self, path: str, payload: dict | None = None) -> Any:
        return self.request("POST", path, json=payload or {})

    def patch(self, path: str, payload: dict) -> Any:
        return self.request("PATCH", path, json=payload)


def login(email: str, password: str) -> dict:
    return DaybookApi().post("/auth/login", {"email": email, "password": password})

