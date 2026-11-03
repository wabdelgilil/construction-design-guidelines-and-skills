"""
Benchmark and Unit Tests for the Isolated Footing Design Engine.
"""

import unittest
from structural.foundations.isolated_footing.scripts.design_engine import (
    FootingInput,
    IsolatedFootingEngine,
)


class TestIsolatedFootingEngine(unittest.TestCase):

    def test_sbc_isolated_footing_standard_case(self):
        """Test standard isolated footing design under SBC 304."""
        data = FootingInput(
            column_length_mm=500.0,
            column_width_mm=300.0,
            dead_load_kn=800.0,
            live_load_kn=400.0,
            allowable_soil_capacity_kpa=200.0,
            fc_prime_mpa=28.0,
            fy_mpa=420.0,
            concrete_cover_mm=75.0,
            preferred_bar_dia_mm=14,
            code="SBC",
        )
        engine = IsolatedFootingEngine(data)
        res = engine.design()

        # Check soil pressure
        self.assertLessEqual(res.actual_soil_pressure_service_kpa, 205.0)

        # Check punching shear safety
        self.assertEqual(res.punching_status, "SAFE")
        self.assertLessEqual(res.punching_safety_ratio, 1.0)

        # Check beam shear safety
        self.assertEqual(res.beam_shear_status, "SAFE")
        self.assertLessEqual(res.beam_shear_safety_ratio, 1.0)

        # Check flexure steel
        self.assertGreater(res.as_provided_l_mm2, res.as_min_l_mm2)
        self.assertGreater(res.as_provided_b_mm2, res.as_min_b_mm2)
        self.assertGreaterEqual(res.bars_l_count, 5)

        # Check overall status
        self.assertEqual(res.overall_status, "SAFE")

    def test_ecp_isolated_footing(self):
        """Test isolated footing design under Egyptian Code ECP 203."""
        data = FootingInput(
            column_length_mm=600.0,
            column_width_mm=300.0,
            dead_load_kn=1000.0,
            live_load_kn=500.0,
            allowable_soil_capacity_kpa=150.0,
            fc_prime_mpa=30.0,  # fcu
            fy_mpa=400.0,
            concrete_cover_mm=70.0,
            preferred_bar_dia_mm=16,
            code="ECP",
        )
        engine = IsolatedFootingEngine(data)
        res = engine.design()

        # ECP Ultimate load: 1.4*1000 + 1.6*500 = 2200 kN
        self.assertAlmostEqual(res.ultimate_load_kn, 2200.0, places=1)
        self.assertEqual(res.punching_status, "SAFE")
        self.assertEqual(res.beam_shear_status, "SAFE")
        self.assertEqual(res.overall_status, "SAFE")

    def test_projections_equality(self):
        """Test that cantilevers in L and B directions are approximately equal."""
        data = FootingInput(
            column_length_mm=600.0,
            column_width_mm=300.0,
            dead_load_kn=600.0,
            live_load_kn=300.0,
            allowable_soil_capacity_kpa=200.0,
            code="SBC",
        )
        engine = IsolatedFootingEngine(data)
        res = engine.design()

        # Difference between cantilevers should be minimal (due to 50mm rounding)
        diff = abs(res.cantilever_l_mm - res.cantilever_b_mm)
        self.assertLessEqual(diff, 50.0)


if __name__ == "__main__":
    unittest.main()
