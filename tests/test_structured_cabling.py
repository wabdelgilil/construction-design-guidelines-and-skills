"""
Unit tests for Structured Cabling Infrastructure & Telecom Racks Skill.
"""

import unittest
from pathlib import Path
import tempfile
from electrical.low_current_elv.structured_cabling.scripts.design_engine import (
    StructuredCablingEngine,
    TelecomZoneInput,
)
from electrical.low_current_elv.structured_cabling.scripts.run_design import generate_structured_cabling_package


class TestStructuredCablingSkill(unittest.TestCase):
    def setUp(self):
        self.engine = StructuredCablingEngine(standard="ANSI/TIA-568-D / ISO/IEC 11801 / SBC 401")

    def test_horizontal_ports_and_rack_space_sizing(self):
        zones = [
            TelecomZoneInput("Zone A", workstations_count=20, wap_count=2, cctv_cameras_count=4, access_control_doors_count=2, max_distance_to_idf_m=50.0),
            TelecomZoneInput("Zone B", workstations_count=10, wap_count=2, cctv_cameras_count=2, access_control_doors_count=1, max_distance_to_idf_m=65.0),
        ]
        res = self.engine.design_system("Office Building SCS", zones, spare_ports_margin=0.20)

        self.assertGreater(res.grand_total_horizontal_ports, 0)
        self.assertGreater(res.spare_ports_equipped, 0)
        self.assertGreaterEqual(res.patch_panels_24p_count, 1)
        self.assertGreaterEqual(res.switches_48p_count, 1)
        self.assertEqual(res.total_42u_racks_count, 1)
        self.assertGreater(res.total_u_utilized, 0)
        self.assertGreater(res.total_u_spare, 0)
        self.assertGreaterEqual(res.spare_u_percentage, 25.0)
        self.assertGreaterEqual(res.recommended_ups_va, 1000)
        self.assertTrue(res.permanent_link_compliant)

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            zones = [
                TelecomZoneInput("Floor 2", workstations_count=15, wap_count=2, cctv_cameras_count=4, access_control_doors_count=2, max_distance_to_idf_m=40.0),
            ]
            files = generate_structured_cabling_package(
                project_name="Regional Branch SCS",
                zones=zones,
                spare_ports_margin=0.20,
                ups_autonomy_min=30.0,
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Regional Branch SCS", content)
                self.assertIn("ANSI/TIA-568-D", content)
                self.assertIn("42U", content)


if __name__ == "__main__":
    unittest.main()
