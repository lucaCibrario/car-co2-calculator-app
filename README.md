# ECO Car Replacement Advisor

A browser application for comparing the life-cycle CO₂ impact of keeping a car with replacing it. The Python model includes vehicle production and end of life, energy use, battery replacement, and maintenance. The responsive interface presents emissions trajectories, an end-of-usage comparison, and CSV/Excel exports.

> **Access:** This tool and its model data are marked confidential for FAAS members. The repository grants no open-source license. Keep deployments behind appropriate authentication; the application itself does not provide user accounts or access control.

## Requirements

- Python 3.11–3.14
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

The web UI uses bundled Plotly JavaScript and needs no Node.js build. The numerical model and workbook assumptions remain in Python.

## Install and run

Install `uv` from the link above, then run these commands in a terminal (PowerShell, Command Prompt, or a Unix shell):

```text
git clone https://github.com/lucaCibrario/ECO-Car-Replacement-Advisor.git
cd ECO-Car-Replacement-Advisor
uv sync --locked
uv run --no-sync uvicorn eco_car_advisor.web.api:app --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Keep the terminal open while using the app; stop the server with `Ctrl+C`. If port 8000 is occupied, replace `8000` in the command and URL with another free port. Binding to `127.0.0.1` limits access to the local machine.

`uv sync --locked` creates the local `.venv` and installs the versions in the committed `uv.lock`. No Node.js installation or frontend build is needed. The source dependencies are in `pyproject.toml`; `requirements.txt` is a runtime-only export for pip-based environments and is not the primary installation method.

## Use

1. Select the current car's segment, powertrain, mileage, and country. The electricity mix is filled from the versioned assumptions; choose **Custom** to edit it.
2. Configure one to eight replacements. Open **Advanced vehicle inputs** to change workbook defaults or enter second-hand vehicle details.
3. Choose annual mileage, maintenance, end of usage, and optional vehicle lifespans.
4. Select **Run analysis**. The **Trajectory** chart shows cumulative emissions and switches between years and kilometres. **Annual breakdown** shows production, end of life, use, and maintenance or battery contributions as stacked bars in tCO₂e/year.
5. Compare vehicles in the table and export the results as CSV or Excel. Drag the separators to resize setup, chart, and table; double-click a separator to restore its default size. On narrow screens, use the **Setup** and **Results** tabs.

The [full user guide](Data/Documentation/README.md) explains the inputs and model. The web UI renders this Markdown guide locally at `/guide`. Analyses and exports are computed from each submitted form; the server does not save scenarios. The browser stores only the chosen panel sizes.

## Verify

```powershell
uv run --no-sync ruff check eco_car_advisor tests
uv run --no-sync ruff format --check eco_car_advisor tests
node --check eco_car_advisor/web/static/app.js
uv run --no-sync python -m unittest discover -s tests -v
```

The tests compare model outputs against captured pre-migration scenarios, check all 27 segment/powertrain defaults, exercise HTTP analysis and both exports, and reject invalid inputs. The JavaScript syntax check requires Node.js only for development; it is not needed to run the app. GitHub Actions runs these checks on Ubuntu and Windows with Python 3.11 and 3.14. These software tests do not independently validate the scientific assumptions in the input workbooks.

## Application structure

| Path | Purpose |
| --- | --- |
| `eco_car_advisor/analysis.py`, `calculations.py` | Qt-independent numerical model |
| `eco_car_advisor/data.py`, `resources.py` | Workbook inputs, assumptions, and resource paths |
| `eco_car_advisor/export.py` | Existing flat CSV/Excel export schema |
| `eco_car_advisor/web/api.py`, `service.py` | Validated HTTP API and model adapter |
| `eco_car_advisor/web/static/` | Responsive HTML, CSS, JavaScript frontend |
| `Data/model_assumptions.json`, `Data/` | Versioned scientific assumptions and documentation |
| `tests/fixtures/` | Captured pre-migration results and form defaults |

API documentation is available locally at `/api/docs`. The endpoints are `/api/config`, `/api/vehicle-defaults`, `/api/analyze`, and `/api/export/{csv|xlsx}`. The API accepts JSON and does not keep session state.

For a remote deployment, run the ASGI server behind HTTPS, authentication, request limits, and process supervision on infrastructure approved for FAAS data. Do not expose this unauthenticated application directly to the public internet.

## Authors

Developed by Luca Cibrario with Chiara Gastaldi at Politecnico di Torino. Model context and contact details are in the [user guide](Data/Documentation/README.md).
