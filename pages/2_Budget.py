import os
import sys

import pandas as pd
import streamlit as st

# Make sure the project root is importable, regardless of the working
# directory Streamlit was launched from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.storage import load_data, save_data, new_id
from utils.currency import get_rates, convert, TARGET_CURRENCIES

st.set_page_config(page_title="Budget", page_icon="💰", layout="wide")
st.markdown(
    "<style>.block-container{max-width:1100px;padding-top:1.5rem;} "
    "@media (max-width:640px){.block-container{padding-left:.8rem;padding-right:.8rem;}}</style>",
    unsafe_allow_html=True,
)

data = load_data()
base = data.get("base_currency", "EUR")

st.title("💰 Budget")
st.caption("Track flights, hotels and tickets/activities, and see totals converted across currencies.")

rates, is_live = get_rates(base)
if not is_live:
    st.warning("Live exchange rates unavailable — showing offline/fallback rates.")
else:
    st.caption(f"Live exchange rates loaded (base: {base}). Cached for 1 hour.")

BUCKETS = {
    "flights": {"label": "✈️ Flights", "extra_fields": ["link"]},
    "hotels": {"label": "🏨 Hotels", "extra_fields": ["address", "link", "check_in", "check_out"]},
    "tickets": {"label": "🎟️ Tickets & Activities", "extra_fields": ["link", "date"]},
}

# ---------- Overview ----------
st.subheader("Overview")

rows = []
for bucket_key, meta in BUCKETS.items():
    for item in data.get(bucket_key, []):
        rows.append(
            {
                "Category": meta["label"],
                "Item": item.get("title") or item.get("name") or "(unnamed)",
                "Cost": item.get("cost") or 0,
                "Currency": item.get("currency", base),
            }
        )

if rows:
    df = pd.DataFrame(rows)
    for target in TARGET_CURRENCIES:
        df[target] = df.apply(
            lambda r: convert(r["Cost"], r["Currency"], target, rates, base), axis=1
        )

    totals = {t: df[t].sum() for t in TARGET_CURRENCIES}
    cols = st.columns(len(TARGET_CURRENCIES))
    for c, t in zip(cols, TARGET_CURRENCIES):
        c.metric(f"Total in {t}", f"{totals[t]:,.2f}")

    st.dataframe(
        df[["Category", "Item", "Cost", "Currency"] + TARGET_CURRENCIES].style.format(
            {t: "{:,.2f}" for t in TARGET_CURRENCIES} | {"Cost": "{:,.2f}"}
        ),
        use_container_width=True,
        hide_index=True,
    )

    by_cat = df.groupby("Category")[base].sum()
    st.bar_chart(by_cat)
else:
    st.info("No expenses added yet — add flights, hotels or tickets below.")

st.divider()

with st.expander("⚙️ Manually override exchange rates"):
    st.caption("Only used as a fallback if live rates can't be fetched.")
    manual = st.session_state.get("manual_rates", {}).get(base, rates)
    m_cols = st.columns(len(TARGET_CURRENCIES))
    new_manual = {}
    for c, cur in zip(m_cols, TARGET_CURRENCIES):
        new_manual[cur] = c.number_input(
            f"1 {base} = ? {cur}", value=float(manual.get(cur, 1.0)), key=f"manual_{cur}"
        )
    if st.button("Save manual rates"):
        st.session_state.setdefault("manual_rates", {})[base] = new_manual
        st.success("Saved for this session.")

st.divider()

# ---------- Manage entries per bucket ----------
for bucket_key, meta in BUCKETS.items():
    st.subheader(meta["label"])
    items = data.get(bucket_key, [])

    for item in items:
        title_field = "name" if bucket_key == "hotels" else "title"
        title = item.get(title_field, "") or "(unnamed)"
        with st.expander(f"{title} — {item.get('cost', 0):,.2f} {item.get('currency', base)}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                new_title = st.text_input(
                    "Name" if bucket_key == "hotels" else "Title",
                    value=item.get(title_field, ""),
                    key=f"{bucket_key}_title_{item['id']}",
                )
            with col2:
                pass

            c1, c2 = st.columns(2)
            with c1:
                new_cost = st.number_input(
                    "Cost", value=float(item.get("cost", 0)), min_value=0.0, key=f"{bucket_key}_cost_{item['id']}"
                )
            with c2:
                new_currency = st.selectbox(
                    "Currency",
                    TARGET_CURRENCIES,
                    index=TARGET_CURRENCIES.index(item.get("currency", base)),
                    key=f"{bucket_key}_cur_{item['id']}",
                )

            extra_values = {}
            for field in meta["extra_fields"]:
                label = field.replace("_", " ").title()
                extra_values[field] = st.text_input(
                    label, value=item.get(field, ""), key=f"{bucket_key}_{field}_{item['id']}"
                )

            new_notes = st.text_area(
                "Notes", value=item.get("notes", ""), key=f"{bucket_key}_notes_{item['id']}", height=68
            )

            b1, b2 = st.columns([1, 1])
            with b1:
                if st.button("Save changes", key=f"{bucket_key}_save_{item['id']}"):
                    item[title_field] = new_title
                    item["cost"] = new_cost
                    item["currency"] = new_currency
                    item["notes"] = new_notes
                    item.update(extra_values)
                    save_data(data)
                    st.success("Saved.")
                    st.rerun()
            with b2:
                if st.button("🗑️ Delete", key=f"{bucket_key}_del_{item['id']}"):
                    data[bucket_key] = [i for i in items if i["id"] != item["id"]]
                    save_data(data)
                    st.rerun()

    with st.form(key=f"add_{bucket_key}_form", clear_on_submit=True):
        st.markdown(f"**Add new {meta['label'].split(' ', 1)[1].lower()} entry**")
        title_field = "name" if bucket_key == "hotels" else "title"
        f_title = st.text_input("Name" if bucket_key == "hotels" else "Title")
        f1, f2 = st.columns(2)
        with f1:
            f_cost = st.number_input("Cost", min_value=0.0, value=0.0)
        with f2:
            f_currency = st.selectbox("Currency", TARGET_CURRENCIES, index=TARGET_CURRENCIES.index(base))

        f_extra = {}
        for field in meta["extra_fields"]:
            label = field.replace("_", " ").title()
            f_extra[field] = st.text_input(label)

        f_notes = st.text_area("Notes", height=68)
        submitted = st.form_submit_button("Add", type="primary")
        if submitted:
            if f_title.strip():
                new_item = {
                    "id": new_id(),
                    title_field: f_title.strip(),
                    "cost": f_cost,
                    "currency": f_currency,
                    "notes": f_notes.strip(),
                }
                new_item.update(f_extra)
                data.setdefault(bucket_key, []).append(new_item)
                save_data(data)
                st.rerun()
            else:
                st.warning("A name/title is required.")

    st.divider()