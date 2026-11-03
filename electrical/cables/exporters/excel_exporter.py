"""
Excel Exporter for Cable Sizing Schedules and Cable Tray Containment Sizing.
"""

from pathlib import Path
from typing import Dict, List
from core.exporters.excel_writer import ExcelWriter
from electrical.cables.scripts.cable_engine import CableSizingResult, CableTraySizingResult


class CableExcelExporter:
    """Exports cable schedules and cable tray calculation workbooks to Excel."""

    def __init__(
        self,
        project_name: str,
        feeders_results: List[Dict],
        tray_result: CableTraySizingResult,
        standard: str = "IEC 60364-5-52 / SBC 401",
    ):
        self.project_name = project_name
        self.feeders = feeders_results
        self.tray = tray_result
        self.standard = standard
        self.writer = ExcelWriter("cable_schedule.xlsx")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "Cable Schedule"

        self.writer.format_title_banner(
            title=f"LOW VOLTAGE FEEDER CABLE SCHEDULE - {self.project_name.upper()}",
            subtitle=f"Code: {self.standard} | Total Sized Feeders: {len(self.feeders)} | 400V/230V 60Hz",
            max_col=9,
        )

        headers = [
            "Feeder Tag",
            "Description / Load",
            "Power (kW)",
            "Ib (A)",
            "Breaker In",
            "Cable Size (Cu/XLPE)",
            "Length (m)",
            "Voltage Drop %",
            "Status",
        ]
        self.writer.add_table_header(4, headers)

        for idx, item in enumerate(self.feeders, start=5):
            res: CableSizingResult = item["result"]
            ws.cell(row=idx, column=1, value=item["tag"])
            ws.cell(row=idx, column=2, value=item["description"])
            ws.cell(row=idx, column=3, value=res.load_kw)
            ws.cell(row=idx, column=4, value=res.design_current_ib)
            ws.cell(row=idx, column=5, value=f"{res.breaker_rating_in}A")
            ws.cell(row=idx, column=6, value=f"{res.cable_size_sqmm} mm²")
            ws.cell(row=idx, column=7, value=res.circuit_length_m)
            ws.cell(row=idx, column=8, value=f"{res.voltage_drop_pct:.2f}%")
            ws.cell(row=idx, column=9, value=res.compliance_status)

        self.writer.auto_fit_columns()

        # Tab 2: Cable Tray Sizing & Fill Ratio
        ws_tray = self.writer.create_sheet("Cable Tray Sizing")
        self.writer.format_title_banner(
            title=f"CABLE TRAY SIZING & FILL RATIO - {self.tray.tray_tag}",
            subtitle=f"Specified Tray: {self.tray.selected_tray_width_mm}x{self.tray.selected_tray_depth_mm}mm | Achieved Fill: {self.tray.achieved_fill_ratio_pct}% (Max 40%)",
            max_col=5,
        )

        headers2 = ["Item", "Containment Parameter", "Value", "Unit", "Code Compliance"]
        self.writer.add_table_header(4, headers2)

        data2 = [
            [1, "Supported Feeders Count", self.tray.cables_count, "Cables", "OK"],
            [2, "Total Cables Cross-Sectional Area", self.tray.total_cables_cross_section_mm2, "mm²", "Sum of pi*D²/4"],
            [3, "Maximum Allowed Fill Ratio", f"{self.tray.max_fill_ratio_allowed_pct}%", "%", "NEC 392 / SBC 401"],
            [4, "Minimum Required Tray Cross-Section", self.tray.min_required_tray_area_mm2, "mm²", "Area / 0.40"],
            [5, "Selected Perforated Tray Width", self.tray.selected_tray_width_mm, "mm", "Standard size"],
            [6, "Selected Perforated Tray Depth", self.tray.selected_tray_depth_mm, "mm", "Standard size"],
            [7, "Actual Tray Cross-Sectional Area", self.tray.actual_tray_area_mm2, "mm²", "Width * Depth"],
            [8, "Achieved Cable Fill Ratio", f"{self.tray.achieved_fill_ratio_pct}%", "%", self.tray.status],
        ]

        for r_idx, row_vals in enumerate(data2, start=5):
            for c_idx, val in enumerate(row_vals, start=1):
                ws_tray.cell(row=r_idx, column=c_idx, value=val)

        self.writer.auto_fit_columns()

        return self.writer.save(filepath)
