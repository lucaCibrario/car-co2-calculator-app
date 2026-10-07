# -*- coding: utf-8 -*-
"""
Created on Sat Aug 24 07:44:14 2024

@author: lucac
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QGroupBox, QScrollArea,
    QSizePolicy, QMessageBox, QFrame, QFileDialog
)
from PySide6.QtGui import QFont, QIcon, QDesktopServices, QAction
from PySide6.QtCore import Qt, QUrl

import src
from src.Utilities import resource_path

from src.BaseClasses.customComboBox import myQComboBox
from src.BaseClasses.customLineEdit import myQLineEdit
from src.BaseClasses.customCheckBox import myQCheckBox

import os

import pandas as pd


class ConfidentialLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)

        # Imposta lo stile della label
        self.setFont(QFont("Arial", 12, QFont.Bold))  # Font grande e in grassetto
        self.setAlignment(Qt.AlignCenter)  # Testo centrato
        self.setStyleSheet("""
            QLabel {
                color: red;  /* Testo rosso */
                border: 2px solid red;  /* Bordo rosso */
                padding: 7px;  /* Spaziatura interna */
                background-color: white;  /* Sfondo bianco */
            }
        """)


class CarReplacementAdvisor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.computed = False
        self.generalSettings = {}

        self.countries = ["Europe", "Custom",
                          "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark",
                          "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy",
                          "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands", "Poland", "Portugal",
                          "Romania", "Slovakia", "Slovenia", "Spain", "Sweden"
                          ]

        self.carSegments = ["Segment B", "Segment C", "SUV"]

        self.carEngineTypes = [
            "Gasoline (Euro 4)", "Gasoline (Euro 5)", "Gasoline (Euro 6)",
            "Diesel (Euro 4)", "Diesel (Euro 5)", "Diesel (Euro 6)",
            "Mild/Full Hybrid", "Plug-in Hybrid", "BEV"
        ]
        self.maxWindowYears = 20

        self.data = src.Utilities.loadData()
        self.tooltip_dict = src.Utilities.tooltips()

        self.cars = []

        self.setWindowTitle("ECO Car Replacement Advisor")
        self.setWindowIcon(QIcon(resource_path(r"Icons/TitleIcon.jpg")))
        self.setGeometry(100, 50, 1200, 700)
        # self.showFullScreen()

        # Container widget with vertical layout (for separator line below menu)
        central_container = QWidget()
        central_vlayout = QVBoxLayout(central_container)
        central_vlayout.setContentsMargins(0, 0, 0, 0)
        central_vlayout.setSpacing(5)

        # Separator line under the menu bar
        separator_line = QFrame()
        separator_line.setFrameShape(QFrame.HLine)
        separator_line.setFrameShadow(QFrame.Plain)
        # separator_line.setStyleSheet("color: white; background-color: white;")
        separator_line.setStyleSheet("color: lightgray; background-color: lightgray;")
        separator_line.setFixedHeight(1)

        central_vlayout.addWidget(separator_line)

        # Main content layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 0, 10, 10)
        main_layout.setSpacing(6)
        central_vlayout.addWidget(central_widget)

        # Set the new container as central widget
        self.setCentralWidget(central_container)

        # Create central widget
        # central_widget = QWidget()
        # self.setCentralWidget(central_widget)

        # Layouts
        # main_layout = QHBoxLayout(central_widget)
        # main_layout.setContentsMargins(10, 0, 10, 10)
        # main_layout.setSpacing(6)
        form_layout = QVBoxLayout()
        result_layout = QVBoxLayout()

        # -------------------------------------------------------------------------------------#
        # CONFIDENTIALITY
        # -------------------------------------------------------------------------------------#

        label = ConfidentialLabel("CONFIDENTIAL: This tool is for FAAS members only")
        form_layout.addWidget(label)

        # -------------------------------------------------------------------------------------#
        # HELP
        # -------------------------------------------------------------------------------------#

        self.create_menu_bar()

        # -------------------------------------------------------------------------------------#
        # GENERAL SETTINGS DIALOG BOX
        # -------------------------------------------------------------------------------------#

        # initialize general options dialog box
        self.defaultKm2YearsConvFactor = 12000
        self.km2yearsConvFactorLineEdit = myQLineEdit("km2yearsConvFactor",
                                                      text=str(self.defaultKm2YearsConvFactor),
                                                      validateLabel="Average Annual Mileage (km)")
        self.km2yearsConvFactorLineEdit.setToolTip(self.tooltip_dict["km2yearsConvFactor"])
        self.maintenanceCheckBox = myQComboBox(variableLabel="maintenance",
                                               items=['Yes', 'No'])
        self.maintenanceCheckBox.setToolTip(self.tooltip_dict["maintenance"])
        self.generalOptionsDialog = src.GeneralOptions.GeneralOptionsDialog(self)

        self.read_general_settings()

        # -------------------------------------------------------------------------------------#
        # DEFINITION OF THE CURRENT CAR
        # ------------------------------------------------------------------------------------ #
        self.rightLabelsWidth = 220
        self.leftLabelsWidth = 180
        self.comboBoxHeight = 25
        self.leftGroupWidth = 475

        self.currentCarBox = src.CurrentCarBox.CurrentCar(self)
        form_layout.addWidget(self.currentCarBox)

        # -------------------------------------------------------------------------------------#
        # DEFINITION OF THE NEW CARS
        # -------------------------------------------------------------------------------------#

        # Setup of the Container for New Car Definitions
        new_car_group = QGroupBox("New Car(s)")
        new_car_group.setFixedWidth(self.leftGroupWidth)
        self.new_car_layout = QVBoxLayout()
        self.new_car_layout.setAlignment(Qt.AlignTop)  # Aligning the new car fields to the top
        self.new_car_layout.setContentsMargins(0, 0, 0, 0)
        new_car_group_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area_container_widget = QWidget()
        scroll_area_container_widget.setLayout(self.new_car_layout)
        new_car_group.setLayout(new_car_group_layout)
        scroll_area.setWidget(scroll_area_container_widget)
        new_car_group_layout.addWidget(scroll_area)
        new_car_group.setLayout(self.new_car_layout)

        # Add Plus and Minus Buttons to Add/Remove New Cars
        button_layout = QHBoxLayout()
        add_car_label = QLabel('Add Car')
        add_car_button = QPushButton()
        add_car_button.setIcon(QIcon(resource_path(r"Icons/Plus.jpg")))
        add_car_button.setToolTip("Click to add a new car to the analysis.")
        add_car_button.setFixedSize(32, 32)
        add_car_button.clicked.connect(self.add_new_car)

        button_layout.addWidget(add_car_button)
        button_layout.addWidget(add_car_label)
        button_layout.addStretch()

        new_car_group_layout.insertLayout(0, button_layout)
        # self.new_car_layout.addLayout(button_layout)

        # Add first new car fields
        self.add_new_car()

        # Add Input Group and New Car Group to the Form Layout
        form_layout.addWidget(new_car_group)

        # -------------------------------------------------------------------------------------#
        # SETTINGS
        # -------------------------------------------------------------------------------------#
        # Input Group Box
        settings_group = QGroupBox("Analysis Settings")
        settings_group.setFixedHeight(160)
        settings_group.setFixedWidth(self.leftGroupWidth)
        settings_form_layout = QVBoxLayout()

        # km to years conversion factor
        self.km2yearsConvFactorLabel = QLabel('Average Annual Mileage (km):')
        self.km2yearsConvFactorLabel.setFixedWidth(self.rightLabelsWidth)
        # self.km2yearsConvFactorLineEdit.setFixedWidth(self.leftLabelsWidth)
        self.km2yearsConvFactorLineEdit.setFixedHeight(self.comboBoxHeight)

        # Analysis options dialog box
        self.generalOptionsButton = QPushButton()
        self.generalOptionsButton.setIcon(QIcon(resource_path(r"Icons/Options.png")))
        self.generalOptionsButton.setToolTip("Click for more analysis settings.")
        self.generalOptionsButton.setFixedSize(32, 32)
        self.generalOptionsButton.clicked.connect(self.display_general_options_dialog)

        settingsFirstLine_layout = QHBoxLayout()
        settingsFirstLine_layout.setAlignment(Qt.AlignVCenter)
        settingsFirstLine_layout.addWidget(self.km2yearsConvFactorLabel)
        settingsFirstLine_layout.addWidget(self.km2yearsConvFactorLineEdit)
        settingsFirstLine_layout.addWidget(self.generalOptionsButton)

        # Keep life span
        eolLine = QHBoxLayout()
        eolLineBis = QHBoxLayout()

        self.keepEOL_label = QLabel("Intended end-of-usage (mileage/age):")

        self.keepEOL_button = myQCheckBox(variableLabel="keepEOL",
                                          text="Keep until EoL",
                                          defaultValue=True)
        self.keepEOL_label.setFixedWidth(self.rightLabelsWidth)
        self.keepEOL_button.stateChanged.connect(self.toggle_line_edit_keepEOL)

        self.keepEOL_emptyLabel = QLabel()
        self.keepEOL_emptyLabel.setFixedWidth(self.rightLabelsWidth)

        self.keepEOL_lineEdit = myQLineEdit("keepLifeSpan",
                                            placeHolderText="Enter estimated life time",
                                            validateLabel="Intended end-of-usage (km/years)",
                                            compulsory=not self.keepEOL_button.read())
        self.keepEOL_lineEdit.setReadOnly(True)
        self.keepEOL_lineEdit.setStyleSheet("background-color: lightgrey;")

        self.keepEOL_comboBox = myQComboBox("keepUnits",
                                            items=['years', 'km'],
                                            )
        self.keepEOL_comboBox.setEnabled(False)
        self.keepEOL_comboBox.setFixedWidth(70)
        self.keepEOL_comboBox.setFixedHeight(self.comboBoxHeight)

        eolLine.addWidget(self.keepEOL_label)
        eolLine.addWidget(self.keepEOL_button)

        eolLineBis.addWidget(self.keepEOL_emptyLabel)
        eolLineBis.addWidget(self.keepEOL_lineEdit)
        eolLineBis.addWidget(self.keepEOL_comboBox)

        # maintenance
        settingsSecondLine_layout = QHBoxLayout()
        settingsSecondLine_layout.setAlignment(Qt.AlignLeft)

        self.maintenanceLabel = QLabel('Maintenance:')
        self.maintenanceLabel.setFixedWidth(self.rightLabelsWidth)
        self.maintenanceCheckBox.setFixedWidth(70)
        self.maintenanceCheckBox.setFixedHeight(self.comboBoxHeight)

        settingsSecondLine_layout.addWidget(self.maintenanceLabel)
        settingsSecondLine_layout.addWidget(self.maintenanceCheckBox)

        # Compose layout
        settings_form_layout.addLayout(settingsFirstLine_layout)
        settings_form_layout.addLayout(eolLine)
        settings_form_layout.addLayout(eolLineBis)
        settings_form_layout.addLayout(settingsSecondLine_layout)

        settings_group.setLayout(settings_form_layout)
        form_layout.addWidget(settings_group)

        # -------------------------------------------------------------------------------------#
        # COMPUTE CARBON FOOTPRINT BUTTON
        # -------------------------------------------------------------------------------------#

        compute_button_layout = QHBoxLayout()
        compute_button_layout.setAlignment(Qt.AlignCenter)
        compute_button_layout.setContentsMargins(5, 5, 5, 5)

        compute_button = QPushButton("Compute Carbon Footprint")
        compute_button.setToolTip("Click to start the analysis.")
        compute_button.clicked.connect(self.plot_carbon_footprint)
        compute_button.setFont(QFont("Arial", 12, QFont.Bold))
        compute_button.setFixedWidth(250)
        compute_button.setFixedHeight(40)

        # # compute_button_layout.addStretch()
        compute_button_layout.addWidget(compute_button)

        # form_layout.addWidget(compute_button)
        form_layout.addLayout(compute_button_layout)

        # -------------------------------------------------------------------------------------#
        # OUTPUT SECTION
        # -------------------------------------------------------------------------------------#

        # Output Section (Plot and Output Data Analysis)
        output_group = QGroupBox("Carbon Footprint Analysis")
        output_layout = QVBoxLayout()

        # -------------------------------------------------------------------------------------#
        # OUTPUT SECTION: Settings
        # -------------------------------------------------------------------------------------#

        analysisUnits_layout = QHBoxLayout()
        analysisTables_layout = QHBoxLayout()

        # Unit of Measure Label and ComboBox
        unit_label = QLabel("Analysis Units:")
        unit_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.unit_combo = myQComboBox("analysisUnits",
                                      ["years", "km"])
        self.unit_combo.setToolTip("Choose the output units for the analysis.")
        self.unit_combo.setFixedWidth(80)
        self.unit_combo.setFixedHeight(self.comboBoxHeight)  # Optional: match other combo sizes
        self.unit_combo.currentTextChanged.connect(
            self.on_analysis_units_changed)  # Call your handler

        analysisUnits_layout.addWidget(unit_label)
        analysisUnits_layout.addWidget(self.unit_combo)
        analysisUnits_layout.addStretch()
        analysisUnits_layout.setContentsMargins(0, 0, 0, 0)

        # -------------------------------------------------------------------------------------#

        # Output Data Analysis Label and Combo Box
        # analysis_label = QLabel("Output data analysis at:")
        # # self.analysisUnits_label = QLabel("years")
        # self.analysis_combo = myQComboBox(items=["Break Even Point (BEP)",
        #                                          "Specific Age (years)"])
        # self.analysis_combo.currentIndexChanged.connect(self.on_analysis_option_change)
        # self.analysis_combo.setFixedWidth(160)
        # self.analysis_combo.setFixedHeight(self.comboBoxHeight)

        # # Mileage Input for "Specify Mileage" option
        # self.specifyMileage_lineEdit = myQLineEdit(placeHolderText="Enter age (compulsory)",
        #                                            validateLabel="Mileage/Age for analysis",
        #                                            compulsory=False)
        # self.specifyMileage_lineEdit.setFixedHeight(self.comboBoxHeight)
        # self.specifyMileage_lineEdit.setFixedWidth(180)
        # self.specifyMileage_lineEdit.setVisible(False)

        # self.refreshTable_button = QPushButton(icon=QIcon(resource_path("Icons/Refresh.png")),
        #                                        text='  Refresh Table')
        # self.refreshTable_button.setFixedSize(120, 28)
        # self.refreshTable_button.setVisible(False)
        # self.refreshTable_button.clicked.connect(self.on_analysis_value_changed)
        # # self.analysisUnits_label.setVisible(False)

        # self.analysis_combo.setToolTip(
        #     "Choose the type of analysis:\n"
        #     "- Break Even Point (BEP): compare emissions when the new car’s total emissions equal the current one.\n"
        #     "- Specific Age (years): compare emissions at a user-defined car age."
        # )

        # self.specifyMileage_lineEdit.setToolTip(
        #     "Enter the car age (in years) at which to evaluate and compare emissions."
        # )

        # self.refreshTable_button.setToolTip(
        #     "Refresh the output table after modifying the analysis settings."
        # )

        # # Hidden by default
        # analysisTables_layout.addWidget(analysis_label)
        # analysisTables_layout.addWidget(self.analysis_combo)
        # analysisTables_layout.addWidget(self.specifyMileage_lineEdit)
        # analysisTables_layout.addWidget(self.refreshTable_button)
        # # analysisTables_layout.addWidget(self.analysisUnits_label)
        # analysisTables_layout.addStretch()

        analysis_label = QLabel("Output data analysis at end-of-usage (EoU):")
        # self.analysisUnits_label = QLabel("years")

        # Hidden by default
        analysisTables_layout.addWidget(analysis_label)

        analysisTables_layout.addStretch()

        # -------------------------------------------------------------------------------------#
        # OUTPUT SECTION: PLOT AREA
        # -------------------------------------------------------------------------------------#

        # Placeholder for Plot Area (to ensure top alignment)

        self.plot_widget = src.PlotWidget.PlotlyWidget(parent=self)
        self.plot_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.plot_widget.initialize_empty_plots()

        # self.dummy_bottom = QWidget()
        # splitter.addWidget(self.dummy_bottom)

        # -------------------------------------------------------------------------------------#
        # OUTPUT SECTION: TABLES
        # -------------------------------------------------------------------------------------#
        # Output Data Analysis Table at specified end-of-usage
        self.table_widget_eou = src.TableWidget.TableWidgetEOU(self)
        self.table_widget_eou.populate_empty()

        # # Output Data Analysis Table for BE
        # self.table_widget_be = src.TableWidget.TableWidgetBE(self)
        # self.table_widget_be.populate_empty(self.unit_combo.read())

        # # Output Data Analysis Table for Specified Mileage
        # self.table_widget_mileage = src.TableWidget.TableWidgetMileage(self)
        # self.table_widget_mileage.populate_empty(self.unit_combo.read())

        # -------------------------------------------------------------------------------------#
        # Update output layout
        output_layout.addLayout(analysisUnits_layout)
        output_layout.addWidget(self.plot_widget)
        output_layout.addLayout(analysisTables_layout)
        output_layout.addWidget(self.table_widget_eou)
        # output_layout.addWidget(self.table_widget_be)
        # output_layout.addWidget(self.table_widget_mileage)

        output_group.setLayout(output_layout)

        # Add Result Group to the Result Layout
        result_layout.addWidget(output_group)

        # -------------------------------------------------------------------------------------#
        # FINAL LAYOUT AND INITIALIZATION
        # -------------------------------------------------------------------------------------#
        main_layout.addLayout(form_layout, 2)
        main_layout.addLayout(result_layout, 3)

        self.update_expected_life()
        self.show_plot()
        self.show_table()
        self.read_general_settings()

    def toggle_line_edit_keepEOL(self, state):
        """Enable or disable mileage input based on checkbox state."""
        if state:
            self.keepEOL_lineEdit.clear()
            self.keepEOL_lineEdit.setStyleSheet("background-color: lightgrey;")
        else:
            self.keepEOL_lineEdit.setStyleSheet("")
            self.keepEOL_lineEdit.write('')
            self.keepEOL_lineEdit.update_stored_value('')

        self.keepEOL_lineEdit.setReadOnly(state)
        self.keepEOL_lineEdit.set_compulsory(not state)
        self.keepEOL_comboBox.setEnabled(not state)

    def read_general_settings(self):
        self.generalSettings = self.generalOptionsDialog.read()
        self.generalSettings["km2yearsConvFactor"] = float(
            self.km2yearsConvFactorLineEdit.read())
        self.generalSettings["maintenance"] = self.maintenanceCheckBox.read()

        if self.generalSettings["maintenance"].lower() == 'yes':
            self.generalSettings["maintenance"] = True
        else:
            self.generalSettings["maintenance"] = False

    def show_plot(self):
        units = self.unit_combo.read()

        # Show plots
        if units == 'km':
            self.plot_widget.show_plot_kilometers()
        else:
            self.plot_widget.show_plot_years()

        # self.plot_widget.setFocus()

    def on_analysis_units_changed(self):
        units = self.unit_combo.read()

        # Change plot visualization
        self.show_plot()

        # # update analysis option for output tables
        # if units == 'km':
        #     self.specifyMileage_lineEdit.setPlaceholderText("Enter mileage (compulsory)")
        #     self.analysis_combo.setItemText(1, "Specific Mileage (km)")
        #     self.specifyMileage_lineEdit.setToolTip(
        #         "Enter the car mileage (in kilometers) at which to evaluate and compare emissions."
        #     )
        #     self.analysis_combo.setToolTip(
        #         "Choose the type of analysis:\n"
        #         "- Break Even Point (BEP): compare emissions when the new car’s total emissions equal the current one.\n"
        #         "- Specific Mileage (km): compare emissions at a user-defined car mileage."
        #     )
        # else:
        #     self.specifyMileage_lineEdit.setPlaceholderText("Enter age (compulsory)")
        #     self.analysis_combo.setItemText(1, "Specific Age (years)")
        #     self.specifyMileage_lineEdit.setToolTip(
        #         "Enter the car age (in years) at which to evaluate and compare emissions."
        #     )
        #     self.analysis_combo.setToolTip(
        #         "Choose the type of analysis:\n"
        #         "- Break Even Point (BEP): compare emissions when the new car’s total emissions equal the current one.\n"
        #         "- Specific Age (years): compare emissions at a user-defined car age."
        #     )

        # self.specifyMileage_lineEdit.clear()

        # # Update table BEP
        # if self.table_widget_be._isEmpty:
        #     self.table_widget_be.populate_empty(units)
        # else:
        #     self.table_widget_be.populate(units)

        # # Update table Specific Mileage/Age
        # self.table_widget_mileage.populate_empty(units)

        self.show_table()

    def show_table(self):
        self.table_widget_eou.show()
        # if "Break" in self.analysis_combo.read():
        #     self.table_widget_be.show()
        #     self.table_widget_mileage.hide()
        # else:
        #     self.table_widget_be.hide()
        #     self.table_widget_mileage.show()

    def update_expected_life(self):
        # read expected life time values from the settings panel
        # self.generalSettings = src.Utilities.read_general_settings(self.generalOptionsDialog)
        self.read_general_settings()

        # Update battery expected life for the current car
        self.currentCarBox.batteryLifeTime_lineEdit.update_default_value(
            f"{self.generalSettings['BEVlifeSpan']:.0f}")

        if not self.currentCarBox.batteryLifeTime_modified:
            self.currentCarBox.batteryLifeTime_lineEdit.write(
                f"{self.generalSettings['BEVlifeSpan']:.0f}")
            self.currentCarBox.batteryLifeTime_lineEdit.save()

        # Update battery expected life for new cars
        if self.cars:
            for car in self.cars:

                car.dialog.batteryLifeTime_lineEdit.update_default_value(
                    f"{self.generalSettings['BEVlifeSpan']:.0f}")

                if not car.dialog.batteryLifeTime_modified:
                    car.dialog.batteryLifeTime_lineEdit.write(
                        f"{self.generalSettings['BEVlifeSpan']:.0f}")
                    car.dialog.batteryLifeTime_lineEdit.save()

        self.oldGeneralSettings = self.generalSettings.copy()

    def display_general_options_dialog(self):
        """Opens the options window."""
        self.generalOptionsDialog.exec()

    def add_new_car(self):
        """Add a new car input section."""
        car = src.Car.Car(self.carSegments, self.carEngineTypes, parent=self)
        self.new_car_layout.addWidget(car)
        self.cars.append(car)
        self.update_expected_life()

    def remove_car(self, car):
        """Removes the given Car instance from the UI and list."""
        if car in self.cars:
            self.cars.remove(car)  # Remove from list

        car.deleteLater()  # Delete from memory

    def on_analysis_option_change(self):
        """Show or hide the mileage input box based on the selected analysis option."""
        if "Specific" in self.analysis_combo.read():
            self.specifyMileage_lineEdit.setVisible(True)
            self.refreshTable_button.setVisible(True)
            # self.analysisUnits_label.setVisible(True)
        else:
            self.specifyMileage_lineEdit.setVisible(False)
            self.refreshTable_button.setVisible(False)
            # self.analysisUnits_label.setVisible(False)

        self.show_table()

    def plot_carbon_footprint(self):
        """Plot the carbon footprint based on the input data."""

        # Check if the current mileage field has been filled by user
        validated = True
        for widget in self.currentCarBox.editableWidgets:
            if hasattr(widget, 'validate_numeric_input'):
                if not widget.validate_numeric_input():
                    widget.save()
                else:
                    validated = False
                    break

        if self.currentCarBox.validate_current_mileage(self.currentCarBox.currentMileage_lineEdit.read()):
            validated = False

        if validated:
            data = self.currentCarBox.read().copy()
            if data["secondHandCarMileage"]:
                if data["secondHandCarMileage"] >= data["mileage"]:
                    validated = False
                    self.currentCarBox.secondHandCarMileage_lineEdit.clear()
                    self.currentCarBox.secondHandCarMileage_lineEdit.save()
                    QMessageBox.warning(self,
                                        "Invalid Input",
                                        "Current Mileage (km) must be greater than Second-hand Car Mileage (km).")
                if data["secondHandCarAge"] >= self.maxWindowYears:
                    validated = False
                    self.currentCarBox.secondHandCarAge_lineEdit.clear()
                    self.currentCarBox.secondHandCarAge_lineEdit.save()
                    QMessageBox.warning(self,
                                        "Invalid Input",
                                        "Second-hand Car Age (km) of the current car must be lower than the maximum allowed age ({self.maxWindowYears} years).")

        if hasattr(self.keepEOL_lineEdit, 'validate_numeric_input'):
            if not self.keepEOL_lineEdit.validate_numeric_input():
                self.keepEOL_lineEdit.save()
            else:
                validated = False

        if validated:
            self.computed = False

            # read general options
            self.read_general_settings()
            self.generalSettings["keepEOL"] = bool(self.keepEOL_button.read())
            self.generalSettings["keepLifeSpan"] = float(self.keepEOL_lineEdit.read()) if self.keepEOL_lineEdit.read() else None
            self.generalSettings["keepUnits"] = str(self.keepEOL_comboBox.read())

            # -------------------------------------------------------------------------------------#
            # CARS ANALYSIS
            # -------------------------------------------------------------------------------------#

            if self.car_analysis():

                # -------------------------------------------------------------------------------------#
                # PLOT CO2 HISTORY
                # -------------------------------------------------------------------------------------#

                if self.plot_widget.plot_co2_hystory():
                    self.computed = True

                    # -------------------------------------------------------------------------------------#
                    # TABLE DATA COMPUTATION
                    # -------------------------------------------------------------------------------------#
                    self.compute_data_tables()
                else:
                    self.plot_widget.initialize_empty_plots()
                    self.table_widget_eou.populate_empty()

            else:
                self.plot_widget.initialize_empty_plots()
                self.table_widget_eou.populate_empty()
                # self.table_widget_be.populate_empty(units)
                # self.table_widget_mileage.populate_empty(units)
        else:
            self.plot_widget.initialize_empty_plots()
            self.table_widget_eou.populate_empty()
            # self.table_widget_be.populate_empty(units)
            # self.table_widget_mileage.populate_empty(units)

        # Show plots and tables
        self.show_plot()
        self.show_table()

    def car_analysis(self):

        # -------------------------------------------------------------------------------------#
        # PRELIMINARY SETUP
        # -------------------------------------------------------------------------------------#

        # get data from current car inputs
        self.currentCarData = self.currentCarBox.read().copy()

        # get data from new cars
        self.newCarData = [car.read() for car in self.cars]

        self.carData = self.newCarData.copy()
        self.carData.insert(0, self.currentCarData)

        # -------------------------------------------------------------------------------------#
        # CAR ANALYSIS
        # -------------------------------------------------------------------------------------#

        country = self.currentCarData['country']
        conversionFactor = self.generalSettings['km2yearsConvFactor']  # km for each year
        energyMix = self.currentCarData['energyMix'] / 1000

        if self.generalSettings["keepLifeSpan"]:
            if self.generalSettings["keepUnits"] == 'km':
                self.generalSettings["keepLifeSpan"] = round(self.generalSettings["keepLifeSpan"], -3)
            else:
                self.generalSettings["keepLifeSpan"] = round(self.generalSettings["keepLifeSpan"] * conversionFactor, -3) / conversionFactor

        for carIndex in range(len(self.carData)):

            carSegment = self.carData[carIndex]['carSegment']
            engineType = self.carData[carIndex]['engineType']
            carMass = self.carData[carIndex]['massValue']
            carProductionFootprint = self.carData[carIndex]['carProductionFootprint']
            WTT = self.carData[carIndex]['WTT']
            TTW = self.carData[carIndex]['TTW']
            consumptionLiter = self.carData[carIndex]['meanConsumptionLiter'] / 100 if self.carData[carIndex]['meanConsumptionLiter'] else None
            consumptionWh = self.carData[carIndex]['meanConsumptionWh'] * 10 if self.carData[carIndex]['meanConsumptionWh'] else None
            drivingShare = self.carData[carIndex]['drivingShare']
            self.carData[carIndex]['country'] = self.currentCarData['country']
            self.carData[carIndex]['energyMix'] = self.currentCarData['energyMix']

            if carIndex != 0:
                self.carData[carIndex]["keepEOL"] = self.generalSettings["keepEOL"]
                self.carData[carIndex]["keepLifeSpan"] = self.generalSettings["keepLifeSpan"]
                self.carData[carIndex]["keepUnits"] = self.generalSettings["keepUnits"]

                if not self.carData[carIndex]["keepLifeSpan"]:
                    self.carData[carIndex]["keepUnits"] = 'km'
                    if engineType == 'BEV':
                        self.carData[carIndex]["keepLifeSpan"] = self.generalSettings["BEVlifeSpan"]
                    else:
                        self.carData[carIndex]["keepLifeSpan"] = self.generalSettings["ICElifeSpan"]
                else:
                    if engineType == 'BEV':
                        defaultLifeSpan = self.generalSettings["BEVlifeSpan"]
                    else:
                        defaultLifeSpan = self.generalSettings["ICElifeSpan"]

                    if self.carData[carIndex]["keepUnits"] == 'years':
                        self.carData[carIndex]["keepLifeSpan"] = min(self.carData[carIndex]["keepLifeSpan"],
                                                                     defaultLifeSpan / conversionFactor)
                    else:
                        self.carData[carIndex]["keepLifeSpan"] = min(self.carData[carIndex]["keepLifeSpan"],
                                                                     defaultLifeSpan)

            # if self.carData[carIndex]["secondHandCarMileage"]:
            #     if self.carData[carIndex]["secondHandCarMileage"] >= self.carData[carIndex]["keepLifeSpan"]:
            #         QMessageBox.warning(self,
            #                             "Invalid Input",
            #                             f"Intended end-of-udage (km/years) must be greater than Second-hand Car Mileage (km) for New Car {carIndex}")
            #         return 0

            # convert years to kilometers
            self.carData[carIndex] = src.Utilities.years_to_kilometers(
                self.carData[carIndex], conversionFactor)

            # -------------------------------------------------------------------------------------#
            # PRODUCTION AND EOL
            # -------------------------------------------------------------------------------------#
            self.carData[carIndex]['productionEoL'] = carMass * carProductionFootprint * 1000

            # Responsibility model for second hand cars and Keep for a limited period
            highValue = 1
            lowValue = 0

            if self.carData[carIndex]['secondHandCar']:
                highValue = src.Utilities.depreciation_curve(
                    self.carData[carIndex]['secondHandCarAge'],
                    conversionFactor,
                    engineType)
                startAge = self.carData[carIndex]['secondHandCarAge']
            else:
                startAge = 0

            if self.carData[carIndex]['keepLifeSpan']:

                lowValue = src.Utilities.depreciation_curve(
                    startAge + self.carData[carIndex]['keepLifeSpan'],
                    conversionFactor,
                    engineType)

            depreciation = highValue - lowValue
            if depreciation < 0:
                depreciation = 0

            self.carData[carIndex]['productionEoL'] = self.carData[carIndex]['productionEoL'] * depreciation
            self.carData[carIndex]['depreciation'] = depreciation

            # -------------------------------------------------------------------------------------#
            # USE PHASE
            # -------------------------------------------------------------------------------------#
            if 'Gasoline' in engineType or 'Mild' in engineType:
                self.carData[carIndex]['usePhaseEmissions'] = (
                    WTT + TTW) * consumptionLiter
            elif 'Diesel' in engineType:
                self.carData[carIndex]['usePhaseEmissions'] = (
                    WTT + TTW) * consumptionLiter
            elif 'Plug' in engineType:
                self.carData[carIndex]['usePhaseEmissions'] = (
                    WTT + TTW) * (1 - drivingShare) * consumptionLiter + drivingShare * consumptionWh * energyMix
            elif 'BEV' in engineType:
                self.carData[carIndex]['usePhaseEmissions'] = consumptionWh * energyMix

        return 1

    def compute_data_tables(self):

        conversionFactor = self.generalSettings['km2yearsConvFactor']

        self.mileageAtChange = self.currentCarData["mileage"]
        self.mileageAtEnd = self.plot_widget.xmaxRangeKm
        self.analysisStart = self.plot_widget.analysisStartKm

        yearSpan = (self.mileageAtEnd - self.mileageAtChange) / conversionFactor
        totalYearSpan = (self.mileageAtEnd - self.analysisStart) / conversionFactor

        self.co2AtChange = src.Utilities.interp_data(
            self.carData[0]['xValues'], self.carData[0]['emissionHystory'], self.mileageAtChange)

        # compute interesection between co2 hystories of new and old cars
        for carIndex in range(len(self.carData)):
            if carIndex != 0:
                x1 = self.carData[0]['xValues']
                y1 = self.carData[0]['emissionHystory']
                x2 = self.carData[carIndex]['xValues']
                y2 = self.carData[carIndex]['emissionHystory']

                self.carData[carIndex]['BEkm'], self.carData[carIndex]['BEco2'] = src.Utilities.compute_intersection(
                    x1, y1, x2, y2)
                if self.carData[carIndex]['BEkm'] is not None and self.carData[carIndex]['BEco2'] is not None:
                    self.carData[carIndex]['DeltaBEkm'] = self.carData[carIndex]['BEkm'] - \
                        self.mileageAtChange
                    self.carData[carIndex]['DeltaBEco2'] = self.carData[carIndex]['BEco2'] - \
                        self.co2AtChange
                else:
                    self.carData[carIndex]['BEkm'] = None
                    self.carData[carIndex]['BEco2'] = None
                    self.carData[carIndex]['DeltaBEkm'] = None
                    self.carData[carIndex]['DeltaBEco2'] = None

        # Compute yearly emissions and relative contributions
        for carIndex in range(0, len(self.carData)):
            self.carData[carIndex]['THco2'] = src.Utilities.interp_data(
                self.carData[carIndex]['xValues'], self.carData[carIndex]['emissionHystory'], self.mileageAtEnd)

            self.carData[carIndex]['DeltaTHco2'] = self.carData[carIndex]['THco2'] - \
                self.co2AtChange

            if carIndex == 0:  # case of the current car
                totalCo2 = self.carData[carIndex]['THco2']
                timePeriod = totalYearSpan
            else:  # for other cars
                totalCo2 = self.carData[carIndex]['DeltaTHco2']
                timePeriod = yearSpan

            productionCo2 = self.carData[carIndex]['productionEoL'] / 1e6
            useCo2 = src.Utilities.interp_data(
                self.carData[carIndex]['xValues'], self.carData[carIndex]['totalUsePhaseEmissions'], self.mileageAtEnd)

            self.carData[carIndex]['yearlyCo2'] = totalCo2 / timePeriod
            self.carData[carIndex]['relativeProductionCo2'] = 100 * productionCo2 * 0.9 / totalCo2
            self.carData[carIndex]['relativeEolCo2'] = 100 * productionCo2 * 0.1 / totalCo2
            self.carData[carIndex]['relativeUseCo2'] = 100 * useCo2 / totalCo2

            if self.generalSettings["maintenance"]:
                self.carData[carIndex]['relativeMaintenanceCo2'] = 100 * (totalCo2 - productionCo2 - useCo2) / totalCo2
            else:
                if self.carData[carIndex]['engineType'] == 'BEV':
                    batteryMaintenanceAtTH = src.Utilities.interp_data(
                        self.carData[carIndex]['xValues'],
                        self.carData[carIndex]['batteryReplacementLog'],
                        self.mileageAtEnd,
                        kind='nearest')
                    self.carData[carIndex]['relativeUseCo2'] = 100 * useCo2 / totalCo2
                    self.carData[carIndex]['relativeMaintenanceCo2'] = 100 * batteryMaintenanceAtTH / totalCo2
                else:
                    self.carData[carIndex]['relativeUseCo2'] = 100 * useCo2 / totalCo2
                    self.carData[carIndex]['relativeMaintenanceCo2'] = 100 * (totalCo2 - productionCo2 - useCo2) / totalCo2

        self.on_analysis_value_changed()

    def on_analysis_value_changed(self):
        # Populate BEP table
        # units = self.unit_combo.read()
        # self.table_widget_be.populate(units)

        # # Populate Specific Mileage/Age table if there is a value
        # value = self.specifyMileage_lineEdit.read()
        # if value:
        #     value = float(value) if units == 'km' else float(value) * \
        #         self.generalSettings['km2yearsConvFactor']
        #     if not self.specifyMileage_lineEdit.validate_numeric_input():
        #         if value >= self.currentCarData["mileage"]:
        #             self.table_widget_mileage.populate(units)
        #         else:
        #             error = "Please enter a mileage/age greater than the old car's value at the time of replacement."
        #             self.specifyMileage_lineEdit.clear()
        #             QMessageBox.warning(self, "Invalid Input", error)
        #             self.table_widget_mileage.populate_empty(units)
        #     else:
        #         self.table_widget_mileage.populate_empty(units)
        # else:
        #     self.table_widget_mileage.populate_empty(units)

        self.table_widget_eou.populate()

    def create_menu_bar(self):
        menubar = self.menuBar()
        menubar.setFixedHeight(32)

        # FILE MENU
        file_menu = menubar.addMenu("File")

        # Export Data action
        export_action = QAction(QIcon(resource_path("Icons/Export.png")), "Export Data", self)
        export_action.triggered.connect(self.try_export_data)
        file_menu.addAction(export_action)

        # HELP MENU
        help_menu = menubar.addMenu("Help")

        # Full documentation action with icon (now HTML)
        doc_icon = QIcon(resource_path("Icons/Help.png"))  # Adjust path if needed
        doc_action = QAction(doc_icon, "Full Documentation", self)
        html_path = resource_path("Data/Documentation/README.html")  # <-- HTML file path
        html_url = QUrl.fromLocalFile(os.path.abspath(html_path))
        doc_action.triggered.connect(lambda: QDesktopServices.openUrl(html_url))
        help_menu.addAction(doc_action)

        # Quick intro action with icon
        info_icon = QIcon(resource_path("Icons/Info.jpg"))  # Adjust if needed
        quick_intro_action = QAction(info_icon, "Quick Intro", self)
        quick_intro_action.triggered.connect(self.show_quick_intro_dialog)
        help_menu.addAction(quick_intro_action)

    def show_quick_intro_dialog(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Quick Intro")
        msg.setText(
            "Welcome to ECO Car Replacement Advisor!\n\n"
            "1. Fill in your current car details.\n"
            "2. Define the new cars to make comparisons with.\n"
            "3. Hit 'Compute Carbon Footprint' to start the analysis.\n\n"
            "Check the full documentation for more insights."
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowIcon(QIcon(resource_path("Icons/TitleIcon.ico")))
        msg.show()  # Non-blocking, no beep

    def renumber_cars(self):
        if self.cars:
            for i in range(len(self.cars)):
                car = self.cars[i]
                carNumber = i + 1
                car.carNumber_label.setText(f'Car {carNumber}:')

    def closeEvent(self, event):
        if hasattr(self, "plot_widget"):
            self.plot_widget.deleteLater()
        event.accept()

    def try_export_data(self):
        if self.computed:
            self.export_data()
        else:
            QMessageBox.information(
                self,
                "Data Not Ready",
                "Please run the analysis and compute the data before exporting.\n"
                "Once the data is computed, you will be able to export it."
            )

    def export_data(self):
        df_full = pd.DataFrame(self.carData)

        # Rename 'mileage' to 'mileageAtChange'
        df_full.rename(columns={"mileage": "mileageAtChange"}, inplace=True)

        # Add new column with the global maintenance setting
        df_full["maintenance"] = self.generalSettings.get("maintenance", False)
        df_full["EoUmileage"] = self.plot_widget.thMileage[1] * 1000
        df_full["EoUage"] = self.plot_widget.thAge[1]

        # Columns to exclude from export
        columns_to_exclude = [
            "xValues",
            "totalUsePhaseEmissions",
            "totalUsePhaseEmissionsPlusMaintenance",
            "emissionHystory",
            "batteryReplacementLog"
        ]
        df_export = df_full.drop(columns=columns_to_exclude, errors="ignore")

        # Add Car ID labels
        df_export.insert(0, "Car ID", ["Current"] + [f"Car {i}" for i in range(1, len(df_export))])

        # Move 'maintenance' to position 18 (zero-based)
        if "maintenance" in df_full.columns:
            col = df_export.pop("maintenance")
            df_export.insert(19, "maintenance", col)

        # Move 'keepEOL' to position 19
        if "keepEOL" in df_full.columns:
            col = df_export.pop("keepEOL")
            df_export.insert(20, "keepEOL", col)

        if "EoUmileage" in df_full.columns:
            col = df_export.pop("EoUmileage")
            df_export.insert(23, "EoUmileage", col)

        if "keepEOL" in df_full.columns:
            col = df_export.pop("EoUage")
            df_export.insert(24, "EoUage", col)

        # Open file dialog
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Data",
            "car_data_export.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )

        if not file_path:
            return  # User cancelled

        try:
            if file_path.endswith(".csv") or "CSV" in selected_filter:
                df_export.to_csv(file_path, index=False)
            else:
                if not file_path.endswith(".xlsx"):
                    file_path += ".xlsx"
                df_export.to_excel(file_path, index=False)

            QMessageBox.information(self, "Export Successful", f"Data successfully exported to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"An error occurred while exporting the data:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path(r"Icons/TitleIcon.ico")))
    app.setStyle("windows10")
    window = CarReplacementAdvisor()
    window.setWindowIcon(QIcon(resource_path(r"Icons/TitleIcon.ico")))
    window.show()

    window.showMaximized()

    app.exec()
    window.destroy()
    app.shutdown()
    sys.exit()
