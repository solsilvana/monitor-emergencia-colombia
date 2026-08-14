from __future__ import annotations

import unittest

from src.data_service import _inside_ring, load_data, load_geojson


class LocalDataTests(unittest.TestCase):
    def test_local_data_has_expected_sections(self):
        data = load_data()
        self.assertTrue({"meta", "event", "figures", "cities", "points", "references"} <= data.keys())
        self.assertGreaterEqual(len(data["cities"]), 5)
        self.assertGreaterEqual(len(data["points"]), 1)

    def test_original_aid_and_blood_points_are_preserved(self):
        points = load_data()["points"]
        self.assertGreaterEqual(len(points), 34)
        point_types = {point.get("type") for point in points}
        self.assertIn("sangre", point_types)
        self.assertTrue(any(point_type != "sangre" for point_type in point_types))

    def test_colombia_layer_has_departments_and_interior_labels(self):
        geojson = load_geojson()
        self.assertEqual(geojson["type"], "FeatureCollection")
        self.assertEqual(len(geojson["features"]), 33)
        for feature in geojson["features"]:
            properties = feature["properties"]
            self.assertIn("label_lat", properties)
            point = (properties["label_lon"], properties["label_lat"])
            rings = [polygon[0] for polygon in feature["geometry"]["coordinates"] if polygon]
            self.assertTrue(
                any(_inside_ring(point, ring) for ring in rings),
                f"La etiqueta de {properties.get('dpto')} quedó fuera del departamento.",
            )

    def test_figures_are_non_negative(self):
        data = load_data()
        for key, value in data["figures"].items():
            if isinstance(value, (int, float)):
                self.assertGreaterEqual(value, 0, key)

    def test_official_reports_have_separate_cuts_and_totals(self):
        figures = load_data()["figures"]
        self.assertEqual(figures["fallecidos_pais"], 285)
        self.assertEqual(figures["heridos_pais"], 3975)
        self.assertEqual(figures["desaparecidos_pais"], 379)
        self.assertEqual(figures["rescatados_pais"], 354)
        self.assertEqual(figures["fallecidos"], 204)
        self.assertFalse(figures["cities_same_cut"])
        self.assertIn("UNGRD", figures["ungrd_source_url"])
        self.assertIn("asocapitales", figures["asocapitales_source_url"])

    def test_forensic_indicators_are_separate_and_valid(self):
        data = load_data()
        forensic = data["forensics"]
        self.assertEqual(forensic["source"], "Instituto Nacional de Medicina Legal y Ciencias Forenses")
        self.assertGreaterEqual(forensic["bodies_received"], forensic["victims_identified"])
        self.assertGreaterEqual(forensic["victims_identified"], forensic["bodies_delivered"])
        self.assertNotEqual(forensic["victims_identified"], data["figures"]["fallecidos"])
        self.assertEqual(forensic["victims_identified"], 246)
        self.assertEqual(sum(item["value"] for item in forensic["sex"]), 246)
        self.assertEqual(sum(item["value"] for item in forensic["age"]["bands"]), 246)
        self.assertEqual(sum(item["value"] for item in forensic["forensic_units"]), 246)
        self.assertEqual(forensic["age"]["bands"][0]["value"], forensic["minors_identified"])

    def test_territorial_sources_are_integrated_in_city_module(self):
        data = load_data()
        cities = {city["name"]: city for city in data["cities"]}
        self.assertEqual(cities["Cali"]["injured"], 1401)
        self.assertEqual(cities["Cali"]["rescued"], 88)
        self.assertEqual(cities["Pereira"]["deaths"], 104)
        self.assertEqual(cities["Pereira"]["injured"], 578)
        self.assertEqual(cities["Pereira"]["rescued"], 260)
        self.assertEqual(cities["Quibdó"]["deaths"], 14)
        self.assertEqual(cities["Quibdó"]["injured"], 139)
        self.assertGreaterEqual(len(cities["Pereira"]["source_links"]), 2)
        self.assertGreaterEqual(len(cities["Quibdó"]["source_links"]), 2)


if __name__ == "__main__":
    unittest.main()
