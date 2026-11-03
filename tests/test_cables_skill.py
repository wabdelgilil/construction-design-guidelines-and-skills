"""
Unit tests for Low Voltage Cable Sizing & Cable Tray Sizing Skill.
"""

import unittest
from pathlib import Path
import tempfile
from electrical.cables.scripts.cable_engine import (
    CableEngine,
    FeederRequest,
)
from electrical.cables.scripts.run_design import generate_cables_package


class TestCablesSkill(unittest.TestCase):
    def test_feeder_sizing_and_derating(self):
        # 3-phase 100 kW load at 400V, length 40m, ambient 45C
        res = CableEngine.size_cable(
            load_kw=100.0,
            phases=3,
            system_voltage_v=400.0,
            circuit_length_m=40.0,
            power_factor=0.85,
            temp_derating_factor=0.96,
            grouping_derating_factor=0.77,
            is_branch_circuit=False,
        )

        self.assertGreater(res.design_current_ib, 150.0)
        self.assertGreaterEqual(res.breaker_rating_in, res.design_current_ib)
        self.assertGreaterEqual(res.cable_ampacity_iz, res.design_current_ib)
        self.assertLessEqual(res.voltage_drop_pct, 2.0)  # Sub-main limit <= 2.0%
        self.assertEqual(res.compliance_status, "SAFE")
        self.assertGreater(res.short_circuit_withstand_ka, 0.0)
        self.assertGreater(res.approx_outer_diameter_mm, 0.0)

    def test_cable_tray_sizing(self):
        diameters = [32.0, 38.0, 45.0, 52.0, 24.0]
        tray_res = CableEngine.size_cable_tray(
            tray_tag="CT-01",
            cable_diameters_mm=diameters,
            standard_depth_mm=50,
            max_fill_ratio_pct=40.0,
        )

        self.assertEqual(tray_res.cables_count, 5)
        self.assertLessEqual(tray_res.achieved_fill_ratio_pct, 40.0)
        self.assertEqual(tray_res.status, "COMPLIANT")
        self.assertIn(tray_res.selected_tray_width_mm, [100, 150, 200, 300, 450, 600, 750, 900])

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            feeders = [
                FeederRequest("F-01", "Main Sub-Panel", 50.0, 30.0, 3, 0.85, False),
            ]
            files = generate_cables_package(
                project_name="Office Building",
                feeders=feeders,
                tray_tag="CT-01",
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Office Building", content)
                self.assertIn("CT-01", content)
                self.assertIn("SAFE", content)


if __name__ == "__main__":
    unittest.main()
