"""
Unit tests for Reinforced Concrete Rectangular Combined Footing Design Engine.
"""

import unittest
from structural.foundations.combined_footing.scripts.design_engine import (
    CombinedFootingInput,
    CombinedFootingEngine,
)


class TestCombinedFooting(unittest.TestCase):

    def test_sbc_combined_footing_standard_case(self):
        """Test combined footing design under SBC 304."""
        data = CombinedFootingInput(
            col1_length_mm=500.0,
            col1_width_mm=300.0,
            col1_dead_load_kn=700.0,
            col1_live_load_kn=350.0,
            col2_length_mm=600.0,
            col2_width_mm=400.0,
            col2_dead_load_kn=1100.0,
            col2_live_load_kn=550.0,
            span_center_to_center_m=4.5,
            col1_edge_distance_m=0.35,
            allowable_soil_capacity_kpa=200.0,
            fc_prime_mpa=28.0,
            fy_mpa=420.0,
            code="SBC",
        )
        engine = CombinedFootingEngine(data)
        res = engine.design()

        # Soil pressure check
        self.assertLessEqual(res.actual_service_soil_pressure_kpa, 205.0)

        # Zero shear must occur between Col 1 and Col 2 (between 0.35m and 4.85m)
        self.assertGreater(res.zero_shear_point_from_left_m, 0.35)
        self.assertLess(res.zero_shear_point_from_left_m, 4.85)

        # Negative moment and top reinforcement
        self.assertGreater(res.max_negative_moment_kn_m, 100.0)
        self.assertIn("Top Continuous Layer", res.top_longitudinal_rebar_desc)

        # Safety checks
        self.assertEqual(res.punching_status, "SAFE")
        self.assertEqual(res.beam_shear_status, "SAFE")
        self.assertEqual(res.overall_status, "SAFE")

    def test_ecp_combined_footing(self):
        """Test combined footing design under ECP 203."""
        data = CombinedFootingInput(
            col1_length_mm=400.0,
            col1_width_mm=300.0,
            col1_dead_load_kn=500.0,
            col1_live_load_kn=250.0,
            col2_length_mm=500.0,
            col2_width_mm=300.0,
            col2_dead_load_kn=800.0,
            col2_live_load_kn=400.0,
            span_center_to_center_m=4.0,
            col1_edge_distance_m=0.30,
            allowable_soil_capacity_kpa=150.0,
            fc_prime_mpa=30.0,
            fy_mpa=400.0,
            code="ECP",
        )
        engine = CombinedFootingEngine(data)
        res = engine.design()

        self.assertEqual(res.overall_status, "SAFE")
        self.assertEqual(res.code_used, "ECP")


if __name__ == "__main__":
    unittest.main()
