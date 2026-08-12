import streamlit as st

# This file is the entry point Streamlit launches (and what Streamlit Cloud's
# "Main file path" should keep pointing to). It doesn't render content itself
# — it just sets the page config once, then hands off to st.navigation, which
# lets us control the sidebar labels (e.g. "Home" instead of the raw
# filename) regardless of what each page file is called.

st.set_page_config(
    page_title="Trip Planner",
    page_icon="🧳",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = [
    st.Page("pages/0_Home.py", title="Home", icon="🧳", default=True),
    st.Page("pages/1_Itinerary.py", title="Itinerary", icon="🗓️"),
    st.Page("pages/2_Budget.py", title="Budget", icon="💰"),
    st.Page("pages/5_Maastricht.py", title="Maastricht", icon="🌷"),
    st.Page("pages/4_Prague.py", title="Prague", icon="🏰"),
    st.Page("pages/6_Amsterdam.py", title="Amsterdam", icon="🚲"),
    st.Page("pages/3_Destinations.py", title="Other destinations", icon="🌍"),
]

nav = st.navigation(pages, position="sidebar")
nav.run()