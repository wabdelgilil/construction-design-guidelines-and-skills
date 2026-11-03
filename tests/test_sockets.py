"""
Unit tests for Electrical Small Power Sockets design engine and multi-deliverable generation.
"""

import unittest
from pathlib import Path
import tempfile
from electrical.power_distribution.sockets.scripts.design_engine import (
    SocketCircuitEngine,
    SocketGroupRequest,
)
from electrical.power_distribution.sockets.scripts.run_design import generate_socket_package


class TestSocketsDesign(unittest.TestCase):
    def setUp(self):
        self.engine = SocketCircuitEngine(voltage_v=230.0, code="SBC")

    def test_general_sockets_grouping(self):
        # 22 sockets in a hall -> should split into ceil(22/10) = 3 circuits under SBC
        reqs = [SocketGroupRequest("Big Hall", 22, [])]
        result = self.engine.design_sockets(reqs)

        self.assertEqual(len(result.circuits), 3)
        self.assertEqual(result.circuits[0].outlet_count, 10)
        self.assertEqual(result.circuits[1].outlet_count, 10)
        self.assertEqual(result.circuits[2].outlet_count, 2)
        self.assertEqual(result.circuits[0].breaker_rating_amps, 16)
        self.assertEqual(result.circuits[0].cable_size_sqmm, 2.5)

    def test_dedicated_appliance_circuit(self):
        # Dedicated split AC unit (2500W) -> breaker should be 20A, cable 4.0 mm2
        reqs = [SocketGroupRequest("Bedroom", 4, ["room_ac_split"])]
        result = self.engine.design_sockets(reqs)

        # 1 general circuit + 1 dedicated AC circuit = 2 circuits
        self.assertEqual(len(result.circuits), 2)
        ac_ckt = next(c for c in result.circuits if c.is_dedicated)
        self.assertEqual(ac_ckt.breaker_rating_amps, 20)
        self.assertEqual(ac_ckt.cable_size_sqmm, 4.0)

    def test_coordination_notices_generation(self):
        # Water heater in bathroom -> should trigger cross-discipline notice
        reqs = [SocketGroupRequest("En-suite Bathroom", 2, ["water_heater"])]
        result = self.engine.design_sockets(reqs)

        self.assertTrue(len(result.coordination_notices) > 0)
        self.assertTrue(any("Water Heater" in n or "water_heater" in n for n in result.coordination_notices))

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            reqs = [
                SocketGroupRequest("Office", 8, ["water_dispenser"]),
                SocketGroupRequest("Server Room", 4, ["room_ac_split"]),
            ]
            files = generate_socket_package(reqs, code="SBC", output_dir=out_path)

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_schematic"].exists())

            # Check calc note contents
            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Office", content)
                self.assertIn("Server Room", content)
                self.assertIn("PASS", content)


if __name__ == "__main__":
    unittest.main()
