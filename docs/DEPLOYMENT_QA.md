# Deployment and QA Notes

## Demo Accounts

| Role | Email | Password | Expected Landing Page |
| --- | --- | --- | --- |
| Employee | `maya.lin@acme.co` | `employee-demo` | My Dashboard |
| Manager | `david.okafor@acme.co` | `manager-demo` | My Dashboard |
| HR / Admin | `grace.hall@acme.co` | `hr-demo` | Overview |

## Local Run

Terminal 1:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m backend.app.seed
uvicorn backend.app.main:app --reload --port 8000
```

Terminal 2:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run frontend/streamlit_app.py
```

Open:

```text
http://localhost:8501
```

FastAPI docs:

```text
http://127.0.0.1:8000/docs
```

For non-local deployments, configure API CORS explicitly:

```powershell
$env:DAYBOOK_CORS_ORIGINS="https://your-streamlit-app.example"
```

## Storage

The seed command creates the build-plan storage files:

- SQLite: `data/daybook.sqlite3`
- Excel workbook: `database excel/daybook_records.xlsx`

SQLite is the source of truth. API writes append records to Excel, and HR/admin users can rebuild the workbook from SQLite from the Records screen or `POST /records/excel/rebuild`.

## Final QA Checklist

- `GET /health` returns `{"status":"ok","service":"daybook-api"}`.
- Employee login only shows personal leave pages.
- Manager login shows approvals, wallchart, burnout, and team statistics pages.
- HR/admin login shows overview, wallchart, all requests, statistics, employees, records, and personal pages.
- Invalid demo passwords are rejected by FastAPI.
- Leave submission persists to SQLite and appends a LeaveRequests workbook row.
- Employee cancellation is limited to the employee's own pending requests.
- Pending requests can be approved or rejected only by an eligible manager.
- HR can add an employee from the Employees screen, and the employee appears immediately after refresh.
- HR-created employees and balances appear in SQLite and `database excel/daybook_records.xlsx`.
- HR can view Excel status and rebuild the workbook from SQLite.
- `python -m unittest discover -s tests` passes.
