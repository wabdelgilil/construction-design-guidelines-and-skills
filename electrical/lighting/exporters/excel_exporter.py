"""
Excel Schedule and Calculation Exporter for Lighting Systems.
Produces professional multi-tab workbooks with Luminaire Schedules, LPD Compliance, and Circuit Data.
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from electrical.lighting.scripts.lumen_engine import LightingDesignResult


class LightingExcelExporter:
    """Exports lighting design data to structured Excel spreadsheet."""

    def __init__(self, result: LightingDesignResult, code: str = "SBC"):
        self.res = result
        self.code = code
        self.writer = ExcelWriter("lighting_schedule.xlsx")

    def export(self, filepath: Path) -> Path:
        """Populates and formats the lighting design workbook."""
        wb = self.writer.wb
        ws = wb.active
        ws.title = "Lighting Schedule"

        self.writer.format_title_banner(
            title="INDOOR LIGHTING DESIGN & LPD SCHEDULE",
            subtitle=f"Project Standard: {self.code} / IESNA | Space: {self.res.room_name}",
            max_col=6,
        )

        headers = [
            "Item",
            "Parameter / Description",
            "Design Value",
            "Unit",
            "Code Requirement / Limit",
            "Compliance",
        ]

        allowed_lpd = 9.5 if self.code == "SBC" else 8.8
        lpd_status = "PASS" if self.res.lighting_power_density_w_per_m2 <= allowed_lpd else "EXCEEDS"

        rows = [
            [1, "Room Length", self.res.room_length_m, "m", "-", "OK"],
            [2, "Room Width", self.res.room_width_m, "m", "-", "OK"],
            [3, "Total Floor Area", self.res.room_area_m2, "m²", "-", "OK"],
            [4, "Target Illuminance", self.res.target_lux, "Lux", f"Min {self.res.target_lux}", "OK"],
            [5, "Achieved Average Illuminance", self.res.achieved_lux, "Lux", f"Min {self.res.target_lux}", self.res.compliance_status],
            [6, "Selected Luminaire Model", self.res.fixture_model, "-", "-", "OK"],
            [7, "Total Fixtures Installed", self.res.total_fixtures_count, "units", "-", "OK"],
            [8, "Array Layout (Cols x Rows)", f"{self.res.grid_columns} x {self.res.grid_rows}", "-", "-", "OPTIMAL"],
            [9, "Spacing Along Length (Sx)", self.res.spacing_x_m, "m", "-", "OK"],
            [10, "Spacing Along Width (Sy)", self.res.spacing_y_m, "m", "-", "OK"],
            [11, "Total Lighting Load", self.res.total_power_watts, "W", "-", "OK"],
            [12, "Lighting Power Density (LPD)", self.res.lighting_power_density_w_per_m2, "W/m²", f"Max {allowed_lpd}", lpd_status],
        ]

        self.writer.add_table_header(4, headers)
        for r_idx, row_vals in enumerate(rows, start=5):
            for c_idx, val in enumerate(row_vals, start=1):
                ws.cell(row=r_idx, column=c_idx, value=val)

        self.writer.auto_fit_columns()

        # Tab 2: Fixture Coordinate Table
        ws_coords = self.writer.create_sheet("Fixture Coordinates")
        self.writer.format_title_banner(
            title="LUMINAIRE CEILING GRID COORDINATES",
            subtitle=f"Room: {self.res.room_name} ({self.res.room_length_m}m x {self.res.room_width_m}m)",
            max_col=5,
        )
        coord_headers = ["Fixture ID", "X Position (m)", "Y Position (m)", "Mounting Type", "Circuit"]
        self.writer.add_table_header(4, coord_headers)

        for idx, (x, y) in enumerate(self.res.fixture_coordinates, 1):
            r_num = 4 + idx
            ws_coords.cell(row=r_num, column=1, value=f"LT-{idx:02d}")
            ws_coords.cell(row=r_num, column=2, value=x)
            ws_coords.cell(row=r_num, column=3, value=y)
            ws_coords.cell(row=r_num, column=4, value="Recessed Ceiling Grid")
            ws_coords.cell(row=r_num, column=5, value="CKT-L01")

        self.writer.auto_fit_columns()

        return self.writer.save(filepath)
