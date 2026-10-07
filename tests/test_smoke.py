"""Minimal checks for the existing application and its bundled input files."""

import unittest

import EcoCarReplacementAdvisor  # noqa: F401 - verifies GUI imports
from src.Utilities import loadData


class ApplicationSmokeTest(unittest.TestCase):
    def test_bundled_workbooks_load(self):
        data = loadData()
        self.assertIn("productionEoL", data)
        self.assertIn("maintenance", data)
        self.assertIn("usePhase", data)
        self.assertFalse(data["maintenance"].empty)
        self.assertFalse(data["usePhase"]["consumptionICE"].empty)


if __name__ == "__main__":
    unittest.main()
