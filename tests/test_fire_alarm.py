"""
Unit tests for Addressable Fire Alarm System Skill.
"""

import unittest
from pathlib import Path
import tempfile
from electrical.low_current_elv.fire_alarm.scripts.design_engine import (
    FireAlarmEngine,
    FireAlarmSpaceInput,
)
from electrical.low_current_elv.fire_alarm.scripts.run_design import generate_fire_alarm_package


class TestFireAlarmSkill(unittest.TestCase):
    def setUp(self):
        self.engine = FireAlarmEngine(standard="NFPA 72 / SBC 801")

    def test_detector_selection_and_counts(self):
        spaces = [
            FireAlarmSpaceInput("Office Hall", 12.0, 10.0, "office", False),     # 120m2 -> 2 optical smoke
            FireAlarmSpaceInput("Kitchen", 8.0, 5.0, "kitchen", False),           # 40m2 -> 1 heat detector
            FireAlarmSpaceInput("Server Room", 6.0, 4.0, "server_room", False),  # 24m2 -> 1 optical/smoke
            FireAlarmSpaceInput("Exit Corridor", 8.0, 2.0, "corridor", True),     # 16m2 -> 1 smoke, 1 MCP
        ]
        res = self.engine.design_fire_alarm("HQ Building", spaces)

        self.assertGreater(res.total_smoke_detectors, 0)
        self.assertEqual(res.total_heat_detectors, 1)
        self.assertEqual(res.total_mcps, 1)
        self.assertGreater(res.grand_total_addressable_devices, 0)
        self.assertEqual(res.total_loops_required, 1)
        self.assertGreaterEqual(res.loop_spare_capacity_pct, 20.0)

    def test_nfpa_battery_calculation(self):
        spaces = [FireAlarmSpaceInput("Office", 10.0, 8.0, "office", False)]
        res = self.engine.design_fire_alarm("Small Office", spaces)

        self.assertEqual(res.standby_duration_hours, 24.0)
        self.assertEqual(res.alarm_duration_minutes, 15.0)
        self.assertGreater(res.calculated_battery_capacity_ah, 0)
        self.assertIn(res.selected_battery_rating_ah, [7.0, 12.0, 17.0, 24.0, 38.0, 65.0])
        self.assertTrue(len(res.coordination_notices) >= 4)

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            spaces = [
                FireAlarmSpaceInput("Control Room", 6.0, 5.0, "office", True),
            ]
            files = generate_fire_alarm_package(
                project_name="Substation Control",
                spaces=spaces,
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Substation Control", content)
                self.assertIn("NFPA 72", content)
                self.assertIn("Battery", content)


if __name__ == "__main__":
    unittest.main()
