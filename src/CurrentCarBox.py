# -*- coding: utf-8 -*-
"""
Created on Wed Apr  9 07:15:56 2025

@author: lucac
"""

from src.BaseClasses.customLineEdit import myQLineEdit
from src.BaseClasses.customComboBox import myQComboBox
from src.BaseClasses.customCheckBox import myQCheckBox
from PySide6.QtWidgets import QGroupBox, QFormLayout, QLabel, QHBoxLayout, QPushButton, QMessageBox
import numpy as np

from PySide6.QtWidgets import (
    QVBoxLayout, QFrame
)
from PySide6.QtCore import Qt, QPoint
from src.Utilities import setLayoutVisible


class CurrentCar(QGroupBox):

    def __init__(self,
                 parent=None):

        super().__init__()
        self.parent = parent

        self.data = parent.data
        self.tooltip_dict = parent.tooltip_dict
        self.carSegments = parent.carSegments
        self.carEngineTypes = parent.carEngineTypes
        self.countries = parent.countries

        self.setTitle("Current Car Details")

        # Input Group Box
        self.setFixedHeight(220)
        input_form_layout = QFormLayout()
        self.setFixedWidth(parent.leftGroupWidth)

        # Current Car Segment
        segments_label = QLabel("Car Segment:")
        segments_label.setFixedWidth(parent.rightLabelsWidth)
        self.segments_comboBox = myQComboBox("carSegment",
                                             self.carSegments)
        self.segments_comboBox.currentIndexChanged.connect(self.set_default_values)
        # self.segments_comboBox.setFixedWidth(parent.leftLabelsWidth)
        self.segments_comboBox.setFixedHeight(parent.comboBoxHeight)
        input_form_layout.addRow(segments_label, self.segments_comboBox)

        # Current Engine Type
        self.engineType_comboBox = myQComboBox("engineType",
                                               self.carEngineTypes,
                                               defaultIndex=2)
        self.engineType_comboBox.currentIndexChanged.connect(self.set_default_values_and_batteries)
        # self.engineType_comboBox.setFixedWidth(parent.leftLabelsWidth)
        self.engineType_comboBox.setFixedHeight(parent.comboBoxHeight)
        input_form_layout.addRow(QLabel("Engine Type:"), self.engineType_comboBox)

        # Current Mileage
        self.currentMileage_lineEdit = myQLineEdit("mileage",
                                                   placeHolderText="Enter mileage (compulsory)",
                                                   validateLabel="Current Mileage (km)")
        self.currentMileage_lineEdit.setFixedHeight(parent.comboBoxHeight)
        self.currentMileage_lineEdit.valueChanged.connect(self.validate_current_mileage)
        # self.currentMileage_lineEdit.setFixedWidth(parent.leftLabelsWidth)

        input_form_layout.addRow(QLabel("Current Mileage (km):"), self.currentMileage_lineEdit)

        # Country Dropdown with European Countries
        energyMix_width = 115
        country_HBoxLayout = QHBoxLayout()
        self.country_comboBox = myQComboBox("country",
                                            self.countries)
        # self.country_comboBox.setFixedWidth(parent.leftLabelsWidth - energyMix_width)
        self.country_comboBox.setFixedHeight(parent.comboBoxHeight)
        self.country_comboBox.currentIndexChanged.connect(self.update_energy_mix)

        self.energyMix_lineEdit = myQLineEdit("energyMix",
                                              placeHolderText="Enter energy mix",
                                              validateLabel="Energy mix (gCO₂/kWh)",
                                              compulsory=True)
        self.energyMix_lineEdit.setFixedWidth(energyMix_width)
        self.energyMix_lineEdit.setReadOnly(True)
        self.energyMix_lineEdit.setStyleSheet("background-color: lightgrey;")

        country_HBoxLayout.addWidget(self.country_comboBox)
        country_HBoxLayout.addWidget(self.energyMix_lineEdit)

        input_form_layout.addRow(QLabel("Energy mix (gCO₂/kWh):"),
                                 country_HBoxLayout)

        # -------------------------------------------------------------------------------------#
        # ADVANCED SETTINGS
        # -------------------------------------------------------------------------------------#
        advancedSettings_HBoxLayout = QHBoxLayout()
        advancedSettings_HBoxLayout.setContentsMargins(0, 5, 5, 0)
        advancedSettings_label = QLabel("Advanced Settings")
        self.advancedSettings_button = QPushButton("▼")
        self.advancedSettings_button.setFixedSize(20, 20)  # Equal width and height
        self.advancedSettings_button.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 10px;  /* Half of 30 = circle */
                background-color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #c8c8c8;
            }
        """)
        # advancedSettings_HBoxLayout.addStretch()
        advancedSettings_HBoxLayout.addWidget(self.advancedSettings_button)
        advancedSettings_HBoxLayout.addWidget(advancedSettings_label)

        input_form_layout.addRow(advancedSettings_HBoxLayout)

        self.advancedSettings_button.clicked.connect(self.toggle_panel)

        # Definition of the popup panel
        self.popup_panel = QFrame(self, Qt.Tool | Qt.FramelessWindowHint)
        self.popup_panel.setFixedWidth(parent.leftGroupWidth)
        # self.popup_panel.setWindowFlags(Qt.FramelessWindowHint)
        self.popup_panel.setFrameShape(QFrame.StyledPanel)
        self.popup_panel.setObjectName("popupPanel")
        self.popup_panel.setStyleSheet("""
            #popupPanel {
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        self.popup_panel.hide()

        advancedSettingsPanel_layout = QVBoxLayout(self.popup_panel)
        advancedSettingsPanel_layout.setContentsMargins(15, 15, 15, 15)
        self.baseData_groupBox = QGroupBox("Car Settings")
        self.batteryData_groupBox = QGroupBox("BEV Battery Settings")
        self.baseData_layout = QVBoxLayout(self.baseData_groupBox)
        self.batteryData_layout = QVBoxLayout(self.batteryData_groupBox)

        self.massLine = QHBoxLayout()
        self.carProductionFootprintLine = QHBoxLayout()
        self.WTTLine = QHBoxLayout()
        self.TTWLine = QHBoxLayout()
        self.iceConsumptionLine = QHBoxLayout()
        self.bevConsumptionLine = QHBoxLayout()
        self.drivingShareLine = QHBoxLayout()
        self.batteryCapacityLine = QHBoxLayout()
        self.batteryProductionFootprintLine = QHBoxLayout()
        self.batteryLifeTimeLine = QHBoxLayout()
        self.secondHandLine = QHBoxLayout()
        self.secondHandMileageLine = QHBoxLayout()
        self.secondHandAgeLine = QHBoxLayout()
        self.WTTLine = QHBoxLayout()
        self.TTWLine = QHBoxLayout()

        # -------------------------------------------------------------------------------------#
        # Base data
        advancedSettingsLeftWidgetWidth = parent.rightLabelsWidth + 15

        # Second hand car options
        secondHandCar_label = QLabel("Second-hand Car:")
        secondHandCar_label.setFixedWidth(advancedSettingsLeftWidgetWidth)

        secondHandCarMileage_label = QLabel("Second-hand Car Mileage (km):")
        secondHandCarMileage_label.setFixedWidth(advancedSettingsLeftWidgetWidth)

        secondHandCarAge_label = QLabel("Second-hand Car Age (years):")
        secondHandCarAge_label.setFixedWidth(advancedSettingsLeftWidgetWidth)

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

        # Mean Consumption
        meanConsumptionLiter_label = QLabel("ICE Consumption (l/100km):")
        meanConsumptionLiter_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
        meanConsumptionWh_label = QLabel("EM Consumption (kWh/100km):")
        meanConsumptionWh_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
        meanDrivingShare_label = QLabel("Driving Share (Plug-in Hybrid only):")
        meanDrivingShare_label.setFixedWidth(advancedSettingsLeftWidgetWidth)

        self.mean_consumption_liter = myQLineEdit("meanConsumptionLiter",
                                                  validateLabel="ICE consumption (l/100km)",
                                                  compulsory=False)
        self.mean_consumption_Wh = myQLineEdit("meanConsumptionWh",
                                               validateLabel="EM Consumption (kWh/100km)",
                                               compulsory=False)
        self.drivingShare_lineEdit = myQLineEdit("drivingShare",
                                                 validateLabel="Driving Share (Plug-in Hybrid only)",
                                                 compulsory=False,
                                                 upperLimit=1)

        self.iceConsumptionLine.addWidget(meanConsumptionLiter_label)
        self.iceConsumptionLine.addWidget(self.mean_consumption_liter)
        self.bevConsumptionLine.addWidget(meanConsumptionWh_label)
        self.bevConsumptionLine.addWidget(self.mean_consumption_Wh)
        self.drivingShareLine.addWidget(meanDrivingShare_label)
        self.drivingShareLine.addWidget(self.drivingShare_lineEdit)

        # User defined mass option
        mass_label = QLabel("Car Mass (kg):")
        mass_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
        self.mass_lineEdit = myQLineEdit("massValue",
                                         validateLabel="Car mass (kg)",
                                         compulsory=False)

        self.massLine.addWidget(mass_label)
        self.massLine.addWidget(self.mass_lineEdit)

        # Car production footprint
        carProductionFootprint_label = QLabel("Car Production-EoL Footprint (kgCO₂/kg):")
        carProductionFootprint_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
        self.carProductionFootprint_lineEdit = myQLineEdit("carProductionFootprint",
                                                           validateLabel="Car Production-EoL Footprint (kgCO₂/kg)",
                                                           compulsory=False)

        self.carProductionFootprintLine.addWidget(carProductionFootprint_label)
        self.carProductionFootprintLine.addWidget(self.carProductionFootprint_lineEdit)

        # WTT and TTW options
        WTT_label = QLabel("WTT Fuel Footprint (gCO₂/l):")
        WTT_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
        self.WTT_lineEdit = myQLineEdit("WTT",
                                        validateLabel="WTT Fuel Footprint (gCO₂/l)",
                                        compulsory=False)
        TTW_label = QLabel("TTW Fuel Footprint (gCO₂/l):")
        TTW_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
        self.TTW_lineEdit = myQLineEdit("TTW",
                                        validateLabel="TTW Fuel Footprint (gCO₂/l)",
                                        compulsory=False)

        self.WTTLine.addWidget(WTT_label)
        self.WTTLine.addWidget(self.WTT_lineEdit)
        self.TTWLine.addWidget(TTW_label)
        self.TTWLine.addWidget(self.TTW_lineEdit)

        # Update layout
        self.baseData_layout.addLayout(self.secondHandLine)
        self.baseData_layout.addLayout(self.secondHandMileageLine)
        self.baseData_layout.addLayout(self.secondHandAgeLine)
        self.baseData_layout.addLayout(self.iceConsumptionLine)
        self.baseData_layout.addLayout(self.bevConsumptionLine)
        self.baseData_layout.addLayout(self.drivingShareLine)
        self.baseData_layout.addLayout(self.massLine)
        self.baseData_layout.addLayout(self.carProductionFootprintLine)
        self.baseData_layout.addLayout(self.WTTLine)
        self.baseData_layout.addLayout(self.TTWLine)

        self.baseData_groupBox.setLayout(self.baseData_layout)

        # -------------------------------------------------------------------------------------#

        # Battery data

        # Capacity
        capacity_label = QLabel("Battery Capacity (kWh):")
        capacity_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
        self.capacity_lineEdit = myQLineEdit("batteryCapacity",
                                             placeHolderText='',
                                             validateLabel="Battery Capacity (kWh)",
                                             compulsory=False)

        self.batteryCapacityLine.addWidget(capacity_label)
        self.batteryCapacityLine.addWidget(self.capacity_lineEdit)

        # Battery production footprint
        batteryProductionFootprint_label = QLabel("Battery Production Footprint (kgCO₂/kWh):")
        batteryProductionFootprint_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
        self.batteryProductionFootprint_lineEdit = myQLineEdit("batteryProductionFootprint",
                                                               text=self.data['batteries']['kgco2/kWh'],
                                                               placeHolderText='',
                                                               validateLabel='Production Footprint (kgCO₂/kWh)',
                                                               compulsory=True)

        self.batteryProductionFootprintLine.addWidget(batteryProductionFootprint_label)
        self.batteryProductionFootprintLine.addWidget(self.batteryProductionFootprint_lineEdit)

        # battery estimated life time
        batteryLifeTime_label = QLabel("Estimated life time (km):")
        batteryLifeTime_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
        self.batteryLifeTime_lineEdit = myQLineEdit("batteryLifeTime",
                                                    placeHolderText='',
                                                    validateLabel="Estimated life time (km):",
                                                    compulsory=False)
        self.batteryLifeTime_lineEdit.valueChanged.connect(self.on_batteryLifeTime_modified)

        self.batteryLifeTimeLine.addWidget(batteryLifeTime_label)
        self.batteryLifeTimeLine.addWidget(self.batteryLifeTime_lineEdit)
        self.batteryLifeTime_modified = False

        # Update advancedSettings_layout
        self.batteryData_layout.addLayout(self.batteryCapacityLine)
        self.batteryData_layout.addLayout(self.batteryProductionFootprintLine)
        self.batteryData_layout.addLayout(self.batteryLifeTimeLine)

        self.batteryData_groupBox.setLayout(self.batteryData_layout)

        # Update Panel layout
        advancedSettingsPanel_layout.addWidget(self.baseData_groupBox)
        advancedSettingsPanel_layout.addWidget(self.batteryData_groupBox)

        # -------------------------------------------------------------------------------------#
        # -------------------------------------------------------------------------------------#

        # Reset button
        resetHBox = QHBoxLayout()
        self.reset_button = QPushButton("Reset")
        self.reset_button.setToolTip("Click to reset to default settings.")
        self.reset_button.setFixedWidth(100)
        self.reset_button.clicked.connect(self.reset_to_default)
        resetHBox.addStretch()
        resetHBox.addWidget(self.reset_button)
        resetHBox.addStretch()
        # resetHBox.setContentsMargins(5, 5, 5, 5)
        input_form_layout.addRow(resetHBox)

        # -------------------------------------------------------------------------------------#
        # -------------------------------------------------------------------------------------#

        # Set layout to GroupBox
        self.setLayout(input_form_layout)

        # store the editable widget for other functions (reset, restore, read)
        self.editableWidgets = [
            self.segments_comboBox,
            self.engineType_comboBox,
            self.currentMileage_lineEdit,
            self.secondHandCar_button,
            self.secondHandCarMileage_lineEdit,
            self.secondHandCarAge_lineEdit,
            self.mass_lineEdit,
            self.carProductionFootprint_lineEdit,
            self.mean_consumption_liter,
            self.mean_consumption_Wh,
            self.drivingShare_lineEdit,
            self.country_comboBox,
            self.energyMix_lineEdit,
            self.capacity_lineEdit,
            self.batteryProductionFootprint_lineEdit,
            self.batteryLifeTime_lineEdit,
            self.WTT_lineEdit,
            self.TTW_lineEdit
        ]

        self.set_tooltips()

        # Activate the consumption fields corresponding to the selected engine type
        self.update_defaults()

        # Store the initial state when the dialog opens
        self.state()

    def on_batteryLifeTime_modified(self, new_value: str):
        if self.batteryLifeTime_lineEdit.read() != self.batteryLifeTime_lineEdit._defaultValue:
            self.batteryLifeTime_modified = True

    def toggle_panel(self):
        if self.popup_panel.isVisible():
            self.popup_panel.hide()
            self.advancedSettings_button.setText("▼")
        else:
            pos = self.advancedSettings_button.mapToGlobal(
                self.advancedSettings_button.rect().bottomLeft())
            pos += QPoint(0, 10)
            self.popup_panel.move(pos)
            self.popup_panel.show()
            self.advancedSettings_button.setText("▲")

    def closeEvent(self, event):
        """
        Quando la MainWindow viene chiusa, se il pannello è aperto viene chiuso anch'esso.
        """
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
            energyMix = self.data['usePhase']['EnergyMix'][country] * 1000
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
            self.batteryProductionFootprint_lineEdit.write(self.data['batteries']['kgco2/kWh'])
            self.batteryProductionFootprint_lineEdit.set_compulsory(True)
            self.batteryProductionFootprint_lineEdit.save()

            self.batteryLifeTime_lineEdit.write(
                self.parent.generalOptionsDialog.BEVlifeSpanLineEdit.read())
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
            self.capacity_lineEdit.save()

        if engineType == "BEV":
            self.batteryData_groupBox.show()
        else:
            self.batteryData_groupBox.hide()

        self.popup_panel.adjustSize()

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

        self.popup_panel.adjustSize()

    def reset_to_default(self):

        # Reset all widgets to their declared defaults
        for widget in self.editableWidgets:
            widget.reset_to_default()
            widget.save()

        # Manual UI logic that doesn't come from widget defaults
        self.secondHandCarMileage_lineEdit.clear()
        self.secondHandCarMileage_lineEdit.setReadOnly(True)
        self.secondHandCarAge_lineEdit.clear()
        self.secondHandCarAge_lineEdit.setReadOnly(True)
        self.batteryLifeTime_modified = False

        self.update_defaults()

    def read(self):
        self.state()

        exportData = self.current_state.copy()
        exportData["keepUnits"] = 'km'
        exportData["mileage"] = round(exportData["mileage"], -3)
        exportData['keepLifeSpan'] = exportData["mileage"]

        return exportData

    def set_tooltips(self):
        for widget in self.editableWidgets:
            variable = getattr(widget, "_variableLabel", None)
            if variable and variable in self.tooltip_dict:
                widget.setToolTip(self.tooltip_dict[variable])

    def validate_current_mileage(self, value):
        if value:
            engineType = self.engineType_comboBox.read()
            maxValue = self.parent.generalOptionsDialog.BEVlifeSpanLineEdit.read() if engineType == 'BEV' else self.parent.generalOptionsDialog.ICElifeSpanLineEdit.read()
            engineTypeLabel = "BEV" if engineType == "BEV" else "ICE"

            if float(value) >= float(maxValue):
                message = f"Current Mileage (km) must be lower than {engineTypeLabel} car life span (km).\nChange the expected life span in the Advanced Analysis Setting."
                QMessageBox.warning(self, "Invalid Input", message)
                self.currentMileage_lineEdit.clear()
                self.currentMileage_lineEdit.update_stored_value("")
                # self.parent.plot_widget.initialize_empty_plots()
                # self.parent.table_widget_eou.populate_empty()
                # self.parent.show_plot()
                # self.parent.show_table()
                return message
            else:
                return 0
        else:
            return 0
