"""
Unit tests for Reinforced Concrete Column Design Engine.
"""

import unittest
from structural.vertical_elements.columns.scripts.design_engine import ColumnInput, ColumnEngine


class TestColumns(unittest.TestCase):

    def test_sbc_short_column_standard(self):
        """Test short column axial capacity and dimensioning under SBC 304."""
        data = ColumnInput(
            dead_load_kn=1000.0,
            live_load_kn=500.0,
            unbraced_length_m=3.0,
            effective_length_factor_k=0.80,  # Standard braced building frame with top/bottom slabs
            preferred_width_mm=250.0,
            fc_prime_mpa=28.0,
            fy_mpa=420.0,
            code="SBC",
        )
        engine = ColumnEngine(data)
        res = engine.design()

        # Capacity check
        self.assertLessEqual(res.capacity_ratio, 1.0)
        self.assertEqual(res.overall_status, "SAFE")

        # Classification
        self.assertEqual(res.classification, "Short Column (No Buckling)")
        self.assertFalse(res.is_slender)

        # Reinforcement ratio must be between 1.0% and 4.0%
        self.assertGreaterEqual(res.actual_steel_ratio_pct, 1.0)
        self.assertLessEqual(res.actual_steel_ratio_pct, 4.0)
        self.assertGreaterEqual(res.total_bar_count, 4)

    def test_slender_column_detection(self):
        """Test slender column buckling detection under tall unbraced height."""
        data = ColumnInput(
            dead_load_kn=600.0,
            live_load_kn=300.0,
            unbraced_length_m=5.0,  # 5m unbraced with 200mm width -> slender
            preferred_width_mm=200.0,
            fc_prime_mpa=28.0,
            code="SBC",
        )
        engine = ColumnEngine(data)
        res = engine.design()

        # Slenderness lambda = 5000 / (0.30 * 200) = 83.3 > 40
        self.assertTrue(res.is_slender)
        self.assertIn("Slender", res.classification)

    def test_ecp_column_design(self):
        """Test column design under ECP 203."""
        data = ColumnInput(
            dead_load_kn=800.0,
            live_load_kn=400.0,
            unbraced_length_m=3.2,
            preferred_width_mm=250.0,
            fc_prime_mpa=30.0,  # fcu
            fy_mpa=400.0,
            code="ECP",
        )
        engine = ColumnEngine(data)
        res = engine.design()

        self.assertEqual(res.code_used, "ECP")
        self.assertEqual(res.overall_status, "SAFE")


if __name__ == "__main__":
    unittest.main()
