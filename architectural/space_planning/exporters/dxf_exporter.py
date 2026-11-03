"""
AutoCAD DXF Exporter for Architectural Space Planning & Room Matrix.
Generates floor layouts, space tags, boundary polylines, and area annotations.
"""

from pathlib import Path
from ezdxf.enums import TextEntityAlignment
from core.exporters.dxf_writer import DXFWriter
from architectural.space_planning.scripts.design_engine import ProjectSpaceAuditResult


class SpacePlanningDXFExporter:
    """Exports architectural space planning plans to AutoCAD .dxf format."""

    def __init__(self, result: ProjectSpaceAuditResult):
        self.res = result
        self.writer = DXFWriter("architectural_spaces.dxf")

    def export(self, filepath: Path) -> Path:
        scale = 1000.0  # mm
        # Draw title block border
        self.writer.add_rectangle(0, 0, 16000, 12000, layer="S-TITLEBLOCK")

        # Title text
        self.writer.add_text(
            f"ARCHITECTURAL SPACE PLANNING & AREA COMPLIANCE - {self.res.project_name.upper()}",
            (500, 11200),
            height=250,
            layer="E-TEXT",
        )
        self.writer.add_text(
            f"Code: {self.res.code_used} | Typology: {self.res.building_typology.upper()} | Gross Area: {self.res.total_gross_area_m2} m2",
            (500, 10700),
            height=180,
            layer="E-TEXT",
        )

        # Draw rooms in a clean grid layout
        cur_x = 800.0
        cur_y = 1000.0
        row_max_h = 0.0

        for idx, rm in enumerate(self.res.rooms_audited):
            w_mm = rm.width_m * scale
            l_mm = rm.length_m * scale

            # If room extends past boundary, move to next row
            if cur_x + l_mm > 14500:
                cur_x = 800.0
                cur_y += row_max_h + 1000.0
                row_max_h = 0.0

            # Draw room perimeter
            self.writer.add_rectangle(cur_x, cur_y, l_mm, w_mm, layer="S-COLUMN")

            # Room center text
            cx = cur_x + l_mm / 2.0
            cy = cur_y + w_mm / 2.0
            self.writer.add_text(rm.tag, (cx, cy + 300), height=140, layer="S-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
            self.writer.add_text(rm.name, (cx, cy), height=110, layer="S-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
            self.writer.add_text(f"{rm.area_m2:.1f} m2 (H={rm.height_m:.2f}m)", (cx, cy - 300), height=90, layer="S-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
            self.writer.add_text(rm.overall_status, (cx, cy - 550), height=90, layer="S-DIMS", align=TextEntityAlignment.MIDDLE_CENTER)

            row_max_h = max(row_max_h, w_mm)
            cur_x += l_mm + 800.0

        return self.writer.save(filepath)
