# ECO Car Replacement Advisor

Desktop application for comparing the life-cycle CO₂ impact of keeping a current car with replacing it. It combines production and end-of-life, energy use, battery replacement, and maintenance inputs, then shows emissions over mileage and age. The [user guide](Data/Documentation/README.md) explains each field and the model's interpretation.

> **Access:** The application is marked confidential for FAAS members. No open-source license is granted by this repository. Distribution and reuse require the project owners' authorization.

The HTML guide in the same directory is used by the application's Help menu.

## Requirements

- Windows 10/11 for the supported desktop and executable workflow. The Python source may also run on other desktop platforms with Qt support, but those platforms have not been verified.
- Python 3.11–3.14 and [uv](https://docs.astral.sh/uv/getting-started/installation/).

## Install and run from source

From a PowerShell prompt in the repository directory:

```powershell
uv sync --locked
uv run --no-sync python EcoCarReplacementAdvisor.py
```

`uv sync` creates `.venv` and installs the versions in the committed `uv.lock`. The application resolves `Data/` and `Icons/` relative to its source or PyInstaller bundle, so the launch command also works from another working directory when given the entry point's absolute path.

`requirements.txt` is a runtime-only export for environments that require pip; `pyproject.toml` and `uv.lock` are the maintained dependency sources.

## Use

1. Enter the current car's segment, powertrain, mileage, and country.
2. Add at least one replacement car and adjust its settings if needed.
3. Choose the intended end of usage and maintenance settings.
4. Click **Compute Carbon Footprint**. Switch the plot between years and kilometres, inspect the summary table, or export CSV/Excel from **File → Export Data**.

The plots ship their JavaScript locally and work without an internet connection.

For definitions of each input and output, see the [full user guide](Data/Documentation/README.md).

## Build the Windows executable

On Windows, from the repository root:

```powershell
uv sync --locked --group build
uv run --no-sync pyinstaller --noconfirm EcoCarReplacementAdvisor.spec
```

The executable appears in `dist/` and is ignored by Git. The spec bundles `Data/`, `Icons/`, and the model assumptions JSON. Run the executable on Windows and check an analysis before distributing a build.

## Verify

```powershell
uv run --no-sync ruff check eco_car_advisor tests EcoCarReplacementAdvisor.py
uv run --no-sync ruff format --check eco_car_advisor tests EcoCarReplacementAdvisor.py
$env:QT_QPA_PLATFORM = "offscreen"
$env:QTWEBENGINE_DISABLE_SANDBOX = "1"
uv run --no-sync python -m unittest discover -s tests -v
```

The tests cover captured pre-refactor model outputs, all 27 segment/powertrain form defaults, a GUI analysis and plot, CSV/Excel export, and resource loading outside the repository working directory. GitHub Actions runs the same checks on Windows with Python 3.11 and 3.14. These are software regression checks; they do not independently validate the scientific assumptions in the input workbooks.

## Project layout

| Path | Purpose |
| --- | --- |
| `EcoCarReplacementAdvisor.py` | GUI entry point |
| `eco_car_advisor/analysis.py`, `calculations.py` | Qt-independent model and numerical functions |
| `eco_car_advisor/data.py`, `resources.py` | Workbook inputs, assumptions, and asset paths |
| `eco_car_advisor/export.py` | CSV and Excel export |
| `eco_car_advisor/ui/` | Qt forms, result table, and Plotly view |
| `Data/model_assumptions.json` | Versioned non-workbook model constants |
| `Data/` | Input workbooks and user documentation |
| `Icons/` | Interface assets |
| `tests/` | Regression fixtures and workflow checks |
| `EcoCarReplacementAdvisor.spec` | PyInstaller configuration |

The historical `Data/Use/usePhaseData_old.xlsx` is retained as research material and is not read by the application. Changes to workbooks or `model_assumptions.json` can change scientific results and should be reviewed separately from interface changes.

## Authors

Developed by Luca Cibrario with Chiara Gastaldi at Politecnico di Torino. Contact details and model context are in the [user guide](Data/Documentation/README.md).
