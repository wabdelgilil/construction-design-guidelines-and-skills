"""
Unit tests for Substation, Transformer, Diesel Generator & MDB Sizing Skill.
"""

import unittest
from pathlib import Path
import tempfile
from electrical.power_distribution.substation.scripts.design_engine import (
    SubstationEngine,
    BuildingLoadsInput,
)
from electrical.power_distribution.substation.scripts.run_design import generate_substation_package


class TestSubstationSkill(unittest.TestCase):
    def setUp(self):
        self.engine = SubstationEngine(voltage_v=400.0, standard="IEC 60076 / SBC 401")

    def test_transformer_and_short_circuit_sizing(self):
        loads = BuildingLoadsInput(
            project_name="Office Tower",
            lighting_kw=50.0,
            sockets_kw=80.0,
            hvac_kw=300.0,
            elevators_kw=60.0,
            pumps_kw=30.0,
            life_safety_kw=40.0,
            it_ups_kw=30.0,
            largest_single_motor_kw=30.0,
        )
        res = self.engine.design_substation(loads)

        self.assertGreater(res.total_connected_kw, 0)
        self.assertGreater(res.max_demand_kva, 0)
        self.assertIn(res.selected_transformer_kva, [500, 630, 800, 1000, 1250, 1500, 1600, 2000, 2500])
        self.assertLessEqual(res.transformer_loading_pct, 85.0)
        self.assertGreater(res.prospective_short_circuit_ka, 10.0)
        self.assertGreaterEqual(res.mdb_incomer_icu_ka, res.prospective_short_circuit_ka)
        self.assertIn(res.selected_generator_kva, [100, 150, 200, 250, 350, 500, 650, 800, 1000, 1250])
        self.assertEqual(res.ats_poles, 4)

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            loads = BuildingLoadsInput(
                project_name="Test Substation",
                lighting_kw=20.0,
                sockets_kw=30.0,
                hvac_kw=100.0,
                elevators_kw=20.0,
                pumps_kw=15.0,
                life_safety_kw=25.0,
                it_ups_kw=10.0,
            )
            files = generate_substation_package(
                loads=loads,
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Test Substation", content)
                self.assertIn("Transformer", content)
                self.assertIn("Generator", content)


if __name__ == "__main__":
    unittest.main()
