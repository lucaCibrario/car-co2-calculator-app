"""Shared workbook defaults and field state for vehicle forms."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class VehicleDefaults:
    """Workbook and assumption values for one engine and vehicle segment."""

    engine_type: str
    consumption_liters_per_km: float
    consumption_wh_per_km: float
    mass_kg: float
    production_kg_per_kg: float
    electric_driving_share: float | None
    fuel_wtt: float | None
    fuel_ttw: float | None
    battery_capacity_kwh: float | None

    @classmethod
    def from_data(cls, data: dict, segment: str, engine_type: str) -> "VehicleDefaults":
        fuel = None
        if engine_type != "BEV":
            fuel_name = "Diesel" if "Diesel" in engine_type else "Gasoline"
            fuel = data["usePhase"][fuel_name]
        return cls(
            engine_type=engine_type,
            consumption_liters_per_km=data["usePhase"]["consumptionICE"].at[engine_type, segment],
            consumption_wh_per_km=data["usePhase"]["consumptionBEV"].at[engine_type, segment],
            mass_kg=data["productionEoL"]["defaultMass"].at[engine_type, segment],
            production_kg_per_kg=data["productionEoL"]["co2/kg"].at[engine_type, segment],
            electric_driving_share=(
                data["usePhase"]["DrivingShare"][segment]
                if engine_type == "Plug-in Hybrid"
                else None
            ),
            fuel_wtt=fuel["WTT"] if fuel else None,
            fuel_ttw=fuel["TTW"] if fuel else None,
            battery_capacity_kwh=(
                data["batteries"]["capacity"].at[engine_type, segment]
                if engine_type == "BEV"
                else None
            ),
        )


def _set_read_only(field, read_only: bool) -> None:
    field.setReadOnly(read_only)
    field.setStyleSheet("background-color: lightgrey;" if read_only else "background-color: white;")


def update_consumption_fields(form) -> None:
    """Enable the fuel and electricity fields used by the selected engine."""
    engine_type = form.engineType_comboBox.read()
    uses_fuel = engine_type != "BEV"
    uses_electricity = engine_type in {"BEV", "Plug-in Hybrid"}
    _set_read_only(form.mean_consumption_liter, not uses_fuel)
    _set_read_only(form.mean_consumption_Wh, not uses_electricity)


def apply_vehicle_defaults(form, *, save_battery_capacity: bool) -> None:
    """Apply matching defaults to either current- or replacement-car form."""
    defaults = VehicleDefaults.from_data(
        form.data, form.segments_comboBox.read(), form.engineType_comboBox.read()
    )
    share_field = form.drivingShare_lineEdit
    if defaults.electric_driving_share is None:
        share_field.set_compulsory(False)
        _set_read_only(share_field, True)
        share_field.write("")
    else:
        share = f"{defaults.electric_driving_share:.2f}"
        share_field.set_compulsory(True)
        _set_read_only(share_field, False)
        share_field.write(share)
        share_field.update_stored_value(share)

    fuel_field = form.mean_consumption_liter
    if np.isnan(defaults.consumption_liters_per_km):
        fuel_field.update_stored_value("")
        fuel_field.set_compulsory(False)
        fuel_field.write("")
    else:
        value = f"{defaults.consumption_liters_per_km * 100:.1f}"
        fuel_field.update_stored_value(value)
        fuel_field.set_compulsory(True)
        fuel_field.write(value)

    electricity_field = form.mean_consumption_Wh
    if np.isnan(defaults.consumption_wh_per_km):
        electricity_field.update_stored_value("")
        electricity_field.set_compulsory(False)
        electricity_field.write("")
    else:
        value = f"{defaults.consumption_wh_per_km / 10:.1f}"
        electricity_field.update_stored_value(value)
        electricity_field.set_compulsory(True)
        electricity_field.write(value)

    mass = f"{defaults.mass_kg:.0f}"
    form.mass_lineEdit.write(mass)
    form.mass_lineEdit.update_stored_value(mass)
    form.mass_lineEdit.set_compulsory(True)

    production = f"{defaults.production_kg_per_kg:.1f}"
    form.carProductionFootprint_lineEdit.write(production)
    form.carProductionFootprint_lineEdit.update_stored_value(production)
    form.carProductionFootprint_lineEdit.set_compulsory(True)

    if defaults.engine_type == "BEV":
        for field in (form.WTT_lineEdit, form.TTW_lineEdit):
            field.set_compulsory(False)
            _set_read_only(field, True)
            field.write("")
        form.capacity_lineEdit.write(defaults.battery_capacity_kwh)
        form.capacity_lineEdit.set_compulsory(True)
        if save_battery_capacity:
            form.capacity_lineEdit.save()
    else:
        for field, value in (
            (form.WTT_lineEdit, defaults.fuel_wtt),
            (form.TTW_lineEdit, defaults.fuel_ttw),
        ):
            text = f"{value:.0f}"
            field.write(text)
            field.update_stored_value(text)
            field.set_compulsory(True)
            _set_read_only(field, False)
        form.capacity_lineEdit.set_compulsory(False)

    battery_group = getattr(form, "batteryData_groupBox", None)
    if battery_group is None:
        battery_group = form.batterySettings_groupBox
    battery_group.setVisible(defaults.engine_type == "BEV")
    if hasattr(form, "popup_panel"):
        form.popup_panel.adjustSize()
    else:
        form.adjustSize()
    update_consumption_fields(form)
