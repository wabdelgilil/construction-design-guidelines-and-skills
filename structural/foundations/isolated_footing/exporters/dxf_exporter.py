"""
AutoCAD DXF Exporter for Isolated Footing.
Draws professional structural Plan and Cross-Section with reinforcement detailing and dimensions.
"""

from pathlib import Path
from typing import Optional
from core.exporters.dxf_writer import DXFWriter
from structural.foundations.isolated_footing.scripts.design_engine import FootingDesignResult


class IsolatedFootingDXFExporter:
    """Generates 2D AutoCAD drawing for isolated footing."""

    def __init__(self, result: FootingDesignResult, column_length_mm: float, column_width_mm: float):
        self.res = result
        self.col_l = column_length_mm
        self.col_w = column_width_mm

    def export(self, filepath: Path) -> Path:
        writer = DXFWriter(str(filepath))

        # Dimensions in millimeters
        l_rc = self.res.length_mm
        b_rc = self.res.width_mm
        t_rc = self.res.thickness_mm
        cover = 75.0
        blinding_offset = 100.0
        blinding_thick = 100.0

        # --- 1. PLAN VIEW (Centered around origin 0,0) ---
        x0_rc = -l_rc / 2.0
        y0_rc = -b_rc / 2.0

        # A. Plain Concrete Blinding Outline
        x0_pc = x0_rc - blinding_offset
        y0_pc = y0_rc - blinding_offset
        w_pc = l_rc + 2 * blinding_offset
        h_pc = b_rc + 2 * blinding_offset
        writer.add_rectangle(x0_pc, y0_pc, w_pc, h_pc, layer="S-CONC-BLINDING")

        # B. Reinforced Concrete Footing Outline
        writer.add_rectangle(x0_rc, y0_rc, l_rc, b_rc, layer="S-CONC-RC")

        # C. Column Outline
        x0_col = -self.col_l / 2.0
        y0_col = -self.col_w / 2.0
        writer.add_rectangle(x0_col, y0_col, self.col_l, self.col_w, layer="S-COLUMN")

        # D. Reinforcement Representation (Longitudinal & Transverse Rebar Grid)
        hook_len = t_rc - 2 * cover
        rebar_x_start = x0_rc + cover
        rebar_x_end = x0_rc + l_rc - cover

        # Bottom Rebar (Long direction) - draw sample indicative bars
        writer.add_line((rebar_x_start, y0_rc + cover), (rebar_x_end, y0_rc + cover), layer="S-REBAR-BOT")
        writer.add_line((rebar_x_start, 0), (rebar_x_end, 0), layer="S-REBAR-BOT")
        writer.add_line((rebar_x_start, -y0_rc - cover), (rebar_x_end, -y0_rc - cover), layer="S-REBAR-BOT")

        # Bottom Rebar (Short direction)
        rebar_y_start = y0_rc + cover
        rebar_y_end = y0_rc + b_rc - cover
        writer.add_line((x0_rc + cover, rebar_y_start), (x0_rc + cover, rebar_y_end), layer="S-REBAR-BOT")
        writer.add_line((0, rebar_y_start), (0, rebar_y_end), layer="S-REBAR-BOT")
        writer.add_line((-x0_rc - cover, rebar_y_start), (-x0_rc - cover, rebar_y_end), layer="S-REBAR-BOT")

        # E. Text Annotations for Plan
        writer.add_text("FOOTING PLAN VIEW", (-l_rc / 2.0, y0_pc - 150.0), height=50.0, layer="S-TEXT")
        rebar_l_tag = f"B.1: {self.res.bars_l_count} T{self.res.bar_dia_l_mm} ({self.res.bars_per_meter_l})"
        rebar_b_tag = f"B.2: {self.res.bars_b_count} T{self.res.bar_dia_b_mm} ({self.res.bars_per_meter_b})"
        writer.add_text(rebar_l_tag, (-l_rc / 2.0, -b_rc / 2.0 - 50.0), height=35.0, layer="S-TEXT")
        writer.add_text(rebar_b_tag, (-l_rc / 2.0, -b_rc / 2.0 - 100.0), height=35.0, layer="S-TEXT")

        # --- 2. CROSS-SECTION VIEW (Drawn to the right of Plan View) ---
        section_offset_x = (l_rc / 2.0) + w_pc + 800.0
        sec_y0 = y0_pc

        # A. Blinding Concrete Section
        sec_x0_pc = section_offset_x
        writer.add_rectangle(sec_x0_pc, sec_y0, w_pc, blinding_thick, layer="S-CONC-BLINDING")

        # B. RC Footing Section
        sec_x0_rc = sec_x0_pc + blinding_offset
        sec_y0_rc = sec_y0 + blinding_thick
        writer.add_rectangle(sec_x0_rc, sec_y0_rc, l_rc, t_rc, layer="S-CONC-RC")

        # C. Column Stem rising from Footing
        col_sec_x0 = sec_x0_rc + (l_rc - self.col_l) / 2.0
        col_sec_y0 = sec_y0_rc + t_rc
        col_height_drawn = 800.0
        writer.add_rectangle(col_sec_x0, col_sec_y0, self.col_l, col_height_drawn, layer="S-COLUMN")

        # D. Bottom Reinforcement in Section with 90-degree end hooks
        bar_y_elev = sec_y0_rc + cover
        writer.add_rebar_with_90deg_hooks(
            sec_x0_rc + cover,
            bar_y_elev,
            sec_x0_rc + l_rc - cover,
            hook_height=hook_len,
            layer="S-REBAR-BOT",
        )

        # E. Column Starter Bars (Dowels)
        dowel_foot_len = 300.0
        dowel_lap_len = 600.0
        # Left dowel
        writer.add_line(
            (col_sec_x0 + 40.0, bar_y_elev + 25.0),
            (col_sec_x0 - dowel_foot_len, bar_y_elev + 25.0),
            layer="S-REBAR-DOWEL",
        )
        writer.add_line(
            (col_sec_x0 + 40.0, bar_y_elev + 25.0),
            (col_sec_x0 + 40.0, col_sec_y0 + dowel_lap_len),
            layer="S-REBAR-DOWEL",
        )

        # Right dowel
        writer.add_line(
            (col_sec_x0 + self.col_l - 40.0, bar_y_elev + 25.0),
            (col_sec_x0 + self.col_l + dowel_foot_len, bar_y_elev + 25.0),
            layer="S-REBAR-DOWEL",
        )
        writer.add_line(
            (col_sec_x0 + self.col_l - 40.0, bar_y_elev + 25.0),
            (col_sec_x0 + self.col_l - 40.0, col_sec_y0 + dowel_lap_len),
            layer="S-REBAR-DOWEL",
        )

        # F. Text Annotations for Section
        writer.add_text("SECTION 1-1 (LONG DIRECTION)", (sec_x0_pc, sec_y0 - 150.0), height=50.0, layer="S-TEXT")
        dim_tag = f"T = {int(t_rc)} mm | Plain Conc = {int(blinding_thick)} mm"
        writer.add_text(dim_tag, (sec_x0_pc, sec_y0 - 80.0), height=35.0, layer="S-TEXT")

        return writer.save(filepath)
