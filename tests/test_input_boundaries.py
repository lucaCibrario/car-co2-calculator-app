"""Reject scenarios that cannot produce a finite comparison period."""

import unittest

from eco_car_advisor.analysis import AnalysisEngine, AnalysisInputError
from eco_car_advisor.calculations import battery_replacement_emissions
from eco_car_advisor.data import DataRepository
from tests.scenarios import scenarios


class InputBoundaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = AnalysisEngine(DataRepository().load())

    def test_replacement_at_maximum_age_has_no_comparison_period(self):
        current, alternatives, settings = scenarios()["gasoline_to_bev_with_maintenance"]
        current["secondHandCar"] = True
        current["secondHandCarMileage"] = 180000
        current["secondHandCarAge"] = 19
        current["mileage"] = 192000
        with self.assertRaisesRegex(AnalysisInputError, "age limit"):
            self.engine.analyze(current, alternatives, settings)

    def test_used_replacement_past_vehicle_lifespan(self):
        current, alternatives, settings = scenarios()["gasoline_to_bev_with_maintenance"]
        alternatives[0]["secondHandCar"] = True
        alternatives[0]["secondHandCarMileage"] = 220000
        alternatives[0]["secondHandCarAge"] = 10
        with self.assertRaisesRegex(AnalysisInputError, "second-hand mileage"):
            self.engine.analyze(current, alternatives, settings)

    def test_zero_annual_mileage_and_tiny_battery_lifetime(self):
        current, alternatives, settings = scenarios()["gasoline_to_bev_with_maintenance"]
        settings["km2yearsConvFactor"] = 0
        with self.assertRaisesRegex(AnalysisInputError, "annual mileage"):
            self.engine.analyze(current, alternatives, settings)
        with self.assertRaisesRegex(ValueError, "at least 500 km"):
            battery_replacement_emissions([0, 1000], 0, 100, 60, 130)


if __name__ == "__main__":
    unittest.main()
