"""
Unit tests for Mechanical Plumbing Drainage & Water Supply Skill.
"""

import unittest
from pathlib import Path
import tempfile
from mechanical.plumbing.scripts.design_engine import (
    PlumbingEngine,
    PlumbingFixturesSchedule,
)
from mechanical.plumbing.scripts.run_design import generate_plumbing_package


class TestPlumbingSkill(unittest.TestCase):
    def setUp(self):
        self.engine = PlumbingEngine(code="SBC")

    def test_dfu_and_stack_sizing(self):
        fixtures = PlumbingFixturesSchedule(
            water_closet_tank=10,  # 10 * 3 = 30
            lavatory=10,           # 10 * 1 = 10
            shower=5,              # 5 * 2 = 10
            kitchen_sink=5,        # 5 * 2 = 10
            washing_machine=2,     # 2 * 3 = 6
            floor_drain=6,         # 6 * 2 = 12
        )                          # Total = 78 DFU
        res = self.engine.design_plumbing("V-01", fixtures)

        self.assertEqual(res.total_dfu, 78.0)
        self.assertEqual(res.selected_soil_stack_diameter_in, 4)
        self.assertEqual(res.selected_building_drain_diameter_in, 4)
        self.assertEqual(res.minimum_drain_slope_pct, 1.0)

    def test_wsfu_and_booster_pump(self):
        fixtures = PlumbingFixturesSchedule(
            water_closet_tank=4,
            lavatory=4,
            shower=2,
            kitchen_sink=2,
        )
        res = self.engine.design_plumbing("V-02", fixtures, building_height_m=15.0)

        self.assertGreater(res.total_wsfu, 0)
        self.assertGreater(res.design_flow_gpm, 0)
        self.assertGreater(res.total_pump_head_m, 15.0)
        self.assertGreater(res.pump_motor_power_kw, 0)
        self.assertTrue(len(res.sleeves_required) >= 2)
        self.assertTrue(len(res.coordination_notices) >= 4)

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            fixtures = PlumbingFixturesSchedule(water_closet_tank=2, lavatory=2)
            files = generate_plumbing_package(
                building_tag="Small Villa",
                fixtures=fixtures,
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Small Villa", content)
                self.assertIn("SBC 701", content)
                self.assertIn("Grade Beam", content)


if __name__ == "__main__":
    unittest.main()
