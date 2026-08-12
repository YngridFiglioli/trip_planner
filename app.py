import datetime as dt
import os
import sys

import streamlit as st

# Make sure the project root (this file's folder) is importable, regardless
# of the working directory Streamlit was launched from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.storage import load_data, save_data
from utils.currency import get_rates, convert, TARGET_CURRENCIES

st.set_page_config(
    page_title="Trip Planner",
    page_icon="🧳",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

ROUTE = [
    ("Oct 24", "Arrival at 14:45 — train to Maastricht (2h30)"),
    ("Oct 24–27", "Maastricht"),
    ("Oct 27", "Maastricht Aachen airport → flight to Prague"),
    ("Oct 27–30", "Prague"),
    ("Oct 30", "Prague airport → flight to Amsterdam"),
    ("Oct 30 – Nov 1", "Amsterdam"),
    ("Nov 1", "Amsterdam airport, 14:30 flight → Mexico City (CDMX)"),
]

for when, what in ROUTE:
    st.markdown(
        f"""<div class="trip-card">
        <b>{when}</b><br/>
        <span style="color:gray;">{what}</span>
        </div>""",
        unsafe_allow_html=True,
    )

st.divider()

with st.expander("✏️ Trip settings", expanded=not data.get("trip_name") or data.get("trip_name") == "My Trip"):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        trip_name = st.text_input("Trip name", value=data.get("trip_name", "My Trip"))
    with col2:
        start_date = st.date_input(
            "Start date",
            value=dt.date.fromisoformat(data["start_date"]) if data.get("start_date") else dt.date.today(),
        )
    with col3:
        end_date = st.date_input(
            "End date",
            value=dt.date.fromisoformat(data["end_date"]) if data.get("end_date") else dt.date.today(),
        )
    base_currency = st.selectbox(
        "Your home currency (used as the default reference)",
        TARGET_CURRENCIES,
        index=TARGET_CURRENCIES.index(data.get("base_currency", "EUR")),
    )
    if st.button("Save settings", type="primary"):
        data["trip_name"] = trip_name or "My Trip"
        data["start_date"] = start_date.isoformat()
        data["end_date"] = end_date.isoformat()
        data["base_currency"] = base_currency
        save_data(data)
        st.success("Saved!")
        st.rerun()

st.divider()

# ---------- Quick stats ----------
num_days = len(data.get("days", []))
num_destinations = len(data.get("destinations", []))
base = data.get("base_currency", "EUR")
rates, is_live = get_rates(base)

total_by_currency = {c: 0.0 for c in TARGET_CURRENCIES}
for bucket in ("flights", "hotels", "tickets"):
    for item in data.get(bucket, []):
        cost = item.get("cost") or 0
        cur = item.get("currency", base)
        for target in TARGET_CURRENCIES:
            total_by_currency[target] += convert(cost, cur, target, rates, base)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Days planned", num_days)
col2.metric("Destinations", num_destinations)
col3.metric(f"Total spend ({base})", f"{total_by_currency[base]:,.2f}")
other = [c for c in TARGET_CURRENCIES if c != base]
col4.metric(f"≈ {other[0]}", f"{total_by_currency[other[0]]:,.2f}")

if not is_live:
    st.caption("⚠️ Using offline/fallback exchange rates — live rates unavailable right now.")

st.divider()

# ---------- Upcoming days preview ----------
st.subheader("📅 Upcoming days")
days_sorted = sorted(data.get("days", []), key=lambda d: d.get("date", ""))
if not days_sorted:
    st.info("No days planned yet. Go to the **Itinerary** page to add your trip days.")
else:
    for day in days_sorted[:5]:
        loc = ", ".join(filter(None, [day.get("city"), day.get("country")]))
        n_act = len(day.get("activities", []))
        st.markdown(
            f"""<div class="trip-card">
            <b>{day.get('date', '')}</b> — {loc or 'No location set'}<br/>
            <span style="color:gray;">{n_act} activit{'y' if n_act == 1 else 'ies'} planned</span>
            </div>""",
            unsafe_allow_html=True,
        )
    if len(days_sorted) > 5:
        st.caption(f"+ {len(days_sorted) - 5} more day(s) — see the Itinerary page.")

st.divider()
st.page_link("pages/1_Itinerary.py", label="Go to Itinerary", icon="🗓️")
st.page_link("pages/2_Budget.py", label="Go to Budget", icon="💰")
st.page_link("pages/3_Destinations.py", label="Go to Destinations", icon="🌍")