"""Qt-independent life-cycle emissions analysis."""

from copy import deepcopy
from dataclasses import dataclass

import numpy as np

from eco_car_advisor.calculations import (
    add_degradation,
    add_maintenance,
    battery_replacement_emissions,
    compute_intersection,
    depreciation_curve,
    interpolate,
    years_to_kilometers,
)
from eco_car_advisor.data import load_assumptions


class AnalysisInputError(ValueError):
    """An input scenario cannot be evaluated within the model limits."""


@dataclass
class AnalysisResult:
    """Calculated vehicle series and table metrics for one analysis run."""

    cars: list[dict]
    settings: dict
    analysis_start_km: float
    analysis_start_years: float
    end_km: float
    min_km: float
    y_range: tuple[float, float]
    threshold_mileage: tuple[float, float]
    threshold_age: tuple[float, float]
    emissions_at_replacement: float
    co2_at_change: float

    @property
    def current_car(self) -> dict:
        return self.cars[0]


class AnalysisEngine:
    """Perform a complete analysis without depending on Qt or Plotly."""

    def __init__(self, data: dict, assumptions: dict | None = None):
        self.data = data
        self.assumptions = assumptions or load_assumptions()

    def analyze(
        self, current_car: dict, alternatives: list[dict], settings: dict
    ) -> AnalysisResult:
        """Calculate histories and summary values for the supplied vehicles."""
        if not alternatives:
            raise AnalysisInputError("At least one replacement car is required")
        if settings["km2yearsConvFactor"] <= 0:
            raise AnalysisInputError("Average annual mileage must be greater than zero")
        if settings["ICElifeSpan"] <= 0 or settings["BEVlifeSpan"] <= 0:
            raise AnalysisInputError("Vehicle lifespans must be greater than zero")
        cars = [deepcopy(current_car), *(deepcopy(car) for car in alternatives)]
        settings = dict(settings)
        self._prepare_cars(cars, settings)
        result = self._compute_histories(cars, settings)
        self._compute_table_metrics(result)
        return result

    def _prepare_cars(self, cars: list[dict], settings: dict) -> None:
        current_car = cars[0]
        annual_mileage = settings["km2yearsConvFactor"]
        energy_mix = current_car["energyMix"] / 1000
        if current_car["secondHandCarMileage"] and (
            current_car["secondHandCarMileage"] >= current_car["mileage"]
        ):
            raise AnalysisInputError("Current mileage must exceed its second-hand starting mileage")

        if settings["keepLifeSpan"]:
            if settings["keepUnits"] == "km":
                settings["keepLifeSpan"] = round(settings["keepLifeSpan"], -3)
            else:
                settings["keepLifeSpan"] = (
                    round(settings["keepLifeSpan"] * annual_mileage, -3) / annual_mileage
                )

        for index, car in enumerate(cars):
            engine_type = car["engineType"]
            default_life = settings["BEVlifeSpan" if engine_type == "BEV" else "ICElifeSpan"]
            if car["secondHandCarMileage"] and car["secondHandCarMileage"] >= default_life:
                raise AnalysisInputError(
                    f"{engine_type} second-hand mileage must be below its vehicle lifespan"
                )
            car["country"] = current_car["country"]
            car["energyMix"] = current_car["energyMix"]

            if index:
                car["keepEOL"] = settings["keepEOL"]
                car["keepLifeSpan"] = settings["keepLifeSpan"]
                car["keepUnits"] = settings["keepUnits"]
                default_life = settings["BEVlifeSpan" if engine_type == "BEV" else "ICElifeSpan"]
                if not car["keepLifeSpan"]:
                    car["keepUnits"] = "km"
                    car["keepLifeSpan"] = default_life
                elif car["keepUnits"] == "years":
                    car["keepLifeSpan"] = min(car["keepLifeSpan"], default_life / annual_mileage)
                else:
                    car["keepLifeSpan"] = min(car["keepLifeSpan"], default_life)

            years_to_kilometers(car, annual_mileage)
            production = car["massValue"] * car["carProductionFootprint"] * 1000
            car["productionEoL"] = production
            high_value = 1
            start_age = 0
            if car["secondHandCar"]:
                start_age = car["secondHandCarAge"]
                high_value = depreciation_curve(start_age, annual_mileage, engine_type)
            low_value = 0
            if car["keepLifeSpan"]:
                low_value = depreciation_curve(
                    start_age + car["keepLifeSpan"], annual_mileage, engine_type
                )
            car["depreciation"] = max(high_value - low_value, 0)
            car["productionEoL"] *= car["depreciation"]

            liters_per_km = (
                car["meanConsumptionLiter"] / 100 if car["meanConsumptionLiter"] else None
            )
            wh_per_km = car["meanConsumptionWh"] * 10 if car["meanConsumptionWh"] else None
            if "Gasoline" in engine_type or "Mild" in engine_type or "Diesel" in engine_type:
                car["usePhaseEmissions"] = (car["WTT"] + car["TTW"]) * liters_per_km
            elif "Plug" in engine_type:
                share = car["drivingShare"]
                car["usePhaseEmissions"] = (car["WTT"] + car["TTW"]) * (
                    1 - share
                ) * liters_per_km + share * wh_per_km * energy_mix
            elif "BEV" in engine_type:
                car["usePhaseEmissions"] = wh_per_km * energy_mix
            else:
                raise AnalysisInputError(f"Unsupported engine type: {engine_type}")

    def _compute_histories(self, cars: list[dict], settings: dict) -> AnalysisResult:
        current_car = cars[0]
        annual_mileage = settings["km2yearsConvFactor"]
        current_used_mileage = current_car["secondHandCarMileage"] or 0
        current_used_age = current_car["secondHandCarAge"] or 0
        analysis_start_km = round(current_used_mileage, -3)
        plot_span = round(
            max(settings["ICElifeSpan"], settings["BEVlifeSpan"])
            * self.assumptions["plot_span_factor"]
            + current_car["mileage"],
            -3,
        )
        plot_x = np.arange(
            analysis_start_km,
            plot_span + 1,
            self.assumptions["plot_step_km"],
        )

        mileage_to_change = current_car["mileage"] - analysis_start_km
        allowed_mileage = (self.assumptions["max_window_years"] - current_used_age) * annual_mileage
        if mileage_to_change >= allowed_mileage:
            raise AnalysisInputError(
                "The current car cannot reach the replacement mileage before the "
                f"{self.assumptions['max_window_years']}-year age limit. "
                "Adjust the mileage, annual mileage, or second-hand car inputs."
            )

        emissions_at_replacement = 0.0
        for index, car in enumerate(cars):
            start_mileage = analysis_start_km if index == 0 else current_car["mileage"]
            x_values = plot_x[plot_x >= start_mileage]
            car["xValues"] = x_values
            emissions = car["usePhaseEmissions"] * (x_values - start_mileage) / 1e6
            used_mileage = car["secondHandCarMileage"] or 0

            growth = self.assumptions[
                "degradation_with_maintenance"
                if settings["maintenance"]
                else "degradation_without_maintenance"
            ]
            multipliers = add_degradation(
                x_values - start_mileage + used_mileage, growth, annual_mileage
            )
            emissions = emissions * multipliers
            car["totalUsePhaseEmissions"] = emissions
            if settings["maintenance"]:
                emissions = add_maintenance(
                    self.data,
                    x_values - start_mileage + used_mileage,
                    emissions,
                    car["depreciation"],
                )
            car["totalUsePhaseEmissionsPlusMaintenance"] = emissions

            if index:
                emissions = emissions + emissions_at_replacement
            emissions = emissions + car["productionEoL"] / 1e6
            if car["engineType"] == "BEV":
                car["batteryReplacementLog"] = battery_replacement_emissions(
                    x_values,
                    start_mileage,
                    car["batteryLifeTime"],
                    car["batteryCapacity"],
                    car["batteryProductionFootprint"],
                    used_mileage,
                )
                emissions += car["batteryReplacementLog"]

            if index == 0:
                cutoff = settings["BEVlifeSpan" if car["engineType"] == "BEV" else "ICElifeSpan"]
            else:
                default_life = settings[
                    "BEVlifeSpan" if car["engineType"] == "BEV" else "ICElifeSpan"
                ]
                cutoff = min(
                    start_mileage + default_life - used_mileage,
                    car["keepLifeSpan"] * annual_mileage + start_mileage,
                )
            car["carLifeSpan"] = cutoff
            car["emissionHystory"] = emissions
            if index == 0:
                replacement_index = int(
                    round((current_car["mileage"] - current_used_mileage) / 1000)
                )
                emissions_at_replacement = emissions[replacement_index]

        max_window_km = (
            self.assumptions["max_window_years"] - current_used_age
        ) * annual_mileage + current_used_mileage
        end_km = min(max_window_km, *(car["carLifeSpan"] for car in cars))
        if end_km <= current_car["mileage"]:
            raise AnalysisInputError(
                "The selected end of usage must be later than the replacement mileage"
            )
        min_km = analysis_start_km - 500
        threshold_mileage = (min_km / 1000, end_km / 1000)
        threshold_age = (
            current_used_age - 0.02,
            (end_km - current_used_mileage) / annual_mileage + current_used_age,
        )
        visible = [0]
        for car in cars:
            visible.extend(
                y
                for x, y in zip(car["xValues"], car["emissionHystory"], strict=True)
                if analysis_start_km <= x <= end_km
            )
        low, high = min(visible), max(visible)
        margin = 0.1 * (high - low) if high > low else 1.0
        return AnalysisResult(
            cars=cars,
            settings=settings,
            analysis_start_km=analysis_start_km,
            analysis_start_years=current_used_age,
            end_km=end_km,
            min_km=min_km,
            y_range=(low, high + margin),
            threshold_mileage=threshold_mileage,
            threshold_age=threshold_age,
            emissions_at_replacement=emissions_at_replacement,
            co2_at_change=0.0,
        )

    def _compute_table_metrics(self, result: AnalysisResult) -> None:
        cars = result.cars
        current = cars[0]
        annual_mileage = result.settings["km2yearsConvFactor"]
        mileage_at_change = current["mileage"]
        year_span = (result.end_km - mileage_at_change) / annual_mileage
        total_year_span = (result.end_km - result.analysis_start_km) / annual_mileage
        result.co2_at_change = interpolate(
            current["xValues"], current["emissionHystory"], mileage_at_change
        )

        for car in cars[1:]:
            car["BEkm"], car["BEco2"] = compute_intersection(
                current["xValues"],
                current["emissionHystory"],
                car["xValues"],
                car["emissionHystory"],
            )
            if car["BEkm"] is not None and car["BEco2"] is not None:
                car["DeltaBEkm"] = car["BEkm"] - mileage_at_change
                car["DeltaBEco2"] = car["BEco2"] - result.co2_at_change
            else:
                car["DeltaBEkm"] = None
                car["DeltaBEco2"] = None

        for index, car in enumerate(cars):
            car["THco2"] = interpolate(car["xValues"], car["emissionHystory"], result.end_km)
            car["DeltaTHco2"] = car["THco2"] - result.co2_at_change
            total_co2 = car["THco2"] if index == 0 else car["DeltaTHco2"]
            period = total_year_span if index == 0 else year_span
            production_co2 = car["productionEoL"] / 1e6
            use_co2 = interpolate(car["xValues"], car["totalUsePhaseEmissions"], result.end_km)
            car["yearlyCo2"] = total_co2 / period
            car["relativeProductionCo2"] = (
                100 * production_co2 * self.assumptions["production_share"] / total_co2
            )
            car["relativeEolCo2"] = (
                100 * production_co2 * self.assumptions["end_of_life_share"] / total_co2
            )
            car["relativeUseCo2"] = 100 * use_co2 / total_co2
            if result.settings["maintenance"]:
                car["relativeMaintenanceCo2"] = (
                    100 * (total_co2 - production_co2 - use_co2) / total_co2
                )
            elif car["engineType"] == "BEV":
                battery_at_end = interpolate(
                    car["xValues"],
                    car["batteryReplacementLog"],
                    result.end_km,
                    kind="nearest",
                )
                car["relativeMaintenanceCo2"] = 100 * battery_at_end / total_co2
            else:
                car["relativeMaintenanceCo2"] = (
                    100 * (total_co2 - production_co2 - use_co2) / total_co2
                )
