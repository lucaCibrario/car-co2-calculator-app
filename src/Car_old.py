# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QWidget, QLabel, QComboBox, QLineEdit,
    QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox,
    QTableWidgetItem, QHeaderView, QSpacerItem, QSizePolicy, QCheckBox,
    QDialog, QMessageBox
)
from PySide6.QtGui import QIcon

import src
from src.Utilities import resource_path
import numpy as np


class Car(QWidget):
    def __init__(self, carSegments, carEngineTypes, parent=None):
        super().__init__()

        self.parent = parent
        self.data = parent.data

        self.carSegments = carSegments
        self.carEngineTypes = carEngineTypes

        self.car_layout = QVBoxLayout()
        self.setLayout(self.car_layout)

        self.input_group = QGroupBox()
        self.verticalBox = QVBoxLayout()
        self.firstLine = QHBoxLayout()
        self.secondLine = QHBoxLayout()
        self.thirdLine = QHBoxLayout()

        self.car_segment = QComboBox()
        self.car_segment.addItems(carSegments)

        self.car_engine_type = QComboBox()
        self.car_engine_type.addItems(carEngineTypes)

        # First Line
        self.remove_button = QPushButton()
        self.remove_button.setIcon(QIcon(resource_path(r"Icons/Minus.png")))
        self.remove_button.setFixedSize(32, 32)
        self.remove_button.clicked.connect(self.remove_car)

        # Second Line
        self.optionsButton = QPushButton()
        self.optionsButton.setIcon(QIcon(resource_path(r"Icons/Options.png")))
        self.optionsButton.setFixedSize(32, 32)
        self.optionsButton.clicked.connect(self.open_options_dialog)
        self.optionsLabel = QLabel("Configure Car")

        self.firstLine.addWidget(self.car_segment)
        self.firstLine.addWidget(self.car_engine_type)
        self.firstLine.addWidget(self.optionsButton)
        self.firstLine.addWidget(self.remove_button)

        # create layout
        self.verticalBox.addLayout(self.firstLine)
        # self.verticalBox.addLayout(self.secondLine)
        self.input_group.setLayout(self.verticalBox)

        # Add Input Group and New Car Group to the Form Layout
        self.car_layout.addWidget(self.input_group)

        # Options Window
        self.dialog = OptionsDialog(self)

        # self.car_segment.currentIndexChanged.connect(self.dialog.update_segment_engineType)
        # self.car_engine_type.currentIndexChanged.connect(self.dialog.update_segment_engineType)

    def open_options_dialog(self):
        """Opens the options window."""

        if self.dialog.exec(self.car_segment.currentText(), self.car_engine_type.currentText()):
            # Update Car class values if the user presses Save
            self.car_segment.setCurrentText(self.dialog.segmentsComboBox.currentText())
            self.car_engine_type.setCurrentText(self.dialog.engineTypeComboBox.currentText())

    def remove_car(self):
        """Remove a specific car input section."""

        if self.parent:
            self.parent.remove_car(self)

        self.close()

    def get_car_data(self):
        """Extracts the current data from the Car widget."""
        self.dialog.segmentsComboBox.setCurrentText(self.car_segment.currentText())
        self.dialog.engineTypeComboBox.setCurrentText(self.car_engine_type.currentText())

        if self.dialog.has_changes():
            self.dialog.set_default_values()
            self.dialog.store_state()

        return {
            "carSegment": self.car_segment.currentText(),
            "engineType": self.car_engine_type.currentText(),
            **self.dialog.get_options_data()  # Merge main and options data
        }


class OptionsDialog(QDialog):
    """Pop-up window containing additional options."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = parent.data
        self.parent = parent

        self.setWindowTitle("Advanced Car Options")
        self.setWindowIcon(QIcon(resource_path(r"Icons/Options.png")))
        self.setFixedSize(500, 300)  # Adjust size as needed

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.carBaseDataLine = QHBoxLayout()
        self.firstLine = QHBoxLayout()
        self.secondLine = QHBoxLayout()
        self.secondHalfLine = QHBoxLayout()
        self.thirdLine = QHBoxLayout()
        self.fourthLine = QHBoxLayout()
        self.fifthLine = QHBoxLayout()
        self.saveLine = QHBoxLayout()

        buttonWidth = 240

        # Base Data Line (reflected from main window)
        self.segmentsComboBox = QComboBox()
        self.segmentsComboBox.addItems(parent.carSegments)
        self.segmentsComboBox.setCurrentText(self.parent.car_segment.currentText())
        self.segmentsComboBox.currentIndexChanged.connect(self.set_default_values)
        self.segmentsComboBox.setFixedWidth(150)

        self.engineTypeComboBox = QComboBox()
        self.engineTypeComboBox.addItems(parent.carEngineTypes)
        self.engineTypeComboBox.setCurrentText(self.parent.car_engine_type.currentText())
        self.engineTypeComboBox.setFixedWidth(150)
        self.engineTypeComboBox.currentIndexChanged.connect(self.set_default_values)

        self.carBaseDataLine.addStretch()
        self.carBaseDataLine.addWidget(self.segmentsComboBox)
        self.carBaseDataLine.addWidget(self.engineTypeComboBox)
        self.carBaseDataLine.addStretch()

        # First Line - second hand car
        self.secondHandCar_label = QLabel("Second-hand Car Mileage (km):")
        self.secondHandCar_button = QCheckBox()
        self.secondHandCar_button.setChecked(False)
        self.secondHandCar_lineEdit = QLineEdit()
        self.secondHandCar_lineEdit.setPlaceholderText("Enter current mileage")
        self.secondHandCar_lineEdit.setReadOnly(True)
        self.secondHandCar_lineEdit.setStyleSheet("background-color: lightgrey;")
        self.secondHandCar_label.setFixedWidth(buttonWidth)
        self.secondHandCar_button.stateChanged.connect(self.toggle_line_edit_secondHand)

        self.firstLine.addWidget(self.secondHandCar_label)
        self.firstLine.addWidget(self.secondHandCar_button)
        self.firstLine.addWidget(self.secondHandCar_lineEdit)

        # Second line - Keep until EOL
        # self.EOL_user_edited = False
        self.keepEOL_label = QLabel("Intended end-of-usage (mileage/age):")
        self.keepEOL_button = QCheckBox("Keep until EoL")
        self.keepEOL_button.setChecked(True)
        self.keepEOL_label.setFixedWidth(buttonWidth)
        self.keepEOL_button.stateChanged.connect(self.toggle_line_edit_keepEOL)

        self.keepEOL_emptyLabel = QLabel()
        self.keepEOL_emptyLabel.setFixedWidth(buttonWidth)
        self.keepEOL_lineEdit = QLineEdit()
        self.keepEOL_lineEdit.setPlaceholderText("Enter estimated life time")
        # self.keepEOL_lineEdit.textEdited.connect(lambda _: setattr(self, 'EOL_user_edited', True))
        self.keepEOL_lineEdit.setReadOnly(True)
        self.keepEOL_lineEdit.setStyleSheet("background-color: lightgrey;")

        self.keepEOL_comboBox = QComboBox()
        self.keepEOL_comboBox.addItems(['km', 'years'])
        self.keepEOL_comboBox.setEnabled(False)
        self.keepEOL_comboBox.setFixedWidth(70)
        self.keepEOL_comboBox.setFixedHeight(parent.parent.comboBoxHeight)

        self.secondLine.addWidget(self.keepEOL_label)
        self.secondLine.addWidget(self.keepEOL_button)

        self.secondHalfLine.addWidget(self.keepEOL_emptyLabel)
        self.secondHalfLine.addWidget(self.keepEOL_lineEdit)
        self.secondHalfLine.addWidget(self.keepEOL_comboBox)

        # Third line - user defined vehicle mass
        self.mass_button = QLabel("Car Mass (kg):")
        self.mass_lineEdit = QLineEdit()
        self.mass_lineEdit.setPlaceholderText("Enter car mass (kg)")
        self.mass_button.setFixedWidth(buttonWidth)

        self.thirdLine.addWidget(self.mass_button)
        self.thirdLine.addWidget(self.mass_lineEdit)

        # User input Consumption (fourth and fifth lines)
        self.mean_consumption_liter = QLineEdit()
        self.mean_consumption_Wh = QLineEdit()
        self.mean_consumption_label = QLabel("ICE Consumption (l/100km):")
        self.mean_consumption_label.setFixedWidth(buttonWidth)
        self.mean_consumption_emptyLabel = QLabel("EM Consumption (kWh/100km):")
        self.mean_consumption_emptyLabel.setFixedWidth(buttonWidth)

        self.fourthLine.addWidget(self.mean_consumption_label)
        self.fourthLine.addWidget(self.mean_consumption_liter)
        self.fifthLine.addWidget(self.mean_consumption_emptyLabel)
        self.fifthLine.addWidget(self.mean_consumption_Wh)

        # Reset and Save buttons
        self.reset_button = QPushButton("Reset")
        self.reset_button.setFixedWidth(100)
        self.reset_button.clicked.connect(self.reset_to_defaults)  # Close dialog when clicked
        self.save_button = QPushButton("Save")
        self.save_button.setFixedWidth(100)
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self.validate_and_accept)  # Close dialog when clicked

        self.saveLine.addStretch()
        self.saveLine.addWidget(self.reset_button)
        self.saveLine.addWidget(self.save_button)
        self.saveLine.addStretch()

        # Create final layaout
        self.layout.addLayout(self.carBaseDataLine)
        self.layout.addLayout(self.firstLine)
        self.layout.addLayout(self.secondLine)
        self.layout.addLayout(self.secondHalfLine)
        self.layout.addLayout(self.thirdLine)
        self.layout.addLayout(self.fourthLine)
        self.layout.addLayout(self.fifthLine)
        self.layout.addLayout(self.saveLine)

        # Activate the consumption fields corresponding to the selected engine type
        self.set_default_values()

        # Store the initial state when the dialog opens
        self.store_state()
        self.initial_state = self.current_state.copy()

    # def update_segment_engineType(self):
    #     segment = self.parent.car_segment.currentText()
    #     engineType = self.parent.car_engine_type.currentText()

    #     self.segmentsComboBox.setCurrentText(segment)
    #     self.engineTypeComboBox.setCurrentText(engineType)

    #     self.set_default_values()
    #     self.store_state()

    def set_default_values(self):
        carSegment = self.segmentsComboBox.currentText()
        engineType = self.engineTypeComboBox.currentText()

        consumptionICE = self.data['usePhase']['consumptionICE'].at[engineType, carSegment]
        consumptionBEV = self.data['usePhase']['consumptionBEV'].at[engineType, carSegment]
        mass = self.data['productionEoL']['defaultMass'].at[engineType, carSegment]

        if not np.isnan(consumptionICE):
            self.mean_consumption_liter.setText(f"{consumptionICE*100:.1f}")
        else:
            self.mean_consumption_liter.setText('')

        if not np.isnan(consumptionBEV):
            self.mean_consumption_Wh.setText(f"{consumptionBEV/10:.1f}")
        else:
            self.mean_consumption_Wh.setText('')

        self.mass_lineEdit.setText(f"{mass:.0f}")

        if self.keepEOL_button.isChecked():
            if engineType == 'BEV':
                self.keepEOL_lineEdit.setText(
                    f"{self.parent.parent.generalSettings['BEVlifeSpan']:.0f}")
            else:
                self.keepEOL_lineEdit.setText(
                    f"{self.parent.parent.generalSettings['ICElifeSpan']:.0f}")

        self.update_consumption_fields()

    def on_exec_start(self, segment, engineType):
        """Function that runs when the dialog is executed via exec()"""
        self.segmentsComboBox.setCurrentText(segment)
        self.engineTypeComboBox.setCurrentText(engineType)

        if self.has_changes():
            self.set_default_values()
            self.store_state()

    def exec(self, segment, engineType):
        """Override exec() to trigger a function before execution"""
        self.on_exec_start(segment, engineType)  # Call the function
        return super().exec()  # Execute the dialog as usual

    def toggle_line_edit_secondHand(self, state):
        """Enable or disable mileage input based on checkbox state."""
        if not state:
            self.secondHandCar_lineEdit.clear()
            self.secondHandCar_lineEdit.setPlaceholderText("Enter current mileage")
            self.secondHandCar_lineEdit.setStyleSheet("background-color: lightgrey;")
        else:
            self.secondHandCar_lineEdit.setStyleSheet("")

        self.secondHandCar_lineEdit.setReadOnly(not state)

    def toggle_line_edit_keepEOL(self, state):
        """Enable or disable mileage input based on checkbox state."""
        if state:
            self.keepEOL_lineEdit.clear()
            # self.keepEOL_lineEdit.setPlaceholderText("Enter extimated life time")
            self.keepEOL_lineEdit.setStyleSheet("background-color: lightgrey;")

            if self.engineTypeComboBox.currentText() == 'BEV':
                self.keepEOL_lineEdit.setText(
                    f"{self.parent.parent.generalSettings['BEVlifeSpan']:.0f}")
            else:
                self.keepEOL_lineEdit.setText(
                    f"{self.parent.parent.generalSettings['ICElifeSpan']:.0f}")
        else:
            self.keepEOL_lineEdit.setStyleSheet("")
            self.keepEOL_lineEdit.setText('')

        self.keepEOL_lineEdit.setReadOnly(state)
        self.keepEOL_comboBox.setEnabled(not state)

    # def toggle_line_edit_keepEOL(self, state):
    #     """Enable or disable mileage input based on checkbox state."""
    #     if state:
    #         self.keepEOL_lineEdit.clear()
    #         self.keepEOL_lineEdit.setPlaceholderText("Enter estimated life time")
    #         self.keepEOL_lineEdit.setStyleSheet("background-color: lightgrey;")
    #     else:
    #         self.keepEOL_lineEdit.setStyleSheet("")

    #     self.keepEOL_lineEdit.setReadOnly(state)

    def toggle_line_edit_mass(self, state):
        """Enable or disable mileage input based on checkbox state."""
        if not state:
            self.mass_lineEdit.clear()
            self.mass_lineEdit.setPlaceholderText("Enter car mass (kg)")
            self.mass_lineEdit.setStyleSheet("background-color: lightgrey;")
        else:
            self.mass_lineEdit.setStyleSheet("")

        self.mass_lineEdit.setReadOnly(not state)

    def store_state(self):
        """Stores the initial state of all fields when the dialog opens."""
        self.current_state = {
            # "EOLuserEdited": self.EOL_user_edited,
            "carSegment": self.segmentsComboBox.currentText(),
            "engineType": self.engineTypeComboBox.currentText(),
            "secondHandCar": self.secondHandCar_button.isChecked(),
            "secondHandCarMileage": self.secondHandCar_lineEdit.text(),
            "keepEOL": self.keepEOL_button.isChecked(),
            "keepLifeSpan": self.keepEOL_lineEdit.text(),
            "keepUnits": self.keepEOL_comboBox.currentText(),
            "massValue": self.mass_lineEdit.text(),
            "meanConsumptionLiter": self.mean_consumption_liter.text(),
            "meanConsumptionWh": self.mean_consumption_Wh.text(),
        }

    def has_changes(self):
        """Checks if any field has changed from the initial state."""
        return any([
            # self.current_state["EOLuserEdited"] != self.EOL_user_edited,
            self.current_state["carSegment"] != self.segmentsComboBox.currentText(),
            self.current_state["engineType"] != self.engineTypeComboBox.currentText(),
            self.current_state["secondHandCar"] != self.secondHandCar_button.isChecked(),
            self.current_state["secondHandCarMileage"] != self.secondHandCar_lineEdit.text(),
            self.current_state["keepEOL"] != self.keepEOL_button.isChecked(),
            self.current_state["keepLifeSpan"] != self.keepEOL_lineEdit.text(),
            self.current_state["keepUnits"] != self.keepEOL_comboBox.currentText(),
            self.current_state["massValue"] != self.mass_lineEdit.text(),
            self.current_state["meanConsumptionLiter"] != self.mean_consumption_liter.text(),
            self.current_state["meanConsumptionWh"] != self.mean_consumption_Wh.text(),
        ])

    def closeEvent(self, event):
        """Resets values only if changes were made."""
        if self.has_changes():
            self.reset_to_previous_state()  # Reset only if changes were made
        event.accept()  # Allow closing

    def reset_to_previous_state(self):
        """Resets all fields to their default values."""
        # self.EOL_user_edited = self.current_state["EOLuserEdited"]
        self.segmentsComboBox.setCurrentText(self.current_state["carSegment"])
        self.engineTypeComboBox.setCurrentText(self.current_state["engineType"])
        self.secondHandCar_button.setChecked(self.current_state["secondHandCar"])
        self.keepEOL_button.setChecked(self.current_state["keepEOL"])
        self.secondHandCar_lineEdit.setText(self.current_state["secondHandCarMileage"])
        self.keepEOL_lineEdit.setText(self.current_state["keepLifeSpan"])
        self.mass_lineEdit.setText(self.current_state["massValue"])
        self.keepEOL_comboBox.setCurrentText(self.current_state["keepUnits"])
        self.mean_consumption_liter.setText(self.current_state["meanConsumptionLiter"])
        self.mean_consumption_Wh.setText(self.current_state["meanConsumptionWh"])

    def reset_to_defaults(self):
        """Resets all fields to their default values."""
        self.segmentsComboBox.setCurrentText(self.initial_state["carSegment"])
        self.engineTypeComboBox.setCurrentText(self.initial_state["engineType"])
        self.secondHandCar_button.setChecked(self.initial_state["secondHandCar"])
        self.keepEOL_button.setChecked(self.initial_state["keepEOL"])
        self.secondHandCar_lineEdit.clear()
        self.secondHandCar_lineEdit.setReadOnly(True)
        self.keepEOL_lineEdit.setText(f"{self.parent.parent.generalSettings['ICElifeSpan']:.0f}")
        self.keepEOL_lineEdit.setReadOnly(True)
        self.keepEOL_comboBox.setEnabled(False)
        self.mass_lineEdit.clear()
        self.keepEOL_comboBox.setCurrentText(self.initial_state["keepUnits"])  # Default to 'km'
        self.mean_consumption_liter.clear()
        self.mean_consumption_Wh.clear()
        self.EOL_user_edited = False

        self.set_default_values()

    def validate_and_accept(self):
        """Validate inputs before accepting the dialog."""
        errors = []

        # Get selected engine type
        selected_engine = self.engineTypeComboBox.currentText()

        # Define categories
        liter_only = {"Gasoline (Euro 4)", "Gasoline (Euro 5)", "Gasoline (Euro 6)",
                      "Diesel (Euro 4)", "Diesel (Euro 5)", "Diesel (Euro 6)",
                      "Mild/Full Hybrid"}

        wh_only = {"BEV"}

        both_required = {"Plug-in Hybrid"}

        carSegment = self.segmentsComboBox.currentText()
        engineType = self.engineTypeComboBox.currentText()

        consumptionICE = self.data['usePhase']['consumptionICE'].at[engineType, carSegment]
        consumptionBEV = self.data['usePhase']['consumptionBEV'].at[engineType, carSegment]
        mass = self.data['productionEoL']['defaultMass'].at[engineType, carSegment]

        # Validate based on engine type
        if selected_engine in liter_only:
            error = src.Utilities.validate_numeric_input(
                self.mean_consumption_liter, "ICE mean consumption (l/100km)", compulsory=False)
            if error:
                errors.append(error)
                if not np.isnan(consumptionICE):
                    self.mean_consumption_liter.setText(f"{consumptionICE*100:.1f}")
                else:
                    self.mean_consumption_liter.setText('')

        elif selected_engine in wh_only:
            error = src.Utilities.validate_numeric_input(
                self.mean_consumption_Wh, "EM mean consumption (kWh/100km)", compulsory=False)
            if error:
                errors.append(error)
                if not np.isnan(consumptionBEV):
                    self.mean_consumption_Wh.setText(f"{consumptionBEV/10:.1f}")
                else:
                    self.mean_consumption_Wh.setText('')

        elif selected_engine in both_required:
            liter_text = self.mean_consumption_liter.text().strip()
            wh_text = self.mean_consumption_Wh.text().strip()

            if liter_text and not wh_text:
                errors.append(
                    "If you enter ICE consumption (l/100km), you must also enter EM consumption (kWh/100km).")
                if not np.isnan(consumptionICE):
                    self.mean_consumption_liter.setText(f"{consumptionICE*100:.1f}")
                else:
                    self.mean_consumption_liter.setText('')
            if wh_text and not liter_text:
                errors.append(
                    "If you enter EM consumption (kWh/100km), you must also enter ICE consumption (l/100km).")
                if not np.isnan(consumptionBEV):
                    self.mean_consumption_Wh.setText(f"{consumptionBEV/10:.1f}")
                else:
                    self.mean_consumption_Wh.setText('')

            # Validate both fields if they are filled
            if liter_text:
                error = src.Utilities.validate_numeric_input(
                    self.mean_consumption_liter, "ICE mean consumption (l/100km)")
                if error:
                    errors.append(error)
                    if not np.isnan(consumptionICE):
                        self.mean_consumption_liter.setText(f"{consumptionICE*100:.1f}")
                    else:
                        self.mean_consumption_liter.setText('')

            if wh_text:
                error = src.Utilities.validate_numeric_input(
                    self.mean_consumption_Wh, "EM mean consumption (kWh/100km)")
                if error:
                    errors.append(error)
                    if not np.isnan(consumptionBEV):
                        self.mean_consumption_Wh.setText(f"{consumptionBEV/10:.1f}")
                    else:
                        self.mean_consumption_Wh.setText('')

        if self.secondHandCar_button.isChecked():
            error = src.Utilities.validate_numeric_input(
                self.secondHandCar_lineEdit, "Current mileage")
            if error:
                errors.append(error)

        # validate Estimated EOL
        if self.engineTypeComboBox.currentText() == 'BEV':
            setText = f"{self.parent.parent.generalSettings['BEVlifeSpan']:.0f}"
        else:
            setText = f"{self.parent.parent.generalSettings['ICElifeSpan']:.0f}"

        error = src.Utilities.validate_numeric_input(
            self.keepEOL_lineEdit, "Intended end-of-usage")
        if error:
            # self.EOL_user_edited = False
            errors.append(error)

        # if self.engineTypeComboBox.currentText() == 'BEV':
        #     if float(self.keepEOL_lineEdit.text()) == self.parent.parent.generalSettings['BEVlifeSpan']:
        #         self.EOL_user_edited = False
        # else:
        #     if float(self.keepEOL_lineEdit.text()) == self.parent.parent.generalSettings['ICElifeSpan']:
        #         self.EOL_user_edited = False

        # Validate Car Mass
        error = src.Utilities.validate_numeric_input(
            self.mass_lineEdit, "Car mass (kg)")
        if error:
            errors.append(error)
            self.mass_lineEdit.setText(f"{mass:.0f}")

        if errors:
            errorMessageBox = QMessageBox.warning(self, "Invalid Input", "\n".join(errors))
        else:
            self.store_state()
            self.accept()  # Close dialog if no errors

    def update_consumption_fields(self):
        """Enables/disables consumption fields based on selected engine type and updates background color."""
        selected_engine = self.engineTypeComboBox.currentText()

        # Define categories
        liter_only = {"Gasoline (Euro 4)", "Gasoline (Euro 5)", "Gasoline (Euro 6)",
                      "Diesel (Euro 4)", "Diesel (Euro 5)", "Diesel (Euro 6)",
                      "Mild/Full Hybrid"}

        wh_only = {"BEV"}  # Only battery-electric vehicles use kWh

        both_enabled = {"Plug-in Hybrid"}  # Plug-in Hybrid uses both fuel & electricity

        # Enable/Disable fields and update styles
        if selected_engine in liter_only:
            self.mean_consumption_liter.setReadOnly(False)  # Enable
            self.mean_consumption_liter.setStyleSheet(
                "background-color: white;")  # Editable -> White
            self.mean_consumption_Wh.setReadOnly(True)  # Disable
            self.mean_consumption_Wh.setStyleSheet(
                "background-color: lightgrey;")  # Disabled -> Light Grey
            # self.mean_consumption_Wh.clear()  # Clear to avoid wrong values
        elif selected_engine in wh_only:
            self.mean_consumption_liter.setReadOnly(True)  # Disable
            self.mean_consumption_liter.setStyleSheet(
                "background-color: lightgrey;")  # Disabled -> Light Grey
            # self.mean_consumption_liter.clear()  # Clear to avoid wrong values
            self.mean_consumption_Wh.setReadOnly(False)  # Enable
            self.mean_consumption_Wh.setStyleSheet("background-color: white;")  # Editable -> White
        elif selected_engine in both_enabled:
            self.mean_consumption_liter.setReadOnly(False)  # Enable
            self.mean_consumption_liter.setStyleSheet(
                "background-color: white;")  # Editable -> White
            self.mean_consumption_Wh.setReadOnly(False)  # Enable
            self.mean_consumption_Wh.setStyleSheet("background-color: white;")  # Editable -> White
        else:
            self.mean_consumption_liter.setReadOnly(True)  # Disable both
            self.mean_consumption_Wh.setReadOnly(True)
            self.mean_consumption_liter.setStyleSheet(
                "background-color: lightgrey;")  # Disabled -> Light Grey
            self.mean_consumption_Wh.setStyleSheet(
                "background-color: lightgrey;")  # Disabled -> Light Grey
            # self.mean_consumption_liter.clear()
            # self.mean_consumption_Wh.clear()

    def get_options_data(self):
        """Returns the selected options data."""
        return {
            "secondHandCar": self.secondHandCar_button.isChecked(),
            "secondHandCarMileage": float(self.secondHandCar_lineEdit.text()) if self.secondHandCar_button.isChecked() else None,
            # "keepEOL": self.keepEOL_button.isChecked(),
            # if not self.keepEOL_button.isChecked() else None,
            "keepLifeSpan": float(self.keepEOL_lineEdit.text()),
            # if not self.keepEOL_button.isChecked() else None,
            "keepUnits": self.keepEOL_comboBox.currentText(),
            'massValue': float(self.mass_lineEdit.text()),
            "meanConsumptionLiter": float(self.mean_consumption_liter.text())/100 if self.mean_consumption_liter.text() else None,
            "meanConsumptionWh": float(self.mean_consumption_Wh.text())*10 if self.mean_consumption_Wh.text() else None,
        }
