"""
Unit tests for Electrical Lighting Leaf Skill and Deliverables.
"""

import unittest
from pathlib import Path
import tempfile
from electrical.lighting.scripts.lumen_engine import LumenEngine, LightingFixture
from electrical.lighting.scripts.run_design import generate_lighting_package


class TestLightingSkill(unittest.TestCase):
    def test_lumen_calculation(self):
        fixture = LightingFixture("LED Panel 36W", lumens_per_fixture=3600.0, power_watts=36.0)
        res = LumenEngine.design_room_lighting(
            room_name="Classroom",
            length_m=8.0,
            width_m=6.0,
            target_lux=350.0,
            ceiling_height_m=3.0,
            fixture=fixture,
        )

        self.assertEqual(res.room_area_m2, 48.0)
        self.assertGreaterEqual(res.achieved_lux, 350.0 * 0.95)
        self.assertEqual(len(res.fixture_coordinates), res.total_fixtures_count)
        self.assertEqual(res.total_fixtures_count, res.grid_columns * res.grid_rows)
        self.assertTrue(res.lighting_power_density_w_per_m2 > 0)

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            files = generate_lighting_package(
                room_name="Conference Room",
                length_m=9.0,
                width_m=5.0,
                space_type="office_conference",
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Conference Room", content)
                self.assertIn("LPD", content)
                self.assertIn("CKT-L01", content)


if __name__ == "__main__":
    unittest.main()
