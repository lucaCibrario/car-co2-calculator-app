"""Check exported values and both supported file formats."""

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from eco_car_advisor.analysis import AnalysisEngine
from eco_car_advisor.data import DataRepository
from eco_car_advisor.export import build_export_frame, write_export
from tests.scenarios import scenarios


class ExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        current, alternatives, settings = scenarios()["gasoline_to_bev_with_maintenance"]
        cls.result = AnalysisEngine(DataRepository().load()).analyze(
            current, alternatives, settings
        )

    def test_csv_and_excel_export(self):
        frame = build_export_frame(self.result)
        self.assertEqual(frame["Car ID"].tolist(), ["Current", "Car 1"])
        self.assertEqual(frame.columns[19], "maintenance")
        self.assertEqual(frame.columns[20], "keepEOL")
        self.assertEqual(frame.columns[23], "EoUmileage")
        self.assertEqual(frame.columns[24], "EoUage")
        self.assertNotIn("emissionHystory", frame)
        self.assertIn("co2Savings", frame)
        self.assertTrue(pd.isna(frame.loc[0, "co2Savings"]))
        self.assertAlmostEqual(
            frame.loc[1, "co2Savings"],
            self.result.cars[0]["THco2"] - self.result.cars[1]["THco2"],
        )

        with tempfile.TemporaryDirectory() as directory:
            csv_path = write_export(frame, str(Path(directory) / "result.csv"), "CSV Files (*.csv)")
            xlsx_path = write_export(frame, str(Path(directory) / "result"), "Excel Files (*.xlsx)")
            self.assertEqual(xlsx_path.suffix, ".xlsx")
            self.assertEqual(pd.read_csv(csv_path)["Car ID"].tolist(), ["Current", "Car 1"])
            self.assertEqual(pd.read_excel(xlsx_path)["Car ID"].tolist(), ["Current", "Car 1"])


if __name__ == "__main__":
    unittest.main()
