from __future__ import annotations

import os
import socket
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(FRONTEND))


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def button_by_label(app, label: str):
    for button in app.button:
        if button.label == label:
            return button
    raise AssertionError(f"Button not found: {label}. Available: {[button.label for button in app.button]}")


class StreamlitE2ETests(unittest.TestCase):
    def setUp(self):
        try:
            import fastapi  # noqa: F401
            import openpyxl  # noqa: F401
            import sqlalchemy  # noqa: F401
            import streamlit  # noqa: F401
            import uvicorn
            from streamlit.testing.v1 import AppTest
        except ImportError:
            self.skipTest("FastAPI, SQLAlchemy, openpyxl, Streamlit, and Uvicorn are required for E2E tests.")

        self.AppTest = AppTest
        self.uvicorn = uvicorn
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "daybook.sqlite3"
        self.excel_path = Path(self.temp_dir.name) / "daybook_records.xlsx"
        self.port = free_port()

        self.original_db_url = os.environ.get("DAYBOOK_DATABASE_URL")
        self.original_excel_path = os.environ.get("DAYBOOK_EXCEL_PATH")
        self.original_api_url = os.environ.get("DAYBOOK_API_BASE_URL")
        os.environ["DAYBOOK_DATABASE_URL"] = f"sqlite:///{self.db_path.as_posix()}"
        os.environ["DAYBOOK_EXCEL_PATH"] = str(self.excel_path)
        os.environ["DAYBOOK_API_BASE_URL"] = f"http://127.0.0.1:{self.port}"

        for name in list(sys.modules):
            if name.startswith("backend.app") or name in {"api_client", "streamlit_app"}:
                sys.modules.pop(name, None)

        from backend.app.main import app
        from backend.app.seed import seed

        seed(reset=True)
        self.server = self.uvicorn.Server(self.uvicorn.Config(app, host="127.0.0.1", port=self.port, log_level="warning"))
        self.server_thread = threading.Thread(target=self.server.run, daemon=True)
        self.server_thread.start()
        self._wait_for_api()

    def tearDown(self):
        if hasattr(self, "server"):
            self.server.should_exit = True
            self.server_thread.join(timeout=5)
        for module_name in ("backend.app.database",):
            module = sys.modules.get(module_name)
            if module is not None:
                module.engine.dispose()
        if self.original_db_url is None:
            os.environ.pop("DAYBOOK_DATABASE_URL", None)
        else:
            os.environ["DAYBOOK_DATABASE_URL"] = self.original_db_url
        if self.original_excel_path is None:
            os.environ.pop("DAYBOOK_EXCEL_PATH", None)
        else:
            os.environ["DAYBOOK_EXCEL_PATH"] = self.original_excel_path
        if self.original_api_url is None:
            os.environ.pop("DAYBOOK_API_BASE_URL", None)
        else:
            os.environ["DAYBOOK_API_BASE_URL"] = self.original_api_url
        self.temp_dir.cleanup()

    def _wait_for_api(self) -> None:
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                response = requests.get(f"http://127.0.0.1:{self.port}/health", timeout=1)
                if response.status_code == 200:
                    return
            except requests.RequestException:
                time.sleep(0.2)
        raise AssertionError("FastAPI server did not start for E2E test.")

    def test_hr_adds_manager_and_employee_then_first_login_sets_passwords(self):
        app = self.AppTest.from_file(str(FRONTEND / "streamlit_app.py")).run(timeout=20)

        button_by_label(app, "HR / Admin").click().run(timeout=20)
        app.radio[0].set_value("Employees").run(timeout=20)

        app.text_input[0].set_value("Iris Manager")
        app.text_input[1].set_value("iris.manager@acme.co")
        app.selectbox[0].set_value("Manager")
        app.text_input[2].set_value("Operations Manager")
        app.selectbox[1].set_value("People")
        app.selectbox[2].set_value("Grace Hall (e7)")
        app.text_input[3].set_value("+1 415 555 0801")
        app.run(timeout=20)
        button_by_label(app, "Add manager").click().run(timeout=20)
        self.assertFalse([item.value for item in app.error])

        manager_option = next(option for option in app.selectbox[2].options if option.startswith("Iris Manager"))
        app.text_input[0].set_value("Evan Employee")
        app.text_input[1].set_value("evan.employee@acme.co")
        app.selectbox[0].set_value("Employee")
        app.text_input[2].set_value("Operations Analyst")
        app.selectbox[1].set_value("People")
        app.selectbox[2].set_value(manager_option)
        app.text_input[3].set_value("+1 415 555 0802")
        app.run(timeout=20)
        button_by_label(app, "Add employee").click().run(timeout=20)
        self.assertFalse([item.value for item in app.error])

        button_by_label(app, "Sign out").click().run(timeout=20)
        app.text_input[0].set_value("iris.manager@acme.co")
        app.text_input[1].set_value("")
        button_by_label(app, "Sign in").click().run(timeout=20)
        self.assertIn("Create your password", [item.value for item in app.header])
        app.text_input[0].set_value("manager-created")
        app.text_input[1].set_value("manager-created")
        button_by_label(app, "Save password").click().run(timeout=20)
        self.assertIn("Sign in to Daybook", [item.value for item in app.header])
        self.assertIsNone(app.session_state.user)
        app.text_input[0].set_value("iris.manager@acme.co")
        app.text_input[1].set_value("manager-created")
        button_by_label(app, "Sign in").click().run(timeout=20)
        self.assertIn("Iris Manager", app.session_state.user["name"])
        self.assertEqual(app.session_state.user["role"], "manager")
        self.assertFalse(app.session_state.pending_password_token)

        button_by_label(app, "Sign out").click().run(timeout=20)
        app.text_input[0].set_value("evan.employee@acme.co")
        app.text_input[1].set_value("")
        button_by_label(app, "Sign in").click().run(timeout=20)
        self.assertIn("Create your password", [item.value for item in app.header])
        app.text_input[0].set_value("employee-created")
        app.text_input[1].set_value("employee-created")
        button_by_label(app, "Save password").click().run(timeout=20)
        self.assertIn("Sign in to Daybook", [item.value for item in app.header])
        self.assertIsNone(app.session_state.user)
        app.text_input[0].set_value("evan.employee@acme.co")
        app.text_input[1].set_value("employee-created")
        button_by_label(app, "Sign in").click().run(timeout=20)
        self.assertIn("Evan Employee", app.session_state.user["name"])
        self.assertEqual(app.session_state.user["role"], "employee")
        self.assertFalse(app.session_state.pending_password_token)


if __name__ == "__main__":
    unittest.main()
