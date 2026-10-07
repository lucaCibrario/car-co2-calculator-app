"""Build the replacement options interface."""

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from eco_car_advisor.resources import resource_path
from eco_car_advisor.ui.layout_helpers import set_layout_visible
from eco_car_advisor.ui.widgets.numeric_line_edit import NumericLineEdit
from eco_car_advisor.ui.widgets.stored_check_box import StoredCheckBox
from eco_car_advisor.ui.widgets.stored_combo_box import StoredComboBox


def build_replacement_options(form):
    parent = form.parent
    form.setWindowTitle("New Car Options")
    form.setWindowIcon(QIcon(resource_path("Icons/Options.png")))
    form.setFixedWidth(520)
    form.layout = QVBoxLayout()
    form.setLayout(form.layout)
    form.carSettings_groupBox = QGroupBox("Car Settings")
    form.batterySettings_groupBox = QGroupBox("Battery settings")
    form.carSettings_layout = QVBoxLayout(form.carSettings_groupBox)
    form.batterySettings_layout = QVBoxLayout(form.batterySettings_groupBox)
    form.carBaseDataLine = QHBoxLayout()
    form.secondHandLine = QHBoxLayout()
    form.secondHandMileageLine = QHBoxLayout()
    form.secondHandAgeLine = QHBoxLayout()
    form.eolLine = QHBoxLayout()
    form.eolLineBis = QHBoxLayout()
    form.massLine = QHBoxLayout()
    form.carProductionFootprintLine = QHBoxLayout()
    form.iceConsumptionLine = QHBoxLayout()
    form.bevConsumptionLine = QHBoxLayout()
    form.drivingShareLine = QHBoxLayout()
    form.batteryCapacityLine = QHBoxLayout()
    form.batteryProductionFootprintLine = QHBoxLayout()
    form.batteryLifeTimeLine = QHBoxLayout()
    form.saveLine = QHBoxLayout()
    form.WTTLine = QHBoxLayout()
    form.TTWLine = QHBoxLayout()
    buttonWidth = 240
    form.segments_comboBox = StoredComboBox("carSegment", parent.carSegments)
    form.segments_comboBox.write(form.parent.segments_comboBox.read())
    form.segments_comboBox.currentIndexChanged.connect(form.set_default_values)
    form.segments_comboBox.setFixedWidth(150)
    form.engineType_comboBox = StoredComboBox("engineType", parent.carEngineTypes, defaultIndex=2)
    form.engineType_comboBox.write(form.parent.engineType_comboBox.read())
    form.engineType_comboBox.setFixedWidth(150)
    form.engineType_comboBox.currentIndexChanged.connect(form.set_default_values_and_batteries)
    form.carBaseDataLine.setContentsMargins(0, 0, 0, 5)
    form.carBaseDataLine.addStretch()
    form.carBaseDataLine.addWidget(form.segments_comboBox)
    form.carBaseDataLine.addWidget(form.engineType_comboBox)
    form.carBaseDataLine.addStretch()
    secondHandCar_label = QLabel("Second-hand Car:")
    secondHandCar_label.setFixedWidth(buttonWidth)
    secondHandCarMileage_label = QLabel("Second-hand Car Mileage (km):")
    secondHandCarMileage_label.setFixedWidth(buttonWidth)
    secondHandCarAge_label = QLabel("Second-hand Car Age (years):")
    secondHandCarAge_label.setFixedWidth(buttonWidth)
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
    form.mass_button = QLabel("Car Mass (kg):")
    form.mass_button.setFixedWidth(buttonWidth)
    form.mass_lineEdit = NumericLineEdit(
        "massValue",
        placeHolderText="Enter car mass (kg)",
        validateLabel="Car mass (kg)",
        compulsory=False,
    )
    form.massLine.addWidget(form.mass_button)
    form.massLine.addWidget(form.mass_lineEdit)
    form.carProductionFootprint_label = QLabel("Car Production-EoL Footprint (kgCO₂/kg):")
    form.carProductionFootprint_label.setFixedWidth(buttonWidth)
    form.carProductionFootprint_lineEdit = NumericLineEdit(
        "carProductionFootprint",
        validateLabel="Car Production-EoL Footprint (kgCO₂/kg)",
        compulsory=False,
    )
    form.carProductionFootprintLine.addWidget(form.carProductionFootprint_label)
    form.carProductionFootprintLine.addWidget(form.carProductionFootprint_lineEdit)
    WTT_label = QLabel("WTT Fuel Footprint (gCO₂/l):")
    WTT_label.setFixedWidth(buttonWidth)
    form.WTT_lineEdit = NumericLineEdit(
        "WTT", validateLabel="WTT Fuel Footprint (gCO₂/l)", compulsory=False
    )
    TTW_label = QLabel("TTW Fuel Footprint (gCO₂/l):")
    TTW_label.setFixedWidth(buttonWidth)
    form.TTW_lineEdit = NumericLineEdit(
        "TTW", validateLabel="TTW Fuel Footprint (gCO₂/l)", compulsory=False
    )
    form.WTTLine.addWidget(WTT_label)
    form.WTTLine.addWidget(form.WTT_lineEdit)
    form.TTWLine.addWidget(TTW_label)
    form.TTWLine.addWidget(form.TTW_lineEdit)
    form.mean_consumption_liter = NumericLineEdit(
        "meanConsumptionLiter",
        validateLabel="ICE Consumption (l/100km)",
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
    form.mean_consumption_label = QLabel("ICE Consumption (l/100km):")
    form.mean_consumption_label.setFixedWidth(buttonWidth)
    form.mean_consumption_emptyLabel = QLabel("EM Consumption (kWh/100km):")
    form.mean_consumption_emptyLabel.setFixedWidth(buttonWidth)
    form.drivingShare_label = QLabel("Driving Share (Plug-in Hybrid only):")
    form.drivingShare_label.setFixedWidth(buttonWidth)
    form.iceConsumptionLine.addWidget(form.mean_consumption_label)
    form.iceConsumptionLine.addWidget(form.mean_consumption_liter)
    form.bevConsumptionLine.addWidget(form.mean_consumption_emptyLabel)
    form.bevConsumptionLine.addWidget(form.mean_consumption_Wh)
    form.drivingShareLine.addWidget(form.drivingShare_label)
    form.drivingShareLine.addWidget(form.drivingShare_lineEdit)
    capacity_label = QLabel("Battery Capacity (kWh):")
    capacity_label.setFixedWidth(buttonWidth)
    capacity_label.setFixedWidth(buttonWidth)
    form.capacity_lineEdit = NumericLineEdit(
        "batteryCapacity",
        placeHolderText="",
        validateLabel="Battery Capacity (kWh)",
        compulsory=False,
    )
    form.batteryCapacityLine.addWidget(capacity_label)
    form.batteryCapacityLine.addWidget(form.capacity_lineEdit)
    batteryProductionFootprint_label = QLabel("Battery Production Footprint (kgCO₂/kWh):")
    batteryProductionFootprint_label.setFixedWidth(buttonWidth)
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
    batteryLifeTime_label.setFixedWidth(buttonWidth)
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
    form.reset_button = QPushButton("Reset")
    form.reset_button.setToolTip("Click to reset to default settings.")
    form.reset_button.setFixedWidth(100)
    form.reset_button.clicked.connect(form.reset_to_defaults)
    form.save_button = QPushButton("Save")
    form.save_button.setToolTip("Click to save the current settings.")
    form.save_button.setFixedWidth(100)
    form.save_button.setDefault(True)
    form.save_button.clicked.connect(form.validate_and_accept)
    form.saveLine.addStretch()
    form.saveLine.addWidget(form.reset_button)
    form.saveLine.addWidget(form.save_button)
    form.saveLine.addStretch()
    form.saveLine.setContentsMargins(5, 5, 5, 5)
    form.carSettings_layout.addLayout(form.carBaseDataLine)
    form.carSettings_layout.addLayout(form.secondHandLine)
    form.carSettings_layout.addLayout(form.secondHandMileageLine)
    form.carSettings_layout.addLayout(form.secondHandAgeLine)
    form.carSettings_layout.addLayout(form.iceConsumptionLine)
    form.carSettings_layout.addLayout(form.bevConsumptionLine)
    form.carSettings_layout.addLayout(form.drivingShareLine)
    form.carSettings_layout.addLayout(form.massLine)
    form.carSettings_layout.addLayout(form.carProductionFootprintLine)
    form.carSettings_layout.addLayout(form.WTTLine)
    form.carSettings_layout.addLayout(form.TTWLine)
    form.batterySettings_layout.addLayout(form.batteryCapacityLine)
    form.batterySettings_layout.addLayout(form.batteryProductionFootprintLine)
    form.batterySettings_layout.addLayout(form.batteryLifeTimeLine)
    form.layout.addWidget(form.carSettings_groupBox)
    form.layout.addWidget(form.batterySettings_groupBox)
    form.layout.addLayout(form.saveLine)
    form.editableWidgets = [
        form.segments_comboBox,
        form.engineType_comboBox,
        form.secondHandCar_button,
        form.secondHandCarMileage_lineEdit,
        form.secondHandCarAge_lineEdit,
        form.mass_lineEdit,
        form.carProductionFootprint_lineEdit,
        form.mean_consumption_liter,
        form.mean_consumption_Wh,
        form.drivingShare_lineEdit,
        form.capacity_lineEdit,
        form.batteryProductionFootprint_lineEdit,
        form.batteryLifeTime_lineEdit,
        form.WTT_lineEdit,
        form.TTW_lineEdit,
    ]
    form.set_tooltips()
    form.set_default_values()
    form.state()
    form.initial_state = form.current_state.copy()
