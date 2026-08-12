import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.storage import load_data
from utils.city_page import inject_css, render_info_box, render_weather, render_photos, render_things_to_do

inject_css()
data = load_data()

st.title("🏰 Prague - Bienvenidos!")

# ---------- Quick info ----------
render_info_box(
    language="Czech",
    currency="Czech Koruna (CZK)",
    address="Rodvinovská 1567/4, Prague 4",
    address_link="https://maps.app.goo.gl/3TtifCHPeJ3EnvBY9",
    extra_rows=[
        "💰 <b>Currency Exchange Rate:</b> 1 CZK ≈ 0.83 MXN",
        "💰 <b>Currency Exchange Rate:</b> 1 EUR ≈ 24.25 CZK",
        "💰 <b>Currency Exchange Rate:</b> 1 EUR ≈ 19.85 MXN",
    ],
)

# ---------- Weather ----------
render_weather("Prague", lat=50.0755, lon=14.4378)

st.divider()

# ---------- Intro ----------
st.markdown(
    """
The Czech Republic is a landlocked country in Central Europe, with its capital in Prague,
set in the historic regions of Bohemia and Moravia. It was part of the Holy Roman Empire
for centuries, and in 1918 Czechoslovakia was born following the collapse of the
Austro-Hungarian Empire.

The Nazis annexed the country in 1938 and occupied it; after World War II, a long communist
regime under Soviet influence followed. Communism only came to an end in 1989, and in 1993
Czechoslovakia peacefully split into the Czech Republic and Slovakia.

Today it is a member of NATO, the European Union, and the Schengen Area.
"""
)

st.divider()

# ---------- Photos ----------
PHOTOS = [
    (
        "https://commons.wikimedia.org/wiki/Special:FilePath/Charles_Bridge_Prague.jpg",
        "Charles Bridge, over the Vltava river",
    ),
    (
        "https://commons.wikimedia.org/wiki/Special:FilePath/Prazsky_hrad_karluv_most_panorama.jpg",
        "Prague Castle and Charles Bridge",
    ),
    (
        "https://commons.wikimedia.org/wiki/Special:FilePath/Old_Town_Square-Prague.jpg",
        "Old Town Square and the Astronomical Clock",
    ),
    (
        "https://commons.wikimedia.org/wiki/Special:FilePath/Prague_panorama.jpg",
        "City panorama from Petřín hill",
    ),
]
render_photos(PHOTOS)

st.divider()

# ---------- Things to do (editable, persisted) ----------
render_things_to_do(data, city_key="Prague")

st.divider()

# ---------- Typical foods ----------
st.subheader("🍽️ Typical foods")

foods = [
    ("Goulash / Guláš", "Beef stew with paprika, served with knedlíky (a type of bread/dumpling)."),
    ("Smažený sýr", "Breaded and fried cheese, served with fries and tartar sauce."),
    ("Vepřové koleno", "Pork knuckle, served with potatoes or sauerkraut."),
    ("Koláč", "Traditional sweet pastry: a dough base with a hollow center filled with something sweet."),
    ("Pilsner Urquell", "Traditional Czech beer — not food, but even more traditional than the rest."),
]

for name, desc in foods:
    st.markdown(f"**{name}** — {desc}")

st.divider()

# ---------- Czech 101 phrasebook ----------
st.subheader("🗣️ Czech 101")

phrasebook = [
    ("Hello", "Dobrý den / Ahoj", "General greeting, or when entering a shop"),
    ("Good morning", "Dobré ráno", "Mornings only"),
    ("Good night", "Dobrou noc", "Nights only"),
    ("Goodbye, take care", "Nashledanou", "Whenever you leave a place"),
    ("Cheers", "Na zdraví", "Cheers, when toasting with beer :)"),
    ("Beer", "Pivo", ""),
    ("Coffee", "Káva", ""),
    ("I don't understand", "Nerozumím", "When someone says something to you in Czech"),
    ("Please / excuse me", "Prosím", "To apologize, or to ask to pass"),
    ("Card (payment)", "Kartou", "Paying by card"),
    ("Here / for here", "Tady", "When you want to eat in, at the restaurant"),
    ("To go", "S sebou", "When you want to take the food home"),
]

st.table(
    {
        "English": [row[0] for row in phrasebook],
        "Czech": [row[1] for row in phrasebook],
        "When to use it": [row[2] for row in phrasebook],
    }
)