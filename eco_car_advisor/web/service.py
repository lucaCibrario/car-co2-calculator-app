"""Translate browser form data into the existing analysis model."""

import math
from functools import lru_cache

from eco_car_advisor.analysis import AnalysisEngine
from eco_car_advisor.data import DataRepository, load_assumptions
from eco_car_advisor.export import table_cars


@lru_cache(maxsize=1)
def repository_data() -> dict:
    return DataRepository().load()


def vehicle_defaults(segment: str, engine_type: str, *, current: bool = False) -> dict:
    """Return the same workbook defaults shown by the desktop vehicle forms."""
    assumptions = load_assumptions()
    if segment not in assumptions["car_segments"] or engine_type not in assumptions["engine_types"]:
        raise ValueError("Unknown vehicle segment or engine type")
    data = repository_data()
    fuel_name = "Diesel" if "Diesel" in engine_type else "Gasoline"
    fuel = data["usePhase"].get(fuel_name) if engine_type != "BEV" else None
    liters = data["usePhase"]["consumptionICE"].at[engine_type, segment]
    electricity = data["usePhase"]["consumptionBEV"].at[engine_type, segment]
    result = {
        "carSegment": segment,
        "engineType": engine_type,
        "massValue": round(float(data["productionEoL"]["defaultMass"].at[engine_type, segment])),
        "carProductionFootprint": round(
            float(data["productionEoL"]["co2/kg"].at[engine_type, segment]), 1
        ),
        "WTT": float(fuel["WTT"]) if fuel else None,
        "TTW": float(fuel["TTW"]) if fuel else None,
        "meanConsumptionLiter": round(float(liters) * 100, 1) if not math.isnan(liters) else None,
        "meanConsumptionWh": round(float(electricity) / 10, 1)
        if not math.isnan(electricity)
        else None,
        "drivingShare": round(float(data["usePhase"]["DrivingShare"][segment]), 2)
        if engine_type == "Plug-in Hybrid"
        else None,
        "secondHandCar": False,
        "secondHandCarMileage": None,
        "secondHandCarAge": None,
        "batteryCapacity": float(data["batteries"]["capacity"].at[engine_type, segment])
        if engine_type == "BEV"
        else None,
        "batteryProductionFootprint": float(data["batteries"]["kgco2/kWh"]),
        "batteryLifeTime": float(assumptions["default_bev_lifespan_km"]),
    }
    if current:
        result.update(
            country="Europe",
            energyMix=round(data["usePhase"]["EnergyMix"]["Europe"] * 1000),
            mileage=None,
        )
    return result


def analyze(current: dict, alternatives: list[dict], settings: dict):
    """Run the unchanged numerical engine after desktop-equivalent normalization."""
    current = dict(current)
    current["mileage"] = round(current["mileage"], -3)
    current["keepUnits"] = "km"
    current["keepLifeSpan"] = current["mileage"]
    settings = dict(settings)
    settings["ICElifeSpan"] = round(settings["ICElifeSpan"], -3)
    settings["BEVlifeSpan"] = round(settings["BEVlifeSpan"], -3)
    return AnalysisEngine(repository_data()).analyze(current, alternatives, settings)


def result_payload(result) -> dict:
    """Build chart and end-of-usage table data for the browser."""
    current = result.current_car
    annual = result.settings["km2yearsConvFactor"]
    used_mileage = current["secondHandCarMileage"] or 0
    used_age = current["secondHandCarAge"] or 0
    rows = []
    series = []
    display_cars = table_cars(result)
    for index, car in enumerate(result.cars):
        display = display_cars[index]
        rows.append(
            {
                "label": "Current" if index == 0 else f"Car {index}",
                "details": f"{car['carSegment']} · {car['engineType']}",
                "changeCo2": round(car["DeltaTHco2"], 1),
                "savingsCo2": None if index == 0 else round(display["co2Savings"], 1),
                "yearlyCo2": round(car["yearlyCo2"], 2),
                "productionPercent": display["relativeProductionCo2"],
                "eolPercent": display["relativeEolCo2"],
                "usePercent": display["relativeUseCo2"],
                "maintenancePercent": display["relativeMaintenanceCo2"],
                "breakEvenKm": car.get("BEkm"),
            }
        )
        xs = car["xValues"]
        series.append(
            {
                "label": f"{'Current car' if index == 0 else f'Car {index}'} · "
                f"{car['carSegment']} · {car['engineType']}",
                "xKm": xs.tolist(),
                "xYears": ((xs - used_mileage) / annual + used_age).tolist(),
                "emissions": car["emissionHystory"].tolist(),
                "lifeSpanKm": float(car["carLifeSpan"]),
            }
        )
    return {
        "rows": rows,
        "series": series,
        "replacementKm": float(current["mileage"]),
        "endKm": float(result.end_km),
        "endYears": float(result.threshold_age[1]),
        "kmRange": list(result.threshold_mileage),
        "yearsRange": list(result.threshold_age),
        "yRange": list(result.y_range),
        "emissionsAtReplacement": float(result.emissions_at_replacement),
    }
