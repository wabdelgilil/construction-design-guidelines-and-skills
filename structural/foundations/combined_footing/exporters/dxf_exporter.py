"""
AutoCAD DXF Exporter for Combined Footing.
Draws professional structural Plan and Longitudinal Section with top and bottom rebar meshes.
"""

from pathlib import Path
from core.exporters.dxf_writer import DXFWriter
from structural.foundations.combined_footing.scripts.design_engine import (
    CombinedFootingDesignResult,
    CombinedFootingInput,
)


class CombinedFootingDXFExporter:
    """Generates 2D AutoCAD drawing for rectangular combined footing."""

    def __init__(self, result: CombinedFootingDesignResult, inp: CombinedFootingInput):
        self.res = result
        self.inp = inp

    def export(self, filepath: Path) -> Path:
        writer = DXFWriter(str(filepath))

        l_mm = self.res.length_m * 1000.0
        b_mm = self.res.width_m * 1000.0
        t_mm = self.res.thickness_mm
        d1_mm = self.inp.col1_edge_distance_m * 1000.0
        span_mm = self.inp.span_center_to_center_m * 1000.0

        # --- 1. PLAN VIEW ---
        # Origin (0,0) at left-bottom of footing
        # Blinding concrete outline (offset 100mm)
        writer.add_rectangle(-100.0, -100.0, l_mm + 200.0, b_mm + 200.0, layer="S-CONC-BLINDING")

        # RC Combined Footing Outline
        writer.add_rectangle(0, 0, l_mm, b_mm, layer="S-CONC-RC")

        # Column 1 Outline
        c1_x0 = d1_mm - (self.inp.col1_length_mm / 2.0)
        c1_y0 = (b_mm / 2.0) - (self.inp.col1_width_mm / 2.0)
        writer.add_rectangle(c1_x0, c1_y0, self.inp.col1_length_mm, self.inp.col1_width_mm, layer="S-COLUMN")

        # Column 2 Outline
        c2_x0 = d1_mm + span_mm - (self.inp.col2_length_mm / 2.0)
        c2_y0 = (b_mm / 2.0) - (self.inp.col2_width_mm / 2.0)
        writer.add_rectangle(c2_x0, c2_y0, self.inp.col2_length_mm, self.inp.col2_width_mm, layer="S-COLUMN")

        # Text Callouts
        writer.add_text("COMBINED FOOTING PLAN VIEW", (l_mm / 2.0 - 500, b_mm + 200.0), height=60.0, layer="S-TEXT")
        dim_label = f"{self.res.length_m:.2f} m x {self.res.width_m:.2f} m x {int(t_mm)} mm"
        writer.add_text(dim_label, (l_mm / 2.0 - 400, -150.0), height=45.0, layer="S-TEXT")
        writer.add_text(f"Top Steel: {self.res.top_longitudinal_rebar_desc}", (100.0, b_mm + 80.0), height=35.0, layer="S-TEXT")

        # --- 2. LONGITUDINAL SECTION VIEW ---
        sec_y0 = -b_mm - 1000.0

        # Blinding
        writer.add_rectangle(-100.0, sec_y0 - 100.0, l_mm + 200.0, 100.0, layer="S-CONC-BLINDING")
        # RC Footing
        writer.add_rectangle(0, sec_y0, l_mm, t_mm, layer="S-CONC-RC")

        # Columns rising up
        writer.add_rectangle(c1_x0, sec_y0 + t_mm, self.inp.col1_length_mm, 800.0, layer="S-COLUMN")
        writer.add_rectangle(c2_x0, sec_y0 + t_mm, self.inp.col2_length_mm, 800.0, layer="S-COLUMN")

        # Top Longitudinal Continuous Rebar with end 90-degree hooks
        top_bar_y = sec_y0 + t_mm - 75.0
        hook_depth = t_mm - 150.0
        writer.add_rebar_with_90deg_hooks(75.0, top_bar_y, l_mm - 75.0, hook_height=-hook_depth, layer="S-REBAR-BOT")

        # Bottom Longitudinal Rebar with upward 90-degree hooks
        bot_bar_y = sec_y0 + 75.0
        writer.add_rebar_with_90deg_hooks(75.0, bot_bar_y, l_mm - 75.0, hook_height=hook_depth, layer="S-REBAR-BOT")

        writer.add_text("LONGITUDINAL SECTION (TOP & BOTTOM STEEL MESHES)", (100.0, sec_y0 - 250.0), height=50.0, layer="S-TEXT")

        return writer.save(filepath)
