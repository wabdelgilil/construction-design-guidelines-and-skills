"""
Unit tests for Automatic Power Factor Correction (APFC) & Detuned Filter Sizing Skill.
"""

import unittest
from pathlib import Path
import tempfile
from electrical.power_distribution.power_factor_correction.scripts.design_engine import (
    PowerFactorCorrectionEngine,
)
from electrical.power_distribution.power_factor_correction.scripts.run_design import generate_apfc_package


class TestPowerFactorCorrectionSkill(unittest.TestCase):
    def setUp(self):
        self.engine = PowerFactorCorrectionEngine(standard="IEC 61921 / IEC 60831 / IEEE 519 / SBC 401")

    def test_kvar_calculation_and_detuning_parameters(self):
        res = self.engine.calculate_apfc_bank(
            project_name="Mall APFC",
            active_power_kw=600.0,
            initial_pf=0.82,
            target_pf=0.97,
            nominal_voltage_v=400.0,
            frequency_hz=60.0,
            detuning_reactor_p_percent=7.0,
        )

        self.assertGreater(res.calculated_kvar, 0.0)
        self.assertGreaterEqual(res.selected_total_kvar, res.calculated_kvar)
        self.assertGreater(res.total_steps_count, 1)

        # 7% tuning frequency check (~227 Hz for 60Hz)
        self.assertAlmostEqual(res.tuning_frequency_hz, 226.8, delta=1.0)

        # Heavy-duty capacitor voltage rating check (must be >= 480V)
        self.assertGreaterEqual(res.capacitor_rated_voltage_v, 480.0)

        # Incomer sizing check (must accommodate 1.43x nominal current)
        self.assertGreaterEqual(res.incomer_mccb_rating_a, res.total_bank_nominal_current_a * 1.3)

        # Apparent power release check
        self.assertGreater(res.apparent_power_released_kva, 0.0)
        self.assertGreater(res.line_current_reduction_a, 0.0)

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            files = generate_apfc_package(
                project_name="Data Center APFC",
                active_power_kw=400.0,
                initial_pf=0.85,
                target_pf=0.96,
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Data Center APFC", content)
                self.assertIn("IEC 61921", content)
                self.assertIn("kVAR", content)


if __name__ == "__main__":
    unittest.main()
