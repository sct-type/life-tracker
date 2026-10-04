"""Life Tracker: upload a CSV, choose which columns to plot, set goals."""
import os
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import core
import plots

st.set_page_config(page_title="Life Tracker", layout="wide")

HERE = Path(__file__).parent
DATA_DIR = HERE / "data"
CONFIG_PATH = HERE / "config.json"
# Set by start.command. A hosted copy never reads or writes a shared config file.
LOCAL = os.environ.get("LIFETRACKER_LOCAL") == "1"

st.title("Life Tracker")

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("CSV file", type="csv")
    year = st.number_input("Year for dates like 3/14", min_value=2000, max_value=2100,
                           value=date.today().year, step=1)

source, source_name = None, None
if uploaded is not None:
    source, source_name = uploaded, uploaded.name
elif DATA_DIR.is_dir() and sorted(DATA_DIR.glob("*.csv")):
    path = sorted(DATA_DIR.glob("*.csv"))[-1]
    source, source_name = path, path.name

if source is None:
    st.info("Upload a CSV in the sidebar to begin. It needs a Date column and at least one numeric column. "
            "Each row is one day.")
    st.stop()

try:
    df, numeric_cols, load_warnings = core.load_csv(source, int(year))
except ValueError as exc:
    st.error(str(exc))
    st.stop()

st.caption(f"{source_name} · {len(df)} rows · {df['Date'].min():%b %d, %Y} to {df['Date'].max():%b %d, %Y}")
for message in load_warnings:
    st.warning(message)

# ------------------------------------------------------------ plot setup state


def set_cards(frame):
    st.session_state["cards"] = frame
    st.session_state["cards_version"] = st.session_state.get("cards_version", 0) + 1


def initial_cards():
    if LOCAL and CONFIG_PATH.exists():
        try:
            frame, _ = core.cards_from_json(CONFIG_PATH.read_text(), numeric_cols)
            if len(frame):
                return frame
        except (ValueError, OSError):
            pass
    return core.default_cards(df, numeric_cols)


signature = tuple(numeric_cols)
if st.session_state.get("cols_signature") != signature:
    previous = st.session_state.get("cards")
    kept = previous[previous["column"].isin(numeric_cols)] if previous is not None else None
    set_cards(kept if kept is not None and len(kept) else initial_cards())
    st.session_state["cols_signature"] = signature

with st.sidebar:
    st.header("Plot setup")
    setup_file = st.file_uploader("Load a saved setup (JSON)", type="json", key="setup_upload")
    if setup_file is not None:
        file_sig = (setup_file.name, setup_file.size)
        if st.session_state.get("setup_sig") != file_sig:
            st.session_state["setup_sig"] = file_sig
            try:
                frame, setup_warnings = core.cards_from_json(setup_file.getvalue().decode("utf-8"), numeric_cols)
                set_cards(frame)
                for message in setup_warnings:
                    st.warning(message)
            except (ValueError, UnicodeDecodeError) as exc:
                st.error(str(exc))

# -------------------------------------------------------------- setup editor
with st.expander("Set up your plots", expanded=not st.session_state["cards"]["show"].any()):
    st.caption("One row per plot. Tick Show, pick a column, and optionally set a goal. "
               "Use Per = week for things you count per week, like hours worked or drinks. "
               "Add a row with the + at the bottom.")
    edited = st.data_editor(
        st.session_state["cards"],
        key=f"cards_editor_{st.session_state['cards_version']}",
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "show": st.column_config.CheckboxColumn("Show", default=True),
            "column": st.column_config.SelectboxColumn("Column", options=numeric_cols, required=True),
            "title": st.column_config.TextColumn("Title"),
            "unit": st.column_config.TextColumn("Unit"),
            "per": st.column_config.SelectboxColumn("Per", options=core.PER_OPTIONS, default="day"),
            "goal": st.column_config.NumberColumn("Goal"),
            "goal_is": st.column_config.SelectboxColumn("Goal is", options=core.GOAL_IS_OPTIONS,
                                                        default="at least"),
            "decimals": st.column_config.NumberColumn("Decimals", min_value=0, max_value=4, step=1, default=1),
            "daily_as": st.column_config.SelectboxColumn("Daily as", options=core.DAILY_AS_OPTIONS,
                                                         default="points"),
        },
    )
    setup_json = core.cards_to_json(edited)
    st.download_button("Download this setup (JSON)", setup_json, file_name="life-tracker-setup.json",
                       mime="application/json")
    if LOCAL:
        try:
            if not CONFIG_PATH.exists() or CONFIG_PATH.read_text() != setup_json:
                CONFIG_PATH.write_text(setup_json)
            st.caption("Saved automatically to config.json on this computer.")
        except OSError:
            st.caption("Could not write config.json here. Use the download button to keep your setup.")
    else:
        st.caption("Download the setup to keep it, then load it from the sidebar next time.")

cards = core.clean_cards(edited, numeric_cols)
shown = [c for c in cards if c["show"]]

df = df.copy()
for message in core.mask_impossible_hours(df, shown):
    st.warning(message)


def fmt(value, card, rate=True):
    if value is None or pd.isna(value):
        return "n/a"
    unit = plots.rate_unit(card) if rate else card["unit"]
    return f"{value:,.{card['decimals']}f}" + (f" {unit}" if unit else "")


# ------------------------------------------------------------ at a glance
if shown:
    st.header("This month at a glance")
    st.caption("Average of the last 30 days. Unrecorded days are left out.")
    per_row = 4
    for start in range(0, len(shown), per_row):
        row = shown[start:start + per_row]
        for col_box, card in zip(st.columns(per_row), row):
            mult = 7 if card["per"] == "week" else 1
            value = core.trailing_30d_mean(core.daily_series(df, card["column"]), mult)
            delta, delta_color = None, "normal"
            if value is not None and card["goal"] is not None:
                diff = value - card["goal"]
                delta = f"{diff:+,.{card['decimals']}f} vs goal"
                delta_color = "normal" if card["goal_is"] == "at least" else "inverse"
            col_box.metric(card["title"], fmt(value, card), delta, delta_color=delta_color)
else:
    st.info("No plots are shown yet. Open Set up your plots and tick Show on a column.")

# ------------------------------------------------------------ one section per plot
for i, card in enumerate(shown):
    st.header(card["title"])
    daily = core.daily_series(df, card["column"])
    if daily.dropna().empty:
        st.info(f"No values recorded in {card['column']}.")
        continue
    mult = 7 if card["per"] == "week" else 1
    windows = core.trailing_windows((daily.index[-1] - daily.index[0]).days)
    pace, recorded = core.trailing(daily, windows, mult)
    monthly = core.monthly_calendar_avg(daily, mult)

    if windows:
        for box, (label, _, days) in zip(st.columns(len(windows)), windows):
            box.metric(label, fmt(pace[label].iloc[-1], card))
            box.caption(f"{int(recorded[label].iloc[-1])} of {days} days recorded")

    if card["goal"] is not None:
        st.caption(f"Goal: {card['goal_is']} {fmt(card['goal'], card)}")
    st.plotly_chart(plots.metric_figure(card, daily, pace, windows, monthly),
                    use_container_width=True, key=f"chart_{i}")

# ------------------------------------------------------------ relationships
st.header("Explore relationships")
st.caption("Each point is one non-overlapping period, so points do not share days. "
           "Week is Monday to Sunday and Month is a calendar month. "
           "A point is the average of its recorded days. Per-week plots use the weekly rate.")

if len(numeric_cols) < 2:
    st.info("Relationships need at least two numeric columns.")
else:
    card_by_col = {c["column"]: c for c in cards}

    def label_for(col):
        return card_by_col[col]["title"] if col in card_by_col else col

    shown_cols = [c["column"] for c in shown]
    defaults = shown_cols + [c for c in numeric_cols if c not in shown_cols]
    c1, c2, c3 = st.columns(3)
    x_col = c1.selectbox("X axis", numeric_cols, index=numeric_cols.index(defaults[0]), format_func=label_for)
    y_default = defaults[1] if len(defaults) > 1 else defaults[0]
    y_col = c2.selectbox("Y axis", numeric_cols, index=numeric_cols.index(y_default), format_func=label_for)
    period = c3.radio("Each point is a", list(core.PERIODS), index=1, horizontal=True)

    min_days = 1
    if period != "Day":
        default_min = {"Week": 4, "Month": 15}[period]
        max_min = {"Week": 7, "Month": 31}[period]
        min_days = st.number_input(f"Minimum recorded days per {period.lower()}", min_value=1, max_value=max_min,
                                   value=default_min, step=1, key=f"min_days_{period}")

    if x_col == y_col:
        st.warning("Pick two different columns.")
    else:
        def axis_data(col):
            card = card_by_col.get(col)
            weekly = card is not None and card["per"] == "week" and period != "Day"
            series = core.period_aggregate(df, col, period, mult=7 if weekly else 1, min_days=int(min_days))
            unit = ""
            if card is not None:
                unit = f"{card['unit']}/wk" if weekly and card["unit"] else card["unit"]
            return series, unit

        xs, x_unit = axis_data(x_col)
        ys, y_unit = axis_data(y_col)
        joined = pd.concat([xs, ys], axis=1, keys=["x", "y"]).dropna()
        n = len(joined)
        if n < 3:
            st.info(f"Only {n} {period.lower()}s have both values. Try a shorter period or a smaller minimum.")
        else:
            when = {"Day": "%b %d, %Y", "Week": "Week of %b %d, %Y", "Month": "%B %Y"}[period]
            labels = joined.index.strftime(when)
            fig = go.Figure()
            fig.add_scatter(x=joined["x"], y=joined["y"], mode="markers", name=period,
                            marker=dict(color=plots.WINDOW_COLORS["Week average"], size=9),
                            customdata=labels,
                            hovertemplate="%{customdata}<br>x: %{x:.2f}<br>y: %{y:.2f}<extra></extra>")
            r = joined["x"].corr(joined["y"])
            if n >= 4 and joined["x"].std() > 0 and joined["y"].std() > 0:
                slope, intercept = np.polyfit(joined["x"], joined["y"], 1)
                xr = np.array([joined["x"].min(), joined["x"].max()])
                fig.add_scatter(x=xr, y=slope * xr + intercept, mode="lines", name="Trend",
                                line=dict(color="#888", dash="dash"), hoverinfo="skip")
            fig.update_layout(height=420, margin=dict(l=10, r=20, t=30, b=10),
                              xaxis_title=plots.with_unit(label_for(x_col), f"({x_unit})" if x_unit else ""),
                              yaxis_title=plots.with_unit(label_for(y_col), f"({y_unit})" if y_unit else ""),
                              legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig, use_container_width=True, key="scatter")
            caption = f"{n} {period.lower()}s"
            if pd.notna(r):
                caption += f" · correlation r = {r:.2f}"
            st.caption(caption + ". Correlation is not causation, and a few points can mislead.")
