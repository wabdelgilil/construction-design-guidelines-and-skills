"""
Unit tests for Earthing & Lightning Protection System (LPS) Skill.
"""

import unittest
from pathlib import Path
import tempfile
from electrical.earthing.scripts.design_engine import (
    EarthingEngine,
    EarthingProjectInput,
)
from electrical.earthing.scripts.run_design import generate_earthing_package


class TestEarthingSkill(unittest.TestCase):
    def setUp(self):
        self.engine = EarthingEngine(standard="IEEE 80 / SBC 401 / IEC 62305")

    def test_dwight_single_rod_and_grid(self):
        inp = EarthingProjectInput(
            project_name="Commercial Complex",
            facility_type="commercial_building",
            building_length_m=30.0,
            building_width_m=20.0,
            building_height_m=15.0,
            soil_resistivity_ohm_m=80.0,
            rod_length_m=3.0,
            rod_diameter_m=0.019,
            lps_level="LPL_III",
        )
        res = self.engine.design_earthing_and_lps(inp)

        self.assertGreater(res.single_rod_resistance_ohms, 0.0)
        self.assertGreater(res.perimeter_ring_resistance_ohms, 0.0)
        self.assertLessEqual(res.combined_earthing_resistance_ohms, 5.0)  # Commercial building limit <= 5.0 Ohm
        self.assertEqual(res.earthing_compliance_status, "COMPLIANT")
        self.assertEqual(res.rolling_sphere_radius_m, 45.0)
        self.assertGreaterEqual(res.down_conductors_count, 4)
        self.assertGreater(res.total_70mm2_bare_copper_m, 0.0)

    def test_substation_critical_earthing(self):
        inp = EarthingProjectInput(
            project_name="High Voltage Substation",
            facility_type="substation",
            building_length_m=40.0,
            building_width_m=30.0,
            building_height_m=8.0,
            soil_resistivity_ohm_m=60.0,
            lps_level="LPL_I",
        )
        res = self.engine.design_earthing_and_lps(inp)

        self.assertEqual(res.target_resistance_ohms, 1.0)
        self.assertLessEqual(res.combined_earthing_resistance_ohms, 1.0)
        self.assertEqual(res.rolling_sphere_radius_m, 20.0)  # LPL I sphere = 20m

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            inp = EarthingProjectInput(
                project_name="Test Facility",
                facility_type="commercial_building",
                building_length_m=20.0,
                building_width_m=15.0,
                building_height_m=10.0,
            )
            files = generate_earthing_package(
                input_data=inp,
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Test Facility", content)
                self.assertIn("IEEE 80", content)
                self.assertIn("Dwight", content)


if __name__ == "__main__":
    unittest.main()
