"""
AutoCAD DXF Exporter for Strap (Cantilever) Footing.
Draws professional structural Plan and Elevation showing boundary property line,
strap beam, footings, and top tensile reinforcement.
"""

from pathlib import Path
from core.exporters.dxf_writer import DXFWriter
from structural.foundations.strap_footing.scripts.design_engine import (
    StrapFootingDesignResult,
    StrapFootingInput,
)


class StrapFootingDXFExporter:
    """Generates 2D AutoCAD drawing for strap footing system."""

    def __init__(self, result: StrapFootingDesignResult, inp: StrapFootingInput):
        self.res = result
        self.inp = inp

    def export(self, filepath: Path) -> Path:
        writer = DXFWriter(str(filepath))

        span_mm = self.inp.span_center_to_center_m * 1000.0
        f1_l_mm = self.res.f1_length_m * 1000.0
        f1_w_mm = self.res.f1_width_m * 1000.0
        f2_l_mm = self.res.f2_length_m * 1000.0
        f2_w_mm = self.res.f2_width_m * 1000.0
        strap_b = self.res.strap_width_mm
        strap_h = self.res.strap_depth_mm

        # --- 1. PLAN VIEW ---
        # Origin (0,0) is at the Property Line / outer face of Column 1
        y0_center = 0.0

        # Property Line (Drawn as long red centerline/dashed line)
        writer.add_line((0, -f1_w_mm), (0, f1_w_mm), layer="S-DIMS")
        writer.add_text("PROPERTY LINE / BOUNDARY", (-50, 0), height=50.0, layer="S-TEXT")

        # Footing 1 (Exterior): starts at x=0, goes to x=f1_l_mm
        f1_y0 = -f1_w_mm / 2.0
        writer.add_rectangle(0, f1_y0, f1_l_mm, f1_w_mm, layer="S-CONC-RC")

        # Column 1 (Flush with property line at x=0)
        col1_l = self.inp.col1_length_mm
        col1_w = self.inp.col1_width_mm
        writer.add_rectangle(0, -col1_w / 2.0, col1_l, col1_w, layer="S-COLUMN")

        # Column 2 (Interior): center at x=span_mm
        col2_l = self.inp.col2_length_mm
        col2_w = self.inp.col2_width_mm
        col2_x0 = span_mm - (col2_l / 2.0)
        writer.add_rectangle(col2_x0, -col2_w / 2.0, col2_l, col2_w, layer="S-COLUMN")

        # Footing 2 (Interior): center at x=span_mm
        f2_x0 = span_mm - (f2_l_mm / 2.0)
        f2_y0 = -f2_w_mm / 2.0
        writer.add_rectangle(f2_x0, f2_y0, f2_l_mm, f2_w_mm, layer="S-CONC-RC")

        # Strap Beam: connecting Column 1 to Column 2
        strap_x0 = col1_l
        strap_len = (col2_x0 + col2_l) - strap_x0
        writer.add_rectangle(0, -strap_b / 2.0, span_mm + (col2_l / 2.0), strap_b, layer="S-CONC-RC")

        # Text Labels
        writer.add_text("STRAP FOOTING PLAN VIEW", (span_mm / 2.0 - 500, f1_w_mm / 2.0 + 300), height=60.0, layer="S-TEXT")
        writer.add_text(f"FOOTING 1: {self.res.f1_length_m:.2f} x {self.res.f1_width_m:.2f} m", (0, -f1_w_mm / 2.0 - 150), height=40.0, layer="S-TEXT")
        writer.add_text(f"FOOTING 2: {self.res.f2_length_m:.2f} x {self.res.f2_width_m:.2f} m", (f2_x0, -f2_w_mm / 2.0 - 150), height=40.0, layer="S-TEXT")
        writer.add_text(f"STRAP BEAM: {int(strap_b)} x {int(strap_h)} mm", (span_mm / 2.0 - 300, strap_b / 2.0 + 100), height=40.0, layer="S-TEXT")

        # --- 2. LONGITUDINAL SECTION VIEW (Below Plan View) ---
        sec_y0 = -f1_w_mm - 1200.0

        # Footing 1 Section
        f1_t = self.res.f1_thickness_mm
        writer.add_rectangle(0, sec_y0, f1_l_mm, f1_t, layer="S-CONC-RC")

        # Footing 2 Section
        f2_t = self.res.f2_thickness_mm
        writer.add_rectangle(f2_x0, sec_y0, f2_l_mm, f2_t, layer="S-CONC-RC")

        # Strap Beam Section (Rising higher than footings)
        writer.add_rectangle(0, sec_y0, span_mm + col2_l / 2.0, strap_h, layer="S-CONC-RC")

        # Columns rising up
        writer.add_rectangle(0, sec_y0 + strap_h, col1_l, 800.0, layer="S-COLUMN")
        writer.add_rectangle(col2_x0, sec_y0 + strap_h, col2_l, 800.0, layer="S-COLUMN")

        # Top Tensile Reinforcement in Strap Beam (Heavy top layer with 90-deg downward hooks)
        top_bar_y = sec_y0 + strap_h - 50.0
        writer.add_line((25.0, top_bar_y), (span_mm + col2_l / 2.0 - 25.0, top_bar_y), layer="S-REBAR-BOT")
        # Hooks downward
        writer.add_line((25.0, top_bar_y), (25.0, top_bar_y - (strap_h - 150.0)), layer="S-REBAR-BOT")
        writer.add_line((span_mm + col2_l / 2.0 - 25.0, top_bar_y), (span_mm + col2_l / 2.0 - 25.0, top_bar_y - (strap_h - 150.0)), layer="S-REBAR-BOT")

        # Text Annotations
        writer.add_text("LONGITUDINAL ELEVATION & STRAP BEAM DETAILING", (0, sec_y0 - 200.0), height=50.0, layer="S-TEXT")
        writer.add_text(f"Top Tension Steel: {self.res.strap_top_rebar_desc}", (span_mm / 4.0, top_bar_y + 80.0), height=35.0, layer="S-TEXT")

        return writer.save(filepath)
