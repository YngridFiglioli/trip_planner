"""
Local JSON-based persistence for the trip planner.

Everything lives in one file (data/trip_data.json) so the app has no
external database dependency. Safe defaults are created on first run.
"""

import json
import os
import uuid

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATA_FILE = os.path.join(DATA_DIR, "trip_data.json")

DEFAULT_DATA = {
    "trip_name": "My Trip",
    "start_date": "",
    "end_date": "",
    "base_currency": "EUR",
    "days": [],          # [{id, date, city, country, activities: [...]}]
    "flights": [],        # [{id, title, link, cost, currency, notes}]
    "hotels": [],         # [{id, name, address, link, check_in, check_out, cost, currency, notes}]
    "tickets": [],         # [{id, title, link, cost, currency, date, notes}]
    "destinations": [],    # [{id, country, city, notes, must_see: [str], links: [str]}]
    "todos": [],            # [{id, text, done}]
    "city_activities": {},  # {city_key: [{id, title, time, price, currency, link, notes}]}
}


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def new_id() -> str:
    return uuid.uuid4().hex[:8]


def load_data() -> dict:
    _ensure_data_dir()
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA.copy())
        return DEFAULT_DATA.copy()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}

    # Backfill any missing keys (safe upgrades between versions)
    changed = False
    for key, default_value in DEFAULT_DATA.items():
        if key not in data:
            data[key] = default_value.copy() if isinstance(default_value, (list, dict)) else default_value
            changed = True

    if changed:
        save_data(data)

    return data


def save_data(data: dict) -> None:
    _ensure_data_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)