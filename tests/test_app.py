"""Integration checks against the real Streamlit app, without a browser."""
from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest
from city_engine import DEMO

APP = Path(__file__).resolve().parents[1] / "app.py"


class AppTests(unittest.TestCase):
    def app(self, page="Overview", inputs=None):
        app = AppTest.from_file(str(APP), default_timeout=30)
        app.session_state["page"] = page
        if inputs is not None:
            app.session_state["inputs"] = inputs
        return app.run()

    def assert_healthy(self, app):
        self.assertEqual(len(app.exception), 0, str(app.exception))
        self.assertEqual(len(app.error), 0, str(app.error))

    def test_all_pages(self):
        app = self.app()
        for page in app.sidebar.radio[0].options:
            # Radio options include display icons; the values are plain names.
            name = next(p for p in ["Overview", "Traffic Management", "Water Supply",
                "Construction Estimator", "Waste Management", "Future Planning",
                "Scenario Lab", "City Report"] if page.endswith(p))
            with self.subTest(page=name):
                app.sidebar.radio[0].set_value(name).run()
                self.assert_healthy(app)
                self.assertEqual(app.session_state["page"], name)

    def test_traffic_edit_and_navigation_persistence(self):
        app = self.app("Traffic Management")
        app.number_input(key="field_vehicles").set_value(100)
        app.number_input(key="field_road_length_km").set_value(2.0).run()
        self.assert_healthy(app)
        self.assertIn("50.00", app.metric[0].value)
        app.sidebar.radio[0].set_value("Water Supply").run()
        app.sidebar.radio[0].set_value("Traffic Management").run()
        self.assertEqual(app.number_input(key="field_vehicles").value, 100)
        self.assertEqual(app.number_input(key="field_road_length_km").value, 2.0)

    def test_water_edits(self):
        app = self.app("Water Supply")
        app.number_input(key="field_population").set_value(1000)
        app.number_input(key="field_available_water_lpd").set_value(135000.0).run()
        self.assert_healthy(app)
        self.assertIn("Balanced", app.metric[1].delta)
        self.assertEqual(app.session_state["inputs"]["population"] * 135, 135000)

    def test_construction_edits(self):
        app = self.app("Construction Estimator")
        for key, value in [("building_length_m", 10.0), ("building_width_m", 12.0),
                           ("floors", 3), ("cost_per_m2", 5000.0)]:
            app.number_input(key=f"field_{key}").set_value(value)
        app.run()
        self.assert_healthy(app)
        self.assertEqual(app.metric[0].value, "360.0 m²")
        self.assertEqual(app.metric[1].value, "PKR 1.80M")

    def test_scenario_apply(self):
        app = self.app("Scenario Lab")
        next(b for b in app.button if b.label == "Apply proposed changes to my city").click().run()
        self.assert_healthy(app)
        values = app.session_state["inputs"]
        self.assertEqual(values["vehicles"], 10000)
        self.assertAlmostEqual(values["available_water_lpd"], 35650000)
        self.assertEqual(values["recycling_percentage"], 50)
        app.sidebar.radio[0].set_value("City Report").run()
        self.assert_healthy(app)

    def test_invalid_input_shows_error(self):
        app = self.app(inputs=dict(DEMO, road_length_km=0))
        self.assertEqual(len(app.exception), 0)
        self.assertIn("Road length", app.error[0].value)

    def test_valid_import_with_small_positive_dimensions(self):
        for page, values in [
            ("Traffic Management", dict(road_length_km=0.0001)),
            ("Construction Estimator", dict(building_length_m=0.0001, cost_per_m2=0.001)),
            ("Waste Management", dict(waste_kg_per_person=0.0001)),
        ]:
            with self.subTest(page=page):
                app = self.app(page, dict(DEMO, **values))
                self.assert_healthy(app)

    def test_scenario_at_valid_supply_limit(self):
        app = self.app("Scenario Lab", dict(DEMO, available_water_lpd=1e15))
        self.assertEqual(len(app.exception), 0, str(app.exception))
        self.assertTrue(app.warning or app.error)


if __name__ == "__main__":
    unittest.main()