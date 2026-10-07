"""Prepare and write analysis data for external use."""

from pathlib import Path

import pandas as pd

from eco_car_advisor.analysis import AnalysisResult


def build_export_frame(result: AnalysisResult) -> pd.DataFrame:
    """Build the historical flat export schema from an analysis result."""
    full = pd.DataFrame(result.cars)
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
