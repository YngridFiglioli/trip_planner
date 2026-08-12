"""
Renders a small monthly calendar (like a Notion/Google-Calendar timeline)
with colored bars spanning the days of each leg of the trip.
"""

import calendar as cal
import datetime as dt

import streamlit as st

DAY_NAMES = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


def _overlaps(a_start, a_end, b_start, b_end) -> bool:
    return a_start <= b_end and b_start <= a_end


def render_route_calendar(segments: list[dict], months: list[tuple[int, int]]):
    """
    segments: [{"start": date, "end": date, "label": str, "color": "#rrggbb"}, ...]
    months:   [(year, month), ...] — which months to render, in order.
    """
    css = """
    <style>
    .rc-month { border: 1px solid rgba(128,128,128,0.25); border-radius: 12px;
                overflow: hidden; margin-bottom: 1rem; }
    .rc-month-header { padding: 0.7rem 1rem; font-weight: 600; font-size: 1.05rem;
                        border-bottom: 1px solid rgba(128,128,128,0.15); }
    .rc-daynames { display: flex; font-size: 0.68rem; color: gray; padding: 0.4rem 0;
                   border-bottom: 1px solid rgba(128,128,128,0.1); }
    .rc-daynames div { flex: 1; text-align: center; }
    .rc-week { position: relative; display: flex;
               border-bottom: 1px solid rgba(128,128,128,0.08); }
    .rc-day { flex: 1; min-height: 44px; padding: 3px 5px; font-size: 0.72rem;
              color: #888; border-right: 1px solid rgba(128,128,128,0.05);
              box-sizing: border-box; }
    .rc-day.empty { background: repeating-linear-gradient(
                    45deg, rgba(128,128,128,0.035), rgba(128,128,128,0.035) 4px,
                    transparent 4px, transparent 8px); }
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
    html = css

    for year, month in months:
        month_label = dt.date(year, month, 1).strftime("%B %Y")
        weeks = cal.Calendar(firstweekday=0).monthdayscalendar(year, month)

        html += f'<div class="rc-month"><div class="rc-month-header">{month_label}</div>'
        html += '<div class="rc-daynames">' + "".join(f"<div>{d}</div>" for d in DAY_NAMES) + "</div>"

        for week in weeks:
            week_dates = [dt.date(year, month, d) if d else None for d in week]
            real_dates = [d for d in week_dates if d]
            if not real_dates:
                continue
            week_start, week_end = real_dates[0], real_dates[-1]

            overlapping = [
                seg for seg in segments if _overlaps(seg["start"], seg["end"], week_start, week_end)
            ]
            overlapping.sort(key=lambda s: s["start"])

            # Greedy lane assignment so bars that don't share any day can sit
            # on the same horizontal line; bars that do overlap stack.
            lane_end_cols: list[int] = []
            placements = []  # (seg, lane, start_col, end_col)
            for seg in overlapping:
                cols = [i for i, d in enumerate(week_dates) if d and seg["start"] <= d <= seg["end"]]
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
            for day in week:
                cls = "rc-day" + (" empty" if day == 0 else "")
                html += f'<div class="{cls}">{day if day else ""}</div>'
            for seg, lane, s_col, e_col in placements:
                left = (s_col / 7) * 100
                width = ((e_col - s_col + 1) / 7) * 100
                top = 24 + lane * 22
                html += (
                    f'<div class="rc-bar" style="left:{left}%; width:calc({width}% - 4px); '
                    f'top:{top}px; background:{seg["color"]};">{seg["label"]}</div>'
                )
            html += "</div>"

        html += "</div>"

    st.markdown(html, unsafe_allow_html=True)