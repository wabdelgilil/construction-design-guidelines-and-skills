"""
Unit tests for CCTV Video Surveillance & Storage Sizing Skill.
"""

import unittest
from pathlib import Path
import tempfile
from electrical.cctv_security.scripts.design_engine import (
    CCTVSecurityEngine,
    CameraRequirement,
)
from electrical.cctv_security.scripts.run_design import generate_cctv_package


class TestCCTVSkill(unittest.TestCase):
    def setUp(self):
        self.engine = CCTVSecurityEngine(standard="EN 62676-4 / NFPA 730")

    def test_dori_and_focal_length_calculation(self):
        cams = [
            CameraRequirement("CAM-01", "Gate", "outdoor_bullet", "4k_8mp", "identification", 15.0, True),
            CameraRequirement("CAM-02", "Hall", "fixed_dome", "2mp_1080p", "recognition", 8.0, False),
        ]
        res = self.engine.design_cctv_system("HQ Security", cams, recording_days=31)

        self.assertEqual(res.total_cameras_count, 2)
        self.assertGreater(res.total_network_bandwidth_mbps, 0.0)
        self.assertGreater(res.net_storage_tb, 0.0)
        self.assertGreater(res.gross_raid_storage_tb, res.net_storage_tb)
        self.assertGreaterEqual(res.required_hdd_count, 2)
        self.assertGreater(res.total_poe_power_budget_watts, 0.0)

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            cams = [
                CameraRequirement("C-01", "Entrance", "fixed_dome", "4mp_1440p", "identification", 5.0),
            ]
            files = generate_cctv_package(
                project_name="Office Security",
                cameras=cams,
                recording_days=30,
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Office Security", content)
                self.assertIn("EN 62676-4", content)
                self.assertIn("NVR", content)


if __name__ == "__main__":
    unittest.main()
