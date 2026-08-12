import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Prague", page_icon="🏰", layout="wide")
st.markdown(
    """
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
    """,
    unsafe_allow_html=True,
)

st.title("🏰 Prague - Bienvenidos!")

# ---------- Quick info ----------
st.markdown(
    """
    <div class="info-box">
        <div class="info-row">🗣️ <b>Language:</b> Czech</div>
        <div class="info-row">💰 <b>Currency:</b> Czech Koruna (CZK)</div>
        <div class="info-row">💰 <b>Currency Exchange Rate:</b> 1CZK ≈ 0.83MXN</div>
        <div class="info-row">💰 <b>Currency Exchange Rate:</b> 1EUR ≈ 24.25CZK</div>
        <div class="info-row">💰 <b>Currency Exchange Rate:</b> 1EUR ≈ 19.85MXN</div>
        <div class="info-row">📍 <b>Address (base):</b> Rodvinovská 1567/4, Prague 4 —
            <a href="https://maps.app.goo.gl/3TtifCHPeJ3EnvBY9" target="_blank">open in Google Maps</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

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
st.subheader("📸 Prague in pictures")

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

cols = st.columns(2)
for i, (url, caption) in enumerate(PHOTOS):
    with cols[i % 2]:
        try:
            st.image(url, caption=caption, use_container_width=True)
        except Exception:
            st.caption(f"(Couldn't load image: {caption})")

st.caption("Photos: Wikimedia Commons, freely licensed.")

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