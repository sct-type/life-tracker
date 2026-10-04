"""Figure builders for Life Tracker."""
import plotly.graph_objects as go

DAY_COLOR = "#000000"
WINDOW_COLORS = {
    "Week average": "#2a78d6",
    "Month average": "#eb6834",
    "Quarter average": "#1baf7a",
    "Year average": "#eda100",
}
MONTHLY_COLOR = "#e87ba4"


def with_unit(text, unit):
    return f"{text} {unit}" if unit else text


def hover_fmt(unit, decimals=1):
    return f"%{{x|%b %d, %Y}}<br>%{{y:.{decimals}f}}{' ' + unit if unit else ''}<extra></extra>"


def rate_unit(card):
    """Unit shown for the trailing lines."""
    if card["per"] == "week":
        return f"{card['unit']}/wk" if card["unit"] else "per week"
    return card["unit"]


def metric_figure(card, daily, pace, windows, monthly):
    """Daily values, trailing averages, calendar-month markers and an optional goal line."""
    d = card["decimals"]
    unit = card["unit"]
    lines_unit = rate_unit(card)
    fig = go.Figure()

    if card["daily_as"] == "bars":
        fig.add_bar(x=daily.index, y=daily, marker_color=DAY_COLOR, name="Day", hovertemplate=hover_fmt(unit, d))
    else:
        fig.add_scatter(x=daily.index, y=daily, mode="markers", marker=dict(color=DAY_COLOR, size=6),
                        name="Day", hovertemplate=hover_fmt(unit, d))
    for label, _, _ in windows:
        fig.add_scatter(x=pace.index, y=pace[label], mode="lines",
                        name="Trailing " + label.lower().replace("average", "avg"),
                        line_color=WINDOW_COLORS[label], connectgaps=True, hovertemplate=hover_fmt(lines_unit, d))
    if not monthly.empty:
        fig.add_scatter(x=monthly.index, y=monthly.values, mode="markers",
                        marker=dict(color=MONTHLY_COLOR, size=11, symbol="diamond"),
                        name="Monthly avg", hovertemplate=hover_fmt(lines_unit, d))
    if card["goal"] is not None:
        fig.add_scatter(x=[daily.index[0], daily.index[-1]], y=[card["goal"]] * 2, mode="lines",
                        line=dict(color="#888", dash="dash"), name=f"Goal: {with_unit(format(card['goal'], 'g'), lines_unit)}",
                        hovertemplate=hover_fmt(lines_unit, d))

    if card["per"] == "week":
        y_title = f"{with_unit('per day', unit)} (Day) · {lines_unit} (trailing)"
    else:
        y_title = unit or card["title"]
    fig.update_layout(height=360, margin=dict(l=10, r=20, t=30, b=10), xaxis_title="Date",
                      yaxis_title=y_title, legend=dict(orientation="h", y=-0.25))
    fig.update_xaxes(tickformat="%b %d", dtick=86400000 if len(daily) <= 14 else None)
    return fig
