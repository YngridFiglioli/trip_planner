# 🧳 Trip Planner

A Streamlit web app to plan a trip: a day-by-day itinerary, flights/hotels/
tickets with links and addresses, a budget overview converted between
**EUR**, **CZK**, and **MXN**, and reference pages for the cities and
countries you're visiting.

Works on desktop and on phones — Streamlit's layout is responsive by
default, and this app adds a bit of extra mobile-friendly styling on top.

## 1. Install

Requires Python 3.9+.

```bash
cd trip_planner
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Run

```bash
streamlit run app.py
```

Streamlit will open the app in your browser (usually `http://localhost:8501`).
On your phone, connect to the same Wi-Fi network as your computer and open
`http://<your-computer-local-ip>:8501` (Streamlit prints this "Network URL"
in the terminal when it starts).

## 3. Pages

- **Home** (`app.py`) — trip name/dates, quick stats, upcoming days.
- **Itinerary** (`pages/1_Itinerary.py`) — add days with city/country, and
  activities per day (time, title, link, notes).
- **Budget** (`pages/2_Budget.py`) — add flights, hotels (with address) and
  tickets/activities, each with a cost and currency. Totals are shown
  converted into EUR, CZK and MXN using live exchange rates (cached for 1
  hour), with a manual-rate fallback if you're offline.
- **Destinations** (`pages/3_Destinations.py`) — one entry per city/country
  with notes, a must-see list, and useful links.

## 4. Data storage

All data is saved locally to `data/trip_data.json`. There's no external
database — back up or version-control that file if you want to keep a
history of your trip planning.

## 5. Hosting for free (so you can use it from your phone anywhere)

The easiest option is **Streamlit Community Cloud**:

1. Push this folder to a GitHub repo.
2. Go to https://share.streamlit.io, sign in with GitHub, and deploy the
   repo (entry point: `app.py`).
3. You'll get a public URL that works on any device.

Note: on Streamlit Cloud, the filesystem is not permanently persistent
across redeploys — if you want your data to survive redeploys/restarts,
consider swapping `utils/storage.py` for a small hosted database (e.g.
Supabase, Google Sheets, or SQLite on a persistent volume). For a solo trip
planned over a few weeks on one deployment, the local JSON file is fine.

## 6. Customizing

- Add more currencies: edit `TARGET_CURRENCIES` in `utils/currency.py`.
- Change the color/theme: create a `.streamlit/config.toml` file — see
  https://docs.streamlit.io/develop/concepts/configuration/theming.
# trip_planner
