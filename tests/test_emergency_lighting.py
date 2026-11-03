"""
Unit tests for Emergency & Exit Lighting (CBS & Self-Contained) Design Skill.
"""

import unittest
from pathlib import Path
import tempfile
from electrical.lighting.emergency_lighting.scripts.design_engine import (
    EmergencyLightingEngine,
    EmergencySpaceInput,
)
from electrical.lighting.emergency_lighting.scripts.run_design import generate_emergency_lighting_package


class TestEmergencyLightingSkill(unittest.TestCase):
    def setUp(self):
        self.engine = EmergencyLightingEngine(standard="NFPA 101 / BS 5266 / SBC 801")

    def test_escape_route_and_cbs_sizing(self):
        spaces = [
            EmergencySpaceInput("Corridor A", "escape_corridor", 30.0, 2.5, 3.0, has_exit_door=True),
            EmergencySpaceInput("Staircase East", "fire_staircase", 12.0, 3.0, 3.0, has_exit_door=True),
            EmergencySpaceInput("Open Lobby", "open_hall", 20.0, 10.0, 3.5, has_exit_door=False),
        ]
        res = self.engine.design_emergency_lighting(
            project_name="Tower Emergency Egress",
            spaces=spaces,
            system_architecture="Central Battery System (CBS)",
            autonomy_hours=1.5,
        )

        self.assertEqual(res.project_name, "Tower Emergency Egress")
        self.assertGreater(res.total_emergency_luminaires, 0)
        self.assertGreater(res.total_exit_signs, 0)
        self.assertEqual(res.grand_total_luminaires, res.total_emergency_luminaires + res.total_exit_signs)
        self.assertGreater(res.total_emergency_load_watts, 0.0)
        self.assertGreaterEqual(res.cbs_inverter_rated_va, 500)
        self.assertGreater(res.cbs_selected_battery_ah, 0.0)
        self.assertEqual(res.cbs_battery_blocks_12v_count, 18)  # 220V DC / 12V = 18 blocks
        self.assertGreater(len(res.coordination_notices), 0)

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            spaces = [
                EmergencySpaceInput("Exit Corridor", "escape_corridor", 20.0, 2.0, 2.8, has_exit_door=True),
            ]
            files = generate_emergency_lighting_package(
                project_name="Clinic Egress",
                spaces=spaces,
                system_architecture="Central Battery System (CBS)",
                autonomy_hours=1.5,
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Clinic Egress", content)
                self.assertIn("NFPA 101", content)
                self.assertIn("CBS", content)


if __name__ == "__main__":
    unittest.main()
