"""Check bundled resources and working-directory independent paths."""

import unittest
from os import chdir, getcwd
from pathlib import Path
from tempfile import TemporaryDirectory

import EcoCarReplacementAdvisor  # noqa: F401 - verifies GUI imports
from eco_car_advisor.data import DataRepository


class ApplicationSmokeTest(unittest.TestCase):
    def test_bundled_workbooks_load(self):
        data = DataRepository().load()
        self.assertIn("productionEoL", data)
        self.assertIn("maintenance", data)
        self.assertIn("usePhase", data)
        self.assertFalse(data["maintenance"].empty)
        self.assertFalse(data["usePhase"]["consumptionICE"].empty)

    def test_resources_load_from_another_working_directory(self):
        original = getcwd()
        with TemporaryDirectory() as directory:
            try:
                chdir(directory)
                self.assertTrue(DataRepository().load()["maintenance"].shape[0] > 0)
                from eco_car_advisor.resources import resource_path

                self.assertTrue(Path(resource_path("Icons/Options.png")).is_file())
            finally:
                chdir(original)


if __name__ == "__main__":
    unittest.main()
