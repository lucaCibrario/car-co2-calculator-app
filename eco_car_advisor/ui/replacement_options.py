from PySide6.QtWidgets import (
    QDialog,
)

from eco_car_advisor.ui.layout_helpers import set_layout_visible
from eco_car_advisor.ui.replacement_options_layout import build_replacement_options
from eco_car_advisor.ui.vehicle_defaults import (
    apply_vehicle_defaults,
    update_consumption_fields,
)


class OptionsDialog(QDialog):
    """Pop-up window containing additional options."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = parent.data
        self.parent = parent
        self.tooltip_dict = parent.tooltip_dict
        build_replacement_options(self)

    def on_batteryLifeTime_modified(self, new_value: str):
        if self.batteryLifeTime_lineEdit.read() != self.batteryLifeTime_lineEdit._defaultValue:
            self.batteryLifeTime_modified = True

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
                self.parent.parent.generalOptionsDialog.BEVlifeSpanLineEdit.read()
            )
            self.batteryLifeTime_lineEdit.set_compulsory(True)
            self.batteryLifeTime_lineEdit.save()
            self.batteryLifeTime_modified = False

    def set_default_values(self):
        apply_vehicle_defaults(self, save_battery_capacity=False)

    def update_consumption_fields(self):
        update_consumption_fields(self)

    def on_exec_start(self, segment, engineType):
        """Function that runs when the dialog is executed via exec()"""
        self.segments_comboBox.write(segment)
        self.engineType_comboBox.write(engineType)
        if self.has_changes():
            self.set_default_values()
            self.state()

    def exec(self, segment, engineType):
        """Override exec() to trigger a function before execution and adjust position."""
        self.on_exec_start(segment, engineType)
        if self.parent.parent:
            parent_top_left = self.parent.parent.geometry().topLeft()
            parent_center_x = parent_top_left.x() + self.parent.parent.width() // 2
            new_x = parent_center_x - self.width() // 2
            new_y = parent_top_left.y() + 150
            self.move(new_x, new_y)
        return super().exec()

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
        self.adjustSize()

    def state(self):
        """Stores the initial state of all fields when the dialog opens."""
        self.current_state = {}
        for widget in self.editableWidgets:
            state = widget.save()
            self.current_state.update(state)
        return self.current_state

    def has_changes(self) -> bool:
        """Checks if any field has changed from the saved state."""
        for widget in self.editableWidgets:
            state = widget.state()
            for key, value in state.items():
                if self.current_state.get(key) != value:
                    return True
        return False

    def closeEvent(self, event):
        """Resets values only if changes were made."""
        if self.has_changes():
            self.reset_to_previous_state()
        event.accept()

    def reset_to_previous_state(self):
        """Resets all fields to their previously saved values."""
        for widget in self.editableWidgets:
            widget.restore_storedValue()

    def reset_to_defaults(self):
        """Resets all fields to their default (initial) values."""
        for widget in self.editableWidgets:
            widget.reset_to_default()
        self.secondHandCarMileage_lineEdit.clear()
        self.secondHandCarMileage_lineEdit.setReadOnly(True)
        self.secondHandCarAge_lineEdit.clear()
        self.secondHandCarAge_lineEdit.setReadOnly(True)
        self.set_default_values()

    def validate_and_accept(self):
        for widget in self.editableWidgets:
            if hasattr(widget, "validate_numeric_input"):
                if widget.validate_numeric_input():
                    return
        self.state()
        self.accept()

    def set_tooltips(self):
        for widget in self.editableWidgets:
            variable = getattr(widget, "_variableLabel", None)
            if variable and variable in self.tooltip_dict:
                widget.setToolTip(self.tooltip_dict[variable])

    def read(self):
        self.state()
        exportData = self.current_state.copy()
        return exportData
