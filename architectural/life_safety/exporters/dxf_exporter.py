"""
AutoCAD DXF Exporter for Architectural Life Safety & Egress Plan.
Generates building perimeter, exit stair enclosures, travel paths, and fire alarm tags.
"""

from pathlib import Path
from ezdxf.enums import TextEntityAlignment
from core.exporters.dxf_writer import DXFWriter
from architectural.life_safety.scripts.design_engine import LifeSafetyProjectResult


class LifeSafetyDXFExporter:
    """Exports life safety egress plan to AutoCAD .dxf format."""

    def __init__(self, result: LifeSafetyProjectResult):
        self.res = result
        self.writer = DXFWriter("egress_plan.dxf")

    def export(self, filepath: Path) -> Path:
        scale = 1000.0  # mm
        l_mm = self.res.building_length_m * scale
        w_mm = self.res.building_width_m * scale
        margin = 1500.0

        # 1. Title Block Border
        self.writer.add_rectangle(-margin, -margin, l_mm + 2 * margin + 2500, w_mm + 2 * margin, layer="S-TITLEBLOCK")
        self.writer.add_text(
            f"LIFE SAFETY & EMERGENCY MEANS OF EGRESS PLAN - {self.res.building_name.upper()}",
            (0, w_mm + 1000),
            height=200,
            layer="E-TEXT",
        )
        self.writer.add_text(
            f"Standards: {self.res.code_used} / NFPA 101 | Total Occupancy: {self.res.total_building_occupants} Persons | Sprinklered: {'YES' if self.res.is_sprinklered else 'NO'}",
            (0, w_mm + 650),
            height=130,
            layer="E-TEXT",
        )
        self.writer.add_text(
            f"Exit Remoteness: {self.res.actual_exit_separation_m}m provided vs {self.res.min_exit_separation_required_m}m required ({'PASS' if self.res.separation_pass else 'FAIL'})",
            (0, w_mm + 350),
            height=110,
            layer="E-TEXT",
        )

        # 2. Building Outer Walls
        self.writer.add_rectangle(0, 0, l_mm, w_mm, layer="S-COLUMN")

        # 3. Exit 1 (Stair Enclosure A - Bottom Left)
        stair_w, stair_h = 3000.0, 5000.0
        self.writer.add_rectangle(0, 0, stair_w, stair_h, layer="S-COLUMN")
        self.writer.add_text("FIRE EXIT STAIR-A", (stair_w / 2, stair_h / 2), height=90, layer="S-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
        self.writer.add_text("2-HR RATED", (stair_w / 2, stair_h / 2 - 150), height=70, layer="S-REBAR-BOT", align=TextEntityAlignment.MIDDLE_CENTER)

        # Exit Door Symbol
        self.writer.add_rectangle(stair_w - 200, 1000, 200, 1200, layer="S-DIMS")
        self.writer.add_text("[EXIT-1]", (stair_w + 300, 1600), height=80, layer="S-DIMS")

        # 4. Exit 2 (Stair Enclosure B - Top Right)
        self.writer.add_rectangle(l_mm - stair_w, w_mm - stair_h, stair_w, stair_h, layer="S-COLUMN")
        self.writer.add_text("FIRE EXIT STAIR-B", (l_mm - stair_w / 2, w_mm - stair_h / 2), height=90, layer="S-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
        self.writer.add_text("2-HR RATED", (l_mm - stair_w / 2, w_mm - stair_h / 2 - 150), height=70, layer="S-REBAR-BOT", align=TextEntityAlignment.MIDDLE_CENTER)

        # Exit Door Symbol
        self.writer.add_rectangle(l_mm - stair_w, w_mm - 2200, 200, 1200, layer="S-DIMS")
        self.writer.add_text("[EXIT-2]", (l_mm - stair_w - 500, w_mm - 1600), height=80, layer="S-DIMS")

        # 5. Separation Distance Diagonal Line
        self.writer.add_line((stair_w, 1600), (l_mm - stair_w, w_mm - 1600), layer="S-DIMS")
        mid_x = (stair_w + l_mm - stair_w) / 2
        mid_y = (1600 + w_mm - 1600) / 2
        self.writer.add_text(
            f"Exit Separation = {self.res.actual_exit_separation_m}m (Min Required = {self.res.min_exit_separation_required_m}m)",
            (mid_x, mid_y + 200),
            height=90,
            layer="S-DIMS",
            align=TextEntityAlignment.MIDDLE_CENTER,
        )

        # 6. Egress Travel Paths with directional arrows
        self.writer.add_line((l_mm / 2, w_mm / 2), (stair_w + 500, 1600), layer="E-POWR-CIRC")
        self.writer.add_line((l_mm / 2, w_mm / 2), (l_mm - stair_w - 500, w_mm - 1600), layer="E-POWR-CIRC")
        self.writer.add_text("Primary Egress Path", (l_mm / 2 - 1000, w_mm / 2 - 400), height=80, layer="E-POWR-CIRC")

        # 7. Legend & Compliance Box
        leg_x = l_mm + 300
        leg_y = w_mm
        self.writer.add_rectangle(leg_x, leg_y - 4500, 2000, 4500, layer="S-TITLEBLOCK")
        self.writer.add_text("LIFE SAFETY EGRESS LEGEND", (leg_x + 100, leg_y - 250), height=110, layer="E-TEXT")

        notes = [
            f"Total Occupant Load: {self.res.total_building_occupants} Persons",
            f"Sprinkler Status: {'Fully Sprinklered' if self.res.is_sprinklered else 'Unsprinklered'}",
            f"Remoteness Rule: D_sep >= 1/3 D_diag ({'PASS' if self.res.separation_pass else 'FAIL'})",
            "Exit Enclosures: 2-Hour Fire-Resistance Rated",
            "Door Egress Width: Min 900mm Clear Opening",
            "Emergency Lighting: 90-Min Battery Backup",
            "Fire Alarm: Manual Pull Station < 1.5m to Exits",
        ]
        for idx, text in enumerate(notes):
            self.writer.add_text(text, (leg_x + 100, leg_y - 600 - (idx * 300)), height=75, layer="E-TEXT")

        return self.writer.save(filepath)
