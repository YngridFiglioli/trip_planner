"""
Renders a compact week-by-week timeline (like a Notion/Google-Calendar view)
with colored bars spanning the days of each leg of the trip — showing only
the weeks that actually overlap the trip, instead of full months.
"""

import datetime as dt

import streamlit as st

DAY_NAMES = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


def _overlaps(a_start, a_end, b_start, b_end) -> bool:
    return a_start <= b_end and b_start <= a_end


def _monday_of_week(d: dt.date) -> dt.date:
    return d - dt.timedelta(days=d.weekday())


def _day_label(d: dt.date, is_first_cell: bool) -> str:
    # Show the month name whenever the month changes (day 1) or on the very
    # first cell rendered, so a week that crosses Oct→Nov is still readable.
    if d.day == 1 or is_first_cell:
        return f"{d.strftime('%b')} {d.day}"
    return str(d.day)


def render_route_calendar(
    segments: list[dict],
    buffer_days: int = 0,
    title: str | None = None,
):
    """
    segments: [{"start": date, "end": date, "label": str, "color": "#rrggbb"}, ...]
    buffer_days: extra days of context to show before/after the trip's own range.
    title: optional heading shown above the calendar (e.g. a date range).
    """
    if not segments:
        return

    trip_start = min(s["start"] for s in segments) - dt.timedelta(days=buffer_days)
    trip_end = max(s["end"] for s in segments) + dt.timedelta(days=buffer_days)

    first_week_start = _monday_of_week(trip_start)
    last_week_start = _monday_of_week(trip_end)

    css = """
    <style>
    .rc-cal { border: 1px solid rgba(128,128,128,0.25); border-radius: 12px;
              overflow: hidden; margin-bottom: 1rem; }
    .rc-cal-header { padding: 0.7rem 1rem; font-weight: 600; font-size: 1.0rem;
                      border-bottom: 1px solid rgba(128,128,128,0.15); }
    .rc-daynames { display: flex; font-size: 0.68rem; color: gray; padding: 0.4rem 0;
                   border-bottom: 1px solid rgba(128,128,128,0.1); }
    .rc-daynames div { flex: 1; text-align: center; }
    .rc-week { position: relative; display: flex;
               border-bottom: 1px solid rgba(128,128,128,0.08); }
    .rc-day { flex: 1; min-height: 44px; padding: 3px 5px; font-size: 0.72rem;
              color: #888; border-right: 1px solid rgba(128,128,128,0.05);
              box-sizing: border-box; }
    .rc-bar { position: absolute; height: 19px; border-radius: 5px; font-size: 0.66rem;
              color: white; display: flex; align-items: center; padding: 0 6px;
              overflow: hidden; white-space: nowrap; box-sizing: border-box;
              font-weight: 500; }
    @media (max-width: 640px) {
        .rc-day { font-size: 0.62rem; min-height: 36px; }
        .rc-bar { font-size: 0.52rem; height: 15px; }
    }
    </style>
    """

    header_label = title
    if header_label is None:
        try:
            header_label = f"{trip_start.strftime('%b %d')} – {trip_end.strftime('%b %d, %Y')}"
        except Exception:
            header_label = f"{trip_start} – {trip_end}"

    html = css + f'<div class="rc-cal"><div class="rc-cal-header">{header_label}</div>'
    html += '<div class="rc-daynames">' + "".join(f"<div>{d}</div>" for d in DAY_NAMES) + "</div>"

    cur = first_week_start
    first_cell_done = False
    while cur <= last_week_start:
        week_dates = [cur + dt.timedelta(days=i) for i in range(7)]

        overlapping = [
            seg for seg in segments if _overlaps(seg["start"], seg["end"], week_dates[0], week_dates[-1])
        ]
        overlapping.sort(key=lambda s: s["start"])

        # Greedy lane assignment: bars that don't share a day sit on the same line.
        lane_end_cols: list[int] = []
        placements = []
        for seg in overlapping:
            cols = [i for i, d in enumerate(week_dates) if seg["start"] <= d <= seg["end"]]
            if not cols:
                continue
            s_col, e_col = cols[0], cols[-1]
            lane = next((i for i, end in enumerate(lane_end_cols) if s_col > end), None)
            if lane is None:
                lane = len(lane_end_cols)
                lane_end_cols.append(e_col)
            else:
                lane_end_cols[lane] = e_col
            placements.append((seg, lane, s_col, e_col))

        n_lanes = max(len(lane_end_cols), 1) if overlapping else 0
        week_height = 30 + n_lanes * 22
        html += f'<div class="rc-week" style="height:{max(week_height, 44)}px;">'
        for d in week_dates:
            label = _day_label(d, is_first_cell=not first_cell_done)
            first_cell_done = True
            html += f'<div class="rc-day">{label}</div>'
        for seg, lane, s_col, e_col in placements:
            left = (s_col / 7) * 100
            width = ((e_col - s_col + 1) / 7) * 100
            top = 24 + lane * 22
            html += (
                f'<div class="rc-bar" style="left:{left}%; width:calc({width}% - 4px); '
                f'top:{top}px; background:{seg["color"]};">{seg["label"]}</div>'
            )
        html += "</div>"

        cur += dt.timedelta(days=7)

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)