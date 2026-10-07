"""Current-vehicle form and state handling."""

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import (
    QGroupBox,
    QMessageBox,
)

from eco_car_advisor.ui.current_car_layout import build_current_car_form
from eco_car_advisor.ui.layout_helpers import set_layout_visible
from eco_car_advisor.ui.vehicle_defaults import (
    apply_vehicle_defaults,
    update_consumption_fields,
)


class CurrentCar(QGroupBox):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.data = parent.data
        self.tooltip_dict = parent.tooltip_dict
        self.carSegments = parent.carSegments
        self.carEngineTypes = parent.carEngineTypes
        self.countries = parent.countries
        build_current_car_form(self)

    def on_batteryLifeTime_modified(self, new_value: str):
        if self.batteryLifeTime_lineEdit.read() != self.batteryLifeTime_lineEdit._defaultValue:
            self.batteryLifeTime_modified = True

    def toggle_panel(self):
        if self.popup_panel.isVisible():
            self.popup_panel.hide()
            self.advancedSettings_button.setText("▼")
        else:
            pos = self.advancedSettings_button.mapToGlobal(
                self.advancedSettings_button.rect().bottomLeft()
            )
            pos += QPoint(0, 10)
            self.popup_panel.move(pos)
            self.popup_panel.show()
            self.advancedSettings_button.setText("▲")

    def closeEvent(self, event):
        """Close the advanced settings panel with the main window."""
        if self.popup_panel.isVisible():
            self.popup_panel.close()
        super().closeEvent(event)

    def state(self):
        """Stores the initial state of all fields when the dialog opens."""
        self.current_state = {}
        for widget in self.editableWidgets:
            state = widget.save()
            self.current_state.update(state)
        return self.current_state

    def update_defaults(self):
        self.set_default_values_and_batteries()
        self.update_energy_mix()

    def update_energy_mix(self):
        country = self.country_comboBox.read()
        if country == "Custom":
            self.energyMix_lineEdit.clear()
            self.energyMix_lineEdit.setReadOnly(False)
            self.energyMix_lineEdit.setStyleSheet("background-color: white;")
        else:
            energyMix = self.data["usePhase"]["EnergyMix"][country] * 1000
            self.energyMix_lineEdit.write(f"{energyMix:.0f}")
            self.energyMix_lineEdit.setReadOnly(True)
            self.energyMix_lineEdit.setStyleSheet("background-color: lightgrey;")

    def set_default_values_and_batteries(self):
        self.set_default_values()
        engineType = self.engineType_comboBox.read()
        if engineType != "BEV":
            self.batteryProductionFootprint_lineEdit.set_compulsory(False)
            self.batteryLifeTime_lineEdit.set_compulsory(False)
        else:
            self.batteryProductionFootprint_lineEdit.write(self.data["batteries"]["kgco2/kWh"])
            self.batteryProductionFootprint_lineEdit.set_compulsory(True)
            self.batteryProductionFootprint_lineEdit.save()
            self.batteryLifeTime_lineEdit.write(
                self.parent.generalOptionsDialog.BEVlifeSpanLineEdit.read()
            )
            self.batteryLifeTime_lineEdit.set_compulsory(True)
            self.batteryLifeTime_lineEdit.save()
            self.batteryLifeTime_modified = False

    def set_default_values(self):
        apply_vehicle_defaults(self, save_battery_capacity=True)

    def update_consumption_fields(self):
        update_consumption_fields(self)

    def toggle_line_edit_secondHandCar(self, state):
        """Show or hide a QLineEdit based on checkbox state."""
        if not state:
            self.secondHandCarMileage_lineEdit.clear()
            self.secondHandCarMileage_lineEdit.setStyleSheet("background-color: lightgrey;")
            self.secondHandCarAge_lineEdit.clear()
            self.secondHandCarAge_lineEdit.setStyleSheet("background-color: lightgrey;")
        else:
            self.secondHandCarMileage_lineEdit.setStyleSheet("")
            self.secondHandCarAge_lineEdit.setStyleSheet("")
        self.secondHandCarMileage_lineEdit.setReadOnly(not state)
        self.secondHandCarMileage_lineEdit.set_compulsory(state)
        self.secondHandCarAge_lineEdit.setReadOnly(not state)
        self.secondHandCarAge_lineEdit.set_compulsory(state)
        set_layout_visible(self.secondHandMileageLine, state)
        set_layout_visible(self.secondHandAgeLine, state)
        self.popup_panel.adjustSize()

    def reset_to_default(self):
        for widget in self.editableWidgets:
            widget.reset_to_default()
            widget.save()
        self.secondHandCarMileage_lineEdit.clear()
        self.secondHandCarMileage_lineEdit.setReadOnly(True)
        self.secondHandCarAge_lineEdit.clear()
        self.secondHandCarAge_lineEdit.setReadOnly(True)
        self.batteryLifeTime_modified = False
        self.update_defaults()

    def read(self):
        self.state()
        exportData = self.current_state.copy()
        exportData["keepUnits"] = "km"
        exportData["mileage"] = round(exportData["mileage"], -3)
        exportData["keepLifeSpan"] = exportData["mileage"]
        return exportData

    def set_tooltips(self):
        for widget in self.editableWidgets:
            variable = getattr(widget, "_variableLabel", None)
            if variable and variable in self.tooltip_dict:
                widget.setToolTip(self.tooltip_dict[variable])

    def validate_current_mileage(self, value):
        if value:
            engineType = self.engineType_comboBox.read()
            maxValue = (
                self.parent.generalOptionsDialog.BEVlifeSpanLineEdit.read()
                if engineType == "BEV"
                else self.parent.generalOptionsDialog.ICElifeSpanLineEdit.read()
            )
            engineTypeLabel = "BEV" if engineType == "BEV" else "ICE"
            if float(value) >= float(maxValue):
                message = f"Current Mileage (km) must be lower than {engineTypeLabel} car life span (km).\nChange the expected life span in the Advanced Analysis Setting."
                QMessageBox.warning(self, "Invalid Input", message)
                self.currentMileage_lineEdit.clear()
                self.currentMileage_lineEdit.update_stored_value("")
                return message
            else:
                return 0
        else:
            return 0
