from datetime import date
from pathlib import Path
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Life tracker", page_icon="🌱", layout="wide")
st.title("Life tracker")
st.caption("A simple view of your weight, work, sleep, and drinks. Keep logging in your spreadsheet and bring your CSV here.")

with st.sidebar:
    st.header("Your data")
    upload = st.file_uploader("Upload your full-history CSV", type="csv")
    year = st.number_input("Year for dates without a year", 2000, 2100, date.today().year)
    sleep_goal = st.number_input("Sleep goal (hours per night)", 0.5, 24.0, 7.5, 0.25)
    calorie_goal = st.number_input("Calorie goal (kcal per day)", 500, 6000, 2800, 50)
    protein_goal = st.number_input("Protein goal (g per day)", 10, 400, 150, 5)
    fiber_goal = st.number_input("Fiber goal (g per day)", 5, 100, 40, 5)
    height_in = st.number_input("Height (inches)", 48, 96, 75, 1)
    bmi_goal = st.number_input("BMI goal", 15.0, 40.0, 25.0, 0.5)
    weight_goal = bmi_goal * height_in ** 2 / 703
    st.caption(f"Weight goal: {weight_goal:.1f} lbs (BMI {bmi_goal:g} at {height_in} in).")
    st.caption("Weeks run Monday–Sunday. Blank values stay missing; enter 0 for a recorded day with no work or no drinks.")

files = sorted((Path(__file__).parent / "data").glob("*.csv"))
source = upload if upload is not None else (files[-1] if files else None)
if source is None:
    st.info("Upload a CSV to see your charts.")
    st.stop()

try:
    raw = pd.read_csv(source)
except Exception as exc:
    st.error(f"Could not read this CSV: {exc}")
    st.stop()
raw.columns = raw.columns.str.strip()
# Older CSVs used "next day" column names; accept them so history keeps working.
raw = raw.rename(columns={"Next morning weight (lbs)": "Weight (lbs)", "Next day feeling (1-10)": "How do I feel (1-10)"})
fields = ["Weight (lbs)", "Work (hrs)", "Sleep time (hours)"]
missing = [c for c in ["Date"] + fields if c not in raw.columns]
if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.stop()

def parse_date(value):
    if pd.isna(value):
        return pd.NaT
    value = str(value).strip()
    if re.fullmatch(r"\d{1,2}/\d{1,2}", value):
        value += f"/{year}"
    return pd.to_datetime(value, errors="coerce")

raw = raw.dropna(how="all")
raw["Date"] = raw["Date"].map(parse_date)
if raw["Date"].isna().any():
    st.warning("Rows with missing or unreadable dates were excluded.")
raw = raw.dropna(subset=["Date"])
optional_cols = ["Drinks", "Calories", "Protein (g)", "Fiber (g)"]
for col in optional_cols:
    if col not in raw.columns:
        raw[col] = float("nan")
for col in fields + optional_cols:
    parsed = pd.to_numeric(raw[col], errors="coerce")
    invalid = (raw[col].notna() & parsed.isna()) | (parsed < 0)
    if col in ["Work (hrs)", "Sleep time (hours)"]:
        invalid |= parsed > 24
    if invalid.any():
        st.warning(f"{col}: {int(invalid.sum())} invalid values were left out.")
    raw[col] = parsed.mask(invalid)
if raw["Date"].duplicated().any():
    st.error("The CSV has duplicate dates. Keep one row per date to avoid double-counting work.")
    st.stop()
df = raw.dropna(subset=fields + optional_cols, how="all").sort_values("Date")
if df.empty:
    st.info("No weight, work, sleep, drink, or nutrition measurements are available yet.")
    st.stop()
st.caption(f"Source: {upload.name if upload is not None else source.name} · {len(df)} dates with measurements. Each row is one day; charts use the row date.")

weight, work, sleep = fields

DAY_COLOR = "#000000"
WINDOW_COLORS = {"Week average": "#2a78d6", "Month average": "#eb6834", "Quarter average": "#1baf7a", "Year average": "#eda100"}
MONTHLY_COLOR = "#e87ba4"
total_days_span = (df.Date.max() - df.Date.min()).days + 1

def hover_fmt(unit, decimals=1):
    return f"%{{x|%b %d, %Y}}<br>%{{y:.{decimals}f}} {unit}<extra></extra>"

def monthly_calendar_avg(daily, mult=1):
    """Calendar-month average (distinct from the trailing windows above), plotted at the 15th of each month."""
    valid = daily.dropna()
    if valid.empty:
        return pd.Series(dtype=float)
    grouped = valid.groupby(valid.index.to_period("M")).mean() * mult
    idx = grouped.index.to_timestamp() + pd.Timedelta(days=14)
    return pd.Series(grouped.values, index=idx)

def add_goal_line(fig, x_values, y, label, unit="", decimals=1):
    if len(x_values) == 0:
        return
    fig.add_scatter(x=[x_values[0], x_values[-1]], y=[y, y], mode="lines", line=dict(color="#888", dash="dash"), name=label, hovertemplate=hover_fmt(unit, decimals))

def trailing_windows():
    windows = [("Week average", "7D", 7), ("Month average", "30D", 30)]
    if total_days_span > 30:
        windows.append(("Quarter average", "90D", 90))
    if total_days_span > 90:
        windows.append(("Year average", "365D", 365))
    return windows

def trailing_30d_mean(col, mult=1):
    sub = df.dropna(subset=[col])
    if sub.empty:
        return None
    daily = df.set_index("Date")[col].reindex(pd.date_range(df.Date.min(), df.Date.max(), freq="D"))
    return daily.rolling("30D", min_periods=1).mean().iloc[-1] * mult

st.subheader("This month at a glance")
st.caption("Trailing 30-day average for each metric, as of your latest entry.")
overview = [
    ("Weight", trailing_30d_mean(weight), "lbs", weight_goal, 1, "inverse"),
    ("Work", trailing_30d_mean(work, mult=7), "hrs/wk", 40, 1, "normal"),
    ("Sleep", trailing_30d_mean(sleep), "hrs", sleep_goal, 2, "normal"),
    ("Calories", trailing_30d_mean("Calories"), "kcal", calorie_goal, 0, "normal"),
    ("Protein", trailing_30d_mean("Protein (g)"), "g", protein_goal, 0, "normal"),
    ("Fiber", trailing_30d_mean("Fiber (g)"), "g", fiber_goal, 0, "normal"),
    ("Drinks", trailing_30d_mean("Drinks", mult=7), "drinks/wk", 7, 1, "inverse"),
]
overview_boxes = st.columns(4) + st.columns(4)
for box, (label, value, unit, goal, decimals, delta_color) in zip(overview_boxes, overview):
    if value is None:
        box.metric(label, "—")
    elif goal is None:
        box.metric(label, f"{value:.{decimals}f} {unit}")
    else:
        box.metric(label, f"{value:.{decimals}f} {unit}", f"{value - goal:+.{decimals}f} vs {goal:g} goal", delta_color=delta_color)

st.subheader("Weight")
st.caption(f"Day is that day's weigh-in; the other lines are trailing averages over that many days, compared to your {weight_goal:.1f}-lb goal (BMI {bmi_goal:g}). Unrecorded days are left out rather than treated as zero. Quarter and year averages appear once you have enough history for them to mean something.")
w3 = df.dropna(subset=[weight]).copy()
if w3.empty:
    st.info("Add weight measurements to see this chart.")
else:
    weight_daily = df.set_index("Date")[weight].reindex(pd.date_range(df.Date.min(), df.Date.max(), freq="D"))
    weight_windows = trailing_windows()
    weight_pace = pd.DataFrame({label: weight_daily.rolling(offset, min_periods=1).mean() for label, offset, _ in weight_windows})
    weight_recorded = pd.DataFrame({label: weight_daily.rolling(offset, min_periods=1).count() for label, offset, _ in weight_windows})
    weight_elapsed = (weight_pace.index - df.Date.min()).days + 1

    cols = st.columns(len(weight_windows))
    for box, (label, offset, span) in zip(cols, weight_windows):
        avg = weight_pace[label].iloc[-1]
        days_recorded = int(weight_recorded[label].iloc[-1])
        days_in_window = int(min(span, weight_elapsed[-1]))
        box.metric(label, f"{avg:.1f} lbs", f"{avg - weight_goal:+.1f} vs {weight_goal:.1f}-lb goal", delta_color="inverse")
        box.caption(f"{days_recorded} of {days_in_window} days recorded")

    weight_monthly = monthly_calendar_avg(weight_daily)

    fig = go.Figure()
    fig.add_scatter(x=weight_daily.index, y=weight_daily, mode="markers", marker=dict(color=DAY_COLOR, size=6), name="Day", hovertemplate=hover_fmt("lbs", 1))
    for label, _, _ in weight_windows:
        fig.add_scatter(x=weight_pace.index, y=weight_pace[label], mode="lines", name=label, line_color=WINDOW_COLORS[label], connectgaps=True, hovertemplate=hover_fmt("lbs", 1))
    if not weight_monthly.empty:
        fig.add_scatter(x=weight_monthly.index, y=weight_monthly.values, mode="markers", marker=dict(color=MONTHLY_COLOR, size=11, symbol="diamond"), name="Monthly avg", hovertemplate=hover_fmt("lbs", 1))
    add_goal_line(fig, weight_daily.index, weight_goal, f"Goal: {weight_goal:.1f} lbs", unit="lbs", decimals=1)
    fig.update_layout(height=360, margin=dict(l=10, r=20, t=30, b=10), xaxis_title="Date", yaxis_title="lbs", legend=dict(orientation="h", y=-0.25))
    fig.update_xaxes(tickformat="%b %d", dtick=86400000 if len(weight_daily) <= 14 else None)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Nutrition")
st.caption("Day is that day's logged amount; the other lines are trailing averages over that many days, compared to your daily goal. Unrecorded days are left out rather than treated as zero. Quarter and year averages appear once you have enough history for them to mean something.")
nutrients = [("Calories", "Calories", "kcal", calorie_goal), ("Protein (g)", "Protein", "g", protein_goal), ("Fiber (g)", "Fiber", "g", fiber_goal)]
for ncol, nlabel, nunit, ngoal in nutrients:
    n2 = df.dropna(subset=[ncol]).copy()
    if n2.empty:
        st.info(f"Add {nlabel.lower()} data to see this chart.")
        continue
    st.markdown(f"**{nlabel}**")
    n_daily = df.set_index("Date")[ncol].reindex(pd.date_range(df.Date.min(), df.Date.max(), freq="D"))
    n_windows = trailing_windows()
    n_pace = pd.DataFrame({label: n_daily.rolling(offset, min_periods=1).mean() for label, offset, _ in n_windows})
    n_recorded = pd.DataFrame({label: n_daily.rolling(offset, min_periods=1).count() for label, offset, _ in n_windows})
    n_elapsed = (n_pace.index - df.Date.min()).days + 1

    cols = st.columns(len(n_windows))
    for box, (label, offset, span) in zip(cols, n_windows):
        rate = n_pace[label].iloc[-1]
        days_recorded = int(n_recorded[label].iloc[-1])
        days_in_window = int(min(span, n_elapsed[-1]))
        box.metric(label, f"{rate:.0f} {nunit}", f"{rate - ngoal:+.0f} vs {ngoal:g}-{nunit} goal", delta_color="normal")
        box.caption(f"{days_recorded} of {days_in_window} days recorded")

    n_monthly = monthly_calendar_avg(n_daily)

    fig = go.Figure()
    fig.add_scatter(x=n_daily.index, y=n_daily, mode="markers", marker=dict(color=DAY_COLOR, size=6), name="Day", hovertemplate=hover_fmt(nunit, 0))
    for label, _, _ in n_windows:
        fig.add_scatter(x=n_pace.index, y=n_pace[label], mode="lines", name=label, line_color=WINDOW_COLORS[label], connectgaps=True, hovertemplate=hover_fmt(nunit, 0))
    if not n_monthly.empty:
        fig.add_scatter(x=n_monthly.index, y=n_monthly.values, mode="markers", marker=dict(color=MONTHLY_COLOR, size=11, symbol="diamond"), name="Monthly avg", hovertemplate=hover_fmt(nunit, 0))
    add_goal_line(fig, n_daily.index, ngoal, f"Goal: {ngoal:g} {nunit}", unit=nunit, decimals=0)
    fig.update_layout(height=340, margin=dict(l=10, r=20, t=30, b=10), xaxis_title="Date", yaxis_title=nunit, legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Work")
st.caption("Day is that day's logged hours; the other lines are trailing rates — the mean hours per day over that window, expressed as hours/week, compared to your 40-hour goal. Unrecorded days are left out rather than treated as zero. Quarter and year averages appear once you have enough history for them to mean something.")
w2 = df.dropna(subset=[work]).copy()
if w2.empty:
    st.info("Add work hours to see this chart.")
else:
    work_daily = df.set_index("Date")[work].reindex(pd.date_range(df.Date.min(), df.Date.max(), freq="D"))
    windows = trailing_windows()
    pace = pd.DataFrame({label: work_daily.rolling(offset, min_periods=1).mean() * 7 for label, offset, _ in windows})
    recorded = pd.DataFrame({label: work_daily.rolling(offset, min_periods=1).count() for label, offset, _ in windows})
    elapsed = (pace.index - df.Date.min()).days + 1

    cols = st.columns(len(windows))
    for box, (label, offset, span) in zip(cols, windows):
        rate = pace[label].iloc[-1]
        days_recorded = int(recorded[label].iloc[-1])
        days_in_window = int(min(span, elapsed[-1]))
        box.metric(label, f"{rate:.1f} hrs/wk", f"{rate - 40:+.1f} vs 40-hr goal", delta_color="normal")
        box.caption(f"{days_recorded} of {days_in_window} days recorded")

    work_monthly = monthly_calendar_avg(work_daily, mult=7)

    fig = go.Figure()
    fig.add_bar(x=work_daily.index, y=work_daily, marker_color=DAY_COLOR, name="Day", hovertemplate=hover_fmt("hours", 1))
    for label, _, _ in windows:
        fig.add_scatter(x=pace.index, y=pace[label], mode="lines", name=label, line_color=WINDOW_COLORS[label], connectgaps=True, hovertemplate=hover_fmt("hrs/wk", 1))
    if not work_monthly.empty:
        fig.add_scatter(x=work_monthly.index, y=work_monthly.values, mode="markers", marker=dict(color=MONTHLY_COLOR, size=11, symbol="diamond"), name="Monthly avg", hovertemplate=hover_fmt("hrs/wk", 1))
    add_goal_line(fig, work_daily.index, 40, "Goal: 40 hrs/wk", unit="hrs/wk", decimals=1)
    fig.update_layout(height=360, margin=dict(l=10, r=20, t=30, b=10), xaxis_title="Date", yaxis_title="hours (Day) · hrs/week (trailing)", legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Sleep")
st.caption(f"Day is that night's logged sleep; the other lines are trailing averages over that many nights, compared to your {sleep_goal:g}-hour goal. Unrecorded nights are left out rather than treated as zero. Quarter and year averages appear once you have enough history for them to mean something.")
s2 = df.dropna(subset=[sleep]).copy()
if s2.empty:
    st.info("Add sleep hours to see this chart.")
else:
    sleep_daily = df.set_index("Date")[sleep].reindex(pd.date_range(df.Date.min(), df.Date.max(), freq="D"))
    sleep_windows = trailing_windows()
    sleep_pace = pd.DataFrame({label: sleep_daily.rolling(offset, min_periods=1).mean() for label, offset, _ in sleep_windows})
    sleep_recorded = pd.DataFrame({label: sleep_daily.rolling(offset, min_periods=1).count() for label, offset, _ in sleep_windows})
    sleep_elapsed = (sleep_pace.index - df.Date.min()).days + 1

    cols = st.columns(len(sleep_windows))
    for box, (label, offset, span) in zip(cols, sleep_windows):
        rate = sleep_pace[label].iloc[-1]
        nights_recorded = int(sleep_recorded[label].iloc[-1])
        nights_in_window = int(min(span, sleep_elapsed[-1]))
        box.metric(label, f"{rate:.2f} hrs", f"{rate - sleep_goal:+.2f} vs {sleep_goal:g}-hr goal", delta_color="normal")
        box.caption(f"{nights_recorded} of {nights_in_window} nights recorded")

    sleep_monthly = monthly_calendar_avg(sleep_daily)

    fig = go.Figure()
    fig.add_scatter(x=sleep_daily.index, y=sleep_daily, mode="markers", marker=dict(color=DAY_COLOR, size=6), name="Day", hovertemplate=hover_fmt("hrs", 2))
    for label, _, _ in sleep_windows:
        fig.add_scatter(x=sleep_pace.index, y=sleep_pace[label], mode="lines", name=label, line_color=WINDOW_COLORS[label], connectgaps=True, hovertemplate=hover_fmt("hrs", 2))
    if not sleep_monthly.empty:
        fig.add_scatter(x=sleep_monthly.index, y=sleep_monthly.values, mode="markers", marker=dict(color=MONTHLY_COLOR, size=11, symbol="diamond"), name="Monthly avg", hovertemplate=hover_fmt("hrs", 2))
    add_goal_line(fig, sleep_daily.index, sleep_goal, f"Goal: {sleep_goal:g} hrs", unit="hrs", decimals=2)
    fig.update_layout(height=360, margin=dict(l=10, r=20, t=30, b=10), xaxis_title="Date", yaxis_title="hours", legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, use_container_width=True)
st.caption("Sleep uses your CSV's Sleep time (hours) column; naps are not added. Correlations can wait until you have more data.")

st.subheader("Drinks")
st.caption("Day is that day's logged drinks; the other lines are trailing rates — the mean drinks per day over that window, expressed as drinks/week, compared to your 7-drink weekly limit. Unrecorded days are left out rather than treated as zero. Quarter and year averages appear once you have enough history for them to mean something. This is a ceiling, not a target — lower is better, and negative here means under the limit.")
d2 = df.dropna(subset=["Drinks"]).copy()
if d2.empty:
    st.info("Log your drink count in the Drinks column. Enter 0 for an alcohol-free day; leave unrecorded days blank.")
else:
    drinks_daily = df.set_index("Date")["Drinks"].reindex(pd.date_range(df.Date.min(), df.Date.max(), freq="D"))
    drinks_windows = trailing_windows()
    drinks_pace = pd.DataFrame({label: drinks_daily.rolling(offset, min_periods=1).mean() * 7 for label, offset, _ in drinks_windows})
    drinks_recorded = pd.DataFrame({label: drinks_daily.rolling(offset, min_periods=1).count() for label, offset, _ in drinks_windows})
    drinks_elapsed = (drinks_pace.index - df.Date.min()).days + 1

    cols = st.columns(len(drinks_windows))
    for box, (label, offset, span) in zip(cols, drinks_windows):
        rate = drinks_pace[label].iloc[-1]
        days_recorded = int(drinks_recorded[label].iloc[-1])
        days_in_window = int(min(span, drinks_elapsed[-1]))
        box.metric(label, f"{rate:.1f} drinks/wk", f"{rate - 7:+.1f} vs 7-drink limit", delta_color="inverse")
        box.caption(f"{days_recorded} of {days_in_window} days recorded")

    drinks_monthly = monthly_calendar_avg(drinks_daily, mult=7)

    fig = go.Figure()
    fig.add_scatter(x=drinks_daily.index, y=drinks_daily, mode="markers", marker=dict(color=DAY_COLOR, size=6), name="Day", hovertemplate=hover_fmt("drinks", 0))
    for label, _, _ in drinks_windows:
        fig.add_scatter(x=drinks_pace.index, y=drinks_pace[label], mode="lines", name=label, line_color=WINDOW_COLORS[label], connectgaps=True, hovertemplate=hover_fmt("drinks/wk", 1))
    if not drinks_monthly.empty:
        fig.add_scatter(x=drinks_monthly.index, y=drinks_monthly.values, mode="markers", marker=dict(color=MONTHLY_COLOR, size=11, symbol="diamond"), name="Monthly avg", hovertemplate=hover_fmt("drinks/wk", 1))
    add_goal_line(fig, drinks_daily.index, 7, "Weekly limit: 7", unit="drinks/wk", decimals=1)
    fig.update_layout(height=360, margin=dict(l=10, r=20, t=30, b=10), xaxis_title="Date", yaxis_title="drinks (Day) · drinks/week (trailing)", legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Explore relationships")
st.caption("Pick two measurements to compare. With only a handful of days logged, treat any pattern here as a hint worth watching, not a conclusion — a correlation from under two weeks of data can flip with the next few entries.")
candidate_cols = ["Weight (lbs)", "Work (hrs)", "Sleep time (hours)", "Travel day", "Sick", "Drinks", "Calories", "Protein (g)", "Fiber (g)",
                  "Sleep quality (1-10)", "How do I feel (1-10)", "Regular exercise (min)", "High-intensity exercise (min)",
                  "Reading (min)", "Awakenings", "Minutes awake overnight", "Nap (min)", "Midnight snack", "Bowel movements"]
numeric_cols = [c for c in candidate_cols if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
if len(numeric_cols) < 2:
    st.info("Log a few more measurements to explore relationships between them.")
else:
    default_x = "Drinks" if "Drinks" in numeric_cols else numeric_cols[0]
    default_y = "Sleep quality (1-10)" if "Sleep quality (1-10)" in numeric_cols else numeric_cols[min(1, len(numeric_cols) - 1)]
    c1, c2 = st.columns(2)
    x_col = c1.selectbox("X axis", numeric_cols, index=numeric_cols.index(default_x))
    y_col = c2.selectbox("Y axis", numeric_cols, index=numeric_cols.index(default_y))
    smooth = st.checkbox("Smooth each point to its trailing 7-day average", value=False)
    if smooth:
        daily_range = pd.date_range(df.Date.min(), df.Date.max(), freq="D")
        smoothed_x = df.set_index("Date")[x_col].reindex(daily_range).rolling("7D", min_periods=1).mean()
        smoothed_y = df.set_index("Date")[y_col].reindex(daily_range).rolling("7D", min_periods=1).mean()
        pair = pd.DataFrame({x_col: smoothed_x, y_col: smoothed_y}).dropna()
    else:
        pair = df[[x_col, y_col]].dropna()
    if len(pair) < 2:
        st.info("Not enough overlapping data for these two measurements yet.")
    else:
        point_label = "7-day avg" if smooth else "Days"
        fig = go.Figure(go.Scatter(x=pair[x_col], y=pair[y_col], mode="markers", marker=dict(color="#527bba", size=11, opacity=0.85), name=point_label))
        has_trend = len(pair) >= 4 and pair[x_col].nunique() > 1 and pair[y_col].nunique() > 1
        if has_trend:
            slope, intercept = np.polyfit(pair[x_col], pair[y_col], 1)
            x_line = np.array([pair[x_col].min(), pair[x_col].max()])
            fig.add_scatter(x=x_line, y=slope * x_line + intercept, mode="lines", line=dict(color="#d48637", dash="dash"), name="Trend")
        fig.update_layout(height=380, margin=dict(l=10, r=20, t=30, b=10), xaxis_title=x_col, yaxis_title=y_col, showlegend=has_trend, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)
        if has_trend:
            r = pair[x_col].corr(pair[y_col])
            if smooth:
                st.caption(f"Correlation across {len(pair)} trailing 7-day-average points: r = {r:.2f} (−1 to 1; 0 means no linear relationship). Smoothing trades daily noise for overlap — each point shares up to 6 days with its neighbors, so these points aren't independent and this correlation is an even rougher hint than the daily version, not evidence. It's meant to make a slower-moving trend easier to see by eye, not to imply causation.")
            else:
                st.caption(f"Correlation across {len(pair)} overlapping days: r = {r:.2f} (−1 to 1; 0 means no linear relationship). The dashed line is a least-squares fit to make the direction easier to see — with this few points it's a rough hint, not evidence, and doesn't imply causation. It will move around a lot as you add more days.")
        else:
            st.caption(f"Only {len(pair)} overlapping {'smoothed points' if smooth else 'days'} so far — too few to compute a meaningful correlation or trend line.")
