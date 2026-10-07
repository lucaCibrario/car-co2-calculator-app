"""Build the current car form interface."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from eco_car_advisor.ui.layout_helpers import set_layout_visible
from eco_car_advisor.ui.widgets.numeric_line_edit import NumericLineEdit
from eco_car_advisor.ui.widgets.stored_check_box import StoredCheckBox
from eco_car_advisor.ui.widgets.stored_combo_box import StoredComboBox


def build_current_car_form(form):
    parent = form.parent
    form.setTitle("Current Car Details")
    form.setFixedHeight(220)
    input_form_layout = QFormLayout()
    form.setFixedWidth(parent.leftGroupWidth)
    segments_label = QLabel("Car Segment:")
    segments_label.setFixedWidth(parent.rightLabelsWidth)
    form.segments_comboBox = StoredComboBox("carSegment", form.carSegments)
    form.segments_comboBox.currentIndexChanged.connect(form.set_default_values)
    form.segments_comboBox.setFixedHeight(parent.comboBoxHeight)
    input_form_layout.addRow(segments_label, form.segments_comboBox)
    form.engineType_comboBox = StoredComboBox("engineType", form.carEngineTypes, defaultIndex=2)
    form.engineType_comboBox.currentIndexChanged.connect(form.set_default_values_and_batteries)
    form.engineType_comboBox.setFixedHeight(parent.comboBoxHeight)
    input_form_layout.addRow(QLabel("Engine Type:"), form.engineType_comboBox)
    form.currentMileage_lineEdit = NumericLineEdit(
        "mileage",
        placeHolderText="Enter mileage (compulsory)",
        validateLabel="Current Mileage (km)",
    )
    form.currentMileage_lineEdit.setFixedHeight(parent.comboBoxHeight)
    form.currentMileage_lineEdit.valueChanged.connect(form.validate_current_mileage)
    input_form_layout.addRow(QLabel("Current Mileage (km):"), form.currentMileage_lineEdit)
    energyMix_width = 115
    country_HBoxLayout = QHBoxLayout()
    form.country_comboBox = StoredComboBox("country", form.countries)
    form.country_comboBox.setFixedHeight(parent.comboBoxHeight)
    form.country_comboBox.currentIndexChanged.connect(form.update_energy_mix)
    form.energyMix_lineEdit = NumericLineEdit(
        "energyMix",
        placeHolderText="Enter energy mix",
        validateLabel="Energy mix (gCO₂/kWh)",
        compulsory=True,
    )
    form.energyMix_lineEdit.setFixedWidth(energyMix_width)
    form.energyMix_lineEdit.setReadOnly(True)
    form.energyMix_lineEdit.setStyleSheet("background-color: lightgrey;")
    country_HBoxLayout.addWidget(form.country_comboBox)
    country_HBoxLayout.addWidget(form.energyMix_lineEdit)
    input_form_layout.addRow(QLabel("Energy mix (gCO₂/kWh):"), country_HBoxLayout)
    advancedSettings_HBoxLayout = QHBoxLayout()
    advancedSettings_HBoxLayout.setContentsMargins(0, 5, 5, 0)
    advancedSettings_label = QLabel("Advanced Settings")
    form.advancedSettings_button = QPushButton("▼")
    form.advancedSettings_button.setFixedSize(20, 20)
    form.advancedSettings_button.setStyleSheet(
        "\n        QPushButton {\n            border: none;\n            border-radius: 10px;  /* Half of 30 = circle */\n            background-color: #e0e0e0;\n        }\n        QPushButton:hover {\n            background-color: #c8c8c8;\n        }\n    "
    )
    advancedSettings_HBoxLayout.addWidget(form.advancedSettings_button)
    advancedSettings_HBoxLayout.addWidget(advancedSettings_label)
    input_form_layout.addRow(advancedSettings_HBoxLayout)
    form.advancedSettings_button.clicked.connect(form.toggle_panel)
    form.popup_panel = QFrame(form, Qt.Tool | Qt.FramelessWindowHint)
    form.popup_panel.setFixedWidth(parent.leftGroupWidth)
    form.popup_panel.setFrameShape(QFrame.StyledPanel)
    form.popup_panel.setObjectName("popupPanel")
    form.popup_panel.setStyleSheet(
        "\n        #popupPanel {\n            border: 1px solid #ccc;\n            border-radius: 4px;\n        }\n    "
    )
    form.popup_panel.hide()
    advancedSettingsPanel_layout = QVBoxLayout(form.popup_panel)
    advancedSettingsPanel_layout.setContentsMargins(15, 15, 15, 15)
    form.baseData_groupBox = QGroupBox("Car Settings")
    form.batteryData_groupBox = QGroupBox("BEV Battery Settings")
    form.baseData_layout = QVBoxLayout(form.baseData_groupBox)
    form.batteryData_layout = QVBoxLayout(form.batteryData_groupBox)
    form.massLine = QHBoxLayout()
    form.carProductionFootprintLine = QHBoxLayout()
    form.WTTLine = QHBoxLayout()
    form.TTWLine = QHBoxLayout()
    form.iceConsumptionLine = QHBoxLayout()
    form.bevConsumptionLine = QHBoxLayout()
    form.drivingShareLine = QHBoxLayout()
    form.batteryCapacityLine = QHBoxLayout()
    form.batteryProductionFootprintLine = QHBoxLayout()
    form.batteryLifeTimeLine = QHBoxLayout()
    form.secondHandLine = QHBoxLayout()
    form.secondHandMileageLine = QHBoxLayout()
    form.secondHandAgeLine = QHBoxLayout()
    form.WTTLine = QHBoxLayout()
    form.TTWLine = QHBoxLayout()
    advancedSettingsLeftWidgetWidth = parent.rightLabelsWidth + 15
    secondHandCar_label = QLabel("Second-hand Car:")
    secondHandCar_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
    secondHandCarMileage_label = QLabel("Second-hand Car Mileage (km):")
    secondHandCarMileage_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
    secondHandCarAge_label = QLabel("Second-hand Car Age (years):")
    secondHandCarAge_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
    form.secondHandCar_button = StoredCheckBox(variableLabel="secondHandCar", defaultValue=False)
    form.secondHandCar_button.stateChanged.connect(form.toggle_line_edit_secondHandCar)
    form.secondHandCarMileage_lineEdit = NumericLineEdit(
        "secondHandCarMileage",
        placeHolderText="Enter car mileage",
        validateLabel="Second-hand car mileage (km)",
        compulsory=False,
    )
    form.secondHandCarMileage_lineEdit.setReadOnly(True)
    form.secondHandCarMileage_lineEdit.setStyleSheet("background-color: lightgrey;")
    form.secondHandCarAge_lineEdit = NumericLineEdit(
        "secondHandCarAge",
        placeHolderText="Enter car age",
        validateLabel="Second-hand car age (years)",
        compulsory=False,
    )
    form.secondHandCarAge_lineEdit.setReadOnly(True)
    form.secondHandCarAge_lineEdit.setStyleSheet("background-color: lightgrey;")
    form.secondHandLine.addWidget(secondHandCar_label)
    form.secondHandLine.addWidget(form.secondHandCar_button)
    form.secondHandMileageLine.addWidget(secondHandCarMileage_label)
    form.secondHandMileageLine.addWidget(form.secondHandCarMileage_lineEdit)
    form.secondHandAgeLine.addWidget(secondHandCarAge_label)
    form.secondHandAgeLine.addWidget(form.secondHandCarAge_lineEdit)
    set_layout_visible(form.secondHandMileageLine, False)
    set_layout_visible(form.secondHandAgeLine, False)
    meanConsumptionLiter_label = QLabel("ICE Consumption (l/100km):")
    meanConsumptionLiter_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
    meanConsumptionWh_label = QLabel("EM Consumption (kWh/100km):")
    meanConsumptionWh_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
    meanDrivingShare_label = QLabel("Driving Share (Plug-in Hybrid only):")
    meanDrivingShare_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
    form.mean_consumption_liter = NumericLineEdit(
        "meanConsumptionLiter",
        validateLabel="ICE consumption (l/100km)",
        compulsory=False,
    )
    form.mean_consumption_Wh = NumericLineEdit(
        "meanConsumptionWh",
        validateLabel="EM Consumption (kWh/100km)",
        compulsory=False,
    )
    form.drivingShare_lineEdit = NumericLineEdit(
        "drivingShare",
        validateLabel="Driving Share (Plug-in Hybrid only)",
        compulsory=False,
        upperLimit=1,
    )
    form.iceConsumptionLine.addWidget(meanConsumptionLiter_label)
    form.iceConsumptionLine.addWidget(form.mean_consumption_liter)
    form.bevConsumptionLine.addWidget(meanConsumptionWh_label)
    form.bevConsumptionLine.addWidget(form.mean_consumption_Wh)
    form.drivingShareLine.addWidget(meanDrivingShare_label)
    form.drivingShareLine.addWidget(form.drivingShare_lineEdit)
    mass_label = QLabel("Car Mass (kg):")
    mass_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
    form.mass_lineEdit = NumericLineEdit(
        "massValue", validateLabel="Car mass (kg)", compulsory=False
    )
    form.massLine.addWidget(mass_label)
    form.massLine.addWidget(form.mass_lineEdit)
    carProductionFootprint_label = QLabel("Car Production-EoL Footprint (kgCO₂/kg):")
    carProductionFootprint_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
    form.carProductionFootprint_lineEdit = NumericLineEdit(
        "carProductionFootprint",
        validateLabel="Car Production-EoL Footprint (kgCO₂/kg)",
        compulsory=False,
    )
    form.carProductionFootprintLine.addWidget(carProductionFootprint_label)
    form.carProductionFootprintLine.addWidget(form.carProductionFootprint_lineEdit)
    WTT_label = QLabel("WTT Fuel Footprint (gCO₂/l):")
    WTT_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
    form.WTT_lineEdit = NumericLineEdit(
        "WTT", validateLabel="WTT Fuel Footprint (gCO₂/l)", compulsory=False
    )
    TTW_label = QLabel("TTW Fuel Footprint (gCO₂/l):")
    TTW_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
    form.TTW_lineEdit = NumericLineEdit(
        "TTW", validateLabel="TTW Fuel Footprint (gCO₂/l)", compulsory=False
    )
    form.WTTLine.addWidget(WTT_label)
    form.WTTLine.addWidget(form.WTT_lineEdit)
    form.TTWLine.addWidget(TTW_label)
    form.TTWLine.addWidget(form.TTW_lineEdit)
    form.baseData_layout.addLayout(form.secondHandLine)
    form.baseData_layout.addLayout(form.secondHandMileageLine)
    form.baseData_layout.addLayout(form.secondHandAgeLine)
    form.baseData_layout.addLayout(form.iceConsumptionLine)
    form.baseData_layout.addLayout(form.bevConsumptionLine)
    form.baseData_layout.addLayout(form.drivingShareLine)
    form.baseData_layout.addLayout(form.massLine)
    form.baseData_layout.addLayout(form.carProductionFootprintLine)
    form.baseData_layout.addLayout(form.WTTLine)
    form.baseData_layout.addLayout(form.TTWLine)
    form.baseData_groupBox.setLayout(form.baseData_layout)
    capacity_label = QLabel("Battery Capacity (kWh):")
    capacity_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
    form.capacity_lineEdit = NumericLineEdit(
        "batteryCapacity",
        placeHolderText="",
        validateLabel="Battery Capacity (kWh)",
        compulsory=False,
    )
    form.batteryCapacityLine.addWidget(capacity_label)
    form.batteryCapacityLine.addWidget(form.capacity_lineEdit)
    batteryProductionFootprint_label = QLabel("Battery Production Footprint (kgCO₂/kWh):")
    batteryProductionFootprint_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
    form.batteryProductionFootprint_lineEdit = NumericLineEdit(
        "batteryProductionFootprint",
        text=form.data["batteries"]["kgco2/kWh"],
        placeHolderText="",
        validateLabel="Production Footprint (kgCO₂/kWh)",
        compulsory=True,
    )
    form.batteryProductionFootprintLine.addWidget(batteryProductionFootprint_label)
    form.batteryProductionFootprintLine.addWidget(form.batteryProductionFootprint_lineEdit)
    batteryLifeTime_label = QLabel("Estimated life time (km):")
    batteryLifeTime_label.setFixedWidth(advancedSettingsLeftWidgetWidth)
    form.batteryLifeTime_lineEdit = NumericLineEdit(
        "batteryLifeTime",
        placeHolderText="",
        validateLabel="Estimated life time (km):",
        compulsory=False,
    )
    form.batteryLifeTime_lineEdit.valueChanged.connect(form.on_batteryLifeTime_modified)
    form.batteryLifeTimeLine.addWidget(batteryLifeTime_label)
    form.batteryLifeTimeLine.addWidget(form.batteryLifeTime_lineEdit)
    form.batteryLifeTime_modified = False
    form.batteryData_layout.addLayout(form.batteryCapacityLine)
    form.batteryData_layout.addLayout(form.batteryProductionFootprintLine)
    form.batteryData_layout.addLayout(form.batteryLifeTimeLine)
    form.batteryData_groupBox.setLayout(form.batteryData_layout)
    advancedSettingsPanel_layout.addWidget(form.baseData_groupBox)
    advancedSettingsPanel_layout.addWidget(form.batteryData_groupBox)
    resetHBox = QHBoxLayout()
    form.reset_button = QPushButton("Reset")
    form.reset_button.setToolTip("Click to reset to default settings.")
    form.reset_button.setFixedWidth(100)
    form.reset_button.clicked.connect(form.reset_to_default)
    resetHBox.addStretch()
    resetHBox.addWidget(form.reset_button)
    resetHBox.addStretch()
    input_form_layout.addRow(resetHBox)
    form.setLayout(input_form_layout)
    form.editableWidgets = [
        form.segments_comboBox,
        form.engineType_comboBox,
        form.currentMileage_lineEdit,
        form.secondHandCar_button,
        form.secondHandCarMileage_lineEdit,
        form.secondHandCarAge_lineEdit,
        form.mass_lineEdit,
        form.carProductionFootprint_lineEdit,
        form.mean_consumption_liter,
        form.mean_consumption_Wh,
        form.drivingShare_lineEdit,
        form.country_comboBox,
        form.energyMix_lineEdit,
        form.capacity_lineEdit,
        form.batteryProductionFootprint_lineEdit,
        form.batteryLifeTime_lineEdit,
        form.WTT_lineEdit,
        form.TTW_lineEdit,
    ]
    form.set_tooltips()
    form.update_defaults()
    form.state()
