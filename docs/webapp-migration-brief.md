# Web application migration

The desktop PySide6 frontend was replaced with a browser interface on `codex/webapp-migration`. The numerical engine, scientific workbooks, model assumptions, and flat export schema are retained.

## Architecture

- FastAPI serves the application and a stateless JSON API.
- `web/service.py` maps form values to the existing analysis engine and prepares chart/table output.
- `web/static/` contains a responsive, buildless HTML/CSS/JavaScript UI. Plotly JavaScript is served from the installed Python package, allowing local/offline use.
- The API validates vehicle, second-hand, and analysis inputs before calling the model. It recalculates exports from the submitted scenario; no server-side user state is stored.

## Parity and scope

The web form covers current and replacement vehicle settings, workbook defaults, country electricity mix, second-hand inputs, maintenance, annual mileage, end-of-usage, and lifespan assumptions. It presents the same emission histories in years or kilometres, the end-of-usage metrics, and CSV/Excel exports. Tests compare captured pre-migration numerical outputs and every segment/powertrain default.

The former Qt UI, executable entry point, and PyInstaller build configuration were removed. Hosting and access controls remain deployment decisions: the application itself has no authentication and must be placed behind an approved access layer before remote use with confidential FAAS data.
