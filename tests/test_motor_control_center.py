"""
Unit tests for Motor Control Center (MCC) & Motor Feeders / Starters Sizing Skill.
"""

import unittest
from pathlib import Path
import tempfile
from electrical.power_distribution.motor_control_center_mcc.scripts.design_engine import (
    MotorControlCenterEngine,
    MotorLoadInput,
)
from electrical.power_distribution.motor_control_center_mcc.scripts.run_design import generate_mcc_package


class TestMotorControlCenterSkill(unittest.TestCase):
    def setUp(self):
        self.engine = MotorControlCenterEngine(standard="IEC 60947-4-1 / IEC 61439-2 / SBC 401")

    def test_starter_method_selection_and_component_sizing(self):
        motors = [
            MotorLoadInput("P-01", "Small Booster Pump", rated_kw=5.5),
            MotorLoadInput("P-02", "Medium Chilled Water Pump", rated_kw=30.0),
            MotorLoadInput("P-03", "Large Secondary Pump VFD", rated_kw=45.0, application_type="variable_speed"),
            MotorLoadInput("P-04", "Heavy Condenser Pump", rated_kw=75.0),
        ]
        res = self.engine.design_mcc("Plant MCC", motors)

        self.assertEqual(res.total_motors_count, 4)
        self.assertGreater(res.total_connected_kw, 0.0)
        self.assertGreater(res.total_full_load_current_a, 0.0)

        # Check starter topologies
        m_dol = next(m for m in res.motors if m.tag == "P-01")
        self.assertIn("DOL", m_dol.starting_method)
        self.assertGreater(m_dol.starting_current_a, m_dol.fla_a * 5.0)

        m_yd = next(m for m in res.motors if m.tag == "P-02")
        self.assertIn("Star-Delta", m_yd.starting_method)
        self.assertIsNotNone(m_yd.contactor_delta_ac3_a)
        self.assertIsNotNone(m_yd.contactor_star_ac3_a)

        m_vfd = next(m for m in res.motors if m.tag == "P-03")
        self.assertIn("VFD", m_vfd.starting_method)
        self.assertLess(m_vfd.starting_current_a, m_vfd.fla_a * 1.5)

        m_soft = next(m for m in res.motors if m.tag == "P-04")
        self.assertIn("Soft", m_soft.starting_method)

        # Voltage drop checks
        for m in res.motors:
            self.assertLessEqual(m.run_voltage_drop_pct, 3.0)
            self.assertLessEqual(m.start_voltage_drop_pct, 12.0)

        # MCC Incomer
        self.assertGreaterEqual(res.mcc_main_incomer_rating_a, 250)
        self.assertGreater(res.total_columns_count, 1)

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            motors = [
                MotorLoadInput("FAN-01", "Exhaust Fan", rated_kw=11.0, application_type="constant_speed"),
            ]
            files = generate_mcc_package(
                project_name="HVAC Exhaust MCC",
                motors=motors,
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("HVAC Exhaust MCC", content)
                self.assertIn("IEC 60947-4-1", content)
                self.assertIn("Form 4b", content)


if __name__ == "__main__":
    unittest.main()
