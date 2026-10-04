"""Loading, cleaning, plot-setup and rolling-window math for Life Tracker.

Nothing in here calls Streamlit, so it is easy to test on its own.
"""
import json
import re

import numpy as np
import pandas as pd

CONFIG_VERSION = 1

# Column names used by older CSVs, mapped to the current ones.
LEGACY_COLUMNS = {
    "Next morning weight (lbs)": "Weight (lbs)",
    "Next day feeling (1-10)": "How do I feel (1-10)",
}

ALL_WINDOWS = [
    ("Week average", "7D", 7),
    ("Month average", "30D", 30),
    ("Quarter average", "90D", 90),
    ("Year average", "365D", 365),
]

# One row per plot the user has set up. Keys are the stored (JSON) names.
CARD_DEFAULTS = {
    "show": True,
    "column": "",
    "title": "",
    "unit": "",
    "per": "day",            # "day": averages are per day. "week": averages are weekly rates.
    "goal": None,            # optional number
    "goal_is": "at least",   # "at least" (higher is better) or "at most" (lower is better)
    "decimals": 1,
    "daily_as": "points",    # how the daily values are drawn: "points" or "bars"
}
PER_OPTIONS = ["day", "week"]
GOAL_IS_OPTIONS = ["at least", "at most"]
DAILY_AS_OPTIONS = ["points", "bars"]
HOURS_UNITS = {"hr", "hrs", "hour", "hours"}


# ---------------------------------------------------------------- loading

def parse_date(value, year):
    if pd.isna(value):
        return pd.NaT
    value = str(value).strip()
    if re.fullmatch(r"\d{1,2}/\d{1,2}", value):
        value += f"/{year}"
    return pd.to_datetime(value, errors="coerce")


def load_csv(source, year):
    """Read a tracker CSV.

    Returns (df, numeric_cols, warnings). Raises ValueError with a friendly
    message when the file cannot be used. Only a Date column is required.
    Any column that is mostly numbers is treated as a metric.
    """
    warnings = []
    try:
        raw = pd.read_csv(source)
    except Exception as exc:
        raise ValueError(f"Could not read this CSV: {exc}")
    raw.columns = raw.columns.astype(str).str.strip()
    raw = raw.rename(columns=LEGACY_COLUMNS)
    if "Date" not in raw.columns:
        raise ValueError("The CSV needs a column named Date.")

    raw = raw.dropna(how="all")
    raw["Date"] = raw["Date"].map(lambda v: parse_date(v, year))
    if raw["Date"].isna().any():
        warnings.append("Rows with missing or unreadable dates were excluded.")
    raw = raw.dropna(subset=["Date"])
    if raw.empty:
        raise ValueError("No rows with readable dates were found.")
    if raw["Date"].duplicated().any():
        raise ValueError("The CSV has duplicate dates. Keep one row per date.")

    numeric_cols = []
    for col in raw.columns:
        if col == "Date":
            continue
        nonblank = raw[col].notna() & (raw[col].astype(str).str.strip() != "")
        if nonblank.sum() == 0:
            continue
        parsed = pd.to_numeric(raw[col], errors="coerce")
        if parsed.notna().sum() >= 0.8 * nonblank.sum():
            bad = nonblank & parsed.isna()
            if bad.any():
                warnings.append(f"{col}: {int(bad.sum())} non-numeric values were left out.")
            raw[col] = parsed
            numeric_cols.append(col)
    if not numeric_cols:
        raise ValueError("No numeric columns were found in this CSV.")
    return raw.sort_values("Date").reset_index(drop=True), numeric_cols, warnings


def mask_impossible_hours(df, cards):
    """Hours-per-day metrics cannot exceed 24. Blank out anything that does."""
    warnings = []
    for card in cards:
        if card["unit"].strip().lower() in HOURS_UNITS:
            col = card["column"]
            bad = df[col] > 24
            if bad.any():
                warnings.append(f"{col}: {int(bad.sum())} values over 24 hours were left out.")
                df[col] = df[col].mask(bad)
    return warnings


# ----------------------------------------------------------- plot setup

def split_title_unit(column):
    """'Weight (lbs)' -> ('Weight', 'lbs'). Scales like '(1-10)' give no unit."""
    match = re.fullmatch(r"(.*?)\s*\((.*?)\)\s*", column)
    if not match:
        return column, ""
    title, unit = match.group(1).strip(), match.group(2).strip()
    if re.fullmatch(r"\d+\s*-\s*\d+", unit):
        return title or column, ""
    return title or column, unit


def is_flag(series):
    values = set(series.dropna().unique())
    return bool(values) and values <= {0, 1, 0.0, 1.0}


def default_cards(df, numeric_cols, max_shown=6):
    """One card per numeric column. The first few non-flag columns start shown."""
    rows, shown = [], 0
    for col in numeric_cols:
        title, unit = split_title_unit(col)
        show = (not is_flag(df[col])) and shown < max_shown
        shown += int(show)
        rows.append({**CARD_DEFAULTS, "show": show, "column": col, "title": title, "unit": unit})
    return cards_frame(rows)


def cards_frame(rows):
    """Cards as the DataFrame shown in the setup editor."""
    frame = pd.DataFrame(rows, columns=list(CARD_DEFAULTS))
    frame["show"] = frame["show"].astype(bool)
    frame["goal"] = pd.to_numeric(frame["goal"], errors="coerce")
    frame["decimals"] = pd.to_numeric(frame["decimals"], errors="coerce")
    return frame


def clean_cards(frame, numeric_cols):
    """Turn the editor DataFrame into a list of valid card dicts (shown or not)."""
    cards = []
    for _, row in frame.iterrows():
        col = row.get("column")
        if not isinstance(col, str) or col not in numeric_cols:
            continue
        card = dict(CARD_DEFAULTS)
        card["show"] = bool(row.get("show", True))
        card["column"] = col
        title = row.get("title")
        card["title"] = title.strip() if isinstance(title, str) and title.strip() else split_title_unit(col)[0]
        unit = row.get("unit")
        card["unit"] = unit.strip() if isinstance(unit, str) else ""
        card["per"] = row.get("per") if row.get("per") in PER_OPTIONS else "day"
        goal = row.get("goal")
        card["goal"] = None if goal is None or pd.isna(goal) else float(goal)
        card["goal_is"] = row.get("goal_is") if row.get("goal_is") in GOAL_IS_OPTIONS else "at least"
        decimals = row.get("decimals")
        card["decimals"] = 1 if decimals is None or pd.isna(decimals) else int(min(max(round(decimals), 0), 4))
        card["daily_as"] = row.get("daily_as") if row.get("daily_as") in DAILY_AS_OPTIONS else "points"
        cards.append(card)
    return cards


def cards_to_json(frame):
    rows = []
    for _, row in frame.iterrows():
        if not isinstance(row.get("column"), str) or not row["column"]:
            continue
        item = {}
        for key in CARD_DEFAULTS:
            value = row.get(key)
            if value is None or (not isinstance(value, str) and pd.isna(value)):
                value = None
            elif isinstance(value, (np.integer,)):
                value = int(value)
            elif isinstance(value, (np.floating,)):
                value = float(value)
            elif isinstance(value, (np.bool_,)):
                value = bool(value)
            item[key] = value
        rows.append(item)
    return json.dumps({"version": CONFIG_VERSION, "plots": rows}, indent=2)


def cards_from_json(text, numeric_cols):
    """Parse a saved setup. Returns (frame, warnings). Raises ValueError if unusable."""
    try:
        data = json.loads(text)
        plots = data["plots"]
        assert isinstance(plots, list)
    except Exception:
        raise ValueError("That file is not a Life Tracker setup file.")
    rows, missing = [], []
    for item in plots:
        if not isinstance(item, dict):
            continue
        column = item.get("column")
        if column not in numeric_cols:
            missing.append(str(column))
            continue
        rows.append({**CARD_DEFAULTS, **{k: v for k, v in item.items() if k in CARD_DEFAULTS}})
    warnings = []
    if missing:
        warnings.append("Skipped plots whose columns are not in this CSV: " + ", ".join(missing) + ".")
    return cards_frame(rows), warnings


# ------------------------------------------------------- rolling-window math

def trailing_windows(span_days):
    """Each average only appears once there is enough history for it."""
    needed = [1, 7, 30, 90]  # week, month, quarter, year
    return [w for w, n in zip(ALL_WINDOWS, needed) if span_days > n]


def daily_series(df, col):
    """The metric on every calendar day from its first to its last recorded value.

    Unrecorded days in between stay NaN (not zero). Nothing is drawn past the
    last recorded value, even if the CSV has later rows.
    """
    series = df.set_index("Date")[col].dropna()
    if series.empty:
        return series
    index = pd.date_range(series.index.min(), series.index.max(), freq="D")
    return series.reindex(index)


def trailing(daily, windows, mult=1):
    """Trailing averages (times mult) and how many days each window actually recorded."""
    pace = pd.DataFrame({label: daily.rolling(off, min_periods=1).mean() * mult for label, off, _ in windows})
    recorded = pd.DataFrame({label: daily.rolling(off, min_periods=1).count() for label, off, _ in windows})
    return pace, recorded


def trailing_30d_mean(daily, mult=1):
    if daily.dropna().empty:
        return None
    return daily.rolling("30D", min_periods=1).mean().iloc[-1] * mult


def monthly_calendar_avg(daily, mult=1):
    """Calendar-month average, placed on the 15th of each month."""
    valid = daily.dropna()
    if valid.empty:
        return pd.Series(dtype=float)
    grouped = valid.groupby(valid.index.to_period("M")).mean() * mult
    centers = grouped.index.to_timestamp() + pd.Timedelta(days=14)
    centers = centers.where(centers <= valid.index.max(), valid.index.max())  # never past the last value
    return pd.Series(grouped.values, index=centers)


PERIODS = {"Day": None, "Week": "W-SUN", "Month": "M"}


def period_aggregate(df, col, period, mult=1, min_days=1):
    """One value per non-overlapping period (week = Monday to Sunday, or calendar month).

    Each value is the average of the days recorded in that period, times mult.
    Periods with fewer than min_days recorded days are dropped, so a thin
    week or month never shows up as a point. Indexed by the period's first day.
    """
    series = df.set_index("Date")[col].dropna()
    freq = PERIODS[period]
    if freq is None:
        return series
    grouped = series.groupby(series.index.to_period(freq))
    out = grouped.mean() * mult
    out = out[grouped.count() >= min_days]
    out.index = out.index.to_timestamp()
    return out
