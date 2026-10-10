"""Exercise the browser API against the captured desktop model behavior."""

import io
import json
import unittest
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from eco_car_advisor.web.api import app
from tests.scenarios import scenarios


class WebApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

    def test_defaults_match_all_captured_desktop_vehicle_forms(self):
        fixture = Path(__file__).parent / "fixtures" / "form_defaults.json"
        expected = json.loads(fixture.read_text(encoding="utf-8"))
        for combination, forms in expected.items():
            segment, engine = combination.split("|", 1)
            response = self.client.get(
                "/api/vehicle-defaults", params={"segment": segment, "engine": engine}
            )
            self.assertEqual(response.status_code, 200, combination)
            defaults = response.json()
            for kind in ("current", "replacement"):
                for field, value in forms[kind].items():
                    if field == "batteryCapacity" and engine != "BEV":
                        # The desktop retained a hidden BEV value after changing powertrains.
                        continue
                    self.assertEqual(defaults[field], value, f"{combination}.{kind}.{field}")

    def test_analysis_table_and_series_preserve_regression_values(self):
        baselines = json.loads(
            (Path(__file__).parent / "fixtures" / "legacy_baseline.json").read_text(
                encoding="utf-8"
            )
        )
        for name, (current, alternatives, settings) in scenarios().items():
            with self.subTest(name=name):
                current.pop("keepUnits")
                current.pop("keepLifeSpan")
                response = self.client.post(
                    "/api/analyze",
                    json={"current": current, "alternatives": alternatives, "settings": settings},
                )
                self.assertEqual(response.status_code, 200, response.text)
                payload = response.json()
                baseline = baselines[name]
                self.assertEqual(len(payload["rows"]), 2)
                self.assertEqual(payload["endKm"], baseline["end_km"])
                for index, car in enumerate(payload["series"]):
                    expected = baseline["cars"][index]
                    self.assertEqual(len(car["xKm"]), expected["x_count"])
                    self.assertAlmostEqual(car["emissions"][0], expected["emission_samples"][0])
                    self.assertAlmostEqual(car["emissions"][-1], expected["emission_samples"][-1])
                self.assertEqual(
                    payload["rows"][1]["savingsCo2"],
                    round(baseline["cars"][0]["THco2"] - baseline["cars"][1]["THco2"], 1),
                )

    def test_csv_excel_and_local_assets(self):
        current, alternatives, settings = scenarios()["gasoline_to_bev_with_maintenance"]
        current.pop("keepUnits")
        current.pop("keepLifeSpan")
        scenario = {"current": current, "alternatives": alternatives, "settings": settings}
        csv = self.client.post("/api/export/csv", json=scenario)
        excel = self.client.post("/api/export/xlsx", json=scenario)
        self.assertEqual(csv.status_code, 200)
        self.assertEqual(excel.status_code, 200)
        self.assertEqual(
            pd.read_csv(io.BytesIO(csv.content))["Car ID"].tolist(), ["Current", "Car 1"]
        )
        self.assertEqual(
            pd.read_excel(io.BytesIO(excel.content))["Car ID"].tolist(), ["Current", "Car 1"]
        )
        for route in (
            "/",
            "/assets/app.js",
            "/assets/styles.css",
            "/assets/plotly.min.js",
            "/guide",
        ):
            self.assertEqual(self.client.get(route).status_code, 200, route)
        guide = self.client.get("/guide").text
        self.assertIn("Run carbon analysis", guide)
        self.assertNotIn("unpkg.com", guide)
        self.assertNotIn(".exe", guide)

    def test_invalid_scenarios_are_rejected(self):
        current, alternatives, settings = scenarios()["gasoline_to_bev_with_maintenance"]
        current.pop("keepUnits")
        current.pop("keepLifeSpan")
        scenario = {"current": current, "alternatives": alternatives, "settings": settings}
        scenario["settings"]["km2yearsConvFactor"] = 0
        self.assertEqual(self.client.post("/api/analyze", json=scenario).status_code, 422)
        scenario["settings"]["km2yearsConvFactor"] = 12000
        scenario["current"]["mileage"] = 250000
        self.assertEqual(self.client.post("/api/analyze", json=scenario).status_code, 422)
        self.assertEqual(
            self.client.get(
                "/api/vehicle-defaults", params={"segment": "bad", "engine": "BEV"}
            ).status_code,
            422,
        )
        scenario["current"]["mileage"] = 80000
        scenario["current"]["massValue"] = 1e308
        self.assertEqual(self.client.post("/api/analyze", json=scenario).status_code, 422)
        scenario["current"]["massValue"] = 1450
        scenario["current"]["energyMix"] = 999
        self.assertEqual(self.client.post("/api/analyze", json=scenario).status_code, 422)


if __name__ == "__main__":
    unittest.main()
