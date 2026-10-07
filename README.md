# ECO Car Replacement Advisor

Desktop application for comparing the life-cycle CO₂ footprint of keeping a car with replacing it. It combines vehicle production and end-of-life, use-phase energy, battery, and maintenance assumptions, then displays plots and tables for alternative cars.

> The application currently labels itself **confidential and for FAAS members only**. This repository has no open-source license. Do not make it public or redistribute it without authorization from the project owners.

The detailed field-by-field user guide is in [Data/Documentation/README.md](Data/Documentation/README.md). The HTML copy in the same directory is used by the application's Help menu.

## Requirements

- Windows 10/11 for the supported desktop and executable workflow. The Python source may also run on other desktop platforms with Qt support, but those platforms have not been verified.
- Python 3.11–3.14 and [uv](https://docs.astral.sh/uv/getting-started/installation/).

## Install and run from source

From the repository root:

```powershell
uv sync --locked
uv run --no-sync python EcoCarReplacementAdvisor.py
```

`uv sync` creates a local `.venv` and installs the direct dependencies declared in `pyproject.toml` at the versions resolved in `uv.lock`. The lockfile is committed for repeatable installs. Run the app from the repository root because its current resource loader resolves `Data/` and `Icons/` from the working directory.

If you only need a conventional pip requirements file, `requirements.txt` is an exported snapshot of the same lockfile. The uv workflow above is the maintained installation path.

## Use

1. Set the current car's segment, powertrain, mileage, and energy assumptions.
2. Add one or more replacement cars and configure their parameters.
3. Adjust the analysis horizon and maintenance settings.
4. Click **Compute Carbon Footprint** to view the plots and tables.

For definitions of each input and output, see the [full user guide](Data/Documentation/README.md).

## Build the Windows executable

On Windows, from the repository root:

```powershell
uv sync --locked --group build
uv run --no-sync pyinstaller --noconfirm EcoCarReplacementAdvisor.spec
```

The executable is produced in `dist/` and is intentionally excluded from Git. The PyInstaller spec includes the `Data/` and `Icons/` assets required at runtime. The source and project metadata are the versioned release inputs.

## Verify

```powershell
uv run --no-sync python -m unittest discover -s tests -v
```

This smoke test imports the GUI and reads the bundled workbooks. GitHub Actions runs it on Windows with Python 3.11 and 3.14; it does not exercise GUI interaction or validate the CO₂ model's scientific results.

## Project layout

| Path | Purpose |
| --- | --- |
| `EcoCarReplacementAdvisor.py` | GUI entry point |
| `src/` | Application widgets and calculation utilities |
| `Data/` | Workbook inputs and in-app documentation |
| `Icons/` | Interface assets |
| `EcoCarReplacementAdvisor.spec` | PyInstaller build configuration |
| `pyproject.toml`, `uv.lock` | Dependency declarations and resolved versions |

## Development status

This is an initial repository publication of the existing application. The current module layout and calculation code have intentionally been preserved; a broader code migration can follow separately. Verification is limited to the smoke test above; there are no model-validation tests or verified cross-platform builds yet.

## Authors and access

Developed by Luca Cibrario with Chiara Gastaldi at Politecnico di Torino. Contact details are in the [user guide](Data/Documentation/README.md). Access and distribution remain subject to the project owners' authorization.
