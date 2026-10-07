"""Main desktop window and user actions."""

import os

from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction, QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
)

from eco_car_advisor.data import DataRepository, load_assumptions
from eco_car_advisor.export import build_export_frame, write_export
from eco_car_advisor.resources import resource_path
from eco_car_advisor.ui.analysis_actions import AnalysisActions
from eco_car_advisor.ui.main_window_layout import build_main_window
from eco_car_advisor.ui.replacement_car import Car
from eco_car_advisor.ui.tooltips import tooltips


class CarReplacementAdvisor(AnalysisActions, QMainWindow):
    def __init__(self):
        super().__init__()
        self.computed = False
        self.generalSettings = {}
        assumptions = load_assumptions()
        self.countries = assumptions["countries"]
        self.carSegments = assumptions["car_segments"]
        self.carEngineTypes = assumptions["engine_types"]
        self.maxWindowYears = assumptions["max_window_years"]
        self.data = DataRepository().load()
        self.tooltip_dict = tooltips()
        self.cars = []
        build_main_window(self)

    def toggle_line_edit_keepEOL(self, state):
        """Enable or disable mileage input based on checkbox state."""
        if state:
            self.keepEOL_lineEdit.clear()
            self.keepEOL_lineEdit.setStyleSheet("background-color: lightgrey;")
        else:
            self.keepEOL_lineEdit.setStyleSheet("")
            self.keepEOL_lineEdit.write("")
            self.keepEOL_lineEdit.update_stored_value("")
        self.keepEOL_lineEdit.setReadOnly(state)
        self.keepEOL_lineEdit.set_compulsory(not state)
        self.keepEOL_comboBox.setEnabled(not state)

    def read_general_settings(self):
        self.generalSettings = self.generalOptionsDialog.read()
        self.generalSettings["km2yearsConvFactor"] = float(self.km2yearsConvFactorLineEdit.read())
        self.generalSettings["maintenance"] = self.maintenanceCheckBox.read()
        if self.generalSettings["maintenance"].lower() == "yes":
            self.generalSettings["maintenance"] = True
        else:
            self.generalSettings["maintenance"] = False

    def show_plot(self):
        units = self.unit_combo.read()
        if units == "km":
            self.plot_widget.show_plot_kilometers()
        else:
            self.plot_widget.show_plot_years()

    def on_analysis_units_changed(self):
        self.show_plot()
        self.show_table()

    def show_table(self):
        self.table_widget_eou.show()

    def update_expected_life(self):
        self.read_general_settings()
        self.currentCarBox.batteryLifeTime_lineEdit.update_default_value(
            f"{self.generalSettings['BEVlifeSpan']:.0f}"
        )
        if not self.currentCarBox.batteryLifeTime_modified:
            self.currentCarBox.batteryLifeTime_lineEdit.write(
                f"{self.generalSettings['BEVlifeSpan']:.0f}"
            )
            self.currentCarBox.batteryLifeTime_lineEdit.save()
        if self.cars:
            for car in self.cars:
                car.dialog.batteryLifeTime_lineEdit.update_default_value(
                    f"{self.generalSettings['BEVlifeSpan']:.0f}"
                )
                if not car.dialog.batteryLifeTime_modified:
                    car.dialog.batteryLifeTime_lineEdit.write(
                        f"{self.generalSettings['BEVlifeSpan']:.0f}"
                    )
                    car.dialog.batteryLifeTime_lineEdit.save()
        self.oldGeneralSettings = self.generalSettings.copy()

    def display_general_options_dialog(self):
        """Opens the options window."""
        self.generalOptionsDialog.exec()

    def add_new_car(self):
        """Add a new car input section."""
        car = Car(self.carSegments, self.carEngineTypes, parent=self)
        self.new_car_layout.addWidget(car)
        self.cars.append(car)
        self.update_expected_life()

    def remove_car(self, car):
        """Removes the given Car instance from the UI and list."""
        if car in self.cars:
            self.cars.remove(car)
        car.deleteLater()

    def create_menu_bar(self):
        menubar = self.menuBar()
        menubar.setFixedHeight(32)
        file_menu = menubar.addMenu("File")
        export_action = QAction(QIcon(resource_path("Icons/Export.png")), "Export Data", self)
        export_action.triggered.connect(self.try_export_data)
        file_menu.addAction(export_action)
        help_menu = menubar.addMenu("Help")
        doc_icon = QIcon(resource_path("Icons/Help.png"))
        doc_action = QAction(doc_icon, "Full Documentation", self)
        html_path = resource_path("Data/Documentation/README.html")
        html_url = QUrl.fromLocalFile(os.path.abspath(html_path))
        doc_action.triggered.connect(lambda: QDesktopServices.openUrl(html_url))
        help_menu.addAction(doc_action)
        info_icon = QIcon(resource_path("Icons/Info.jpg"))
        quick_intro_action = QAction(info_icon, "Quick Intro", self)
        quick_intro_action.triggered.connect(self.show_quick_intro_dialog)
        help_menu.addAction(quick_intro_action)

    def show_quick_intro_dialog(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Quick Intro")
        msg.setText(
            "Welcome to ECO Car Replacement Advisor!\n\n1. Fill in your current car details.\n2. Define the new cars to make comparisons with.\n3. Hit 'Compute Carbon Footprint' to start the analysis.\n\nCheck the full documentation for more insights."
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowIcon(QIcon(resource_path("Icons/TitleIcon.ico")))
        msg.show()

    def renumber_cars(self):
        if self.cars:
            for i in range(len(self.cars)):
                car = self.cars[i]
                carNumber = i + 1
                car.carNumber_label.setText(f"Car {carNumber}:")

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
                "Please run the analysis and compute the data before exporting.\nOnce the data is computed, you will be able to export it.",
            )

    def export_data(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Data",
            "car_data_export.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv)",
        )
        if not file_path:
            return
        try:
            frame = build_export_frame(self.analysis_result)
            saved_path = write_export(frame, file_path, selected_filter)
            QMessageBox.information(
                self,
                "Export Successful",
                f"Data successfully exported to:\n{saved_path}",
            )
        except (OSError, ValueError, ImportError) as error:
            QMessageBox.critical(self, "Export Failed", f"Export failed:\n{error}")
