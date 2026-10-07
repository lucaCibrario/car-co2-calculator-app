# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox, QDialog, QMessageBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from src.Utilities import resource_path, setLayoutVisible
import numpy as np

from src.BaseClasses.customLineEdit import myQLineEdit
from src.BaseClasses.customComboBox import myQComboBox
from src.BaseClasses.customCheckBox import myQCheckBox


class Car(QWidget):
    def __init__(self, carSegments, carEngineTypes, parent=None):
        super().__init__()

        self.parent = parent
        self.data = parent.data
        self.tooltip_dict = parent.tooltip_dict

        self.carSegments = carSegments
        self.carEngineTypes = carEngineTypes

        self.carLayout = QVBoxLayout()
        self.carLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.carLayout)

        self.input_group = QGroupBox()
        self.firstLineLayout = QHBoxLayout()

        # Car number label
        carNumber = len(self.parent.cars) + 1 if self.parent.cars else 1
        self.carNumber_label = QLabel(f'Car {carNumber}:')
        self.carNumber_label.setFixedWidth(45)

        # Combo boxes
        self.segments_comboBox = myQComboBox("carSegment", self.carSegments)
        self.engineType_comboBox = myQComboBox("engineType", self.carEngineTypes, defaultIndex=2)

        # Options Button
        self.optionsButton = QPushButton()
        self.optionsButton.setIcon(QIcon(resource_path(r"Icons/Options.png")))
        self.optionsButton.setToolTip("Click for more setting parameters.")
        self.optionsButton.setFixedSize(32, 32)
        self.optionsButton.clicked.connect(self.open_options_dialog)
        self.optionsLabel = QLabel("Configure Car")

        # Minus Button
        self.remove_button = QPushButton()
        self.remove_button.setIcon(QIcon(resource_path(r"Icons/Minus.png")))
        self.remove_button.setToolTip("Click to remove the car from the analysis.")
        self.remove_button.setFixedSize(32, 32)
        self.remove_button.clicked.connect(self.remove_car)

        # Add widgets to layout
        self.firstLineLayout.addWidget(self.carNumber_label)
        self.firstLineLayout.addWidget(self.segments_comboBox)
        self.firstLineLayout.addWidget(self.engineType_comboBox)
        self.firstLineLayout.addWidget(self.optionsButton)
        self.firstLineLayout.addWidget(self.remove_button)

        # create layout
        self.input_group.setLayout(self.firstLineLayout)

        # Add Input Group and New Car Group to the Form Layout
        self.carLayout.addWidget(self.input_group)

        # Options Window
        self.dialog = OptionsDialog(self)

        self.segments_comboBox.setToolTip(self.tooltip_dict["carSegment"])
        self.engineType_comboBox.setToolTip(self.tooltip_dict["engineType"])

    def open_options_dialog(self):
        """Opens the options window."""

        if self.dialog.exec(self.segments_comboBox.read(), self.engineType_comboBox.read()):
            # Update Car class values if the user presses Save
            self.segments_comboBox.write(self.dialog.segments_comboBox.read())
            self.engineType_comboBox.write(self.dialog.engineType_comboBox.read())

    def remove_car(self):
        """Remove a specific car input section."""

        if self.parent:
            self.parent.remove_car(self)

        self.close()
        self.parent.renumber_cars()

    def read(self):
        """Extracts the current data from the Car widget."""
        self.dialog.segments_comboBox.write(self.segments_comboBox.read())
        self.dialog.engineType_comboBox.write(self.engineType_comboBox.read())

        if self.dialog.has_changes():
            self.dialog.set_default_values()
            self.dialog.state()

        exportData = self.dialog.current_state.copy()
        # exportData["meanConsumptionLiter"] = exportData["meanConsumptionLiter"] / \
        #     100 if exportData["meanConsumptionLiter"] else None
        # exportData["meanConsumptionWh"] = exportData["meanConsumptionWh"] * \
        #     10 if exportData["meanConsumptionWh"] else None

        return exportData


class OptionsDialog(QDialog):
    """Pop-up window containing additional options."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = parent.data
        self.parent = parent
        self.tooltip_dict = parent.tooltip_dict

        self.setWindowTitle("New Car Options")
        self.setWindowIcon(QIcon(resource_path(r"Icons/Options.png")))
        # self.setFixedSize(500, 300)  # Adjust size as needed
        self.setFixedWidth(520)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Definition of the group Boxes
        self.carSettings_groupBox = QGroupBox("Car Settings")
        self.batterySettings_groupBox = QGroupBox("Battery settings")

        # Definition of the layouts
        self.carSettings_layout = QVBoxLayout(self.carSettings_groupBox)
        self.batterySettings_layout = QVBoxLayout(self.batterySettings_groupBox)

        self.carBaseDataLine = QHBoxLayout()
        self.secondHandLine = QHBoxLayout()
        self.secondHandMileageLine = QHBoxLayout()
        self.secondHandAgeLine = QHBoxLayout()
        self.eolLine = QHBoxLayout()
        self.eolLineBis = QHBoxLayout()
        self.massLine = QHBoxLayout()
        self.carProductionFootprintLine = QHBoxLayout()
        self.iceConsumptionLine = QHBoxLayout()
        self.bevConsumptionLine = QHBoxLayout()
        self.drivingShareLine = QHBoxLayout()
        self.batteryCapacityLine = QHBoxLayout()
        self.batteryProductionFootprintLine = QHBoxLayout()
        self.batteryLifeTimeLine = QHBoxLayout()
        self.saveLine = QHBoxLayout()
        self.WTTLine = QHBoxLayout()
        self.TTWLine = QHBoxLayout()

        buttonWidth = 240

        # # -------------------------------------------------------------------------------------#
        # # ADVANCED SETTINGS CECKBOX
        # # -------------------------------------------------------------------------------------#
        # self.advancedSettings_layout = QHBoxLayout()
        # self.advancedSettings_layout.setContentsMargins(5, 5, 0, 0)

        # advancedSettings_label = QLabel("Advanced Settings")
        # self.advancedSettings_checkBox = myQCheckBox()
        # self.advancedSettings_checkBox.clicked.connect(self.toggle_advanced_settings)

        # self.advancedSettings_layout.setAlignment(Qt.AlignLeft)
        # self.advancedSettings_layout.addWidget(self.advancedSettings_checkBox)
        # self.advancedSettings_layout.addWidget(advancedSettings_label)

        # -------------------------------------------------------------------------------------#
        # CAR SETTINGS
        # -------------------------------------------------------------------------------------#

        # Base Data Line (reflected from main window)
        self.segments_comboBox = myQComboBox("carSegment", parent.carSegments)
        self.segments_comboBox.write(self.parent.segments_comboBox.read())
        self.segments_comboBox.currentIndexChanged.connect(self.set_default_values)
        self.segments_comboBox.setFixedWidth(150)

        self.engineType_comboBox = myQComboBox("engineType", parent.carEngineTypes, defaultIndex=2)
        self.engineType_comboBox.write(self.parent.engineType_comboBox.read())
        self.engineType_comboBox.setFixedWidth(150)
        self.engineType_comboBox.currentIndexChanged.connect(self.set_default_values_and_batteries)

        self.carBaseDataLine.setContentsMargins(0, 0, 0, 5)
        self.carBaseDataLine.addStretch()
        self.carBaseDataLine.addWidget(self.segments_comboBox)
        self.carBaseDataLine.addWidget(self.engineType_comboBox)
        self.carBaseDataLine.addStretch()

        # Second hand car Line
        secondHandCar_label = QLabel("Second-hand Car:")
        secondHandCar_label.setFixedWidth(buttonWidth)

        secondHandCarMileage_label = QLabel("Second-hand Car Mileage (km):")
        secondHandCarMileage_label.setFixedWidth(buttonWidth)

        secondHandCarAge_label = QLabel("Second-hand Car Age (years):")
        secondHandCarAge_label.setFixedWidth(buttonWidth)

        self.secondHandCar_button = myQCheckBox(variableLabel="secondHandCar",
                                                defaultValue=False)
        self.secondHandCar_button.stateChanged.connect(self.toggle_line_edit_secondHandCar)

        self.secondHandCarMileage_lineEdit = myQLineEdit("secondHandCarMileage",
                                                         placeHolderText="Enter car mileage",
                                                         validateLabel="Second-hand car mileage (km)",
                                                         compulsory=False)
        self.secondHandCarMileage_lineEdit.setReadOnly(True)
        self.secondHandCarMileage_lineEdit.setStyleSheet("background-color: lightgrey;")

        self.secondHandCarAge_lineEdit = myQLineEdit("secondHandCarAge",
                                                     placeHolderText="Enter car age",
                                                     validateLabel="Second-hand car age (years)",
                                                     compulsory=False)

        self.secondHandCarAge_lineEdit.setReadOnly(True)
        self.secondHandCarAge_lineEdit.setStyleSheet("background-color: lightgrey;")

        self.secondHandLine.addWidget(secondHandCar_label)
        self.secondHandLine.addWidget(self.secondHandCar_button)

        self.secondHandMileageLine.addWidget(secondHandCarMileage_label)
        self.secondHandMileageLine.addWidget(self.secondHandCarMileage_lineEdit)

        self.secondHandAgeLine.addWidget(secondHandCarAge_label)
        self.secondHandAgeLine.addWidget(self.secondHandCarAge_lineEdit)

        setLayoutVisible(self.secondHandMileageLine, False)
        setLayoutVisible(self.secondHandAgeLine, False)

        # # Keep until EOL Line
        # self.keepEOL_label = QLabel("Intended end-of-usage (mileage/age):")

        # self.keepEOL_button = myQCheckBox(variableLabel="keepEOL",
        #                                   text="Keep until EoL",
        #                                   defaultValue=True)
        # self.keepEOL_label.setFixedWidth(buttonWidth)
        # self.keepEOL_button.stateChanged.connect(self.toggle_line_edit_keepEOL)

        # self.keepEOL_emptyLabel = QLabel()
        # self.keepEOL_emptyLabel.setFixedWidth(buttonWidth)

        # self.keepEOL_lineEdit = myQLineEdit("keepLifeSpan",
        #                                     placeHolderText="Enter estimated life time",
        #                                     validateLabel="Intended end-of-usage (km/years)",
        #                                     compulsory=not self.keepEOL_button.read())
        # self.keepEOL_lineEdit.setReadOnly(True)
        # self.keepEOL_lineEdit.setStyleSheet("background-color: lightgrey;")

        # self.keepEOL_comboBox = myQComboBox("keepUnits",
        #                                     items=['km', 'years'],
        #                                     )
        # self.keepEOL_comboBox.setEnabled(False)
        # self.keepEOL_comboBox.setFixedWidth(70)
        # self.keepEOL_comboBox.setFixedHeight(parent.parent.comboBoxHeight)

        # self.eolLine.addWidget(self.keepEOL_label)
        # self.eolLine.addWidget(self.keepEOL_button)

        # self.eolLineBis.addWidget(self.keepEOL_emptyLabel)
        # self.eolLineBis.addWidget(self.keepEOL_lineEdit)
        # self.eolLineBis.addWidget(self.keepEOL_comboBox)

        # Car Mass
        self.mass_button = QLabel("Car Mass (kg):")
        self.mass_button.setFixedWidth(buttonWidth)

        self.mass_lineEdit = myQLineEdit("massValue",
                                         placeHolderText="Enter car mass (kg)",
                                         validateLabel="Car mass (kg)",
                                         compulsory=False)

        self.massLine.addWidget(self.mass_button)
        self.massLine.addWidget(self.mass_lineEdit)

        # Car Production Footprint
        self.carProductionFootprint_label = QLabel("Car Production-EoL Footprint (kgCO₂/kg):")
        self.carProductionFootprint_label.setFixedWidth(buttonWidth)
        self.carProductionFootprint_lineEdit = myQLineEdit("carProductionFootprint",
                                                           validateLabel="Car Production-EoL Footprint (kgCO₂/kg)",
                                                           compulsory=False)

        self.carProductionFootprintLine.addWidget(self.carProductionFootprint_label)
        self.carProductionFootprintLine.addWidget(self.carProductionFootprint_lineEdit)

        # WTT and TTW options
        WTT_label = QLabel("WTT Fuel Footprint (gCO₂/l):")
        WTT_label.setFixedWidth(buttonWidth)
        self.WTT_lineEdit = myQLineEdit("WTT",
                                        validateLabel="WTT Fuel Footprint (gCO₂/l)",
                                        compulsory=False)
        TTW_label = QLabel("TTW Fuel Footprint (gCO₂/l):")
        TTW_label.setFixedWidth(buttonWidth)
        self.TTW_lineEdit = myQLineEdit("TTW",
                                        validateLabel="TTW Fuel Footprint (gCO₂/l)",
                                        compulsory=False)

        self.WTTLine.addWidget(WTT_label)
        self.WTTLine.addWidget(self.WTT_lineEdit)
        self.TTWLine.addWidget(TTW_label)
        self.TTWLine.addWidget(self.TTW_lineEdit)

        # User input Consumption (fourth and fifth lines)
        self.mean_consumption_liter = myQLineEdit("meanConsumptionLiter",
                                                  validateLabel="ICE Consumption (l/100km)",
                                                  compulsory=False)
        self.mean_consumption_Wh = myQLineEdit("meanConsumptionWh",
                                               validateLabel="EM Consumption (kWh/100km)",
                                               compulsory=False)
        self.drivingShare_lineEdit = myQLineEdit("drivingShare",
                                                 validateLabel="Driving Share (Plug-in Hybrid only)",
                                                 compulsory=False,
                                                 upperLimit=1)

        self.mean_consumption_label = QLabel("ICE Consumption (l/100km):")
        self.mean_consumption_label.setFixedWidth(buttonWidth)
        self.mean_consumption_emptyLabel = QLabel("EM Consumption (kWh/100km):")
        self.mean_consumption_emptyLabel.setFixedWidth(buttonWidth)
        self.drivingShare_label = QLabel("Driving Share (Plug-in Hybrid only):")
        self.drivingShare_label.setFixedWidth(buttonWidth)

        self.iceConsumptionLine.addWidget(self.mean_consumption_label)
        self.iceConsumptionLine.addWidget(self.mean_consumption_liter)
        self.bevConsumptionLine.addWidget(self.mean_consumption_emptyLabel)
        self.bevConsumptionLine.addWidget(self.mean_consumption_Wh)
        self.drivingShareLine.addWidget(self.drivingShare_label)
        self.drivingShareLine.addWidget(self.drivingShare_lineEdit)

        # -------------------------------------------------------------------------------------#
        # BATTERY SETTINGS
        # -------------------------------------------------------------------------------------#

        capacity_label = QLabel("Battery Capacity (kWh):")
        capacity_label.setFixedWidth(buttonWidth)
        capacity_label.setFixedWidth(buttonWidth)
        self.capacity_lineEdit = myQLineEdit("batteryCapacity",
                                             placeHolderText='',
                                             validateLabel="Battery Capacity (kWh)",
                                             compulsory=False)

        self.batteryCapacityLine.addWidget(capacity_label)
        self.batteryCapacityLine.addWidget(self.capacity_lineEdit)

        # Battery production footprint
        batteryProductionFootprint_label = QLabel("Battery Production Footprint (kgCO₂/kWh):")
        batteryProductionFootprint_label.setFixedWidth(buttonWidth)
        self.batteryProductionFootprint_lineEdit = myQLineEdit("batteryProductionFootprint",
                                                               text=self.data['batteries']['kgco2/kWh'],
                                                               placeHolderText='',
                                                               validateLabel='Production Footprint (kgCO₂/kWh)',
                                                               compulsory=True)

        self.batteryProductionFootprintLine.addWidget(batteryProductionFootprint_label)
        self.batteryProductionFootprintLine.addWidget(self.batteryProductionFootprint_lineEdit)

        # battery estimated life time
        batteryLifeTime_label = QLabel("Estimated life time (km):")
        batteryLifeTime_label.setFixedWidth(buttonWidth)
        self.batteryLifeTime_lineEdit = myQLineEdit("batteryLifeTime",
                                                    placeHolderText='',
                                                    validateLabel="Estimated life time (km):",
                                                    compulsory=False)
        self.batteryLifeTime_lineEdit.valueChanged.connect(self.on_batteryLifeTime_modified)

        self.batteryLifeTimeLine.addWidget(batteryLifeTime_label)
        self.batteryLifeTimeLine.addWidget(self.batteryLifeTime_lineEdit)
        self.batteryLifeTime_modified = False

        # -------------------------------------------------------------------------------------#
        # SAVE LINE
        # -------------------------------------------------------------------------------------#

        # Reset and Save buttons
        self.reset_button = QPushButton("Reset")
        self.reset_button.setToolTip("Click to reset to default settings.")
        self.reset_button.setFixedWidth(100)
        self.reset_button.clicked.connect(self.reset_to_defaults)  # Close dialog when clicked
        self.save_button = QPushButton("Save")
        self.save_button.setToolTip("Click to save the current settings.")
        self.save_button.setFixedWidth(100)
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self.validate_and_accept)  # Close dialog when clicked

        self.saveLine.addStretch()
        self.saveLine.addWidget(self.reset_button)
        self.saveLine.addWidget(self.save_button)
        self.saveLine.addStretch()
        self.saveLine.setContentsMargins(5, 5, 5, 5)

        # -------------------------------------------------------------------------------------#
        # FINAL LAYOUT
        # -------------------------------------------------------------------------------------#

        # Car Settings - Create final layout
        self.carSettings_layout.addLayout(self.carBaseDataLine)
        # self.carSettings_layout.addLayout(self.eolLine)
        # self.carSettings_layout.addLayout(self.eolLineBis)
        self.carSettings_layout.addLayout(self.secondHandLine)
        self.carSettings_layout.addLayout(self.secondHandMileageLine)
        self.carSettings_layout.addLayout(self.secondHandAgeLine)
        self.carSettings_layout.addLayout(self.iceConsumptionLine)
        self.carSettings_layout.addLayout(self.bevConsumptionLine)
        self.carSettings_layout.addLayout(self.drivingShareLine)
        self.carSettings_layout.addLayout(self.massLine)
        self.carSettings_layout.addLayout(self.carProductionFootprintLine)
        self.carSettings_layout.addLayout(self.WTTLine)
        self.carSettings_layout.addLayout(self.TTWLine)

        # Battery Settings - Create final layout
        self.batterySettings_layout.addLayout(self.batteryCapacityLine)
        self.batterySettings_layout.addLayout(self.batteryProductionFootprintLine)
        self.batterySettings_layout.addLayout(self.batteryLifeTimeLine)

        # Add layouts to the main window
        self.layout.addWidget(self.carSettings_groupBox)
        self.layout.addWidget(self.batterySettings_groupBox)
        # self.layout.addLayout(self.advancedSettings_layout)
        self.layout.addLayout(self.saveLine)

        # store the editable widget for other functions (reset, restore, read)
        self.editableWidgets = [
            self.segments_comboBox,
            self.engineType_comboBox,
            self.secondHandCar_button,
            self.secondHandCarMileage_lineEdit,
            self.secondHandCarAge_lineEdit,
            # self.keepEOL_button,
            # self.keepEOL_lineEdit,
            # self.keepEOL_comboBox,
            self.mass_lineEdit,
            self.carProductionFootprint_lineEdit,
            self.mean_consumption_liter,
            self.mean_consumption_Wh,
            self.drivingShare_lineEdit,
            self.capacity_lineEdit,
            self.batteryProductionFootprint_lineEdit,
            self.batteryLifeTime_lineEdit,
            self.WTT_lineEdit,
            self.TTW_lineEdit
        ]

        # Activate the consumption fields corresponding to the selected engine type
        self.set_tooltips()
        self.set_default_values()
        # self.toggle_advanced_settings()

        # Store the initial state when the dialog opens
        self.state()
        self.initial_state = self.current_state.copy()

    def on_batteryLifeTime_modified(self, new_value: str):
        if self.batteryLifeTime_lineEdit.read() != self.batteryLifeTime_lineEdit._defaultValue:
            self.batteryLifeTime_modified = True

    # def toggle_advanced_settings(self):
    #     advancedSettingsFlag = self.advancedSettings_checkBox.read()

    #     setLayoutVisible(self.carProductionFootprintLine, advancedSettingsFlag)
    #     setLayoutVisible(self.drivingShareLine, advancedSettingsFlag)
    #     setLayoutVisible(self.WTTLine, advancedSettingsFlag)
    #     setLayoutVisible(self.TTWLine, advancedSettingsFlag)
    #     setLayoutVisible(self.iceConsumptionLine, advancedSettingsFlag)
    #     setLayoutVisible(self.bevConsumptionLine, advancedSettingsFlag)
    #     setLayoutVisible(self.massLine, advancedSettingsFlag)
    #     self.batterySettings_groupBox.setVisible(False)
    #     if self.engineType_comboBox.read() == "BEV":
    #         self.batterySettings_groupBox.setVisible(advancedSettingsFlag)

        # self.adjustSize()

    def set_default_values_and_batteries(self):
        self.set_default_values()

        engineType = self.engineType_comboBox.read()

        if engineType != "BEV":
            self.batteryProductionFootprint_lineEdit.set_compulsory(False)
            self.batteryLifeTime_lineEdit.set_compulsory(False)

        else:
            self.batteryProductionFootprint_lineEdit.write(self.data['batteries']['kgco2/kWh'])
            self.batteryProductionFootprint_lineEdit.set_compulsory(True)
            self.batteryProductionFootprint_lineEdit.save()

            self.batteryLifeTime_lineEdit.write(
                self.parent.parent.generalOptionsDialog.BEVlifeSpanLineEdit.read())
            self.batteryLifeTime_lineEdit.set_compulsory(True)
            self.batteryLifeTime_lineEdit.save()
            self.batteryLifeTime_modified = False

    def set_default_values(self):
        carSegment = self.segments_comboBox.read()
        engineType = self.engineType_comboBox.read()

        consumptionICE = self.data['usePhase']['consumptionICE'].at[engineType, carSegment]
        consumptionBEV = self.data['usePhase']['consumptionBEV'].at[engineType, carSegment]
        mass = self.data['productionEoL']['defaultMass'].at[engineType, carSegment]
        carProductionFootprint = self.data['productionEoL']['co2/kg'].at[engineType, carSegment]

        if engineType == "Plug-in Hybrid":
            self.drivingShare_lineEdit.set_compulsory(True)
            self.drivingShare_lineEdit.setReadOnly(False)
            drivingShare = self.data['usePhase']['DrivingShare'][carSegment]
            self.drivingShare_lineEdit.write(f"{drivingShare:.2f}")
            self.drivingShare_lineEdit.setStyleSheet("background-color: white;")
            self.drivingShare_lineEdit.update_stored_value(f"{drivingShare:.2f}")
        else:
            self.drivingShare_lineEdit.set_compulsory(False)
            self.drivingShare_lineEdit.setReadOnly(True)
            self.drivingShare_lineEdit.write('')
            self.drivingShare_lineEdit.setStyleSheet("background-color: lightgrey;")

        if not np.isnan(consumptionICE):
            self.mean_consumption_liter.update_stored_value(f"{consumptionICE*100:.1f}")
            self.mean_consumption_liter.set_compulsory(True)
            self.mean_consumption_liter.write(f"{consumptionICE*100:.1f}")
        else:
            self.mean_consumption_liter.update_stored_value('')
            self.mean_consumption_liter.set_compulsory(False)
            self.mean_consumption_liter.write('')

        if not np.isnan(consumptionBEV):
            self.mean_consumption_Wh.update_stored_value(f"{consumptionBEV/10:.1f}")
            self.mean_consumption_Wh.set_compulsory(True)
            self.mean_consumption_Wh.write(f"{consumptionBEV/10:.1f}")
        else:
            self.mean_consumption_Wh.update_stored_value('')
            self.mean_consumption_Wh.set_compulsory(False)
            self.mean_consumption_Wh.write('')

        self.mass_lineEdit.write(f"{mass:.0f}")
        self.mass_lineEdit.update_stored_value(f"{mass:.0f}")
        self.mass_lineEdit.set_compulsory(True)

        self.carProductionFootprint_lineEdit.write(f"{carProductionFootprint:.1f}")
        self.carProductionFootprint_lineEdit.update_stored_value(f"{carProductionFootprint:.1f}")
        self.carProductionFootprint_lineEdit.set_compulsory(True)

        if engineType != "BEV":
            if "Gasoline" in engineType or "Hybrid" in engineType:
                WTT = self.data['usePhase']['Gasoline']['WTT']
                TTW = self.data['usePhase']['Gasoline']['TTW']
            elif "Diesel" in engineType:
                WTT = self.data['usePhase']['Diesel']['WTT']
                TTW = self.data['usePhase']['Diesel']['TTW']

            self.WTT_lineEdit.write(f"{WTT:.0f}")
            self.WTT_lineEdit.update_stored_value(f"{WTT:.0f}")
            self.WTT_lineEdit.set_compulsory(True)

            self.TTW_lineEdit.write(f"{TTW:.0f}")
            self.TTW_lineEdit.update_stored_value(f"{TTW:.0f}")
            self.TTW_lineEdit.set_compulsory(True)

            self.WTT_lineEdit.setReadOnly(False)  # Enable
            self.WTT_lineEdit.setStyleSheet(
                "background-color: white;")
            self.TTW_lineEdit.setReadOnly(False)  # Enable
            self.TTW_lineEdit.setStyleSheet(
                "background-color: white;")

            self.capacity_lineEdit.set_compulsory(False)

        else:
            self.WTT_lineEdit.set_compulsory(False)
            self.WTT_lineEdit.setReadOnly(True)
            self.WTT_lineEdit.write('')
            self.WTT_lineEdit.setStyleSheet("background-color: lightgrey;")

            self.TTW_lineEdit.set_compulsory(False)
            self.TTW_lineEdit.setReadOnly(True)
            self.TTW_lineEdit.write('')
            self.TTW_lineEdit.setStyleSheet("background-color: lightgrey;")

            self.capacity_lineEdit.write(
                self.data['batteries']['capacity'].at[engineType, carSegment])
            self.capacity_lineEdit.set_compulsory(True)

        # if self.keepEOL_button.read():
        #     if engineType == 'BEV':
        #         self.keepEOL_lineEdit.write(
        #             f"{self.parent.parent.generalSettings['BEVlifeSpan']:.0f}")
        #     else:
        #         self.keepEOL_lineEdit.write(
        #             f"{self.parent.parent.generalSettings['ICElifeSpan']:.0f}")

        self.carProductionFootprint_lineEdit.write(f"{carProductionFootprint:.1f}")
        self.carProductionFootprint_lineEdit.update_stored_value(f"{carProductionFootprint:.1f}")
        self.carProductionFootprint_lineEdit.set_compulsory(True)

        if engineType == "BEV":
            # if self.advancedSettings_checkBox.read():
            self.batterySettings_groupBox.show()
        else:
            self.batterySettings_groupBox.hide()

        self.adjustSize()

        self.update_consumption_fields()

    def update_consumption_fields(self):
        """Enables/disables consumption fields based on selected engine type and updates background color."""
        selected_engine = self.engineType_comboBox.read()

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
        elif selected_engine in wh_only:
            self.mean_consumption_liter.setReadOnly(True)  # Disable
            self.mean_consumption_liter.setStyleSheet(
                "background-color: lightgrey;")  # Disabled -> Light Grey
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

    def on_exec_start(self, segment, engineType):
        """Function that runs when the dialog is executed via exec()"""
        self.segments_comboBox.write(segment)
        self.engineType_comboBox.write(engineType)

        if self.has_changes():
            self.set_default_values()
            self.state()

    # def exec(self, segment, engineType):
    #     """Override exec() to trigger a function before execution"""
    #     self.on_exec_start(segment, engineType)  # Call the function
    #     return super().exec()  # Execute the dialog as usual

    def exec(self, segment, engineType):
        """Override exec() to trigger a function before execution and adjust position."""
        self.on_exec_start(segment, engineType)  # Load initial data

        if self.parent.parent:
            # Get top-left of parent window
            parent_top_left = self.parent.parent.geometry().topLeft()

            # Calculate new position: same horizontal center, but 150px from top
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

        setLayoutVisible(self.secondHandMileageLine, state)
        setLayoutVisible(self.secondHandAgeLine, state)

        self.adjustSize()

    # def toggle_line_edit_keepEOL(self, state):
    #     """Enable or disable mileage input based on checkbox state."""
    #     if state:
    #         self.keepEOL_lineEdit.clear()
    #         self.keepEOL_lineEdit.setStyleSheet("background-color: lightgrey;")

    #         if self.engineType_comboBox.currentText() == 'BEV':
    #             self.keepEOL_lineEdit.write(
    #                 f"{self.parent.parent.generalSettings['BEVlifeSpan']:.0f}")
    #         else:
    #             self.keepEOL_lineEdit.write(
    #                 f"{self.parent.parent.generalSettings['ICElifeSpan']:.0f}")
    #     else:
    #         self.keepEOL_lineEdit.setStyleSheet("")
    #         self.keepEOL_lineEdit.write('')
    #         self.keepEOL_lineEdit.update_stored_value('')

    #     self.keepEOL_lineEdit.setReadOnly(state)
    #     self.keepEOL_lineEdit.set_compulsory(not state)
    #     self.keepEOL_comboBox.setEnabled(not state)

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
            self.reset_to_previous_state()  # Reset only if changes were made
        event.accept()  # Allow closing

    def reset_to_previous_state(self):
        """Resets all fields to their previously saved values."""
        for widget in self.editableWidgets:
            widget.restore_storedValue()

    def reset_to_defaults(self):
        """Resets all fields to their default (initial) values."""

        # Reset all widgets to their declared defaults
        for widget in self.editableWidgets:
            widget.reset_to_default()

        # Manual UI logic that doesn't come from widget defaults
        self.secondHandCarMileage_lineEdit.clear()
        self.secondHandCarMileage_lineEdit.setReadOnly(True)
        self.secondHandCarAge_lineEdit.clear()
        self.secondHandCarAge_lineEdit.setReadOnly(True)

        # self.keepEOL_lineEdit.setText(f"{self.parent.parent.generalSettings['ICElifeSpan']:.0f}")
        # self.keepEOL_lineEdit.setReadOnly(True)

        # self.keepEOL_comboBox.setEnabled(False)

        # Optional: trigger any additional logic after resetting
        self.set_default_values()

    def validate_and_accept(self):
        validated = True
        for widget in self.editableWidgets:
            if hasattr(widget, 'validate_numeric_input'):
                if widget.validate_numeric_input():
                    validated = False
                    break

        # if validated:
        #     if self.secondHandCar_button.read():
        #         if self.keepEOL_comboBox.read() == 'km':
        #             keepEoL = float(self.keepEOL_lineEdit.read())
        #         else:
        #             keepEoL = float(self.keepEOL_lineEdit.read()) * float(
        #                 self.parent.parent.km2yearsConvFactorLineEdit.text())

        #         if float(self.secondHandCar_lineEdit.read()) >= keepEoL:
        #             if not self.keepEOL_button.read():
        #                 self.keepEOL_lineEdit.clear()
        #             self.secondHandCar_lineEdit.clear()
        #             QMessageBox.warning(self,
        #                                 "Invalid Input",
        #                                 "Intended end-of-udage (km/years) must be greater than Second-hand Car Mileage (km)")
        #             return

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
