from __future__ import annotations

import unittest

from src.data_service import _inside_ring, load_data, load_geojson


class LocalDataTests(unittest.TestCase):
    def test_local_data_has_expected_sections(self):
        data = load_data()
        self.assertTrue({"meta", "event", "figures", "cities", "points", "references"} <= data.keys())
        self.assertGreaterEqual(len(data["cities"]), 5)
        self.assertGreaterEqual(len(data["points"]), 1)

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
        self.assertEqual(figures["fallecidos_pais"], 273)
        self.assertEqual(figures["heridos_pais"], 3824)
        self.assertEqual(figures["desaparecidos_pais"], 377)
        self.assertEqual(figures["fallecidos"], 204)
        self.assertIn("UNGRD", figures["ungrd_source_url"])
        self.assertIn("asocapitales", figures["asocapitales_source_url"])

    def test_forensic_indicators_are_separate_and_valid(self):
        data = load_data()
        forensic = data["forensics"]
        self.assertEqual(forensic["source"], "Instituto Nacional de Medicina Legal y Ciencias Forenses")
        self.assertGreaterEqual(forensic["bodies_received"], forensic["victims_identified"])
        self.assertGreaterEqual(forensic["victims_identified"], forensic["bodies_delivered"])
        self.assertNotEqual(forensic["victims_identified"], data["figures"]["fallecidos"])


if __name__ == "__main__":
    unittest.main()
