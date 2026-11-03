"""
AutoCAD DXF Exporter for Reinforced Concrete Column.
Draws professional structural cross-section detailing with longitudinal rebar and ties.
"""

from pathlib import Path
from core.exporters.dxf_writer import DXFWriter
from structural.vertical_elements.columns.scripts.design_engine import ColumnDesignResult, ColumnInput


class ColumnDXFExporter:
    """Generates 2D AutoCAD drawing for column cross-section."""

    def __init__(self, result: ColumnDesignResult, inp: ColumnInput):
        self.res = result
        self.inp = inp

    def export(self, filepath: Path) -> Path:
        writer = DXFWriter(str(filepath))

        b = self.res.width_mm
        h = self.res.length_mm
        cover = self.inp.concrete_cover_mm

        # 1. Outer Concrete Cross-Section (Origin at 0,0)
        writer.add_rectangle(0, 0, h, b, layer="S-COLUMN")

        # 2. Closed Lateral Tie Perimeter
        tie_x0 = cover
        tie_y0 = cover
        tie_w = h - 2 * cover
        tie_h = b - 2 * cover
        writer.add_rectangle(tie_x0, tie_y0, tie_w, tie_h, layer="S-REBAR-BOT")

        # 3. Longitudinal Bars
        # Minimum 4 corner bars
        bar_radius = self.res.bar_dia_mm / 2.0
        n_total = self.res.total_bar_count

        # Corner coordinates
        corners = [
            (tie_x0 + bar_radius, tie_y0 + bar_radius),
            (tie_x0 + tie_w - bar_radius, tie_y0 + bar_radius),
            (tie_x0 + tie_w - bar_radius, tie_y0 + tie_h - bar_radius),
            (tie_x0 + bar_radius, tie_y0 + tie_h - bar_radius),
        ]
        for cx, cy in corners:
            writer.msp.add_circle((cx, cy), radius=bar_radius, dxfattribs={"layer": "S-REBAR-BOT"})

        # Intermediate bars along length h (distributed on top and bottom faces)
        n_intermediate = n_total - 4
        if n_intermediate > 0:
            n_per_side = n_intermediate // 2
            spacing = (tie_w - 2 * bar_radius) / (n_per_side + 1)
            for i in range(1, n_per_side + 1):
                x_pos = tie_x0 + bar_radius + (i * spacing)
                # Bottom face
                writer.msp.add_circle((x_pos, tie_y0 + bar_radius), radius=bar_radius, dxfattribs={"layer": "S-REBAR-BOT"})
                # Top face
                writer.msp.add_circle((x_pos, tie_y0 + tie_h - bar_radius), radius=bar_radius, dxfattribs={"layer": "S-REBAR-BOT"})

        # 4. Text Annotations & Dimensions
        writer.add_text("COLUMN CROSS-SECTION DETAIL", (0, b + 150.0), height=40.0, layer="S-TEXT")
        tag_1 = f"Section: {int(b)} x {int(h)} mm ({self.res.classification})"
        tag_2 = f"Bars: {self.res.longitudinal_rebar_desc}"
        tag_3 = f"Ties: {self.res.tie_desc}"
        writer.add_text(tag_1, (0, -80.0), height=30.0, layer="S-TEXT")
        writer.add_text(tag_2, (0, -130.0), height=30.0, layer="S-TEXT")
        writer.add_text(tag_3, (0, -180.0), height=30.0, layer="S-TEXT")

        return writer.save(filepath)
