# ECO Car Replacement Advisor

A browser application for comparing the life-cycle CO₂ impact of keeping a car with replacing it. The Python model includes vehicle production and end of life, energy use, battery replacement, and maintenance. The responsive interface presents emissions trajectories, an end-of-usage comparison, and CSV/Excel exports.

> **Access:** This tool and its model data are marked confidential for FAAS members. The repository grants no open-source license. Keep deployments behind appropriate authentication; the application itself does not provide user accounts or access control.

## Requirements

- Python 3.11–3.14
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

The web UI uses bundled Plotly JavaScript and needs no Node.js build. The numerical model and workbook assumptions remain in Python.

## Install and run

From the repository root:

```powershell
uv sync --locked
uv run --no-sync uvicorn eco_car_advisor.web.api:app --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The server binds to localhost by default in this example, so only the local machine can reach it. Stop it with `Ctrl+C`.

The committed `uv.lock` fixes dependency versions. `requirements.txt` is a runtime-only export for environments that require pip; maintain dependencies in `pyproject.toml` and regenerate the export after changing the lockfile.

## Use

1. Select the current car's segment, powertrain, mileage, and country. The electricity mix is filled from the versioned assumptions; choose **Custom** to edit it.
2. Configure one to eight replacements. Open **Advanced vehicle inputs** to change workbook defaults or enter second-hand vehicle details.
3. Choose annual mileage, maintenance, end of usage, and optional vehicle lifespans.
4. Run the analysis. Switch the chart between years and kilometres, compare the summary table, and download CSV or Excel data.

The [full user guide](Data/Documentation/README.md) explains the meaning of the inputs and model. The web UI renders this Markdown guide locally at `/guide`. No data is stored by the application: each analysis and export is computed from the submitted form and the versioned model files.

## Verify

```powershell
uv run --no-sync ruff check eco_car_advisor tests
uv run --no-sync ruff format --check eco_car_advisor tests
uv run --no-sync python -m unittest discover -s tests -v
```

The tests compare model outputs against captured pre-migration scenarios, check all 27 segment/powertrain defaults, exercise HTTP analysis and both exports, and reject invalid inputs. GitHub Actions runs the same checks on Ubuntu and Windows with Python 3.11 and 3.14. These software tests do not independently validate the scientific assumptions in the input workbooks.

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
