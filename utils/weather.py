"""
Live current-weather lookup using Open-Meteo (free, no API key required).
"""

import requests
import streamlit as st

WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    56: ("Freezing drizzle", "🌧️"),
    57: ("Freezing drizzle", "🌧️"),
    61: ("Light rain", "🌧️"),
    63: ("Rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Freezing rain", "🌧️"),
    67: ("Freezing rain", "🌧️"),
    71: ("Light snow", "🌨️"),
    73: ("Snow", "🌨️"),
    75: ("Heavy snow", "❄️"),
    77: ("Snow grains", "🌨️"),
    80: ("Rain showers", "🌦️"),
    81: ("Rain showers", "🌦️"),
    82: ("Violent rain showers", "⛈️"),
    85: ("Snow showers", "🌨️"),
    86: ("Snow showers", "🌨️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm w/ hail", "⛈️"),
    99: ("Thunderstorm w/ hail", "⛈️"),
}

API_URL = "https://api.open-meteo.com/v1/forecast"


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_current_weather(lat: float, lon: float) -> dict | None:
    try:
        resp = requests.get(
            API_URL,
            params={"latitude": lat, "longitude": lon, "current_weather": True, "timezone": "auto"},
            timeout=6,
        )
        resp.raise_for_status()
        return resp.json().get("current_weather")
    except Exception:
        return None