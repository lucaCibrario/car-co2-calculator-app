"""Prepare and write analysis data for external use."""

from pathlib import Path

import pandas as pd

from eco_car_advisor.analysis import AnalysisResult


def table_cars(result: AnalysisResult) -> list[dict]:
    """Apply the historical table rounding and savings to copies of vehicle data."""
    cars = [dict(car) for car in result.cars]
    current_total = cars[0]["THco2"]
    for index, car in enumerate(cars):
        car["co2Savings"] = None if index == 0 else current_total - car["THco2"]
        production = round(car["relativeProductionCo2"], 1)
        eol = round(car["relativeEolCo2"], 1)
        use = round(car["relativeUseCo2"], 1)
        maintenance = car["relativeMaintenanceCo2"]
        if result.settings["maintenance"] or (car["engineType"] == "BEV" and maintenance != 0):
            maintenance = round(100 - production - eol - use, 1)
        else:
            maintenance = None
            use = round(100 - production - eol, 1)
        car["relativeProductionCo2"] = production
        car["relativeEolCo2"] = eol
        car["relativeUseCo2"] = use
        car["relativeMaintenanceCo2"] = maintenance
    return cars


def build_export_frame(result: AnalysisResult) -> pd.DataFrame:
    """Build the historical flat export schema from an analysis result."""
    full = pd.DataFrame(table_cars(result))
    full.rename(columns={"mileage": "mileageAtChange"}, inplace=True)
    full["maintenance"] = result.settings.get("maintenance", False)
    full["EoUmileage"] = result.threshold_mileage[1] * 1000
    full["EoUage"] = result.threshold_age[1]
    exported = full.drop(
        columns=[
            "xValues",
            "totalUsePhaseEmissions",
            "totalUsePhaseEmissionsPlusMaintenance",
            "emissionHystory",
            "batteryReplacementLog",
        ],
        errors="ignore",
    )
    exported.insert(
        0, "Car ID", ["Current"] + [f"Car {index}" for index in range(1, len(exported))]
    )
    for name, position in (
        ("maintenance", 19),
        ("keepEOL", 20),
        ("EoUmileage", 23),
        ("EoUage", 24),
    ):
        if name in exported:
            column = exported.pop(name)
            exported.insert(position, name, column)
    return exported


def write_export(frame: pd.DataFrame, path: str, selected_filter: str) -> Path:
    """Write a CSV or workbook using the selected file-dialog format."""
    target = Path(path)
    if target.suffix.lower() == ".csv" or "CSV" in selected_filter:
        frame.to_csv(target, index=False)
    else:
        if target.suffix.lower() != ".xlsx":
            target = target.with_name(target.name + ".xlsx")
        frame.to_excel(target, index=False)
    return target
