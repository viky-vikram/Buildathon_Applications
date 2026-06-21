from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from api_client import ApiError, DaybookApi, login, set_password
from shared.demo_data import DEMO_USERS, DEPARTMENTS, LEAVE_TYPES, LT, ROLE_LABEL, TODAY
from shared.theme import inject_daybook_theme


st.set_page_config(page_title="Daybook Leave Management", page_icon="DB", layout="wide", initial_sidebar_state="expanded")


def api() -> DaybookApi:
    return DaybookApi(st.session_state.get("token"))


def init_state() -> None:
    st.session_state.setdefault("token", None)
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("selected_page", None)
    st.session_state.setdefault("flash", None)
    st.session_state.setdefault("pending_password_token", None)
    st.session_state.setdefault("pending_password_user", None)


def set_flash(level: str, message: str, title: str = "Notification") -> None:
    st.session_state.flash = {"level": level, "message": message, "title": title}


def normalize_flash(flash: dict | tuple | None) -> tuple[str, str, str] | None:
    if not flash:
        return None
    if isinstance(flash, dict):
        return flash.get("level", "success"), flash.get("message", ""), flash.get("title", "Notification")
    if len(flash) == 2:
        level, message = flash
        return level, message, "Notification"
    level, message, title = flash
    return level, message, title


def render_flash_banner() -> None:
    flash = normalize_flash(st.session_state.flash)
    if not flash:
        return
    level, message, title = flash
    safe_level = level if level in {"success", "error", "warning", "info"} else "success"
    st.markdown(
        f"""
        <div class="db-toast {escape(safe_level)}" role="status" aria-live="polite">
          <span class="db-toast-dot"></span>
          <span>
            <span class="db-toast-title">{escape(title)}</span>
            <span class="db-toast-message">{escape(message)}</span>
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state.flash = None


def parse_day(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(value[:10], "%Y-%m-%d").date()


def fmt_range(request: dict) -> str:
    start = parse_day(request["start_date"]).strftime("%b %d")
    end = parse_day(request["end_date"]).strftime("%b %d")
    suffix = " (1/2 day)" if request.get("half_day") else ""
    return f"{start}{suffix}" if request["start_date"] == request["end_date"] else f"{start} - {end}"


def initials_for(name: str) -> str:
    return "".join(part[:1] for part in name.split()[:2]).upper()


def status_badge_html(status: str) -> str:
    return f'<span class="db-status {escape(status)}">{escape(status.title())}</span>'


def nav_items() -> list[str]:
    role = st.session_state.user["role"]
    mine = ["My Dashboard", "Book Leave", "My Leave History", "My Details"]
    if role == "employee":
        return mine
    if role == "manager":
        return mine + ["Approvals", "Wallchart", "Burnout Board", "Team Statistics"]
    return ["Overview", "Wallchart", "All Requests", "Burnout Board", "Statistics", "Employees", "Records"] + mine


def load_dashboard() -> dict | None:
    try:
        return api().get("/analytics/dashboard")
    except ApiError as exc:
        st.error(str(exc))
        return None


def employee_map(data: dict) -> dict[str, dict]:
    return {item["id"]: item for item in data.get("employees", [])}


def complete_login(response: dict) -> None:
    if response.get("must_set_password"):
        st.session_state.pending_password_token = response["token"]
        st.session_state.pending_password_user = response["user"]
        st.rerun()
    st.session_state.token = response["token"]
    st.session_state.user = response["user"]
    st.session_state.pending_password_token = None
    st.session_state.pending_password_user = None
    st.session_state.selected_page = None
    st.rerun()


def render_password_setup() -> None:
    user = st.session_state.pending_password_user
    token = st.session_state.pending_password_token
    st.markdown('<div class="db-login-card"><div class="db-eyebrow">First sign in</div>', unsafe_allow_html=True)
    st.header("Create your password")
    st.caption(f"{user['name']} - {user['email']}")
    with st.form("first_login_password_form"):
        password = st.text_input("New password", type="password")
        confirm = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Save password", type="primary")
    if submitted:
        if password != confirm:
            st.error("Passwords do not match.")
        else:
            try:
                set_password(token, password)
                st.session_state.token = None
                st.session_state.user = None
                st.session_state.pending_password_token = None
                st.session_state.pending_password_user = None
                st.session_state.selected_page = None
                set_flash("success", "Password created. Sign in with your new password.")
                st.rerun()
            except ApiError as exc:
                st.error(str(exc))
    if st.button("Back to sign in", width="stretch"):
        st.session_state.pending_password_token = None
        st.session_state.pending_password_user = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_login() -> None:
    left, right = st.columns([1.1, 1])
    with left:
        st.markdown(
            """
            <div class="db-login-hero">
              <div><h1>Daybook</h1><div class="tag">Leave Management</div></div>
              <div class="big">A clear record of every day<br><em>taken, owed, and away.</em></div>
              <div>
                <p><b>01</b> &nbsp; Register employees and access role-based dashboards</p>
                <p><b>02</b> &nbsp; Submit leave requests and track every approval status</p>
                <p><b>03</b> &nbsp; Manage approvals with secure SQLite and Excel records</p>
              </div>
              <div class="tag">ACME CO - INTERNAL</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        if st.session_state.pending_password_token and st.session_state.pending_password_user:
            render_password_setup()
            return
        st.markdown('<div class="db-login-card"><div class="db-eyebrow">Welcome back</div>', unsafe_allow_html=True)
        st.header("Sign in to Daybook")
        st.caption("Demo version")
        email = st.text_input("Work email")
        password = st.text_input("Password", type="password")
        st.caption("New employees and managers can enter their work email and leave the password blank on first sign in.")
        if st.button("Sign in", type="primary", width="stretch"):
            try:
                response = login(email, password)
                complete_login(response)
            except ApiError as exc:
                st.error(str(exc))
        st.divider()
        demo_cols = st.columns(3)
        for col, account in zip(demo_cols, DEMO_USERS):
            col.markdown(f"**{escape(account['label'])}**")
            col.caption(account["email"])
            if col.button(account["label"], width="stretch"):
                try:
                    response = login(account["email"], account["password"])
                    complete_login(response)
                except ApiError as exc:
                    st.error(str(exc))
        with st.expander("Demo credentials"):
            for account in DEMO_USERS:
                st.code(f"{account['email']} / {account['password']}", language="text")
        st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar(data: dict) -> str:
    user = st.session_state.user
    st.sidebar.markdown('<div class="db-brand">Daybook</div><div class="db-brand-sub">Leave Management</div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        f'<span class="db-avatar">{initials_for(user["name"])}</span><b>{escape(user["name"])}</b><br>'
        f'<span style="color:#676B70;font-size:.82rem">{ROLE_LABEL[user["role"]]} - {escape(user["department"])}</span>',
        unsafe_allow_html=True,
    )
    st.sidebar.divider()
    options = nav_items()
    if st.session_state.selected_page not in options:
        st.session_state.selected_page = options[0]
    selected = st.sidebar.radio("Navigation", options, key="selected_page", label_visibility="collapsed")
    with st.sidebar.expander("Notifications", expanded=False):
        for item in data.get("activity", [])[:8]:
            st.write(f"**{item['created_at'][:10]}**")
            st.caption(item["text"])
        if not data.get("activity"):
            st.caption("No activity yet.")
    if st.sidebar.button("Sign out", width="stretch"):
        st.session_state.token = None
        st.session_state.user = None
        st.session_state.pending_password_token = None
        st.session_state.pending_password_user = None
        st.rerun()
    return selected


def render_balance_cards(balances: list[dict]) -> None:
    cards = []
    colors = {item["key"]: item["color"] for item in LEAVE_TYPES}
    for item in balances:
        cap = item["cap"]
        if cap is None:
            main = f'{item["used"]:g}<small> taken</small>'
            sub = "no annual cap"
            pct = 0
        else:
            main = f'{item["available"]:g}<small> / {cap:g} left</small>'
            sub = f'{item["used"]:g} taken'
            if item["approved_future"]:
                sub += f' - {item["approved_future"]:g} booked'
            if item["pending"]:
                sub += f' - {item["pending"]:g} pending'
            pct = min(100, round(item["used"] / cap * 100)) if cap else 0
        cards.append(
            f'<div class="db-bal" style="--accent:{colors.get(item["leave_type"], "#26473C")}">'
            f'<div class="label">{escape(item["name"])}</div><div class="num">{main}</div>'
            f'<div class="sub">{escape(sub)}</div><div class="db-gauge" style="--pct:{pct}%"><span></span></div></div>'
        )
    st.markdown('<div class="db-bal-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)


def render_request_table(requests: list[dict], include_employee: bool = False) -> None:
    if not requests:
        st.info("No leave requests to show.")
        return
    headers = ["Employee"] if include_employee else []
    headers += ["Type", "Dates", "Days", "Status", "Reason"]
    head = "".join(f"<th>{escape(item)}</th>" for item in headers)
    body_rows = []
    for item in requests:
        cells = []
        if include_employee:
            cells.append(f'<td><span class="db-avatar">{initials_for(item["employee_name"])}</span>{escape(item["employee_name"])}</td>')
        type_cell = f'<span style="display:inline-flex;align-items:center;gap:.45rem">{escape(item["leave_type_name"])}</span>'
        cells.extend(
            [
                f"<td>{type_cell}</td>",
                f"<td>{escape(fmt_range(item))}</td>",
                f'<td>{item["days"]:g}</td>',
                f'<td>{status_badge_html(item["status"])}</td>',
                f'<td>{escape(item.get("reason") or "-")}</td>',
            ]
        )
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    st.markdown(
        f'<div class="db-table-wrap"><table class="db-table"><thead><tr>{head}</tr></thead><tbody>{"".join(body_rows)}</tbody></table></div>',
        unsafe_allow_html=True,
    )


def show_request_details(request: dict) -> None:
    with st.expander(f"Details: {request['employee_name']} - {request['leave_type_name']} - {fmt_range(request)}"):
        c1, c2, c3, c4 = st.columns(4)
        c1.write(f"**Employee:** {request['employee_name']}")
        c2.write(f"**Type:** {request['leave_type_name']}")
        c3.write(f"**Days:** {request['days']:g}")
        c4.write(f"**Status:** {request['status'].title()}")
        st.write(f"**Reason:** {escape(request.get('reason') or '-')}")
        st.write(f"**Contact while away:** {escape(request.get('contact') or '-')}")
        st.write(f"**Handover notes:** {escape(request.get('handover') or '-')}")
        decision = request.get("decided_by_name") or "-"
        if request.get("decision_reason"):
            decision += f" - {escape(request['decision_reason'])}"
        st.write(f"**Decision:** {decision}")


def render_dashboard(data: dict) -> None:
    user = data["user"]
    st.title(f"Good to see you, {user['name'].split()[0]}.")
    st.caption("Your allowance, your requests, and upcoming leave around you.")
    render_balance_cards(data["balances"])
    if user["role"] in {"manager", "hr"}:
        try:
            pending = api().get("/approvals/pending")
        except ApiError as exc:
            st.error(str(exc))
            return
        st.subheader(f"Pending approval requests ({len(pending)})")
        render_request_table(pending, include_employee=True)
        for item in pending:
            show_request_details(item)
        return

    mine = [item for item in data["requests"] if item["employee_id"] == user["id"]]
    pending = [item for item in mine if item["status"] == "pending"]
    st.subheader("Waiting on approval")
    render_request_table(pending)
    for item in pending:
        if st.button(f"Cancel {item['leave_type_name']} {fmt_range(item)}", key=f"cancel_dash_{item['id']}"):
            try:
                api().post(f"/leave-requests/{item['id']}/cancel", {"note": "Cancelled by employee"})
                st.success("Request cancelled.")
                st.rerun()
            except ApiError as exc:
                st.error(str(exc))


def render_book_leave(data: dict) -> None:
    st.title("Book leave")
    with st.form("leave_form"):
        leave_name = st.selectbox("Leave type", [item["name"] for item in LEAVE_TYPES])
        leave_type = next(item["key"] for item in LEAVE_TYPES if item["name"] == leave_name)
        half_day = st.checkbox("Half day")
        c1, c2 = st.columns(2)
        start = c1.date_input("Start date", value=TODAY + timedelta(days=3))
        end = c2.date_input("End date", value=start if half_day else TODAY + timedelta(days=4), disabled=half_day)
        reason = st.text_area("Reason", placeholder="Family holiday")
        contact = st.text_input("Contact while away", placeholder="Phone or email, optional")
        handover = st.text_input("Handover notes", placeholder="Who covers / what's pending")
        submitted = st.form_submit_button("Submit request", type="primary")
    if submitted:
        try:
            request = api().post(
                "/leave-requests",
                {
                    "leave_type": leave_type,
                    "start_date": start.isoformat(),
                    "end_date": (start if half_day else end).isoformat(),
                    "half_day": half_day,
                    "reason": reason,
                    "contact": contact,
                    "handover": handover,
                },
            )
            set_flash("success", f"{request['leave_type_name']} leave submitted successfully.", "Leave submitted")
            st.rerun()
        except ApiError as exc:
            st.error(str(exc))


def render_history(data: dict) -> None:
    st.title("My leave history")
    mine = [item for item in data["requests"] if item["employee_id"] == data["user"]["id"]]
    render_request_table(mine)
    for item in mine:
        show_request_details(item)


def render_details(data: dict, employee_id: str | None = None) -> None:
    employees = employee_map(data)
    target = employees.get(employee_id or data["user"]["id"], data["user"])
    st.title("My details" if target["id"] == data["user"]["id"] else target["name"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Employee ID", target["id"].upper())
    c2.metric("Department", target["department"])
    c3.metric("Role", ROLE_LABEL[target["role"]])
    st.write(f"**Title:** {target['title']}")
    st.write(f"**Reports to:** {target.get('manager_name') or '-'}")
    st.write(f"**Join date:** {target['join_date']}")
    st.write(f"**Email:** {target['email']}")
    st.write(f"**Phone:** {target['phone']}")
    if target["id"] == data["user"]["id"]:
        render_balance_cards(data["balances"])


def render_approvals(data: dict) -> None:
    st.title("Approvals")
    try:
        pending = api().get("/approvals/pending")
    except ApiError as exc:
        st.error(str(exc))
        return
    st.subheader(f"Pending decision ({len(pending)})")
    for item in pending:
        with st.container(border=True):
            st.write(f"**{item['employee_name']}** - {item['leave_type_name']} - {fmt_range(item)}")
            show_request_details(item)
            approve_note = st.text_input("Approval note", key=f"approve_note_{item['id']}")
            reject_reason = st.text_input("Rejection reason", key=f"reject_reason_{item['id']}")
            c1, c2 = st.columns(2)
            if c1.button("Approve", key=f"approve_{item['id']}", type="primary"):
                try:
                    request = api().post(f"/leave-requests/{item['id']}/approve", {"note": approve_note})
                    set_flash("success", f"{request['leave_type_name']} leave approved.", "Leave approved")
                    st.rerun()
                except ApiError as exc:
                    st.error(str(exc))
            if c2.button("Reject", key=f"reject_{item['id']}"):
                try:
                    request = api().post(f"/leave-requests/{item['id']}/reject", {"note": reject_reason})
                    set_flash("warning", f"{request['leave_type_name']} leave rejected.", "Leave rejected")
                    st.rerun()
                except ApiError as exc:
                    st.error(str(exc))
    if not pending:
        st.info("Nothing pending.")


def render_wallchart(data: dict) -> None:
    st.title("Wallchart")
    st.caption("Approved is solid, pending is dashed, weekends and policy dates are shaded.")
    month_name = TODAY.strftime("%B %Y")
    days_in_month = (date(TODAY.year + (TODAY.month // 12), TODAY.month % 12 + 1, 1) - timedelta(days=1)).day

    def left_pct(day: int) -> float:
        return (day - 1) / days_in_month * 100

    def width_pct(span: int) -> float:
        return span / days_in_month * 100

    ticks = [1, 5, 10, 15, 20, 25, days_in_month]
    tick_html = "".join(f'<span class="db-scale-tick" style="left:{(item - .5) / days_in_month * 100:.3f}%">{item}</span>' for item in ticks)
    bands = []
    for day_num in range(1, days_in_month + 1):
        day = date(TODAY.year, TODAY.month, day_num)
        if day.weekday() >= 5:
            bands.append(f'<span class="db-band weekend" style="left:{left_pct(day_num):.3f}%;width:{width_pct(1):.3f}%"></span>')
    today_line = f'<span class="db-today" style="left:{(TODAY.day - .5) / days_in_month * 100:.3f}%"></span>'
    shared_track = "".join(bands) + today_line
    rows = []
    for person in data["employees"]:
        segments = []
        for request in data["requests"]:
            if request["employee_id"] != person["id"] or request["status"] not in {"approved", "pending"}:
                continue
            start = parse_day(request["start_date"])
            end = parse_day(request["end_date"])
            if start.month != TODAY.month and end.month != TODAY.month:
                continue
            start_day = 1 if start.month < TODAY.month else start.day
            end_day = days_in_month if end.month > TODAY.month else end.day
            span = max(1, end_day - start_day + 1)
            color = LT.get(request["leave_type"], {}).get("color", "#26473C")
            label = request["leave_type_name"] if span >= 3 else ("1/2" if request["half_day"] else "")
            status_class = "db-seg pending" if request["status"] == "pending" else "db-seg"
            style = f"left:{left_pct(start_day):.3f}%;width:{width_pct(span):.3f}%;--accent:{color};--soft:{color}44;" + (f"background:{color};" if request["status"] == "approved" else "")
            segments.append(f'<span class="{status_class}" style="{style}" title="{escape(request["employee_name"])} - {escape(request["leave_type_name"])}">{escape(label)}</span>')
        short_name = f"{person['name'].split()[0]} {person['name'].split()[-1][0]}."
        rows.append(
            f'<div class="db-lane"><div class="db-lane-name"><span class="db-avatar">{initials_for(person["name"])}</span>{escape(short_name)}</div>'
            f'<div class="db-lane-track">{shared_track}{"".join(segments)}</div></div>'
        )
    st.markdown(
        '<div class="db-ribbon"><div class="db-ribbon-scale">'
        f'<div class="db-gut">{escape(month_name)}</div><div class="db-scale-track">{tick_html}</div></div>'
        f'{"".join(rows)}<div class="db-legend"><span>Approved: solid</span><span>Pending: dashed</span><span>Weekend shaded</span><span>Today: ochre line</span></div></div>',
        unsafe_allow_html=True,
    )


def render_burnout() -> None:
    st.title("Burnout Board")
    try:
        rows = api().get("/analytics/burnout")["rows"]
    except ApiError as exc:
        st.error(str(exc))
        return
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)
    else:
        st.success("Everyone has taken leave recently.")


def render_stats(data: dict, scope: str) -> None:
    st.title("Team statistics" if scope == "team" else "Company statistics")
    endpoint = "/analytics/team" if scope == "team" else "/analytics/org"
    try:
        payload = api().get(endpoint)
    except ApiError as exc:
        st.error(str(exc))
        return
    metrics = payload["metrics"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total requests", metrics["total_requests"])
    c2.metric("Approval rate", f'{metrics["approval_rate"]}%')
    c3.metric("Days taken", f'{metrics["days_taken"]:g}')
    c4.metric("Pending", metrics["pending"])
    render_request_table(payload["requests"], include_employee=True)


def render_overview(data: dict) -> None:
    st.title("Organisation overview")
    metrics = data["metrics"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Employees", metrics["employees"])
    c2.metric("On leave today", metrics["on_leave_today"])
    c3.metric("Pending", metrics["pending"])
    c4.metric("Total requests", metrics["total_requests"], f'{metrics["approved"]} approved')
    render_wallchart(data)


def render_all_requests(data: dict) -> None:
    st.title("All requests")
    c1, c2, c3 = st.columns(3)
    dept_filter = c1.selectbox("Department", ["All"] + DEPARTMENTS)
    status_filter = c2.selectbox("Status", ["All", "pending", "approved", "rejected", "cancelled"])
    type_filter = c3.selectbox("Type", ["All"] + [item["name"] for item in LEAVE_TYPES])
    rows = list(data["requests"])
    if dept_filter != "All":
        rows = [item for item in rows if item["department"] == dept_filter]
    if status_filter != "All":
        rows = [item for item in rows if item["status"] == status_filter]
    if type_filter != "All":
        leave_type = next(item["key"] for item in LEAVE_TYPES if item["name"] == type_filter)
        rows = [item for item in rows if item["leave_type"] == leave_type]
    render_request_table(rows, include_employee=True)
    for item in rows:
        show_request_details(item)


def render_employees(data: dict) -> None:
    st.title("Employees")
    metrics = data["metrics"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Employees", metrics["employees"])
    c2.metric("Pending requests", metrics["pending"])
    c3.metric("On leave today", metrics["on_leave_today"])
    if st.session_state.user["role"] == "hr":
        with st.expander("Add employee or manager", expanded=False):
            with st.form("add_employee_form"):
                c1, c2 = st.columns(2)
                name = c1.text_input("Name")
                email = c2.text_input("Work email")
                role_label = c1.selectbox("Role", ["Employee", "Manager"])
                role = "manager" if role_label == "Manager" else "employee"
                title = c2.text_input("Title")
                department = c1.selectbox("Department", DEPARTMENTS)
                managers = [item for item in data["employees"] if item["role"] in {"manager", "hr"}]
                manager_options = [""] + [f"{item['name']} ({item['id']})" for item in managers]
                manager_choice = c2.selectbox("Manager", manager_options)
                join_date = c1.date_input("Join date", value=TODAY)
                phone = c2.text_input("Phone")
                active = st.checkbox("Active", value=True)
                b1, b2, b3 = st.columns(3)
                annual = b1.number_input("Annual balance used", min_value=0.0, value=0.0, step=0.5)
                earned = b2.number_input("Earned balance used", min_value=0.0, value=0.0, step=0.5)
                sick = b3.number_input("Sick balance used", min_value=0.0, value=0.0, step=0.5)
                submitted = st.form_submit_button(f"Add {role_label.lower()}", type="primary")
            if submitted:
                manager_id = manager_choice.split("(")[-1].rstrip(")") if manager_choice else None
                try:
                    api().post(
                        "/employees",
                        {
                            "name": name,
                            "email": email,
                            "role": role,
                            "title": title,
                            "department": department,
                            "manager_id": manager_id,
                            "join_date": join_date.isoformat(),
                            "phone": phone,
                            "is_active": active,
                            "balances": {"annual": annual, "earned": earned, "sick": sick},
                        },
                    )
                    set_flash("success", f"{role_label} {name.strip()} added and recorded in SQLite and Excel.")
                    st.rerun()
                except ApiError as exc:
                    st.error(str(exc))
    rows = [
        {"Name": item["name"], "Title": item["title"], "Department": item["department"], "Manager": item.get("manager_name") or "-", "Role": ROLE_LABEL[item["role"]]}
        for item in data["employees"]
    ]
    st.dataframe(rows, width="stretch", hide_index=True)
    selected = st.selectbox("Open employee profile", [item["name"] for item in data["employees"]])
    target = next(item for item in data["employees"] if item["name"] == selected)
    render_details(data, target["id"])


def render_records() -> None:
    st.title("Excel records")
    try:
        status = api().get("/records/excel/status")
    except ApiError as exc:
        st.error(str(exc))
        return
    st.write(f"**Workbook:** {status['path']}")
    st.dataframe([{"Sheet": key, "Rows": value} for key, value in status["sheets"].items()], width="stretch", hide_index=True)
    if status.get("last_error"):
        st.warning(status["last_error"])
    if st.button("Rebuild workbook from SQLite", type="primary"):
        try:
            api().post("/records/excel/rebuild")
            st.success("Workbook rebuilt from SQLite.")
            st.rerun()
        except ApiError as exc:
            st.error(str(exc))


def render_page(page: str, data: dict) -> None:
    if page == "My Dashboard":
        render_dashboard(data)
    elif page == "Book Leave":
        render_book_leave(data)
    elif page == "My Leave History":
        render_history(data)
    elif page == "My Details":
        render_details(data)
    elif page == "Approvals":
        render_approvals(data)
    elif page == "Wallchart":
        render_wallchart(data)
    elif page == "Burnout Board":
        render_burnout()
    elif page == "Team Statistics":
        render_stats(data, "team")
    elif page == "Overview":
        render_overview(data)
    elif page == "All Requests":
        render_all_requests(data)
    elif page == "Statistics":
        render_stats(data, "company")
    elif page == "Employees":
        render_employees(data)
    elif page == "Records":
        render_records()
    else:
        st.error("Page not available.")


def main() -> None:
    init_state()
    inject_daybook_theme()
    render_flash_banner()
    if not st.session_state.token or not st.session_state.user:
        render_login()
        return
    data = load_dashboard()
    if not data:
        return
    st.session_state.user = data["user"]
    page = render_sidebar(data)
    render_page(page, data)


if __name__ == "__main__":
    main()
