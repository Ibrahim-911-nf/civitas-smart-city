"""Run: python -m unittest discover -s tests -v"""
import copy
import math
import unittest

from city_engine import (
    DEMO, WATER_LITRES_PER_PERSON, calculate_city,
    construction_estimator, forecast_city, traffic_management,
    validate_city, waste_management, water_management,
)
from reports import create_pdf_report


class SmartCityTests(unittest.TestCase):
    def test_full_city(self):
        result = calculate_city(DEMO)
        self.assertEqual(result["traffic"]["condition"], "High")
        self.assertAlmostEqual(result["traffic"]["density"], 12500 / 180)
        self.assertEqual(result["water"]["demand_lpd"], 33_750_000)
        self.assertEqual(result["water"]["balance_lpd"], -2_750_000)
        self.assertEqual(result["water"]["status"], "Shortage")
        self.assertEqual(result["construction"]["total_floor_area_m2"], 10_800)
        self.assertEqual(result["construction"]["total_cost_pkr"], 810_000_000)
        self.assertEqual(result["waste"]["total_kgpd"], 187_500)
        self.assertEqual(result["waste"]["recycled_kgpd"], 65_625)
        self.assertEqual(result["waste"]["remaining_kgpd"], 121_875)
        self.assertEqual(len(result["recommendations"]), 3)

    def test_traffic_boundary_categories(self):
        for vehicles, category in [(0, "Low"), (25, "Low"),
                                   (26, "Moderate"), (60, "Moderate"),
                                   (61, "High"), (100, "High"),
                                   (101, "Critical")]:
            self.assertEqual(traffic_management(vehicles, 1)["condition"], category)

    def test_balanced_water(self):
        self.assertEqual(water_management(10, 1350)["status"], "Balanced")
        self.assertEqual(water_management(10, 1500)["status"], "Surplus")
        self.assertEqual(water_management(10, 1000)["status"], "Shortage")

    def test_construction_and_waste(self):
        b = construction_estimator(10, 12, 3, 5000)
        self.assertEqual(b["total_floor_area_m2"], 360)
        self.assertEqual(b["total_cost_pkr"], 1_800_000)
        w = waste_management(1000, .5, 25)
        self.assertEqual((w["total_kgpd"], w["recycled_kgpd"], w["remaining_kgpd"]),
                         (500, 125, 375))

    def test_invalid_inputs(self):
        for field, value in [("population", 0), ("population", 5.5),
                             ("road_length_km", 0), ("available_water_lpd", -1),
                             ("recycling_percentage", 101), ("floors", 2.5),
                             ("cost_per_m2", "abc"), ("vehicles", float("nan")),
                             ("forecast_years", 31)]:
            candidate = dict(DEMO)
            candidate[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                validate_city(candidate)

    def test_projection(self):
        future = forecast_city(DEMO)
        self.assertEqual(len(future), 11)
        self.assertEqual(future[0]["population"], 250000)
        self.assertAlmostEqual(future[0]["water_demand_lpd"], 33_750_000)
        self.assertEqual(future[10]["recycling_pct"], 60)
        self.assertGreater(future[10]["population"], future[0]["population"])

    def test_pdf_export(self):
        report = create_pdf_report(calculate_city(DEMO), forecast_city(DEMO))
        self.assertTrue(report.startswith(b"%PDF-"))
        self.assertGreater(len(report), 3500)


if __name__ == "__main__":
    unittest.main()
