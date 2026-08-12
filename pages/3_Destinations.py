import os
import sys

import streamlit as st

# Make sure the project root is importable, regardless of the working
# directory Streamlit was launched from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.storage import load_data, save_data, new_id

st.markdown(
    "<style>.block-container{max-width:1000px;padding-top:1.5rem;} "
    "@media (max-width:640px){.block-container{padding-left:.8rem;padding-right:.8rem;}}</style>",
    unsafe_allow_html=True,
)

data = load_data()

st.title("🌍 Cities & Countries")
st.caption("Keep notes, must-see spots and useful links for every place you're visiting.")

with st.form(key="add_destination_form", clear_on_submit=True):
    st.markdown("**Add a destination**")
    c1, c2 = st.columns(2)
    with c1:
        f_city = st.text_input("City")
    with c2:
        f_country = st.text_input("Country")
    f_notes = st.text_area("General notes", height=80)
    submitted = st.form_submit_button("Add destination", type="primary")
    if submitted:
        if f_city.strip() or f_country.strip():
            data.setdefault("destinations", []).append(
                {
                    "id": new_id(),
                    "city": f_city.strip(),
                    "country": f_country.strip(),
                    "notes": f_notes.strip(),
                    "must_see": [],
                    "links": [],
                }
            )
            save_data(data)
            st.rerun()
        else:
            st.warning("Add at least a city or country.")

st.divider()

destinations = data.get("destinations", [])
if not destinations:
    st.info("No destinations yet — add one above.")

for dest in destinations:
    label = ", ".join(filter(None, [dest.get("city"), dest.get("country")])) or "(unnamed)"
    with st.expander(f"📍 {label}"):
        c1, c2, c3 = st.columns([1.5, 1.5, 0.6])
        with c1:
            new_city = st.text_input("City", value=dest.get("city", ""), key=f"dest_city_{dest['id']}")
        with c2:
            new_country = st.text_input("Country", value=dest.get("country", ""), key=f"dest_country_{dest['id']}")
        with c3:
            st.write("")
            st.write("")
            if st.button("🗑️", key=f"dest_del_{dest['id']}", help="Delete this destination"):
                data["destinations"] = [d for d in destinations if d["id"] != dest["id"]]
                save_data(data)
                st.rerun()

        new_notes = st.text_area(
            "General notes", value=dest.get("notes", ""), key=f"dest_notes_{dest['id']}", height=90
        )

        if (
            new_city != dest.get("city", "")
            or new_country != dest.get("country", "")
            or new_notes != dest.get("notes", "")
        ):
            dest["city"] = new_city
            dest["country"] = new_country
            dest["notes"] = new_notes
            save_data(data)

        st.markdown("**Must-see spots**")
        for i, spot in enumerate(dest.get("must_see", [])):
            sc1, sc2 = st.columns([5, 1])
            sc1.markdown(f"- {spot}")
            if sc2.button("Remove", key=f"dest_{dest['id']}_spot_{i}"):
                dest["must_see"].pop(i)
                save_data(data)
                st.rerun()
        new_spot = st.text_input("Add a must-see spot", key=f"dest_new_spot_{dest['id']}")
        if st.button("Add spot", key=f"dest_add_spot_{dest['id']}"):
            if new_spot.strip():
                dest.setdefault("must_see", []).append(new_spot.strip())
                save_data(data)
                st.rerun()

        st.markdown("**Useful links** (guides, maps, transit passes...)")
        for i, link in enumerate(dest.get("links", [])):
            lc1, lc2 = st.columns([5, 1])
            lc1.markdown(f"- [{link}]({link})")
            if lc2.button("Remove", key=f"dest_{dest['id']}_link_{i}"):
                dest["links"].pop(i)
                save_data(data)
                st.rerun()
        new_link = st.text_input("Add a link", key=f"dest_new_link_{dest['id']}")
        if st.button("Add link", key=f"dest_add_link_{dest['id']}"):
            if new_link.strip():
                dest.setdefault("links", []).append(new_link.strip())
                save_data(data)
                st.rerun()