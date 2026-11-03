"""
Unit tests for Architectural Life Safety & Means of Egress Skill.
"""

import unittest
from pathlib import Path
import tempfile
from architectural.life_safety.scripts.design_engine import (
    LifeSafetyEngine,
    EgressZoneInput,
)
from architectural.life_safety.scripts.run_design import generate_life_safety_package


class TestLifeSafetySkill(unittest.TestCase):
    def setUp(self):
        self.engine = LifeSafetyEngine(is_sprinklered=True, code="SBC")
        self.factors = {
            "business_office": 9.3,
            "assembly_unconcentrated": 1.4,
        }

    def test_occupant_load_and_exits(self):
        zones = [
            EgressZoneInput("Office Hall", 200.0, "business_office", 20.0),
            EgressZoneInput("Auditorium", 140.0, "assembly_unconcentrated", 15.0),
        ]
        res = self.engine.compute_life_safety(
            building_name="HQ",
            building_length_m=30.0,
            building_width_m=20.0,
            actual_exit_separation_m=18.0,
            zones_data=zones,
            load_factors=self.factors,
        )

        # Diagonal = sqrt(900 + 400) = 36.06 m. Required separation = 36.06 / 3 = 12.02 m. Actual 18.0m -> PASS
        self.assertTrue(res.separation_pass)
        self.assertEqual(res.overall_status, "FULLY COMPLIANT")
        self.assertGreater(res.total_building_occupants, 100)

    def test_insufficient_exit_separation_detection(self):
        zones = [
            EgressZoneInput("Office", 100.0, "business_office", 10.0),
        ]
        # Diagonal = sqrt(1600 + 900) = 50.0 m. Required separation = 50 / 3 = 16.67 m. Actual = 8.0 m -> VIOLATION
        res = self.engine.compute_life_safety(
            building_name="Violation Bldg",
            building_length_m=40.0,
            building_width_m=30.0,
            actual_exit_separation_m=8.0,
            zones_data=zones,
            load_factors=self.factors,
        )

        self.assertFalse(res.separation_pass)
        self.assertEqual(res.overall_status, "LIFE SAFETY VIOLATIONS")

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            zones = [
                EgressZoneInput("Classroom", 80.0, "business_office", 12.0),
            ]
            files = generate_life_safety_package(
                building_name="Training Center",
                building_length_m=20.0,
                building_width_m=15.0,
                actual_exit_separation_m=12.0,
                zones_data=zones,
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Training Center", content)
                self.assertIn("SBC 801", content)
                self.assertIn("EXIT", content)


if __name__ == "__main__":
    unittest.main()
