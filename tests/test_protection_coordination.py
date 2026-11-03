"""
Unit tests for Short-Circuit Calculation & Protection Discrimination (TCC Curves) Skill.
"""

import unittest
from pathlib import Path
import tempfile
from electrical.power_distribution.protection_coordination.scripts.design_engine import (
    ProtectionCoordinationEngine,
    TransformerInput,
    FeederCableInput,
)
from electrical.power_distribution.protection_coordination.scripts.run_design import generate_protection_coordination_package


class TestProtectionCoordinationSkill(unittest.TestCase):
    def setUp(self):
        self.engine = ProtectionCoordinationEngine(standard="IEC 60909 / IEC 60947-2 / IEEE 242 / SBC 401")
        self.tr = TransformerInput(rating_kva=1500.0, voltage_primary_v=13800.0, voltage_secondary_v=400.0, uk_percent=6.0)
        self.smdb_feed = FeederCableInput("MDB to SMDB", "MDB", "SMDB", length_m=45.0, csa_mm2=300.0, runs_per_phase=3)
        self.db_feed = FeederCableInput("SMDB to DB", "SMDB", "DB", length_m=35.0, csa_mm2=16.0, runs_per_phase=1)

    def test_impedance_and_short_circuit_damping(self):
        res = self.engine.calculate_coordination(
            project_name="Power Coordination Test",
            transformer=self.tr,
            smdb_feeder=self.smdb_feed,
            db_feeder=self.db_feed,
        )

        self.assertEqual(len(res.bus_faults), 3)
        # Symmetrical fault current must decrease down the hierarchy due to cable impedance
        isc_mdb = res.bus_faults[0].isc_sym_ka
        isc_smdb = res.bus_faults[1].isc_sym_ka
        isc_db = res.bus_faults[2].isc_sym_ka

        self.assertGreater(isc_mdb, isc_smdb)
        self.assertGreater(isc_smdb, isc_db)

        # Breaking capacity Icu must exceed prospective fault current
        for b in res.bus_faults:
            self.assertGreaterEqual(b.rated_breaking_capacity_icu_ka, b.isc_sym_ka)

        # Incomer ACB withstand Icw(1s) must exceed MDB fault
        self.assertGreaterEqual(res.bus_faults[0].rated_withstand_icw_ka, isc_mdb * 0.9)

        # Discrimination verification
        self.assertEqual(len(res.selectivity_pairs), 2)
        self.assertEqual(res.selectivity_pairs[0].selectivity_status, "TOTAL DISCRIMINATION")
        self.assertGreaterEqual(res.selectivity_pairs[0].time_margin_ms, 100.0)

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            files = generate_protection_coordination_package(
                project_name="Facility Substation TCC",
                transformer=self.tr,
                smdb_feeder=self.smdb_feed,
                db_feeder=self.db_feed,
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Facility Substation TCC", content)
                self.assertIn("IEC 60909", content)
                self.assertIn("LSIG", content)


if __name__ == "__main__":
    unittest.main()
