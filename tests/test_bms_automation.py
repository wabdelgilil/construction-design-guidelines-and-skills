"""
Unit tests for Building Management System (BMS) & DDC Automation Control Skill.
"""

import unittest
from pathlib import Path
import tempfile
from electrical.low_current_elv.bms_automation.scripts.design_engine import (
    BMSDesignEngine,
    MEPEquipmentBMSInput,
)
from electrical.low_current_elv.bms_automation.scripts.run_design import generate_bms_package


class TestBMSAutomationSkill(unittest.TestCase):
    def setUp(self):
        self.engine = BMSDesignEngine(standard="ASHRAE 135 (BACnet) / ISO 16484 / SBC 601")

    def test_point_schedule_and_ddc_sizing(self):
        equipment = [
            MEPEquipmentBMSInput("AHU-01", "ahu", "Office AHU", "Roof Plant", has_vfd=True),
            MEPEquipmentBMSInput("CH-01", "chiller", "Chiller 1", "Basement Plant"),
            MEPEquipmentBMSInput("P-01", "pump", "CHW Pump", "Basement Plant", has_vfd=True),
            MEPEquipmentBMSInput("MDB", "substation_mdb", "Main MDB", "Substation"),
        ]
        res = self.engine.generate_bms_design("Facility BMS", equipment)

        self.assertEqual(len(res.equipment_points), 4)
        self.assertGreater(res.grand_total_active_points, 0)
        self.assertGreater(res.grand_total_spare_points, 0)
        self.assertGreaterEqual(res.grand_total_equipped_points, res.grand_total_active_points * 1.20)

        # DDC panels created for distinct locations (Roof Plant, Basement Plant, Substation)
        self.assertEqual(res.total_ddc_panels_count, 3)

        for p in res.ddc_panels:
            self.assertGreaterEqual(p.spare_points, math.ceil(p.active_points * 0.20))
            self.assertGreaterEqual(p.base_ddc_units_count, 1)

        self.assertGreaterEqual(res.recommended_ups_va, 1000)

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            equipment = [
                MEPEquipmentBMSInput("AHU-01", "ahu", "Supply AHU", "Mechanical Room", has_vfd=False),
            ]
            files = generate_bms_package(
                project_name="Clinic Automation",
                equipment_list=equipment,
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Clinic Automation", content)
                self.assertIn("BACnet", content)
                self.assertIn("DDC", content)


import math
if __name__ == "__main__":
    unittest.main()
