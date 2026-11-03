"""
Unit tests for Architectural Space Planning & Room Matrix Compliance Skill.
"""

import unittest
from pathlib import Path
import tempfile
from architectural.space_planning.scripts.design_engine import (
    SpacePlanningEngine,
    RoomDefinition,
)
from architectural.space_planning.scripts.run_design import generate_space_planning_package


class TestSpacePlanningSkill(unittest.TestCase):
    def setUp(self):
        self.engine = SpacePlanningEngine(typology="residential", code="SBC")
        self.rules = {
            "master_bedroom": {"min_area_m2": 14.0, "min_width_m": 3.2, "min_height_m": 2.8, "min_glazing_ratio": 0.10},
            "bathroom": {"min_area_m2": 3.2, "min_width_m": 1.4, "min_height_m": 2.4, "min_glazing_ratio": 0.05},
        }

    def test_compliant_room(self):
        rooms = [
            RoomDefinition("MBR", "Master Bedroom", "master_bedroom", 5.0, 4.0, 3.0, 2.5),
        ]
        res = self.engine.audit_spaces("Villa 1", rooms, self.rules)

        self.assertTrue(res.all_rooms_pass)
        self.assertEqual(res.rooms_audited[0].overall_status, "COMPLIANT")
        self.assertEqual(res.rooms_audited[0].area_m2, 20.0)

    def test_undersized_room_detection(self):
        rooms = [
            RoomDefinition("MBR-Small", "Substandard Room", "master_bedroom", 3.0, 3.0, 2.5, 0.5),
        ]
        res = self.engine.audit_spaces("Villa 2", rooms, self.rules)

        self.assertFalse(res.all_rooms_pass)
        self.assertEqual(res.rooms_audited[0].overall_status, "NON-COMPLIANT")
        self.assertFalse(res.rooms_audited[0].area_pass)   # 9m2 < 14m2
        self.assertFalse(res.rooms_audited[0].height_pass) # 2.5m < 2.8m

    def test_multi_deliverables_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            rooms = [
                RoomDefinition("MBR", "Master Bed", "master_bedroom", 4.5, 3.5, 3.0, 2.0),
            ]
            files = generate_space_planning_package(
                project_name="Test Villa",
                rooms=rooms,
                typology="residential",
                code="SBC",
                output_dir=out_path,
            )

            self.assertTrue(files["calc_note_md"].exists())
            self.assertTrue(files["excel_workbook"].exists())
            self.assertTrue(files["dxf_drawing"].exists())

            with open(files["calc_note_md"], "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Test Villa", content)
                self.assertIn("Master Bed", content)


if __name__ == "__main__":
    unittest.main()
