"""Characterization tests for the pre-refactor numerical behavior."""

import json
import math
import unittest
from pathlib import Path
from types import SimpleNamespace

from eco_car_advisor.analysis import AnalysisEngine
from eco_car_advisor.data import DataRepository
from tests.scenarios import scenarios, summarize

BASELINE_PATH = Path(__file__).parent / "fixtures" / "legacy_baseline.json"


class AnalysisRegressionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        cls.engine = AnalysisEngine(DataRepository().load())

    def assert_equivalent(self, actual, expected, path="result"):
        if isinstance(expected, dict):
            self.assertEqual(set(actual), set(expected), path)
            for key in expected:
                self.assert_equivalent(actual[key], expected[key], f"{path}.{key}")
        elif isinstance(expected, list):
            self.assertEqual(len(actual), len(expected), path)
            for index, (left, right) in enumerate(zip(actual, expected, strict=True)):
                self.assert_equivalent(left, right, f"{path}[{index}]")
        elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
            self.assertTrue(
                math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-10),
                f"{path}: {actual} != {expected}",
            )
        else:
            self.assertEqual(actual, expected, path)

    def test_characterized_scenarios(self):
        for name, (current, alternatives, settings) in scenarios().items():
            with self.subTest(name=name):
                result = self.engine.analyze(current, alternatives, settings)
                adapter = SimpleNamespace(
                    carData=result.cars,
                    plot_widget=SimpleNamespace(
                        analysisStartKm=result.analysis_start_km,
                        xmaxRangeKm=result.end_km,
                        yRange=result.y_range,
                    ),
                )
                self.assert_equivalent(summarize(adapter), self.baseline[name])


if __name__ == "__main__":
    unittest.main()
