# Web application migration brief

This note records the next planned phase after the desktop refactor. It is not an implementation plan or a change to the current application.

## Objective

Replace the Qt desktop interface with a modern, responsive HTML/CSS web interface while preserving the current application's input meaning, calculations, plots, tables, and CSV/Excel exports. The new frontend should be visually polished and usable on desktop and smaller screens.

## Starting point

- `eco_car_advisor/analysis.py` and `calculations.py` contain the Qt-independent numerical model.
- `eco_car_advisor/data.py` loads the versioned workbooks and `Data/model_assumptions.json`.
- `eco_car_advisor/export.py` builds the existing export schema.
- `tests/fixtures/legacy_baseline.json` and `form_defaults.json` capture desktop behavior. The regression and GUI tests are in `tests/`.
- `eco_car_advisor/ui/` is the Qt interface that must be mapped to web forms, plots, and tables.

## Proposed direction

Keep the established Python model as the backend computation engine and expose a narrow API for input defaults, analysis, and export. Use a modern HTML/CSS/TypeScript frontend for the interface. This avoids translating the scientific formulas into JavaScript during the interface migration and lets the current regression fixtures verify parity. Select the specific web framework and deployment model after checking hosting, authentication, and FAAS access requirements.

## First steps for the next phase

1. Inventory every form field, default, validation rule, plot, table metric, and export column in the desktop UI.
2. Define a versioned request/response contract and compare API results against the captured numerical fixtures.
3. Build the interface with responsive layouts and accessible controls, then test the same user workflows as the desktop application.
4. Decide how confidential FAAS data and access will be hosted before publishing the web application.
