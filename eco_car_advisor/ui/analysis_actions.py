"""Main-window actions for validating and running an analysis."""

from PySide6.QtWidgets import QMessageBox

from eco_car_advisor.analysis import AnalysisEngine, AnalysisInputError


class AnalysisActions:
    """Bridge validated widget values to the Qt-independent analysis engine."""

    def plot_carbon_footprint(self) -> None:
        """Validate inputs, calculate a scenario, and refresh the result views."""
        if not self._validate_analysis_inputs():
            self._clear_analysis()
            return

        self.computed = False
        self.read_general_settings()
        settings = dict(self.generalSettings)
        settings["keepEOL"] = bool(self.keepEOL_button.read())
        settings["keepLifeSpan"] = (
            float(self.keepEOL_lineEdit.read()) if self.keepEOL_lineEdit.read() else None
        )
        settings["keepUnits"] = str(self.keepEOL_comboBox.read())
        try:
            result = AnalysisEngine(self.data).analyze(
                self.currentCarBox.read(), [car.read() for car in self.cars], settings
            )
        except (AnalysisInputError, ValueError, ZeroDivisionError) as error:
            QMessageBox.warning(self, "Invalid Input", str(error))
            self._clear_analysis()
            return

        self.analysis_result = result
        self.carData = result.cars
        self.currentCarData = result.current_car
        self.newCarData = result.cars[1:]
        self.generalSettings = result.settings
        self.mileageAtChange = result.current_car["mileage"]
        self.mileageAtEnd = result.end_km
        self.analysisStart = result.analysis_start_km
        self.co2AtChange = result.co2_at_change
        self.plot_widget.render_analysis(result)
        self.computed = True
        self.on_analysis_value_changed()
        self.show_plot()
        self.show_table()

    def _validate_analysis_inputs(self) -> bool:
        if self.km2yearsConvFactorLineEdit.validate_numeric_input():
            return False
        if float(self.km2yearsConvFactorLineEdit.read()) <= 0:
            QMessageBox.warning(
                self, "Invalid Input", "Average annual mileage must be greater than zero."
            )
            return False
        self.km2yearsConvFactorLineEdit.save()
        for widget in self.currentCarBox.editableWidgets:
            if hasattr(widget, "validate_numeric_input"):
                if widget.validate_numeric_input():
                    return False
                widget.save()

        if self.currentCarBox.validate_current_mileage(
            self.currentCarBox.currentMileage_lineEdit.read()
        ):
            return False

        current = self.currentCarBox.read()
        if current["secondHandCarMileage"]:
            if current["secondHandCarMileage"] >= current["mileage"]:
                self.currentCarBox.secondHandCarMileage_lineEdit.clear()
                self.currentCarBox.secondHandCarMileage_lineEdit.save()
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Current Mileage (km) must be greater than Second-hand Car Mileage (km).",
                )
                return False
            if current["secondHandCarAge"] >= self.maxWindowYears:
                self.currentCarBox.secondHandCarAge_lineEdit.clear()
                self.currentCarBox.secondHandCarAge_lineEdit.save()
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    f"Second-hand car age must be below {self.maxWindowYears} years.",
                )
                return False

        if hasattr(self.keepEOL_lineEdit, "validate_numeric_input"):
            if self.keepEOL_lineEdit.validate_numeric_input():
                return False
            self.keepEOL_lineEdit.save()
        return True

    def _clear_analysis(self) -> None:
        self.computed = False
        self.plot_widget.initialize_empty_plots()
        self.table_widget_eou.populate_empty()
        self.show_plot()
        self.show_table()

    def on_analysis_value_changed(self) -> None:
        self.table_widget_eou.populate()
