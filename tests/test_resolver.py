"""
Unit tests for the Hierarchical Context & Code Resolver.
"""

import unittest
from pathlib import Path
from core.resolver import TreeResolver


class TestTreeResolver(unittest.TestCase):

    def setUp(self):
        self.workspace_root = Path(__file__).resolve().parent.parent
        self.resolver = TreeResolver(self.workspace_root)

    def test_root_config_loaded(self):
        """Verify project_root.json is loaded correctly."""
        cfg = self.resolver.get_project_root_config()
        self.assertEqual(cfg.get("active_code"), "SBC")
        self.assertEqual(cfg.get("unit_system"), "SI")
        self.assertIn("SBC", cfg.get("supported_codes", []))

    def test_structural_parent_resolution_sbc(self):
        """Verify structural parent rules under SBC."""
        context = self.resolver.resolve_context("structural", code="SBC")
        self.assertEqual(context["active_code"], "SBC")
        rules = context["rules"]
        self.assertEqual(rules.get("concrete_strength_type"), "cylinder_fc")
        self.assertEqual(rules.get("default_fc_prime_mpa"), 28.0)
        self.assertEqual(rules.get("default_fy_mpa"), 420.0)
        self.assertEqual(rules.get("load_combinations", {}).get("uls_gravity"), "1.2D + 1.6L")

    def test_structural_parent_resolution_ecp(self):
        """Verify structural parent rules switch dynamically when ECP code is requested."""
        context = self.resolver.resolve_context("structural", code="ECP")
        self.assertEqual(context["active_code"], "ECP")
        rules = context["rules"]
        self.assertEqual(rules.get("concrete_strength_type"), "cube_fcu")
        self.assertEqual(rules.get("default_fcu_mpa"), 30.0)
        self.assertEqual(rules.get("default_fy_mpa"), 400.0)
        self.assertEqual(rules.get("load_combinations", {}).get("uls_gravity"), "1.4D + 1.6L")

    def test_electrical_parent_resolution(self):
        """Verify electrical voltage and frequency resolution for SBC vs NEC."""
        # SBC Test
        sbc_context = self.resolver.resolve_context("electrical", code="SBC")
        self.assertEqual(sbc_context["rules"].get("nominal_voltage_1phase_v"), 230)
        self.assertEqual(sbc_context["rules"].get("nominal_voltage_3phase_v"), 400)
        self.assertEqual(sbc_context["rules"].get("frequency_hz"), 60)

        # NEC Test
        nec_context = self.resolver.resolve_context("electrical", code="NEC")
        self.assertEqual(nec_context["rules"].get("nominal_voltage_1phase_v"), 120)
        self.assertEqual(nec_context["rules"].get("nominal_voltage_3phase_v"), 208)
        self.assertEqual(nec_context["rules"].get("frequency_hz"), 60)

    def test_mechanical_parent_resolution(self):
        """Verify mechanical indoor comfort setpoints."""
        context = self.resolver.resolve_context("mechanical", code="SBC")
        rules = context["rules"]
        comfort = rules.get("indoor_comfort", {})
        self.assertEqual(comfort.get("summer_temp_c"), 23.5)
        self.assertEqual(comfort.get("winter_temp_c"), 21.0)

    def test_architectural_parent_resolution(self):
        """Verify architectural minimum clearances."""
        context = self.resolver.resolve_context("architectural", code="SBC")
        rules = context["rules"]
        self.assertGreaterEqual(rules.get("min_ceiling_height_habitable_m"), 2.80)
        self.assertLessEqual(rules.get("stairs", {}).get("max_riser_mm"), 175)


if __name__ == "__main__":
    unittest.main()
