# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 08:33:45 2025

@author: lucac
"""

from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox, QFormLayout, QDialog
)
from PySide6.QtGui import QIcon
from src.Utilities import resource_path

from src.BaseClasses.customLineEdit import myQLineEdit


defaultICElifeSpan = 200000
defaultBEVlifeSpan = 200000
defaultKm2YearsConvFactor = 12000


class GeneralOptionsDialog(QDialog):
    def __init__(self, parent):

        super().__init__()
        self.parent = parent
        self.tooltip_dict = parent.tooltip_dict

        self.setWindowIcon(QIcon(resource_path(r"Icons/Options.png")))
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 150)  # Adjust size as needed

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # -------------------------------------------------------------------------------------#
        # ANALYSIS SETTINGS
        # -------------------------------------------------------------------------------------#

        labelWidth = 250

        self.analysisSettingGroup = QGroupBox('Analysis settings')
        self.analysisSettingQFormLayout = QFormLayout()

        # ICE life span
        self.ICElifeSpanLabel = QLabel('ICE car life span (km):')
        self.ICElifeSpanLineEdit = myQLineEdit("ICElifeSpan",
                                               text=str(defaultICElifeSpan),
                                               validateLabel='ICE car life span (km)')
        self.ICElifeSpanLabel.setFixedWidth(labelWidth)

        self.analysisSettingQFormLayout.addRow(self.ICElifeSpanLabel, self.ICElifeSpanLineEdit)

        # BEV life span
        self.BEVlifeSpanLabel = QLabel('BEV car life span (km):')
        self.BEVlifeSpanLineEdit = myQLineEdit("BEVlifeSpan",
                                               text=str(defaultBEVlifeSpan),
                                               validateLabel="BEV car life span (km)")
        self.BEVlifeSpanLabel.setFixedWidth(labelWidth)

        self.analysisSettingQFormLayout.addRow(self.BEVlifeSpanLabel, self.BEVlifeSpanLineEdit)

        # compose layout
        self.analysisSettingGroup.setLayout(self.analysisSettingQFormLayout)
        self.layout.addWidget(self.analysisSettingGroup)

        # -------------------------------------------------------------------------------------#
        # SAVE AND RESET
        # -------------------------------------------------------------------------------------#
        self.saveLine = QHBoxLayout()

        # Reset and Save buttons
        self.reset_button = QPushButton("Reset")
        self.reset_button.setFixedWidth(100)
        self.reset_button.clicked.connect(self.reset_to_default)  # Close dialog when clicked
        self.save_button = QPushButton("Save")
        self.save_button.setFixedWidth(100)
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self.validate_and_accept)  # Close dialog when clicked

        self.saveLine.addStretch()
        self.saveLine.addWidget(self.reset_button)
        self.saveLine.addWidget(self.save_button)
        self.saveLine.addStretch()

        self.layout.addLayout(self.saveLine)

        self.editableWidgets = [
            self.ICElifeSpanLineEdit,
            self.BEVlifeSpanLineEdit,
        ]

        self.set_tooltips()
        # save starting state
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
        exportData["BEVlifeSpan"] = round(exportData["ICElifeSpan"], -3)

        return exportData

    def reset_to_default(self):

        # Reset all widgets to their declared defaults
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
            if hasattr(widget, 'validate_numeric_input'):
                if widget.validate_numeric_input():
                    validated = False
                    break

        if validated:
            self.state()

            # Update battery lifetime of the current car
            currentCar = self.parent.currentCarBox
            if currentCar.engineType_comboBox.read() == 'BEV':
                if not currentCar.batteryLifeTime_modified:
                    currentCar.batteryLifeTime_lineEdit.write(
                        self.BEVlifeSpanLineEdit.read())
                    currentCar.batteryLifeTime_lineEdit.save()

            # Update new cars
            for car in self.parent.cars:
                # Update default battery lifetime
                if car.engineType_comboBox.read() == 'BEV':
                    if not car.dialog.batteryLifeTime_modified:
                        car.dialog.batteryLifeTime_lineEdit.write(
                            self.BEVlifeSpanLineEdit.read())
                        car.dialog.batteryLifeTime_lineEdit.save()

                # Update default Eol
                # if car.dialog.keepEOL_button.read():
                #     if car.engineType_comboBox.read() == 'BEV':
                #         car.dialog.keepEOL_lineEdit.write(self.BEVlifeSpanLineEdit.read())
                #     else:
                #         car.dialog.keepEOL_lineEdit.write(self.ICElifeSpanLineEdit.read())
                #     car.dialog.keepEOL_lineEdit.save()

            self.accept()

    def closeEvent(self, event):
        """Resets values only if changes were made."""
        if self.has_changes():
            self.reset_to_previous_state()  # Reset only if changes were made
        event.accept()  # Allow closing

    def reset_to_previous_state(self):
        """Resets all fields to their previously saved values."""
        for widget in self.editableWidgets:
            widget.restore_storedValue()

    def set_tooltips(self):
        for widget in self.editableWidgets:
            variable = getattr(widget, "_variableLabel", None)
            if variable and variable in self.tooltip_dict:
                widget.setToolTip(self.tooltip_dict[variable])
