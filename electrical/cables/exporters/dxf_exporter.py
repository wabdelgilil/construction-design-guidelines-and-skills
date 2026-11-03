"""
AutoCAD DXF Exporter for Cable Tray Cross-Section and Containment Layout.
Generates scaled tray sections, cable bundle layouts, fill ratio indicators, and schedule tables.
"""

from pathlib import Path
from typing import Dict, List
from ezdxf.enums import TextEntityAlignment
from core.exporters.dxf_writer import DXFWriter
from electrical.cables.scripts.cable_engine import CableTraySizingResult


class CableDXFExporter:
    """Exports cable tray section and cable layout to AutoCAD .dxf format."""

    def __init__(
        self,
        project_name: str,
        feeders_data: List[Dict],
        tray_result: CableTraySizingResult,
        standard: str = "IEC 60364-5-52 / SBC 401",
    ):
        self.project_name = project_name
        self.feeders = feeders_data
        self.tray = tray_result
        self.standard = standard
        self.writer = DXFWriter("cable_tray_section.dxf")

    def export(self, filepath: Path) -> Path:
        # Sheet Border
        self.writer.add_rectangle(0, 0, 1500, 1000, layer="S-TITLEBLOCK")

        # Title Block
        self.writer.add_text("CABLE SIZING & CABLE TRAY CONTAINMENT DETAIL", (40, 940), height=22, layer="E-TEXT")
        self.writer.add_text(f"Project: {self.project_name} | Standards: {self.standard}", (40, 910), height=14, layer="E-TEXT")
        self.writer.add_text(
            f"Cable Tray: {self.tray.tray_tag} ({self.tray.selected_tray_width_mm}x{self.tray.selected_tray_depth_mm}mm) | Fill Ratio: {self.tray.achieved_fill_ratio_pct}% (Max {self.tray.max_fill_ratio_allowed_pct}%)",
            (40, 885),
            height=14,
            layer="E-TEXT",
        )

        # 1. Draw Scaled Cable Tray Cross-Section
        # Center in left side: (x=100 to 500, y=500)
        tw = self.tray.selected_tray_width_mm
        td = self.tray.selected_tray_depth_mm

        tray_scale = 0.8
        tw_scaled = tw * tray_scale
        td_scaled = td * tray_scale

        origin_x = 100.0
        origin_y = 550.0

        # Draw U-shaped tray profile (thick polyline)
        points = [
            (origin_x, origin_y + td_scaled),
            (origin_x, origin_y),
            (origin_x + tw_scaled, origin_y),
            (origin_x + tw_scaled, origin_y + td_scaled),
        ]
        self.writer.msp.add_lwpolyline(points, dxfattribs={"layer": "E-POWR-PANL"})

        # Tray Dimensions
        self.writer.add_text(f"TRAY WIDTH = {tw} mm", (origin_x + tw_scaled / 2, origin_y - 30), height=12, layer="S-DIMS", align=TextEntityAlignment.TOP_CENTER)
        self.writer.add_text(f"{td} mm", (origin_x - 30, origin_y + td_scaled / 2), height=10, layer="S-DIMS", align=TextEntityAlignment.MIDDLE_RIGHT)

        # 2. Draw Cables nested inside tray
        cur_cx = origin_x + 20.0
        cur_cy = origin_y + 20.0

        for f_idx, f_item in enumerate(self.feeders):
            res = f_item["result"]
            od = res.approx_outer_diameter_mm
            od_scaled = od * tray_scale
            r_scaled = od_scaled / 2.0

            # If cable extends past tray width, create second layer
            if cur_cx + r_scaled > origin_x + tw_scaled - 10:
                cur_cx = origin_x + 20.0
                cur_cy += 30.0

            self.writer.msp.add_circle((cur_cx + r_scaled, cur_cy + r_scaled), radius=r_scaled, dxfattribs={"layer": "E-POWR-CABL" if "E-POWR-CABL" in self.writer.doc.layers else "E-POWR-SCKT"})
            self.writer.add_text(f"F{f_idx+1}", (cur_cx + r_scaled, cur_cy + r_scaled), height=6, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
            cur_cx += od_scaled + 8.0

        # Tray Fill Callout Box
        fill_box_x = origin_x
        fill_box_y = origin_y - 80
        self.writer.add_rectangle(fill_box_x, fill_box_y - 70, tw_scaled, 70, layer="S-TITLEBLOCK")
        self.writer.add_text(f"CONTAINMENT STATUS: {self.tray.status}", (fill_box_x + 15, fill_box_y - 25), height=11, layer="E-TEXT")
        self.writer.add_text(f"Cables Area: {self.tray.total_cables_cross_section_mm2} mm2 | Achieved Fill: {self.tray.achieved_fill_ratio_pct}%", (fill_box_x + 15, fill_box_y - 50), height=9, layer="E-TEXT")

        # 3. Feeder Schedule Table (Right Side)
        table_x = origin_x + tw_scaled + 80
        table_y = 800.0

        self.writer.add_rectangle(table_x, table_y - 450, 750, 450, layer="S-TITLEBLOCK")
        self.writer.add_text("FEEDER CABLE SIZING SCHEDULE", (table_x + 20, table_y - 30), height=14, layer="E-TEXT")

        sched_headers = "Tag   Description           kW      Ib(A)   Breaker   Cable Size   VD(%)   Status"
        self.writer.add_text(sched_headers, (table_x + 20, table_y - 70), height=9, layer="E-POWR-PANL")
        self.writer.add_line((table_x + 10, table_y - 85), (table_x + 730, table_y - 85), layer="S-DIMS")

        for s_idx, f_item in enumerate(self.feeders):
            res = f_item["result"]
            line_y = table_y - 110 - (s_idx * 35)
            row_text = f"{f_item['tag']:<5} {f_item['description']:<20} {res.load_kw:<6.1f} {res.design_current_ib:<7.1f} {res.breaker_rating_in:<7}A {res.cable_size_sqmm:<4.0f}mm2 Cu   {res.voltage_drop_pct:<5.2f}%  {res.compliance_status}"
            self.writer.add_text(row_text, (table_x + 20, line_y), height=8, layer="E-TEXT")

        # 4. Mandatory Installation Notes
        notes_x = 100.0
        notes_y = 300.0
        self.writer.add_rectangle(notes_x, notes_y - 200, 1300, 200, layer="S-TITLEBLOCK")
        self.writer.add_text("CABLE INSTALLATION & CONTAINMENT CRITERIA", (notes_x + 20, notes_y - 30), height=13, layer="E-TEXT")

        rules = [
            "1. Conductor Material: Multi-core plain annealed copper conductors, Class 2 stranded, XLPE insulated, PVC or LSZH sheathed.",
            "2. Derating Factors: Ambient temperature derating (Ca = 0.96 @ 45°C) and grouping factor (Cg = 0.77 for 4 grouped feeders in tray).",
            "3. Voltage Drop: Sub-main feeders limited to max 2.0% (source to distribution board) and total load voltage drop <= 5.0%.",
            "4. Tray Fill: Maximum allowable cable tray cross-sectional fill ratio <= 40% (leaving 60% free space for heat dissipation & future additions).",
            "5. Fire Separation: Cable trays passing through fire-rated walls must be sealed with 2-hour fire-stop transit systems.",
        ]
        for r_idx, r_text in enumerate(rules):
            self.writer.add_text(r_text, (notes_x + 20, notes_y - 65 - (r_idx * 28)), height=8, layer="E-TEXT")

        return self.writer.save(filepath)
