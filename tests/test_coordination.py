"""
Unit tests for Cross-Discipline Coordination and Interface Registry.
"""

import unittest
from core.coordination.coordinator import DisciplineCoordinator


class TestDisciplineCoordinator(unittest.TestCase):

    def setUp(self):
        self.coord = DisciplineCoordinator()

    def test_query_hvac_to_electrical_interfaces(self):
        """Verify thermostat and AC isolator interfaces are surfaced for electrical."""
        results = self.coord.query_interfaces("electrical", keywords=["thermostat"])
        self.assertGreater(len(results), 0)
        item = results[0]
        self.assertEqual(item["id"], "INT-HVAC-ELEC-01")
        self.assertIn("thermostat", item["element"])
        self.assertIn("150 cm AFF", item["requirement_for_target"])

    def test_query_plumbing_to_structural_pipe_sleeves(self):
        """Verify pipe sleeves in foundation walls are surfaced for structural."""
        results = self.coord.query_interfaces("structural", keywords=["foundation"])
        self.assertGreater(len(results), 0)
        ids = [r["id"] for r in results]
        self.assertIn("INT-PLUMB-STRUCT-01", ids)

    def test_markdown_checklist_generation(self):
        """Verify checklist formatting for electrical design."""
        checklist = self.coord.generate_coordination_checklist(
            "electrical", keywords=["ac", "heater"]
        )
        self.assertIn("Cross-Discipline Coordination Checklist", checklist)
        self.assertIn("INT-HVAC-ELEC-02", checklist)
        self.assertIn("INT-PLUMB-ELEC-01", checklist)


if __name__ == "__main__":
    unittest.main()
