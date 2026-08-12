import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.storage import load_data
from utils.city_page import inject_css, render_info_box, render_photos, render_things_to_do

inject_css()
data = load_data()

st.title("🚲 Amsterdam")

# ---------- Quick info ----------
render_info_box(
    language="Dutch",
    currency="Euro (EUR)",
)

# ---------- Intro ----------
st.markdown(
    """
Amsterdam is the capital of the Netherlands, known for its network of canals — a UNESCO
World Heritage Site — its cycling culture, and its role as a major center of trade during
the Dutch Golden Age in the 17th century.
"""
)

st.divider()

# ---------- Photos ----------
PHOTOS = [
    (
        "https://commons.wikimedia.org/wiki/Special:FilePath/Amsterdam_Canal_with_boat.jpg",
        "One of Amsterdam's canals",
    ),
    (
        "https://commons.wikimedia.org/wiki/Special:FilePath/Amsterdam_-_Rijksmuseum.jpg",
        "The Rijksmuseum",
    ),
]
render_photos(PHOTOS)

st.divider()

# ---------- Things to do (editable, persisted) ----------
render_things_to_do(data, city_key="Amsterdam")