import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.storage import load_data
from utils.city_page import inject_css, render_info_box, render_weather, render_photos, render_things_to_do

inject_css()
data = load_data()

st.title("🌷 Maastricht")

# ---------- Quick info ----------
render_info_box(
    language="Dutch",
    currency="Euro (EUR)",
)

# ---------- Weather ----------
render_weather("Maastricht", lat=50.8514, lon=5.6910)

st.divider()

# ---------- Intro ----------
st.markdown(
    """
Maastricht is a city in the southeastern Netherlands, capital of the province of Limburg,
close to the borders with Belgium and Germany. It is one of the oldest cities in the
Netherlands, with roots going back to Roman times.

It gave its name to the 1992 Maastricht Treaty, the agreement that formally established
the European Union.
"""
)

st.divider()

# ---------- Photos ----------
PHOTOS = [
    (
        "https://commons.wikimedia.org/wiki/Special:FilePath/2010.07.20.150755_Sint_Servaasbrug_Maastricht.jpg",
        "Sint Servaasbrug bridge over the Meuse",
    ),
    (
        "https://commons.wikimedia.org/wiki/Special:FilePath/Vrijthof,_Maastricht,_Netherlands.jpg",
        "Vrijthof square",
    ),
]
render_photos(PHOTOS)

st.divider()

# ---------- Things to do (editable, persisted) ----------
render_things_to_do(data, city_key="Maastricht")