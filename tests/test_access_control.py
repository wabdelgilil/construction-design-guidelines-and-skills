"""
Unit tests for Access Control System (ACS) & Security Door Interlocks Skill.
"""

import unittest
from pathlib import Path
import tempfile
from electrical.low_current_elv.access_control.scripts.design_engine import (
    AccessControlEngine,
    ControlledDoorInput,
)
from electrical.low_current_elv.access_control.scripts.run_design import generate_access_control_package


class TestAccessControlSkill(unittest.TestCase):
    def setUp(self):
        self.engine = AccessControlEngine(standard="NFPA 101 / UL 294 / SBC 801")

    def test_door_hardware_current_and_battery_sizing(self):
        doors = [
            ControlledDoorInput("D-01", "Main Lobby", "double_leaf", "perimeter_heavy", "maglock_1200lbs", "card_reader"),
            ControlledDoorInput("D-02", "Data Center", "single_leaf", "server_biometric", "maglock_600lbs", "biometric_reader"),
            ControlledDoorInput("D-03", "Stair Egress", "single_leaf", "standard_interior", "maglock_600lbs", "card_reader", on_egress_route=True),
        ]
        res = self.engine.design_system("Facility ACS", doors, autonomy_hours=4.0)

        self.assertEqual(res.total_doors_count, 3)
        self.assertEqual(res.total_controllers_count, 1)  # 3 doors fits on 1x 4-door controller
        self.assertGreater(res.total_system_current_a, 0.0)
        self.assertGreater(res.total_system_power_watts, 0.0)
        self.assertGreaterEqual(res.recommended_psu_current_a, 3.0)
        self.assertGreater(res.calculated_battery_ah, 0.0)
        self.assertGreaterEqual(res.selected_battery_ah, res.calculated_battery_ah)
        self.assertTrue(res.fire_alarm_interlock_mandatory)

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            doors = [
                ControlledDoorInput("D-01", "Secure Lab", "single_leaf", "standard_interior", "maglock_600lbs", "card_reader"),
            ]
            files = generate_access_control_package(
                project_name="Research Lab ACS",
                doors=doors,
                autonomy_hours=4.0,
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Research Lab ACS", content)
                self.assertIn("NFPA 101", content)
                self.assertIn("Fail-Safe", content)


if __name__ == "__main__":
    unittest.main()
