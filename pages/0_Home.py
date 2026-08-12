import datetime as dt
import os
import sys

import streamlit as st

# Make sure the project root is importable, regardless of the working
# directory Streamlit was launched from. (Page config is set once, centrally,
# in app.py — this file is only ever run through st.navigation.)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.storage import load_data, save_data, new_id
from utils.route_calendar import render_route_calendar

# ---------- Mobile-friendly global styling ----------
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1000px;
        }
        [data-testid="stMetricValue"] { font-size: 1.4rem; }
        h1, h2, h3 { letter-spacing: -0.02em; }
        .trip-card {
            border: 1px solid rgba(128,128,128,0.25);
            border-radius: 12px;
            padding: 1rem 1.2rem;
            margin-bottom: 0.75rem;
        }
        @media (max-width: 640px) {
            .block-container { padding-left: 0.8rem; padding-right: 0.8rem; }
            [data-testid="stMetricValue"] { font-size: 1.15rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

data = load_data()

# ---------- Route overview ----------
st.subheader("🗺️ Route overview")

ROUTE_SEGMENTS = [
    {"start": dt.date(2026, 10, 24), "end": dt.date(2026, 10, 27), "label": "Maastricht", "color": "#4f7cff"},
    {"start": dt.date(2026, 10, 27), "end": dt.date(2026, 10, 30), "label": "Prague", "color": "#ff6584"},
    {"start": dt.date(2026, 10, 30), "end": dt.date(2026, 11, 1), "label": "Amsterdam", "color": "#ffb648"},
]

# ---------- Exchange rates ----------
st.markdown(
    """
    <div class="trip-card">
        <div>💰 <b>Currency Exchange Rate:</b> 1 CZK ≈ 0.83 MXN</div>
        <div>💰 <b>Currency Exchange Rate:</b> 1 EUR ≈ 24.25 CZK</div>
        <div>💰 <b>Currency Exchange Rate:</b> 1 EUR ≈ 19.85 MXN</div>
    </div>
    """,
    unsafe_allow_html=True,
)

render_route_calendar(ROUTE_SEGMENTS, buffer_days=0)

st.caption(
    "Key transfers — Oct 24: arrival 14:45, train to Maastricht (2h30). "
    "Oct 27: Maastricht Aachen airport → flight to Prague. "
    "Oct 30: Prague airport → flight to Amsterdam. "
    "Nov 1: Amsterdam airport, 14:30 flight → Mexico City (CDMX)."
)

st.divider()

# ---------- To-do list ----------
st.subheader("✅ To-do list")
st.caption("Trip prep tasks — book this, buy that, don't forget the other thing.")

todos = data.setdefault("todos", [])

for todo in todos:
    c1, c2 = st.columns([10, 1])
    with c1:
        checked = st.checkbox(
            todo["text"],
            value=todo.get("done", False),
            key=f"todo_{todo['id']}",
        )
        if checked != todo.get("done", False):
            todo["done"] = checked
            save_data(data)
            st.rerun()
    with c2:
        if st.button("🗑️", key=f"del_todo_{todo['id']}", help="Remove"):
            data["todos"] = [t for t in todos if t["id"] != todo["id"]]
            save_data(data)
            st.rerun()

with st.form(key="add_todo_form", clear_on_submit=True):
    c1, c2 = st.columns([5, 1])
    with c1:
        new_todo_text = st.text_input("Add a task", label_visibility="collapsed", placeholder="e.g. Buy travel insurance")
    with c2:
        submitted = st.form_submit_button("Add", type="primary")
    if submitted and new_todo_text.strip():
        todos.append({"id": new_id(), "text": new_todo_text.strip(), "done": False})
        save_data(data)
        st.rerun()

st.divider()
st.page_link("pages/1_Itinerary.py", label="Go to Itinerary", icon="🗓️")
st.page_link("pages/2_Budget.py", label="Go to Budget", icon="💰")
st.page_link("pages/5_Maastricht.py", label="Go to Maastricht", icon="🌷")
st.page_link("pages/4_Prague.py", label="Go to Prague", icon="🏰")
st.page_link("pages/6_Amsterdam.py", label="Go to Amsterdam", icon="🚲")