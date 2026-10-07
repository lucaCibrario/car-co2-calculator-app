"""Numerical primitives shared by the analysis pipeline."""

import numpy as np
from scipy.interpolate import interp1d

from eco_car_advisor.data import load_assumptions


def years_to_kilometers(car_data: dict, annual_mileage_km: float) -> dict:
    """Convert the stored usage limit to years after 1,000 km rounding."""
    if "km" in car_data["keepUnits"]:
        car_data["keepLifeSpan"] = round(car_data["keepLifeSpan"], -3) / annual_mileage_km
    else:
        car_data["keepLifeSpan"] = (
            round(car_data["keepLifeSpan"] * annual_mileage_km, -3) / annual_mileage_km
        )
    return car_data


def depreciation_curve(age_years: float, annual_mileage_km: float, engine_type: str) -> float:
    """Return the remaining ownership value fraction used by the model."""
    category = "BEV" if engine_type == "BEV" else "other"
    coefficients = load_assumptions()["depreciation"][category]
    return np.exp(
        -(
            coefficients["age_coefficient"] * age_years
            + coefficients["mileage_coefficient"] * age_years * annual_mileage_km / 1000
        )
    )


def compute_intersection(x1, y1, x2, y2):
    """Find the first crossing of two sampled emission histories."""
    first = interp1d(x1, y1, fill_value="extrapolate", kind="previous")
    second = interp1d(x2, y2, fill_value="extrapolate", kind="previous")
    common_x = np.linspace(max(min(x1), min(x2)), min(max(x1), max(x2)), 1000)
    first_y = first(common_x)
    second_y = second(common_x)
    sign_changes = np.where(np.diff(np.sign(first_y - second_y)))[0]
    if not sign_changes.size:
        return None, None
    index = sign_changes[0]
    return (
        round((common_x[index] + common_x[index + 1]) / 2),
        round((first_y[index] + second_y[index + 1]) / 2),
    )


def interpolate(old_x, old_y, new_x, kind: str = "cubic"):
    """Interpolate or extrapolate a sampled series."""
    return interp1d(old_x, old_y, kind=kind, fill_value="extrapolate")(new_x)


def add_maintenance(data: dict, mileage, emissions, depreciation: float):
    """Add cumulative maintenance emissions using the supplied workbook."""
    maintenance_mileage = data["maintenance"]["Mileage"].values
    maintenance_emissions = data["maintenance"]["Delta Maintenance (tonCO2)"].values
    indices = np.searchsorted(maintenance_mileage, mileage, side="right") - 1
    additions = np.where(indices >= 0, maintenance_emissions[indices], 0.0)
    if len(additions) > 0:
        scaled_start = additions[0] * depreciation
        additions[1:] -= additions[0] - scaled_start
        additions[0] = scaled_start
    return emissions + additions


def add_degradation(mileage, growth_factor: float, annual_mileage_km: float):
    """Return cumulative use-phase growth multipliers."""
    rate = np.log(growth_factor) / annual_mileage_km
    first_mileage = mileage[0]
    first_multiplier = np.exp(rate * first_mileage)
    return first_multiplier * np.exp(rate * (mileage - first_mileage))


def battery_replacement_emissions(
    x_axis_km,
    start_km: float,
    battery_life_km: float,
    capacity_kwh: float,
    footprint_kg_per_kwh: float,
    second_hand_mileage_km: float = 0,
):
    """Return cumulative battery replacement emissions in tonnes CO₂."""
    if battery_life_km <= 0:
        raise ValueError("Battery lifetime must be greater than zero")
    replacements = np.zeros(len(x_axis_km))
    replacement_value = capacity_kwh * footprint_kg_per_kwh / 1000
    battery_life_km = round(battery_life_km, -3)
    if battery_life_km <= 0:
        raise ValueError("Battery lifetime must be at least 500 km")
    next_replacement_km = start_km + battery_life_km - second_hand_mileage_km
    while next_replacement_km <= x_axis_km[-1]:
        index = np.searchsorted(x_axis_km, next_replacement_km)
        if index + 1 < len(x_axis_km):
            replacements[index + 1 :] += replacement_value
        next_replacement_km += battery_life_km
    return replacements
