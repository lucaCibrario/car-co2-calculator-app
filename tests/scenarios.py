"""Deterministic scenarios captured from the original analysis pipeline."""


def car(engine, *, current=False, used=False):
    is_bev = engine == "BEV"
    is_plugin = engine == "Plug-in Hybrid"
    is_diesel = "Diesel" in engine
    result = {
        "carSegment": "Segment C",
        "engineType": engine,
        "massValue": 1850.0 if is_bev else 1450.0,
        "carProductionFootprint": 5.2 if is_bev else 4.4,
        "WTT": None if is_bev else (697.0 if is_diesel else 572.0),
        "TTW": None if is_bev else (2650.0 if is_diesel else 2360.0),
        "meanConsumptionLiter": None if is_bev else (5.1 if is_diesel else 6.4),
        "meanConsumptionWh": 17.2 if is_bev else (19.0 if is_plugin else None),
        "drivingShare": 0.44 if is_plugin else None,
        "secondHandCar": used,
        "secondHandCarMileage": 40000.0 if current and used else (20000.0 if used else None),
        "secondHandCarAge": 3.0 if current and used else (2.0 if used else None),
        "batteryCapacity": 65.0 if is_bev else None,
        "batteryProductionFootprint": 130.0 if is_bev else None,
        "batteryLifeTime": 120000.0 if is_bev else None,
    }
    if current:
        result.update(
            country="Italy",
            energyMix=225.0,
            mileage=80000.0,
            keepUnits="km",
            keepLifeSpan=80000.0,
        )
    return result


def scenarios():
    return {
        "gasoline_to_bev_with_maintenance": (
            car("Gasoline (Euro 6)", current=True),
            [car("BEV")],
            {
                "ICElifeSpan": 200000.0,
                "BEVlifeSpan": 200000.0,
                "km2yearsConvFactor": 12000.0,
                "maintenance": True,
                "keepEOL": True,
                "keepLifeSpan": None,
                "keepUnits": "km",
            },
        ),
        "used_diesel_to_used_plugin_without_maintenance": (
            car("Diesel (Euro 5)", current=True, used=True),
            [car("Plug-in Hybrid", used=True)],
            {
                "ICElifeSpan": 200000.0,
                "BEVlifeSpan": 200000.0,
                "km2yearsConvFactor": 12000.0,
                "maintenance": False,
                "keepEOL": False,
                "keepLifeSpan": 5.0,
                "keepUnits": "years",
            },
        ),
        "gasoline_to_diesel_without_maintenance": (
            car("Gasoline (Euro 4)", current=True),
            [car("Diesel (Euro 6)")],
            {
                "ICElifeSpan": 200000.0,
                "BEVlifeSpan": 200000.0,
                "km2yearsConvFactor": 12000.0,
                "maintenance": False,
                "keepEOL": True,
                "keepLifeSpan": None,
                "keepUnits": "km",
            },
        ),
    }


def summarize(harness):
    keys = (
        "productionEoL",
        "depreciation",
        "usePhaseEmissions",
        "carLifeSpan",
        "THco2",
        "DeltaTHco2",
        "yearlyCo2",
        "relativeProductionCo2",
        "relativeEolCo2",
        "relativeUseCo2",
        "relativeMaintenanceCo2",
        "BEkm",
        "BEco2",
        "DeltaBEkm",
        "DeltaBEco2",
    )
    cars = []
    for values in harness.carData:
        series = values["emissionHystory"]
        car_summary = {
            key: float(values[key]) if values.get(key) is not None else None for key in keys
        }
        car_summary["x_first"] = float(values["xValues"][0])
        car_summary["x_last"] = float(values["xValues"][-1])
        car_summary["x_count"] = len(values["xValues"])
        car_summary["emission_samples"] = [
            float(series[index]) for index in (0, len(series) // 2, len(series) - 1)
        ]
        if "batteryReplacementLog" in values:
            car_summary["battery_replacement_total"] = float(values["batteryReplacementLog"][-1])
        cars.append(car_summary)
    plot = harness.plot_widget
    return {
        "cars": cars,
        "analysis_start_km": float(plot.analysisStartKm),
        "end_km": float(plot.xmaxRangeKm),
        "y_range": [float(value) for value in plot.yRange],
    }
