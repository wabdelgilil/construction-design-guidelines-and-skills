"""
Unit tests for Specialized Hospital Operating Room Isolated Power System (IPS).
"""

import unittest
from pathlib import Path
import tempfile
from electrical.power_distribution.medical_isolated_power_ips.scripts.design_engine import (
    MedicalIPSEngine,
    MedicalLoadItem,
)
from electrical.power_distribution.medical_isolated_power_ips.scripts.run_design import generate_medical_ips_package


class TestMedicalIPSSkill(unittest.TestCase):
    def setUp(self):
        self.engine = MedicalIPSEngine(voltage_v=230.0, standard="IEC 60364-7-710 / SBC 401")

    def test_transformer_sizing(self):
        loads = [
            MedicalLoadItem("L1", "Surgical Lights", 500.0, 0.9, True, 1),
            MedicalLoadItem("L2", "Anesthesia Machine", 1500.0, 0.85, True, 1),
            MedicalLoadItem("L3", "Electrosurgical Unit", 1200.0, 0.8, True, 1),
        ]
        res = self.engine.design_system("OR-01", loads)

        # Total load ~ 3.2 kW -> design kVA with demand factor ~ 3.6 kVA -> selected transformer 4.0 or 5.0 kVA
        self.assertIn(res.selected_transformer_kva, [3.15, 4.0, 5.0, 6.3, 8.0, 10.0])
        self.assertEqual(res.imd_alarm_threshold_kohm, 50.0)
        self.assertEqual(res.equipotential_bonding_max_resistance_ohms, 0.10)
        self.assertEqual(res.primary_mcb_curve, "Curve D (High Inrush Withstand)")

    def test_double_pole_branch_circuits(self):
        loads = [
            MedicalLoadItem("L1", "Ventilator", 400.0, 0.85, True, 2),
        ]
        res = self.engine.design_system("OR-02", loads)
        # 2 load circuits + 2 spare circuits = 4 circuits
        self.assertEqual(len(res.secondary_circuits), 4)
        for ckt in res.secondary_circuits:
            self.assertEqual(ckt.breaker_type, "2-Pole (DP) MCB")
            self.assertEqual(ckt.breaker_rating_amps, 16)
            self.assertEqual(ckt.cable_size_sqmm, 4.0)

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            loads = [
                MedicalLoadItem("EQ-01", "OR Table", 500.0, 0.8, False, 1),
                MedicalLoadItem("EQ-02", "Diathermy", 1500.0, 0.8, True, 1),
            ]
            files = generate_medical_ips_package(
                room_name="General Surgery OR",
                medical_loads=loads,
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("General Surgery OR", content)
                self.assertIn("IEC 60364-7-710", content)
                self.assertIn("50 k", content)


if __name__ == "__main__":
    unittest.main()
