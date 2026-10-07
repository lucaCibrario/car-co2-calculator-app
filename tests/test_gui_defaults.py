"""Compare all vehicle form defaults with the captured original UI."""

import json
import os
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QTWEBENGINE_DISABLE_SANDBOX", "1")

from PySide6.QtWidgets import QApplication

from eco_car_advisor.ui.main_window import CarReplacementAdvisor


class FormDefaultsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.window = CarReplacementAdvisor()
        cls.window.currentCarBox.currentMileage_lineEdit.write("80000")
        fixture = Path(__file__).parent / "fixtures" / "form_defaults.json"
        cls.baseline = json.loads(fixture.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.window.close()

    def test_current_and_replacement_defaults(self):
        window = self.window
        for segment in window.carSegments:
            for engine in window.carEngineTypes:
                values = self.baseline[f"{segment}|{engine}"]
                with self.subTest(segment=segment, engine=engine):
                    current_form = window.currentCarBox
                    current_form.segments_comboBox.write(segment)
                    current_form.engineType_comboBox.write(engine)
                    current = current_form.read()
                    replacement_form = window.cars[0]
                    replacement_form.segments_comboBox.write(segment)
                    replacement_form.engineType_comboBox.write(engine)
                    replacement = replacement_form.read()
                    for field, expected in values["current"].items():
                        self.assertEqual(current.get(field), expected, f"current.{field}")
                    for field, expected in values["replacement"].items():
                        self.assertEqual(replacement.get(field), expected, f"replacement.{field}")


if __name__ == "__main__":
    unittest.main()
