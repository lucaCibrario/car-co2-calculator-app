"""Load versioned model assumptions and workbook inputs."""

import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

import pandas as pd

from eco_car_advisor.resources import resource_path


@lru_cache(maxsize=1)
def load_assumptions() -> dict:
    """Load the model's fixed assumptions from its versioned JSON file."""
    path = Path(resource_path("Data/model_assumptions.json"))
    with path.open(encoding="utf-8") as source:
        return json.load(source)


class DataRepository:
    """Read spreadsheet inputs and expose the legacy data schema to the UI."""

    def load(self) -> dict:
        assumptions = deepcopy(load_assumptions())
        production = resource_path("Data/ProductionEoL/productionEoLData.xlsx")
        maintenance = resource_path("Data/Maintenance/maintenance.xlsx")
        use_phase = resource_path("Data/Use/usePhaseData.xlsx")

        maintenance_data = pd.read_excel(maintenance, sheet_name="maintenance")
        maintenance_data = (
            maintenance_data.groupby("Mileage")["Delta Maintenance (tonCO2)"]
            .max()
            .reset_index()
            .sort_values("Mileage")
            .reset_index(drop=True)
        )

        return {
            "maintenance": maintenance_data,
            "productionEoL": {
                "co2/kg": pd.read_excel(production, sheet_name="productionEoLCOkg", index_col=0),
                "defaultMass": pd.read_excel(production, sheet_name="mass", index_col=0),
            },
            "usePhase": {
                "consumptionICE": pd.read_excel(
                    use_phase, sheet_name="consumptionICE", index_col=0
                ),
                "consumptionBEV": pd.read_excel(
                    use_phase, sheet_name="consumptionBEV", index_col=0
                ),
                "Gasoline": assumptions["fuel_emissions"]["Gasoline"],
                "Diesel": assumptions["fuel_emissions"]["Diesel"],
                "DrivingShare": assumptions["driving_share"],
                "EnergyMix": assumptions["energy_mix_kg_per_kwh"],
            },
            "batteries": {
                "capacity": pd.read_excel(maintenance, sheet_name="batteryCapacity", index_col=0),
                "kgco2/kWh": assumptions["battery_production_kg_per_kwh"],
            },
        }
