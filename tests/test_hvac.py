"""
Unit tests for Mechanical HVAC Cooling Load & Air Distribution Skill.
"""

import unittest
from pathlib import Path
import tempfile
from mechanical.hvac.heat_load.scripts.design_engine import (
    CoolingLoadEngine,
    HVACSpaceInput,
)
from mechanical.hvac.heat_load.scripts.run_design import generate_hvac_package


class TestHVACSkill(unittest.TestCase):
    def setUp(self):
        self.engine = CoolingLoadEngine(code="SBC")

    def test_cooling_load_calculation(self):
        inp = HVACSpaceInput(
            space_name="Office Room",
            length_m=6.0,
            width_m=5.0,
            height_m=3.0,
            occupant_count=3,
            lighting_power_watts=150.0,
            equipment_power_watts=450.0,
            external_wall_area_m2=15.0,
            glass_window_area_m2=3.0,
        )
        res = self.engine.compute_cooling_load(inp)

        self.assertEqual(res.area_m2, 30.0)
        self.assertGreater(res.grand_total_heat_w, 0)
        self.assertGreater(res.selected_unit_tons_tr, 0)
        self.assertGreater(res.supply_airflow_cfm, 0)
        self.assertGreater(res.supply_diffusers_count, 0)
        self.assertTrue(0.70 <= res.sensible_heat_ratio_shr <= 0.95)

    def test_electrical_coordination_parameters(self):
        inp = HVACSpaceInput(
            space_name="Large Open Office",
            length_m=12.0,
            width_m=8.0,
            occupant_count=12,
            lighting_power_watts=600.0,
            equipment_power_watts=1800.0,
            external_wall_area_m2=36.0,
            glass_window_area_m2=12.0,
        )
        res = self.engine.compute_cooling_load(inp)

        self.assertGreater(res.equipment_electrical_kw, 0)
        self.assertGreater(res.electrical_mca_amps, 0)
        self.assertGreater(res.electrical_mop_amps, res.electrical_mca_amps)
        self.assertEqual(res.thermostat_height_aff_m, 1.50)
        self.assertEqual(res.isolator_height_aff_m, 2.20)
        self.assertTrue(len(res.coordination_notices) >= 4)

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            inp = HVACSpaceInput(
                space_name="Board Room",
                length_m=7.0,
                width_m=5.0,
                occupant_count=6,
                lighting_power_watts=200.0,
                equipment_power_watts=500.0,
            )
            files = generate_hvac_package(inp, code="SBC", output_dir=out_path)

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Board Room", content)
                self.assertIn("SBC 501", content)
                self.assertIn("Thermostat", content)


if __name__ == "__main__":
    unittest.main()
