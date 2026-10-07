"""Exercise a complete desktop analysis without displaying windows."""

import os
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QTWEBENGINE_DISABLE_SANDBOX", "1")

from PySide6.QtWidgets import QApplication

from eco_car_advisor.ui.main_window import CarReplacementAdvisor


class ApplicationWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.window = CarReplacementAdvisor()

    @classmethod
    def tearDownClass(cls):
        cls.window.close()

    def test_compute_switch_units_and_render_offline_plot(self):
        window = self.window
        window.currentCarBox.currentMileage_lineEdit.write("80000")
        window.currentCarBox.engineType_comboBox.write("Gasoline (Euro 6)")
        window.cars[0].engineType_comboBox.write("BEV")
        window.plot_carbon_footprint()

        self.assertTrue(window.computed)
        self.assertEqual(len(window.analysis_result.cars), 2)
        self.assertEqual(window.table_widget_eou.rowCount(), 2)
        self.assertGreater(len(window.plot_widget.plotYears.data), 1)
        self.assertGreater(len(window.plot_widget.plotKilometers.data), 1)

        window.unit_combo.write("km")
        self.assertEqual(window.unit_combo.read(), "km")
        plot_directory = Path(window.plot_widget._plot_directory.name)
        self.assertTrue((plot_directory / "plot.html").is_file())
        self.assertTrue((plot_directory / "plotly.min.js").is_file())
        self.assertNotIn("cdn.plot.ly", (plot_directory / "plot.html").read_text(encoding="utf-8"))

    def test_distinct_bev_lifespan_and_invalid_replacement_setting(self):
        window = self.window
        settings = window.generalOptionsDialog
        settings.BEVlifeSpanLineEdit.write("250000")
        self.assertEqual(settings.read()["BEVlifeSpan"], 250000)
        settings.BEVlifeSpanLineEdit.write("200000")
        settings.read()

        dialog = window.cars[0].dialog
        with (
            patch.object(
                dialog.editableWidgets[-1], "validate_numeric_input", return_value="invalid"
            ),
            patch.object(dialog, "accept") as accept,
        ):
            dialog.validate_and_accept()
            accept.assert_not_called()

    def test_invalid_annual_mileage_does_not_raise(self):
        window = self.window
        window.km2yearsConvFactorLineEdit.setText("abc")
        with patch("eco_car_advisor.ui.widgets.numeric_line_edit.QMessageBox.warning"):
            window.plot_carbon_footprint()
        self.assertFalse(window.computed)
        window.km2yearsConvFactorLineEdit.write("12000")


if __name__ == "__main__":
    unittest.main()
