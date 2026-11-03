"""
Unit tests for Reinforced Concrete Strap (Cantilever) Footing Design Engine.
"""

import unittest
from structural.foundations.strap_footing.scripts.design_engine import (
    StrapFootingInput,
    StrapFootingEngine,
)


class TestStrapFooting(unittest.TestCase):

    def test_sbc_strap_footing_standard_case(self):
        """Test strap footing design under SBC 304."""
        data = StrapFootingInput(
            col1_length_mm=600.0,
            col1_width_mm=300.0,
            col1_dead_load_kn=900.0,
            col1_live_load_kn=450.0,
            col2_length_mm=600.0,
            col2_width_mm=400.0,
            col2_dead_load_kn=1400.0,
            col2_live_load_kn=700.0,
            span_center_to_center_m=5.5,
            allowable_soil_capacity_kpa=200.0,
            fc_prime_mpa=28.0,
            fy_mpa=420.0,
            code="SBC",
        )
        engine = StrapFootingEngine(data)
        res = engine.design()

        # Check overturning reaction magnification
        p1_service = 900.0 + 450.0
        self.assertGreater(res.f1_service_reaction_kn, p1_service)

        # Check strap beam sizing
        self.assertGreaterEqual(res.strap_depth_mm, 700.0)
        self.assertGreater(res.strap_max_negative_moment_kn_m, 100.0)
        self.assertGreater(res.strap_top_steel_as_mm2, 500.0)

        # Check safety statuses
        self.assertEqual(res.f1_status, "SAFE")
        self.assertEqual(res.f2_status, "SAFE")
        self.assertEqual(res.strap_status, "SAFE")
        self.assertEqual(res.overall_status, "SAFE")

    def test_ecp_strap_footing(self):
        """Test strap footing design under ECP 203."""
        data = StrapFootingInput(
            col1_length_mm=500.0,
            col1_width_mm=300.0,
            col1_dead_load_kn=700.0,
            col1_live_load_kn=350.0,
            col2_length_mm=500.0,
            col2_width_mm=300.0,
            col2_dead_load_kn=1000.0,
            col2_live_load_kn=500.0,
            span_center_to_center_m=5.0,
            allowable_soil_capacity_kpa=150.0,
            fc_prime_mpa=30.0,
            fy_mpa=400.0,
            code="ECP",
        )
        engine = StrapFootingEngine(data)
        res = engine.design()

        self.assertEqual(res.overall_status, "SAFE")
        self.assertEqual(res.code_used, "ECP")


if __name__ == "__main__":
    unittest.main()
