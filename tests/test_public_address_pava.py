"""
Unit tests for Public Address & Voice Alarm (PA/VA) System Skill.
"""

import unittest
from pathlib import Path
import tempfile
from electrical.low_current_elv.public_address_pava.scripts.design_engine import (
    PAVADesignEngine,
    PAVAZoneInput,
)
from electrical.low_current_elv.public_address_pava.scripts.run_design import generate_pava_package


class TestPublicAddressPAVASkill(unittest.TestCase):
    def setUp(self):
        self.engine = PAVADesignEngine(standard="BS 5839-8 / EN 54-16 / EN 54-24 / SBC 801")

    def test_acoustic_coverage_and_battery_sizing(self):
        zones = [
            PAVAZoneInput("Main Corridor", "corridor", length_m=30.0, width_m=2.5, is_emergency_egress=True),
            PAVAZoneInput("Corporate Office", "office", length_m=20.0, width_m=15.0, is_emergency_egress=False),
            PAVAZoneInput("Plant Room", "plant_room", length_m=15.0, width_m=10.0, speaker_type="weatherproof_horn"),
        ]
        res = self.engine.design_system("Corporate Tower PAVA", zones)

        self.assertEqual(res.total_zones_count, 3)
        self.assertGreater(res.total_speakers_count, 0)
        self.assertGreater(res.total_circuit_a_speakers, 0)
        self.assertGreater(res.total_circuit_b_speakers, 0)
        self.assertTrue(res.ab_interleaving_compliant)

        # SPL & STI checks
        for z in res.zones:
            self.assertGreaterEqual(z.calculated_spl_at_ear_dba, 65.0)
            self.assertGreaterEqual(z.snr_achieved_dba, 10.0)
            self.assertGreaterEqual(z.sti_estimate, 0.50)

        # Amplifier N+1 check
        self.assertGreaterEqual(res.main_amplifiers_count, 1)
        self.assertEqual(res.standby_amplifiers_count, 1)

        # 24h+30m Battery Sizing
        self.assertGreater(res.calculated_battery_ah, 0.0)
        self.assertGreaterEqual(res.selected_battery_ah, res.calculated_battery_ah)

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            zones = [
                PAVAZoneInput("Lobby", "lobby", length_m=15.0, width_m=10.0, ceiling_height_m=3.5),
            ]
            files = generate_pava_package(
                project_name="Hotel PAVA",
                zones=zones,
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Hotel PAVA", content)
                self.assertIn("BS 5839-8", content)
                self.assertIn("EN 54-16", content)


if __name__ == "__main__":
    unittest.main()
