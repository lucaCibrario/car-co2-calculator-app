"""Build the main window interface."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from eco_car_advisor.data import load_assumptions
from eco_car_advisor.resources import resource_path
from eco_car_advisor.ui.current_car import CurrentCar
from eco_car_advisor.ui.end_of_usage_table import TableWidgetEOU
from eco_car_advisor.ui.general_options import GeneralOptionsDialog
from eco_car_advisor.ui.labels import ConfidentialLabel
from eco_car_advisor.ui.plot_widget import PlotlyWidget
from eco_car_advisor.ui.widgets.numeric_line_edit import NumericLineEdit
from eco_car_advisor.ui.widgets.stored_check_box import StoredCheckBox
from eco_car_advisor.ui.widgets.stored_combo_box import StoredComboBox


def build_main_window(window):
    window.setWindowTitle("ECO Car Replacement Advisor")
    window.setWindowIcon(QIcon(resource_path("Icons/TitleIcon.jpg")))
    window.setGeometry(100, 50, 1200, 700)
    central_container = QWidget()
    central_vlayout = QVBoxLayout(central_container)
    central_vlayout.setContentsMargins(0, 0, 0, 0)
    central_vlayout.setSpacing(5)
    separator_line = QFrame()
    separator_line.setFrameShape(QFrame.HLine)
    separator_line.setFrameShadow(QFrame.Plain)
    separator_line.setStyleSheet("color: lightgray; background-color: lightgray;")
    separator_line.setFixedHeight(1)
    central_vlayout.addWidget(separator_line)
    central_widget = QWidget()
    main_layout = QHBoxLayout(central_widget)
    main_layout.setContentsMargins(10, 0, 10, 10)
    main_layout.setSpacing(6)
    central_vlayout.addWidget(central_widget)
    window.setCentralWidget(central_container)
    form_layout = QVBoxLayout()
    result_layout = QVBoxLayout()
    label = ConfidentialLabel("CONFIDENTIAL: This tool is for FAAS members only")
    form_layout.addWidget(label)
    window.create_menu_bar()
    window.defaultKm2YearsConvFactor = load_assumptions()["default_annual_mileage_km"]
    window.km2yearsConvFactorLineEdit = NumericLineEdit(
        "km2yearsConvFactor",
        text=str(window.defaultKm2YearsConvFactor),
        validateLabel="Average Annual Mileage (km)",
    )
    window.km2yearsConvFactorLineEdit.setToolTip(window.tooltip_dict["km2yearsConvFactor"])
    window.maintenanceCheckBox = StoredComboBox(variableLabel="maintenance", items=["Yes", "No"])
    window.maintenanceCheckBox.setToolTip(window.tooltip_dict["maintenance"])
    window.generalOptionsDialog = GeneralOptionsDialog(window)
    window.read_general_settings()
    window.rightLabelsWidth = 220
    window.leftLabelsWidth = 180
    window.comboBoxHeight = 25
    window.leftGroupWidth = 475
    window.currentCarBox = CurrentCar(window)
    form_layout.addWidget(window.currentCarBox)
    new_car_group = QGroupBox("New Car(s)")
    new_car_group.setFixedWidth(window.leftGroupWidth)
    window.new_car_layout = QVBoxLayout()
    window.new_car_layout.setAlignment(Qt.AlignTop)
    window.new_car_layout.setContentsMargins(0, 0, 0, 0)
    new_car_group_layout = QVBoxLayout()
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area_container_widget = QWidget()
    scroll_area_container_widget.setLayout(window.new_car_layout)
    new_car_group.setLayout(new_car_group_layout)
    scroll_area.setWidget(scroll_area_container_widget)
    new_car_group_layout.addWidget(scroll_area)
    button_layout = QHBoxLayout()
    add_car_label = QLabel("Add Car")
    add_car_button = QPushButton()
    add_car_button.setIcon(QIcon(resource_path("Icons/Plus.jpg")))
    add_car_button.setToolTip("Click to add a new car to the analysis.")
    add_car_button.setFixedSize(32, 32)
    add_car_button.clicked.connect(window.add_new_car)
    button_layout.addWidget(add_car_button)
    button_layout.addWidget(add_car_label)
    button_layout.addStretch()
    new_car_group_layout.insertLayout(0, button_layout)
    window.add_new_car()
    form_layout.addWidget(new_car_group)
    settings_group = QGroupBox("Analysis Settings")
    settings_group.setFixedHeight(160)
    settings_group.setFixedWidth(window.leftGroupWidth)
    settings_form_layout = QVBoxLayout()
    window.km2yearsConvFactorLabel = QLabel("Average Annual Mileage (km):")
    window.km2yearsConvFactorLabel.setFixedWidth(window.rightLabelsWidth)
    window.km2yearsConvFactorLineEdit.setFixedHeight(window.comboBoxHeight)
    window.generalOptionsButton = QPushButton()
    window.generalOptionsButton.setIcon(QIcon(resource_path("Icons/Options.png")))
    window.generalOptionsButton.setToolTip("Click for more analysis settings.")
    window.generalOptionsButton.setFixedSize(32, 32)
    window.generalOptionsButton.clicked.connect(window.display_general_options_dialog)
    settingsFirstLine_layout = QHBoxLayout()
    settingsFirstLine_layout.setAlignment(Qt.AlignVCenter)
    settingsFirstLine_layout.addWidget(window.km2yearsConvFactorLabel)
    settingsFirstLine_layout.addWidget(window.km2yearsConvFactorLineEdit)
    settingsFirstLine_layout.addWidget(window.generalOptionsButton)
    eolLine = QHBoxLayout()
    eolLineBis = QHBoxLayout()
    window.keepEOL_label = QLabel("Intended end-of-usage (mileage/age):")
    window.keepEOL_button = StoredCheckBox(
        variableLabel="keepEOL", text="Keep until EoL", defaultValue=True
    )
    window.keepEOL_label.setFixedWidth(window.rightLabelsWidth)
    window.keepEOL_button.stateChanged.connect(window.toggle_line_edit_keepEOL)
    window.keepEOL_emptyLabel = QLabel()
    window.keepEOL_emptyLabel.setFixedWidth(window.rightLabelsWidth)
    window.keepEOL_lineEdit = NumericLineEdit(
        "keepLifeSpan",
        placeHolderText="Enter estimated life time",
        validateLabel="Intended end-of-usage (km/years)",
        compulsory=not window.keepEOL_button.read(),
    )
    window.keepEOL_lineEdit.setReadOnly(True)
    window.keepEOL_lineEdit.setStyleSheet("background-color: lightgrey;")
    window.keepEOL_comboBox = StoredComboBox("keepUnits", items=["years", "km"])
    window.keepEOL_comboBox.setEnabled(False)
    window.keepEOL_comboBox.setFixedWidth(70)
    window.keepEOL_comboBox.setFixedHeight(window.comboBoxHeight)
    eolLine.addWidget(window.keepEOL_label)
    eolLine.addWidget(window.keepEOL_button)
    eolLineBis.addWidget(window.keepEOL_emptyLabel)
    eolLineBis.addWidget(window.keepEOL_lineEdit)
    eolLineBis.addWidget(window.keepEOL_comboBox)
    settingsSecondLine_layout = QHBoxLayout()
    settingsSecondLine_layout.setAlignment(Qt.AlignLeft)
    window.maintenanceLabel = QLabel("Maintenance:")
    window.maintenanceLabel.setFixedWidth(window.rightLabelsWidth)
    window.maintenanceCheckBox.setFixedWidth(70)
    window.maintenanceCheckBox.setFixedHeight(window.comboBoxHeight)
    settingsSecondLine_layout.addWidget(window.maintenanceLabel)
    settingsSecondLine_layout.addWidget(window.maintenanceCheckBox)
    settings_form_layout.addLayout(settingsFirstLine_layout)
    settings_form_layout.addLayout(eolLine)
    settings_form_layout.addLayout(eolLineBis)
    settings_form_layout.addLayout(settingsSecondLine_layout)
    settings_group.setLayout(settings_form_layout)
    form_layout.addWidget(settings_group)
    compute_button_layout = QHBoxLayout()
    compute_button_layout.setAlignment(Qt.AlignCenter)
    compute_button_layout.setContentsMargins(5, 5, 5, 5)
    compute_button = QPushButton("Compute Carbon Footprint")
    compute_button.setToolTip("Click to start the analysis.")
    compute_button.clicked.connect(window.plot_carbon_footprint)
    compute_button.setFont(QFont("Arial", 12, QFont.Bold))
    compute_button.setFixedWidth(250)
    compute_button.setFixedHeight(40)
    compute_button_layout.addWidget(compute_button)
    form_layout.addLayout(compute_button_layout)
    output_group = QGroupBox("Carbon Footprint Analysis")
    output_layout = QVBoxLayout()
    analysisUnits_layout = QHBoxLayout()
    analysisTables_layout = QHBoxLayout()
    unit_label = QLabel("Analysis Units:")
    unit_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    window.unit_combo = StoredComboBox("analysisUnits", ["years", "km"])
    window.unit_combo.setToolTip("Choose the output units for the analysis.")
    window.unit_combo.setFixedWidth(80)
    window.unit_combo.setFixedHeight(window.comboBoxHeight)
    window.unit_combo.currentTextChanged.connect(window.on_analysis_units_changed)
    analysisUnits_layout.addWidget(unit_label)
    analysisUnits_layout.addWidget(window.unit_combo)
    analysisUnits_layout.addStretch()
    analysisUnits_layout.setContentsMargins(0, 0, 0, 0)
    analysis_label = QLabel("Output data analysis at end-of-usage (EoU):")
    analysisTables_layout.addWidget(analysis_label)
    analysisTables_layout.addStretch()
    window.plot_widget = PlotlyWidget(parent=window)
    window.plot_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    window.plot_widget.initialize_empty_plots()
    window.table_widget_eou = TableWidgetEOU(window)
    window.table_widget_eou.populate_empty()
    output_layout.addLayout(analysisUnits_layout)
    output_layout.addWidget(window.plot_widget)
    output_layout.addLayout(analysisTables_layout)
    output_layout.addWidget(window.table_widget_eou)
    output_group.setLayout(output_layout)
    result_layout.addWidget(output_group)
    main_layout.addLayout(form_layout, 2)
    main_layout.addLayout(result_layout, 3)
    window.update_expected_life()
    window.show_plot()
    window.show_table()
    window.read_general_settings()
