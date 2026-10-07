"""General analysis settings dialog."""

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from eco_car_advisor.data import load_assumptions
from eco_car_advisor.resources import resource_path
from eco_car_advisor.ui.widgets.numeric_line_edit import NumericLineEdit

DEFAULTS = load_assumptions()
defaultICElifeSpan = DEFAULTS["default_ice_lifespan_km"]
defaultBEVlifeSpan = DEFAULTS["default_bev_lifespan_km"]


class GeneralOptionsDialog(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.tooltip_dict = parent.tooltip_dict
        self.setWindowIcon(QIcon(resource_path("Icons/Options.png")))
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 150)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        labelWidth = 250
        self.analysisSettingGroup = QGroupBox("Analysis settings")
        self.analysisSettingQFormLayout = QFormLayout()
        self.ICElifeSpanLabel = QLabel("ICE car life span (km):")
        self.ICElifeSpanLineEdit = NumericLineEdit(
            "ICElifeSpan",
            text=str(defaultICElifeSpan),
            validateLabel="ICE car life span (km)",
        )
        self.ICElifeSpanLabel.setFixedWidth(labelWidth)
        self.analysisSettingQFormLayout.addRow(self.ICElifeSpanLabel, self.ICElifeSpanLineEdit)
        self.BEVlifeSpanLabel = QLabel("BEV car life span (km):")
        self.BEVlifeSpanLineEdit = NumericLineEdit(
            "BEVlifeSpan",
            text=str(defaultBEVlifeSpan),
            validateLabel="BEV car life span (km)",
        )
        self.BEVlifeSpanLabel.setFixedWidth(labelWidth)
        self.analysisSettingQFormLayout.addRow(self.BEVlifeSpanLabel, self.BEVlifeSpanLineEdit)
        self.analysisSettingGroup.setLayout(self.analysisSettingQFormLayout)
        self.layout.addWidget(self.analysisSettingGroup)
        self.saveLine = QHBoxLayout()
        self.reset_button = QPushButton("Reset")
        self.reset_button.setFixedWidth(100)
        self.reset_button.clicked.connect(self.reset_to_default)
        self.save_button = QPushButton("Save")
        self.save_button.setFixedWidth(100)
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self.validate_and_accept)
        self.saveLine.addStretch()
        self.saveLine.addWidget(self.reset_button)
        self.saveLine.addWidget(self.save_button)
        self.saveLine.addStretch()
        self.layout.addLayout(self.saveLine)
        self.editableWidgets = [self.ICElifeSpanLineEdit, self.BEVlifeSpanLineEdit]
        self.set_tooltips()
        self.state()

    def state(self):
        """Stores the initial state of all fields when the dialog opens."""
        self.current_state = {}
        for widget in self.editableWidgets:
            state = widget.save()
            self.parent.generalSettings.update(state)
            self.current_state.update(state)
        return self.current_state

    def read(self):
        self.state()
        exportData = self.current_state.copy()
        exportData["ICElifeSpan"] = round(exportData["ICElifeSpan"], -3)
        exportData["BEVlifeSpan"] = round(exportData["BEVlifeSpan"], -3)
        return exportData

    def reset_to_default(self):
        for widget in self.editableWidgets:
            widget.reset_to_default()

    def has_changes(self) -> bool:
        """Checks if any field has changed from the saved state."""
        for widget in self.editableWidgets:
            state = widget.state()
            for key, value in state.items():
                if self.current_state.get(key) != value:
                    return True
        return False

    def validate_and_accept(self):
        validated = True
        for widget in self.editableWidgets:
            if hasattr(widget, "validate_numeric_input"):
                if widget.validate_numeric_input():
                    validated = False
                    break
        if validated:
            self.state()
            currentCar = self.parent.currentCarBox
            if currentCar.engineType_comboBox.read() == "BEV":
                if not currentCar.batteryLifeTime_modified:
                    currentCar.batteryLifeTime_lineEdit.write(self.BEVlifeSpanLineEdit.read())
                    currentCar.batteryLifeTime_lineEdit.save()
            for car in self.parent.cars:
                if car.engineType_comboBox.read() == "BEV":
                    if not car.dialog.batteryLifeTime_modified:
                        car.dialog.batteryLifeTime_lineEdit.write(self.BEVlifeSpanLineEdit.read())
                        car.dialog.batteryLifeTime_lineEdit.save()
            self.accept()

    def closeEvent(self, event):
        """Resets values only if changes were made."""
        if self.has_changes():
            self.reset_to_previous_state()
        event.accept()

    def reset_to_previous_state(self):
        """Resets all fields to their previously saved values."""
        for widget in self.editableWidgets:
            widget.restore_storedValue()

    def set_tooltips(self):
        for widget in self.editableWidgets:
            variable = getattr(widget, "_variableLabel", None)
            if variable and variable in self.tooltip_dict:
                widget.setToolTip(self.tooltip_dict[variable])
