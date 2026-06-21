from __future__ import annotations

import streamlit as st

def inject_daybook_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --paper:#E7E5DC;
            --surface:#FBFAF6;
            --surface-2:#F0EEE6;
            --ink:#1C1E22;
            --muted:#676B70;
            --faint:#9B9C94;
            --line:#D8D5CA;
            --pine:#26473C;
            --pine-2:#2F5A4B;
            --pine-soft:#DDE7DF;
            --ochre:#B26A2E;
            --reject:#9C3A2E;
        }
        .stApp {background: var(--paper); color: var(--ink);}
        .block-container {padding-top: 1.25rem; max-width: 1180px;}
        section[data-testid="stSidebar"] {
            background: var(--surface);
            border-right: 1px solid var(--line);
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] label {color: var(--muted);}
        h1, h2, h3 {
            color: var(--ink);
            letter-spacing: -0.01em;
        }
        div[data-testid="stButton"] button,
        div[data-testid="stFormSubmitButton"] button {
            background: var(--surface) !important;
            color: var(--ink) !important;
            border-radius: 7px;
            border: 1px solid var(--line);
            font-weight: 700;
        }
        div[data-testid="stButton"] button p,
        div[data-testid="stButton"] button span,
        div[data-testid="stFormSubmitButton"] button p,
        div[data-testid="stFormSubmitButton"] button span {
            color: inherit !important;
        }
        div[data-testid="stButton"] button:hover,
        div[data-testid="stFormSubmitButton"] button:hover {
            background: var(--surface-2) !important;
            color: var(--ink) !important;
            border-color: var(--line) !important;
        }
        div[data-testid="stButton"] button[kind="primary"],
        div[data-testid="stFormSubmitButton"] button[kind="primary"] {
            background: var(--pine) !important;
            color: #FBFAF6 !important;
            border-color: var(--pine) !important;
        }
        div[data-testid="stButton"] button[kind="primary"]:hover,
        div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
            background: var(--pine-2) !important;
            color: #FBFAF6 !important;
            border-color: var(--pine-2) !important;
        }
        .db-brand {
            font-size: 1.55rem;
            font-weight: 800;
            color: var(--ink);
            line-height: 1;
            margin-bottom: .1rem;
        }
        .db-brand-sub {
            font-size: .68rem;
            letter-spacing: .22em;
            text-transform: uppercase;
            color: var(--faint);
            border-bottom: 1px solid var(--line);
            padding-bottom: 1rem;
            margin-bottom: 1rem;
        }
        .db-login-hero {
            min-height: 560px;
            background: var(--pine);
            color: #EFEFE7;
            border-radius: 10px;
            padding: 2.4rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .db-login-hero h1 {
            color: #EFEFE7;
            font-size: 2.45rem;
            margin: 0;
        }
        .db-login-hero .tag {
            font-size: .72rem;
            letter-spacing: .22em;
            text-transform: uppercase;
            opacity: .72;
        }
        .db-login-hero .big {
            font-size: 1.8rem;
            line-height: 1.18;
            max-width: 430px;
        }
        .db-login-card {
            background: transparent;
            padding: 1.25rem 0;
        }
        .db-eyebrow {
            font-size: .72rem;
            letter-spacing: .14em;
            text-transform: uppercase;
            color: var(--faint);
            font-weight: 800;
            margin-bottom: .45rem;
        }
        .db-card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 1.1rem;
            box-shadow: 0 1px 2px rgba(28,30,34,.06), 0 2px 8px rgba(28,30,34,.04);
        }
        .db-bal-grid {
            display:grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: .85rem;
            margin: .5rem 0 1.25rem;
        }
        .db-bal {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 1rem;
            border-left: 4px solid var(--accent);
        }
        .db-bal .label {
            font-size: .72rem;
            letter-spacing: .08em;
            text-transform: uppercase;
            color: var(--muted);
            font-weight: 800;
        }
        .db-bal .num {
            font-size: 1.8rem;
            font-weight: 900;
            margin-top: .35rem;
        }
        .db-bal .sub {
            color: var(--faint);
            font-size: .78rem;
            margin-top: .2rem;
        }
        .db-gauge {
            height: 8px;
            border: 1px solid var(--line);
            background: var(--surface-2);
            border-radius: 4px;
            overflow: hidden;
            margin-top: .75rem;
        }
        .db-gauge span {
            display: block;
            height: 100%;
            width: var(--pct);
            background: var(--accent);
        }
        .db-table-wrap {
            overflow-x: auto;
            border: 1px solid var(--line);
            border-radius: 10px;
            background: var(--surface);
            margin: .5rem 0 1rem;
        }
        table.db-table {
            width: 100%;
            border-collapse: collapse;
            font-size: .9rem;
        }
        .db-table th {
            text-align: left;
            font-size: .68rem;
            letter-spacing: .11em;
            text-transform: uppercase;
            color: var(--faint);
            border-bottom: 1px solid var(--line);
            padding: .75rem .9rem;
            white-space: nowrap;
        }
        .db-table td {
            border-bottom: 1px solid #E6E3D9;
            padding: .78rem .9rem;
            vertical-align: middle;
        }
        .db-table tr:last-child td {border-bottom: none;}
        .db-status {
            display:inline-flex;
            align-items:center;
            gap:.35rem;
            border-radius: 5px;
            padding:.16rem .5rem;
            font-size:.74rem;
            font-weight:900;
            letter-spacing:.02em;
        }
        .db-status.pending {background:#F3E6CC;color:#9A6A1C;}
        .db-status.approved {background:#DCEBE0;color:#2C6A4E;}
        .db-status.rejected {background:#F1DAD4;color:#9C3A2E;}
        .db-status.cancelled {background:#E7E5DC;color:#6C7076;}
        .db-avatar {
            display:inline-grid;
            place-items:center;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: var(--pine);
            color: #FBFAF6;
            font-size: .72rem;
            font-weight: 900;
            margin-right: .45rem;
        }
        .db-chip {
            display:inline-block;
            border:1px solid var(--line);
            background:var(--surface-2);
            border-radius:6px;
            padding:.1rem .45rem;
            font-size:.74rem;
            color:var(--muted);
            font-weight:800;
        }
        .db-ribbon {
            border: 1px solid var(--line);
            border-radius: 10px;
            overflow: hidden;
            background: var(--surface);
            margin: .75rem 0 1.2rem;
        }
        .db-ribbon-scale,
        .db-lane {
            display: grid;
            grid-template-columns: 150px 1fr;
        }
        .db-ribbon-scale {
            background: var(--surface-2);
            border-bottom: 1px solid var(--line);
        }
        .db-gut {
            padding: .65rem .8rem;
            border-right: 1px solid var(--line);
            color: var(--faint);
            font-size: .68rem;
            letter-spacing: .11em;
            text-transform: uppercase;
            font-weight: 900;
        }
        .db-scale-track,
        .db-lane-track {
            position: relative;
            min-height: 38px;
        }
        .db-scale-tick {
            position:absolute;
            top:.55rem;
            transform:translateX(-50%);
            color: var(--faint);
            font-size:.68rem;
            font-weight:800;
        }
        .db-group-row {
            padding: .45rem .8rem;
            background: var(--surface-2);
            border-bottom: 1px solid #E6E3D9;
            color: var(--muted);
            font-size: .68rem;
            letter-spacing: .12em;
            text-transform: uppercase;
            font-weight: 900;
        }
        .db-lane {
            border-bottom: 1px solid #E6E3D9;
        }
        .db-lane:last-child {border-bottom: none;}
        .db-lane-name {
            display:flex;
            align-items:center;
            gap:.45rem;
            padding: .5rem .8rem;
            border-right: 1px solid #E6E3D9;
            min-height: 44px;
            font-weight: 800;
        }
        .db-band {
            position:absolute;
            top:0;
            bottom:0;
            z-index:0;
        }
        .db-band.weekend {background:#E6E3D9; opacity:.65;}
        .db-band.holiday {background:repeating-linear-gradient(45deg,#DDE7DF 0 5px,transparent 5px 10px);}
        .db-band.locked {background:repeating-linear-gradient(45deg,rgba(178,106,46,.26) 0 5px,transparent 5px 10px);}
        .db-today {
            position:absolute;
            top:0;
            bottom:0;
            width:2px;
            background: var(--ochre);
            z-index:3;
        }
        .db-seg {
            position:absolute;
            top:9px;
            height:26px;
            border-radius:6px;
            z-index:2;
            overflow:hidden;
            white-space:nowrap;
            color:#fff;
            font-size:.68rem;
            font-weight:900;
            padding:.28rem .45rem;
        }
        .db-seg.pending {
            color: var(--ink);
            background: transparent !important;
            border: 1.5px dashed var(--accent);
            background-image: repeating-linear-gradient(45deg,var(--soft) 0 6px,transparent 6px 12px) !important;
        }
        .db-legend {
            display:flex;
            flex-wrap:wrap;
            gap:1rem;
            border-top:1px solid #E6E3D9;
            padding:.65rem .8rem;
            color:var(--muted);
            font-size:.75rem;
            font-weight:800;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

