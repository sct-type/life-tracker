# Tally

Tally turns the spreadsheet you already keep into plots and patterns. One row a day, your own columns. No wearable, no lock-in.

Run `./start.command`, or double-click it in Finder. The first run installs everything it needs (Python via Homebrew if it isn't already installed, plus the packages in requirements.txt), then starts the app. Later runs skip straight to starting it. The app runs locally at http://localhost:8501.

## Your data

Pick a source in the sidebar. Upload a CSV, paste a link to a Google Sheet published as CSV (File, Share, Publish to web, CSV), or choose a saved name. Locally, with Upload selected and nothing uploaded, the app uses the alphabetically last file in `data/`. Uploads are not written to disk. Keep the original spreadsheet as your source of truth.

Only a `Date` column is required, one row per day. Every other column that is mostly numbers becomes a metric you can plot. Dates with a year work best. For dates like 3/14, set the year in the sidebar. Leave a cell blank for an unrecorded day. Blank is not zero.

## Your plots

Open "Set up your plots". Nothing is ticked at first. Each row is a plot: pick a column, a title and unit, and optionally a goal (at least or at most). Set Per to `week` for things you count per week, such as hours worked or drinks. Those show the daily value plus weekly rates (daily average times 7) against a weekly goal.

Each plot shows the daily values with week, month, quarter and year trailing averages, calendar-month averages on the 15th, and the goal line.

## Saving your setup

Every visit starts with no plots on. Tick what you want. Remembering a setup is built but switched off for now: `USE_LOCAL_CONFIG` in `app.py` saves it to `config.json` on your computer (not tracked by git), and `SHOW_SETUP_FILES` adds JSON download and upload.

## Relationships

"Explore relationships" compares two columns. Each point is a non-overlapping day, week (Monday to Sunday) or calendar month, averaged over its recorded days. Weeks and months with too few recorded days are dropped.

## Saved names

Names and sheet links live in Streamlit secrets, never in the repo, because a published link lets anyone with it read the sheet. Locally, put them in `.streamlit/secrets.toml` (gitignored). On Streamlit Community Cloud, paste the same text into the app's Settings, then Secrets.

```toml
[people]
"Name One" = "https://docs.google.com/spreadsheets/d/e/.../pub?gid=0&single=true&output=csv"
"Name Two" = ""
```

An empty link shows "no sheet link yet". Anyone who can open the app can pick any saved name.
