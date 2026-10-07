# Production refactoring plan

## Scope and invariant

The work takes place on `refactor/production-ready`. `main` is unchanged until the owner tests and approves a merge. The application's visible controls, input interpretation, CO₂ calculations, plot traces, table values, export columns, and bundled data remain compatible unless a separately documented defect requires a fix. New source code, comments, and identifiers use English.

## Current architecture and risks

- `EcoCarReplacementAdvisor.py` constructs the main window, reads widgets, calculates vehicle inputs and result tables, and exports files.
- `src/PlotWidget.py` mixes numerical time-series calculations with Qt/Plotly rendering.
- `src/Utilities.py` mixes workbook loading, default assumptions, interpolation, and resource lookup.
- The current-car and replacement-car forms duplicate default lookup and field-enabling logic.
- `src/Car_old.py` and `Data/Use/usePhaseData_old.xlsx` are not referenced by the application; their historical role must be determined before removal.
- The current resource path depends on the process working directory. The root `__init__.py` refers to a nonexistent `GUI` module.
- Tests currently exercise only import and workbook loading; there are no reference outputs for model behavior or GUI workflows.

## Execution

1. **Characterize the baseline.** Add repeatable scenarios for gasoline, diesel, hybrid, plug-in hybrid, and BEV; cover used-car ownership, maintenance, battery replacement, finite usage, tables, and export. Save numerical reference results before changing calculations.
2. **Separate the model.** Move assumptions, workbook access, input preparation, emission histories, break-even calculations, and table metrics into typed, testable modules with no Qt dependency. Keep unit conversions and current rounding semantics explicit.
3. **Separate the interface.** Keep Qt widgets responsible for input, validation feedback, layout, and rendering. Split the long main-window, vehicle-form, plot, and table modules. Move export preparation and file writing out of the main window.
4. **Remove hardcoded infrastructure values.** Centralize car types, country choices, modeling constants, and default settings. Retain the supplied workbook data as the source of vehicle-specific defaults.
5. **Clean the repository.** Use a real Python package, a small entry point, consistent naming, explicit resource lookup, English comments, structured errors, and updated uv/PyInstaller/README configuration. Remove only demonstrably unused legacy code and preserve research data unless confirmed redundant.
6. **Verify and debug.** Compare the refactored model against baseline snapshots, run unit/integration/GUI smoke tests, build the executable, and inspect failures. Then request an independent subagent review and test pass, fix confirmed findings, and push the branch for owner testing.

## Acceptance checks

- Characterized numerical scenarios match baseline within stated floating-point tolerances.
- The GUI opens, loads workbook defaults, performs an analysis, changes output units, and exports a file.
- Source execution works from outside the repository working directory; PyInstaller includes all runtime assets.
- `uv sync --locked`, automated tests, static checks, and the Windows build complete successfully.
- No generated executable, environment, cache, or secret enters Git. The final branch has a clean status and `main` is untouched.

## Implementation record

The new `eco_car_advisor` package separates workbook and assumption loading, Qt-independent calculations, export, form defaults, and view rendering. Three captured numerical scenarios and 27 form-default combinations are regression fixtures. Additional tests exercise the GUI analysis, offline plot assets, CSV/Excel export, resource paths, and invalid input boundaries. Plotly JavaScript is now written beside the temporary plot page, so graphs load without a CDN.

The refactor also fixes confirmed input defects: distinct BEV lifespan settings, replacement-option validation, zero-length comparison periods, used-car mileage beyond modeled lifetime, invalid annual mileage, and tiny battery lifetimes rounded to zero. The golden scenarios are unaffected. The old `src` package, broken root package file, and obsolete build command are removed; the historical workbook remains available for research.
