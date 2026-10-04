# Life tracker

Run `./start.command`, or double-click it in Finder. The first run installs everything it needs (Python via Homebrew if it isn't already installed, plus the packages in requirements.txt), then starts the app. Later runs skip straight to starting it. The app runs locally at http://localhost:8501.

## Your data

Upload a CSV in the sidebar, or drop one in `data/` and the app uses the alphabetically last file there. Uploads are not written to disk. Keep the original spreadsheet as your source of truth.

Only a `Date` column is required, one row per day. Every other column that is mostly numbers becomes a metric you can plot. Dates with a year work best. For dates like 3/14, set the year in the sidebar. Leave a cell blank for an unrecorded day. Blank is not zero.

## Your plots

Open "Set up your plots". Each row is a plot: pick a column, a title and unit, and optionally a goal (at least or at most). Set Per to `week` for things you count per week, such as hours worked or drinks. Those show the daily value plus weekly rates (daily average times 7) against a weekly goal.

Each plot shows the daily values with week, month, quarter and year trailing averages, calendar-month averages on the 15th, and the goal line.

## Saving your setup

Download the setup as JSON and load it again from the sidebar. When started with `start.command`, the setup also saves automatically to `config.json` on your computer (not tracked by git).

## Relationships

"Explore relationships" compares two columns. Each point is a non-overlapping day, week (Monday to Sunday) or calendar month, averaged over its recorded days. Weeks and months with too few recorded days are dropped.
