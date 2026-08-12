"""
Shared building blocks for per-city pages (Prague, Maastricht, Amsterdam, ...).

Each city page calls these to render the common bits (styling, quick info
box, photo gallery, and an editable "things to do" list with planned/actual
price, time, and a booking link) and then adds its own extra content
(history, food, phrasebook, etc.) around them.
"""

import streamlit as st

from utils.storage import save_data, new_id
from utils.currency import TARGET_CURRENCIES, get_rates, convert
from utils.weather import fetch_current_weather, WEATHER_CODES

PAGE_CSS = """
<style>
    .block-container {max-width: 1000px; padding-top: 1.5rem; padding-bottom: 3rem;}
    @media (max-width: 640px) {
        .block-container {padding-left: .8rem; padding-right: .8rem;}
    }
    .info-box {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }
    .info-row {margin-bottom: 0.3rem;}
</style>
"""


def inject_css():
    st.markdown(PAGE_CSS, unsafe_allow_html=True)


def render_info_box(language: str, currency: str, address: str = "", address_link: str = "", extra_rows=None):
    rows = f'<div class="info-row">🗣️ <b>Language:</b> {language}</div>'
    rows += f'<div class="info-row">💰 <b>Currency:</b> {currency}</div>'
    for extra in extra_rows or []:
        rows += f'<div class="info-row">{extra}</div>'
    if address:
        link_html = (
            f' — <a href="{address_link}" target="_blank">open in Google Maps</a>' if address_link else ""
        )
        rows += f'<div class="info-row">📍 <b>Address:</b> {address}{link_html}</div>'
    st.markdown(f'<div class="info-box">{rows}</div>', unsafe_allow_html=True)


def render_weather(city_name: str, lat: float, lon: float):
    st.subheader("🌤️ Current weather")
    weather = fetch_current_weather(lat, lon)
    if not weather:
        st.caption("Weather data unavailable right now.")
        return
    code = weather.get("weathercode")
    desc, icon = WEATHER_CODES.get(code, ("—", "🌡️"))
    temp = weather.get("temperature")
    wind = weather.get("windspeed")

    c1, c2, c3 = st.columns(3)
    c1.metric("Temperature", f"{temp:.0f}°C" if temp is not None else "—")
    c2.metric("Condition", f"{icon} {desc}")
    c3.metric("Wind", f"{wind:.0f} km/h" if wind is not None else "—")
    st.caption(
        f"Live conditions in {city_name} right now — for the trip dates, check a forecast "
        f"app closer to the day (forecasts only get reliable ~10-14 days out)."
    )


def render_photos(photos: list[tuple[str, str]]):
    st.subheader("📸 Photos")
    cols = st.columns(2)
    for i, (url, caption) in enumerate(photos):
        with cols[i % 2]:
            try:
                st.image(url, caption=caption, use_container_width=True)
            except Exception:
                st.caption(f"(Couldn't load image: {caption})")
    st.caption("Photos: Wikimedia Commons, freely licensed.")


def planned_price(act: dict) -> float:
    # Backward-compatible with older items that only had "price".
    return float(act.get("planned_price", act.get("price", 0)) or 0)


def effective_price(act: dict) -> float:
    # What actually gets counted as spend: the actual price if one was set,
    # otherwise the planned price (never silently drops to zero).
    actual = act.get("actual_price")
    return float(actual) if actual is not None else planned_price(act)


_planned_price = planned_price  # short internal aliases used below
_actual_price = effective_price


def render_things_to_do(data: dict, city_key: str):
    """
    An editable, persisted checklist of things to do in this city. Each item
    has a time, a link, and two prices: what you planned to pay, and what you
    actually paid (defaults to the planned price until you change it).
    """
    st.subheader("✅ Things to do")
    st.caption("Activities, tours, tickets — with price, time, and a link to book.")

    all_city_activities = data.setdefault("city_activities", {})
    activities = all_city_activities.setdefault(city_key, [])

    # ---------- Cost summary for this city ----------
    base = data.get("base_currency", "EUR")
    rates, is_live = get_rates(base)
    total_planned = sum(
        convert(_planned_price(a), a.get("currency", base), base, rates, base) for a in activities
    )
    total_actual = sum(
        convert(_actual_price(a), a.get("currency", base), base, rates, base) for a in activities
    )
    c1, c2 = st.columns(2)
    c1.metric(f"Planned ({base})", f"{total_planned:,.2f}")
    c2.metric(f"Spent ({base})", f"{total_actual:,.2f}")
    if not is_live:
        st.caption("⚠️ Using offline/fallback exchange rates for this summary.")

    # ---------- List + edit existing activities ----------
    activities_sorted = sorted(activities, key=lambda a: a.get("time") or "99:99")
    for act in activities_sorted:
        title = act.get("title") or "(untitled)"
        planned = _planned_price(act)
        actual = _actual_price(act)
        currency = act.get("currency", "EUR")
        time_str = f"{act['time']} — " if act.get("time") else ""
        if abs(actual - planned) > 0.005:
            price_str = f" · {actual:,.2f} {currency} (planned {planned:,.2f})"
        else:
            price_str = f" · {planned:,.2f} {currency}" if planned else ""

        with st.expander(f"{time_str}{title}{price_str}"):
            c1, c2 = st.columns([2, 1])
            with c1:
                new_title = st.text_input("What", value=title, key=f"title_{city_key}_{act['id']}")
            with c2:
                new_time = st.text_input("Time", value=act.get("time", ""), key=f"time_{city_key}_{act['id']}")

            c3, c4, c5 = st.columns(3)
            with c3:
                new_planned = st.number_input(
                    "Planned price", min_value=0.0, value=planned, key=f"planned_{city_key}_{act['id']}"
                )
            with c4:
                new_actual = st.number_input(
                    "Actual price (paid)",
                    min_value=0.0,
                    value=actual,
                    key=f"actual_{city_key}_{act['id']}",
                    help="Defaults to the planned price until you change it.",
                )
            with c5:
                new_currency = st.selectbox(
                    "Currency",
                    TARGET_CURRENCIES,
                    index=TARGET_CURRENCIES.index(currency) if currency in TARGET_CURRENCIES else 0,
                    key=f"cur_{city_key}_{act['id']}",
                )

            new_link = st.text_input("Link to buy tickets / more info", value=act.get("link", ""), key=f"link_{city_key}_{act['id']}")
            new_notes = st.text_area("Notes", value=act.get("notes", ""), key=f"notes_{city_key}_{act['id']}", height=68)

            b1, b2 = st.columns(2)
            with b1:
                if st.button("💾 Save changes", key=f"save_act_{city_key}_{act['id']}"):
                    act["title"] = new_title
                    act["time"] = new_time
                    act["planned_price"] = new_planned
                    act["actual_price"] = new_actual
                    act["currency"] = new_currency
                    act["link"] = new_link
                    act["notes"] = new_notes
                    act.pop("price", None)  # migrate away from the old field name
                    save_data(data)
                    st.success("Saved.")
                    st.rerun()
            with b2:
                if st.button("🗑️ Remove", key=f"del_act_{city_key}_{act['id']}"):
                    all_city_activities[city_key] = [a for a in activities if a["id"] != act["id"]]
                    save_data(data)
                    st.rerun()

    # ---------- Add a new activity ----------
    with st.form(key=f"add_activity_form_{city_key}", clear_on_submit=True):
        st.markdown("**Add something to do**")
        c1, c2 = st.columns([2, 1])
        with c1:
            f_title = st.text_input("What")
        with c2:
            f_time = st.text_input("Time (e.g. 10:00, or a date)")
        c3, c4 = st.columns(2)
        with c3:
            f_price = st.number_input("Planned price", min_value=0.0, value=0.0)
        with c4:
            f_currency = st.selectbox("Currency", TARGET_CURRENCIES)
        f_link = st.text_input("Link to buy tickets / more info")
        f_notes = st.text_area("Notes", height=68)
        submitted = st.form_submit_button("Add", type="primary")
        if submitted:
            if f_title.strip():
                activities.append(
                    {
                        "id": new_id(),
                        "title": f_title.strip(),
                        "time": f_time.strip(),
                        "planned_price": f_price,
                        "actual_price": f_price,  # mirrors planned until edited
                        "currency": f_currency,
                        "link": f_link.strip(),
                        "notes": f_notes.strip(),
                    }
                )
                save_data(data)
                st.rerun()
            else:
                st.warning("Give it a name first.")