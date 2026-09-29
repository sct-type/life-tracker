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
fields = ["Next morning weight (lbs)", "Work (hrs)", "Sleep time (hours)"]
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
st.caption(f"Source: {upload.name if upload is not None else source.name} · {len(df)} dates with measurements. Charts use the spreadsheet row date, including next-morning weight and that night's sleep.")

weight, work, sleep = fields
cols = st.columns(3)
for box, col, label, unit in zip(cols, fields, ["Latest weight", "Work logged", "Average sleep"], ["lbs", "hrs", "hrs"]):
    vals = df[col].dropna()
    value = None if vals.empty else (vals.iloc[-1] if col == weight else vals.sum() if col == work else vals.mean())
    box.metric(label, "—" if value is None else f"{value:.1f} {unit}")

def chart(col, title, unit, goal=None, bars=False):
    st.subheader(title)
    values = df.set_index("Date")[col].reindex(pd.date_range(df.Date.min(), df.Date.max(), freq="D"))
    fig = go.Figure()
    if bars:
        fig.add_bar(x=values.index, y=values, marker_color="#527bba", name=title)
    else:
        fig.add_scatter(x=values.index, y=values, mode="lines+markers", connectgaps=False, line_color="#348979", name=title)
    if goal is not None:
        fig.add_hline(y=goal, line_dash="dash", line_color="#d48637", annotation_text=f"Goal: {goal:g} {unit}")
    fig.update_layout(height=310, margin=dict(l=10,r=20,t=30,b=10), xaxis_title="Date", yaxis_title=unit, showlegend=False)
    fig.update_xaxes(tickformat="%b %d", dtick=86400000 if len(values) <= 14 else None)
    st.plotly_chart(fig, use_container_width=True)

chart(weight, "Weight over time", "lbs")

st.subheader("Weight moving average")
st.caption("Each window is a trailing average: mean weight over that many days. Unrecorded days are left out rather than treated as zero. With limited history the windows track together; they separate as you build up more days.")
w3 = df.dropna(subset=[weight]).copy()
if w3.empty:
    st.info("Add weight measurements to see your moving average.")
else:
    weight_daily = df.set_index("Date")[weight].reindex(pd.date_range(df.Date.min(), df.Date.max(), freq="D"))
    weight_windows = [("Last 7 days", "7D", 7), ("Last 30 days", "30D", 30), ("Last 90 days", "90D", 90), ("Trailing year", "365D", 365)]
    weight_pace = pd.DataFrame({label: weight_daily.rolling(offset, min_periods=1).mean() for label, offset, _ in weight_windows})
    weight_recorded = pd.DataFrame({label: weight_daily.rolling(offset, min_periods=1).count() for label, offset, _ in weight_windows})
    weight_elapsed = (weight_pace.index - df.Date.min()).days + 1

    cols = st.columns(len(weight_windows))
    for box, (label, offset, span) in zip(cols, weight_windows):
        avg = weight_pace[label].iloc[-1]
        days_recorded = int(weight_recorded[label].iloc[-1])
        days_in_window = int(min(span, weight_elapsed[-1]))
        box.metric(label, f"{avg:.1f} lbs")
        box.caption(f"{days_recorded} of {days_in_window} days recorded")

    fig = go.Figure()
    weight_colors = {"Last 7 days": "#2a78d6", "Last 30 days": "#eb6834", "Last 90 days": "#1baf7a", "Trailing year": "#eda100"}
    for label, _, _ in weight_windows:
        fig.add_scatter(x=weight_pace.index, y=weight_pace[label], mode="lines", name=label, line_color=weight_colors[label], connectgaps=True)
    fig.update_layout(height=340, margin=dict(l=10, r=20, t=30, b=10), xaxis_title="Date", yaxis_title="lbs", legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Nutrition")
nutrients = [("Calories", "Calories", "kcal", calorie_goal), ("Protein (g)", "Protein", "g", protein_goal), ("Fiber (g)", "Fiber", "g", fiber_goal)]
for ncol, nlabel, nunit, ngoal in nutrients:
    chart(ncol, f"{nlabel} over time", nunit, goal=ngoal)

st.subheader("Nutrition pace toward daily goals")
st.caption("Each window is a trailing average: mean daily intake over that many days. Unrecorded days are left out rather than treated as zero. With limited history the windows track together; they separate as you build up more days.")
for ncol, nlabel, nunit, ngoal in nutrients:
    n2 = df.dropna(subset=[ncol]).copy()
    if n2.empty:
        st.info(f"Add {nlabel.lower()} data to see your pace toward the {nlabel.lower()} goal.")
        continue
    st.markdown(f"**{nlabel}**")
    n_daily = df.set_index("Date")[ncol].reindex(pd.date_range(df.Date.min(), df.Date.max(), freq="D"))
    n_windows = [("Last 7 days", "7D", 7), ("Last 30 days", "30D", 30), ("Last 90 days", "90D", 90), ("Trailing year", "365D", 365)]
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

    fig = go.Figure()
    n_colors = {"Last 7 days": "#2a78d6", "Last 30 days": "#eb6834", "Last 90 days": "#1baf7a", "Trailing year": "#eda100"}
    for label, _, _ in n_windows:
        fig.add_scatter(x=n_pace.index, y=n_pace[label], mode="lines", name=label, line_color=n_colors[label], connectgaps=True)
    fig.add_hline(y=ngoal, line_dash="dash", line_color="#888", annotation_text=f"Goal: {ngoal:g} {nunit}")
    fig.update_layout(height=300, margin=dict(l=10, r=20, t=30, b=10), xaxis_title="Date", yaxis_title=nunit, legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(fig, use_container_width=True)

chart(work, "Daily work hours", "hours", bars=True)
st.subheader("Weekly work · 40-hour goal")
w = df.dropna(subset=[work]).copy()
if w.empty:
    st.info("Add work hours to see weekly totals.")
else:
    w["Week starting"] = w.Date - pd.to_timedelta(w.Date.dt.weekday, unit="D")
    weekly = w.groupby("Week starting")[work].agg(["sum", "count"]).rename(columns={"sum":"Hours logged", "count":"Days recorded"})
    weekly["Status"] = weekly["Days recorded"].map(lambda n: "Complete" if n == 7 else "Partial")
    weekly["Goal (hrs)"] = 40
    weekly["Hours to goal"] = (40 - weekly["Hours logged"]).clip(lower=0)
    st.metric("Average hours per recorded week", f"{weekly['Hours logged'].mean():.1f} hrs", f"{weekly['Hours logged'].mean() - 40:+.1f} hrs vs 40-hour goal", delta_color="normal")
    st.caption("Average = total logged work ÷ number of weeks with work entries. Partial weeks are included, so this may understate a full week's work. Missing days and entirely unrecorded weeks are not assumed to be zero.")
    fig = go.Figure(go.Bar(x=weekly.index.strftime("%b %d, %Y"), y=weekly["Hours logged"], marker_color="#527bba", customdata=weekly["Days recorded"], hovertemplate="Week of %{x}: %{y} hours<br>%{customdata} days recorded<extra></extra>"))
    fig.update_xaxes(type="category")
    fig.add_hline(y=40, line_dash="dash", line_color="#d48637", annotation_text="40-hour goal")
    fig.update_layout(height=280, xaxis_title="Week starting Monday", yaxis_title="Hours logged", margin=dict(t=30,b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(weekly, use_container_width=True)

st.subheader("Work pace toward 40 hrs/week, year-round")
st.caption("Each window is a trailing rate: total hours logged in that many days, expressed as hours/week. Unrecorded days are left out rather than treated as zero, so the rate reflects the days you actually logged. With limited history the windows track together; they separate as you build up more days.")
w2 = df.dropna(subset=[work]).copy()
if w2.empty:
    st.info("Add work hours to see your pace toward the goal.")
else:
    work_daily = df.set_index("Date")[work].reindex(pd.date_range(df.Date.min(), df.Date.max(), freq="D"))
    windows = [("Last 7 days", "7D", 7), ("Last 30 days", "30D", 30), ("Last 90 days", "90D", 90), ("Trailing year", "365D", 365)]
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

    fig = go.Figure()
    colors = {"Last 7 days": "#2a78d6", "Last 30 days": "#eb6834", "Last 90 days": "#1baf7a", "Trailing year": "#eda100"}
    for label, _, _ in windows:
        fig.add_scatter(x=pace.index, y=pace[label], mode="lines", name=label, line_color=colors[label], connectgaps=True)
    fig.add_hline(y=40, line_dash="dash", line_color="#888", annotation_text="Goal: 40 hrs/wk")
    fig.update_layout(height=340, margin=dict(l=10, r=20, t=30, b=10), xaxis_title="Date", yaxis_title="hrs/week", legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, use_container_width=True)

chart(sleep, "Sleep over time", "hours", goal=sleep_goal)
st.caption("Sleep uses your CSV's Sleep time (hours) column; naps are not added. Correlations can wait until you have more data.")

st.subheader(f"Sleep pace toward {sleep_goal:g} hrs/night")
st.caption("Each window is a trailing average: mean nightly sleep over that many days. Unrecorded nights are left out rather than treated as zero. With limited history the windows track together; they separate as you build up more nights.")
s2 = df.dropna(subset=[sleep]).copy()
if s2.empty:
    st.info("Add sleep hours to see your pace toward the goal.")
else:
    sleep_daily = df.set_index("Date")[sleep].reindex(pd.date_range(df.Date.min(), df.Date.max(), freq="D"))
    sleep_windows = [("Last 7 nights", "7D", 7), ("Last 30 nights", "30D", 30), ("Last 90 nights", "90D", 90), ("Trailing year", "365D", 365)]
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

    fig = go.Figure()
    sleep_colors = {"Last 7 nights": "#2a78d6", "Last 30 nights": "#eb6834", "Last 90 nights": "#1baf7a", "Trailing year": "#eda100"}
    for label, _, _ in sleep_windows:
        fig.add_scatter(x=sleep_pace.index, y=sleep_pace[label], mode="lines", name=label, line_color=sleep_colors[label], connectgaps=True)
    fig.add_hline(y=sleep_goal, line_dash="dash", line_color="#888", annotation_text=f"Goal: {sleep_goal:g} hrs")
    fig.update_layout(height=340, margin=dict(l=10, r=20, t=30, b=10), xaxis_title="Date", yaxis_title="hrs/night", legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Weekly drinks · limit of 7")
d = df.dropna(subset=["Drinks"]).copy()
if d.empty:
    st.info("Log your drink count in the Drinks column. Enter 0 for an alcohol-free day; leave unrecorded days blank.")
else:
    d["Week starting"] = d.Date - pd.to_timedelta(d.Date.dt.weekday, unit="D")
    drinks_weekly = d.groupby("Week starting")["Drinks"].agg(["sum", "count"]).rename(columns={"sum": "Drinks logged", "count": "Days recorded"})
    drinks_weekly["Status"] = drinks_weekly.apply(
        lambda row: "Over limit" if row["Drinks logged"] > 7 else ("Within limit" if row["Days recorded"] == 7 else "Partial · total so far"), axis=1
    )
    drinks_weekly["Weekly limit"] = 7
    latest = drinks_weekly.iloc[-1]
    st.metric("Latest recorded week · " + drinks_weekly.index[-1].strftime("%b %d, %Y"), f"{latest['Drinks logged']:g} / 7 drinks")
    st.caption(f"{int(latest['Days recorded'])} of 7 days recorded. Seven is your upper limit, not a target to reach. Partial totals do not confirm a whole week stayed within the limit.")
    fig = go.Figure(go.Bar(
        x=drinks_weekly.index.strftime("%b %d, %Y"), y=drinks_weekly["Drinks logged"],
        marker_color=["#b96048" if n > 7 else "#527bba" for n in drinks_weekly["Drinks logged"]],
        customdata=drinks_weekly["Days recorded"],
        hovertemplate="Week of %{x}: %{y} drinks<br>%{customdata} days recorded<extra></extra>"
    ))
    fig.update_xaxes(type="category")
    fig.add_hline(y=7, line_dash="dash", line_color="#d48637", annotation_text="Weekly limit: 7")
    fig.update_layout(height=280, xaxis_title="Week starting Monday", yaxis_title="Drinks logged", margin=dict(t=30,b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(drinks_weekly, use_container_width=True)
    st.caption("Totals use your existing Drinks entries. Keep the meaning of one drink consistent when logging. Weeks with no recorded drink counts are omitted.")

st.subheader("Drinks pace vs 7/week limit")
st.caption("Each window is a trailing rate: total drinks in that many days, expressed as drinks/week. Unrecorded days are left out rather than treated as zero. This is a ceiling, not a target — lower is better, and negative here means under the limit.")
d2 = df.dropna(subset=["Drinks"]).copy()
if d2.empty:
    st.info("Log your drink count to see your pace against the limit.")
else:
    drinks_daily = df.set_index("Date")["Drinks"].reindex(pd.date_range(df.Date.min(), df.Date.max(), freq="D"))
    drinks_windows = [("Last 7 days", "7D", 7), ("Last 30 days", "30D", 30), ("Last 90 days", "90D", 90), ("Trailing year", "365D", 365)]
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

    fig = go.Figure()
    drinks_colors = {"Last 7 days": "#2a78d6", "Last 30 days": "#eb6834", "Last 90 days": "#1baf7a", "Trailing year": "#eda100"}
    for label, _, _ in drinks_windows:
        fig.add_scatter(x=drinks_pace.index, y=drinks_pace[label], mode="lines", name=label, line_color=drinks_colors[label], connectgaps=True)
    fig.add_hline(y=7, line_dash="dash", line_color="#d48637", annotation_text="Weekly limit: 7")
    fig.update_layout(height=340, margin=dict(l=10, r=20, t=30, b=10), xaxis_title="Date", yaxis_title="drinks/week", legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Explore relationships")
st.caption("Pick two measurements to compare. With only a handful of days logged, treat any pattern here as a hint worth watching, not a conclusion — a correlation from under two weeks of data can flip with the next few entries.")
candidate_cols = ["Next morning weight (lbs)", "Work (hrs)", "Sleep time (hours)", "Travel day", "Sick", "Drinks", "Calories", "Protein (g)", "Fiber (g)",
                  "Sleep quality (1-10)", "Next day feeling (1-10)", "Regular exercise (min)", "High-intensity exercise (min)",
                  "Reading (min)", "Awakenings", "Minutes awake overnight", "Nap (min)", "Bowel movements"]
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

with st.expander("View imported records"):
    st.dataframe(raw.sort_values("Date"), use_container_width=True, hide_index=True)
