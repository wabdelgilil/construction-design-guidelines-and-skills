"""
Unit tests for CAD, Excel, and BOQ Exporters.
"""

import unittest
from pathlib import Path
import ezdxf
import openpyxl

from structural.foundations.isolated_footing.scripts.run_design import (
    generate_isolated_footing_package,
)


class TestEngineeringExporters(unittest.TestCase):

    def setUp(self):
        self.output_dir = Path(__file__).resolve().parent.parent / "output" / "test_run"
        self.files = generate_isolated_footing_package(
            col_l_mm=500,
            col_w_mm=300,
            dead_load_kn=800,
            live_load_kn=400,
            soil_capacity_kpa=200,
            code="SBC",
            element_id="TEST-F01",
            output_dir=self.output_dir,
        )

    def test_all_deliverables_created(self):
        """Verify all 4 core deliverables exist on disk."""
        self.assertTrue(self.files["calc_note_md"].is_file())
        self.assertTrue(self.files["autocad_dxf"].is_file())
        self.assertTrue(self.files["excel_workbook"].is_file())
        self.assertTrue(self.files["revit_script"].is_file())

    def test_dxf_drawing_layers_and_entities(self):
        """Verify AutoCAD DXF has valid entities and standard engineering layers."""
        doc = ezdxf.readfile(str(self.files["autocad_dxf"]))
        msp = doc.modelspace()
        self.assertGreater(len(list(msp)), 15)

        layer_names = [l.dxf.name for l in doc.layers]
        self.assertIn("S-CONC-RC", layer_names)
        self.assertIn("S-REBAR-BOT", layer_names)
        self.assertIn("S-COLUMN", layer_names)
        self.assertIn("S-TEXT", layer_names)

    def test_excel_workbook_sheets_and_content(self):
        """Verify Excel workbook tabs, BBS, and BOQ items."""
        wb = openpyxl.load_workbook(str(self.files["excel_workbook"]), data_only=False)
        self.assertEqual(
            wb.sheetnames,
            ["Design Calculation", "Bar Bending Schedule", "BOQ & Cost Estimation"],
        )

        ws_calc = wb["Design Calculation"]
        self.assertEqual(ws_calc["A1"].value, "STRUCTURAL DESIGN CALCULATION SHEET")

        ws_bbs = wb["Bar Bending Schedule"]
        self.assertEqual(ws_bbs["A4"].value, "Bar Mark")

        ws_boq = wb["BOQ & Cost Estimation"]
        self.assertEqual(ws_boq["B4"].value, "Description of Works")


if __name__ == "__main__":
    unittest.main()
