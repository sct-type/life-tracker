# Life tracker

Run `./start.command`, or double-click it in Finder. The app runs locally at http://localhost:8501.

Setup if needed: `python3 -m venv .venv`, then `.venv/bin/python -m pip install -r requirements.txt`.

Upload a full-history CSV exported from your spreadsheet. Without an upload, the app uses the alphabetically last CSV in data/. Uploads replace the displayed dataset and are not written to disk. Keep the original spreadsheet as your source of truth.

Required columns: Date, Next morning weight (lbs), Work (hrs), Sleep time (hours).
Use dates with a year for history spanning multiple years. For month/day dates, select the year in the sidebar. All charts use the spreadsheet row date, including next-morning weight and overnight sleep.

Weekly work is summed Monday–Sunday. Average weekly work includes each week with a work entry, including partial weeks. Seven recorded days marks a complete week; enter 0 explicitly for non-working days. Unrecorded weeks are excluded. The weekly goal is 40 hours. Sleep goal defaults to 7.5 hours and is adjustable.

Drink tracking uses the optional Drinks column. Weekly totals run Monday–Sunday with an upper limit of 7, not a consumption target. Blank days remain unknown; zero records an alcohol-free day. A week is marked within limit only when all seven days are recorded; a partial week exceeding 7 is already marked over limit.
