"""
Unit tests for Electrical Design Engines and CAD Space Extractor.
"""

import unittest
from core.cad_engine.space_extractor import point_in_polygon, polygon_area, polygon_centroid
from electrical.power_distribution.scripts.panel_balancer import BranchCircuit, PanelBalancer
from electrical.lighting.scripts.lumen_engine import LumenEngine
from electrical.cables.scripts.cable_engine import CableEngine


class TestElectricalAndCAD(unittest.TestCase):

    def test_cad_geometry_algorithms(self):
        """Test Point-in-Polygon and Shoelace polygon area algorithms."""
        # 5m x 4m rectangle
        rect = [(0.0, 0.0), (5.0, 0.0), (5.0, 4.0), (0.0, 4.0)]
        area = polygon_area(rect)
        self.assertEqual(area, 20.0)

        centroid = polygon_centroid(rect)
        self.assertEqual(centroid, (2.5, 2.0))

        # Test internal and external points
        self.assertTrue(point_in_polygon(2.5, 2.0, rect))
        self.assertFalse(point_in_polygon(6.0, 2.0, rect))
        self.assertFalse(point_in_polygon(-1.0, 2.0, rect))

    def test_panel_load_balancer(self):
        """Test 3-phase electrical panel load balancer unbalance optimization."""
        circuits = [
            BranchCircuit("C-1", "Living Room Sockets", 2000.0),
            BranchCircuit("C-2", "Kitchen Refrigerator", 1500.0),
            BranchCircuit("C-3", "Master Bed AC", 2800.0),
            BranchCircuit("C-4", "Living AC", 3200.0),
            BranchCircuit("C-5", "General Lighting", 1200.0),
            BranchCircuit("C-6", "Water Heater", 2000.0),
        ]
        res = PanelBalancer.balance_panel("DB-GF", circuits, system_voltage_v=400.0)

        # Unbalance must be minimized (< 5% or close)
        self.assertLessEqual(res.unbalance_pct, 10.0)
        self.assertGreater(res.main_breaker_rating_a, 20)
        self.assertEqual(len(res.circuits), 6)

    def test_lumen_lighting_engine(self):
        """Test room lumen method and fixture grid spacing."""
        # 6m x 4m office room, target 400 lux
        res = LumenEngine.design_room_lighting(
            room_name="Office_101",
            length_m=6.0,
            width_m=4.0,
            target_lux=400.0,
        )
        self.assertGreaterEqual(res.achieved_lux, 380.0)
        self.assertGreater(res.total_fixtures_count, 0)
        self.assertEqual(len(res.fixture_coordinates), res.total_fixtures_count)
        self.assertEqual(res.compliance_status, "COMPLIANT")

    def test_cable_sizing_and_voltage_drop(self):
        """Test cable ampacity and voltage drop compliance."""
        # 5 kW 1-phase load over 35 meters
        res = CableEngine.size_cable(
            load_kw=5.0,
            phases=1,
            system_voltage_v=230.0,
            circuit_length_m=35.0,
            is_branch_circuit=True,
        )
        self.assertEqual(res.compliance_status, "SAFE")
        self.assertLessEqual(res.voltage_drop_pct, 3.0)
        self.assertGreaterEqual(res.breaker_rating_in, res.design_current_ib)


if __name__ == "__main__":
    unittest.main()
