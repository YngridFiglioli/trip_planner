"""
Currency helpers for the trip planner.

Fetches live exchange rates (free, no API key) from open.er-api.com.
Falls back to manually-entered rates (stored in session state) if the
request fails, e.g. when there is no internet access.
"""

import requests
import streamlit as st

TARGET_CURRENCIES = ["EUR", "CZK", "MXN"]
API_URL = "https://open.er-api.com/v6/latest/{base}"

# Used only if the live API call fails and the user hasn't set manual rates.
FALLBACK_RATES = {
    "EUR": {"EUR": 1.0, "CZK": 25.0, "MXN": 20.0},
    "CZK": {"EUR": 0.04, "CZK": 1.0, "MXN": 0.80},
    "MXN": {"EUR": 0.05, "CZK": 1.25, "MXN": 1.0},
}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_rates(base: str) -> dict | None:
    """Return {currency: rate} for TARGET_CURRENCIES relative to `base`, or None on failure."""
    try:
        resp = requests.get(API_URL.format(base=base), timeout=6)
        resp.raise_for_status()
        payload = resp.json()
        rates = payload.get("rates", {})
        result = {cur: rates[cur] for cur in TARGET_CURRENCIES if cur in rates}
        result[base] = 1.0
        if len(result) < len(TARGET_CURRENCIES):
            return None
        return result
    except Exception:
        return None


def get_rates(base: str) -> tuple[dict, bool]:
    """
    Returns (rates_dict, is_live).
    Tries the live API first, then session-manual overrides, then hardcoded fallback.
    """
    live = fetch_rates(base)
    if live:
        return live, True

    manual = st.session_state.get("manual_rates")
    if manual and base in manual:
        return manual[base], False

    return FALLBACK_RATES.get(base, {"EUR": 1.0, "CZK": 25.0, "MXN": 20.0}), False


def convert(amount: float, from_currency: str, to_currency: str, rates_from_base: dict, base: str) -> float:
    """
    Convert `amount` in `from_currency` to `to_currency`, given a rates table
    quoted relative to `base` (rates_from_base[base] == 1.0).
    """
    if from_currency == to_currency:
        return amount
    if from_currency not in rates_from_base or to_currency not in rates_from_base:
        return amount
    # Convert amount -> base -> target
    amount_in_base = amount / rates_from_base[from_currency]
    return amount_in_base * rates_from_base[to_currency]