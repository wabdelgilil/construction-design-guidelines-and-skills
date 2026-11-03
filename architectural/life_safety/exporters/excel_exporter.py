"""
Excel Exporter for Life Safety, Occupant Load, and Means of Egress Schedule.
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from architectural.life_safety.scripts.design_engine import LifeSafetyProjectResult


class LifeSafetyExcelExporter:
    """Exports life safety egress schedule to Excel."""

    def __init__(self, result: LifeSafetyProjectResult):
        self.res = result
        self.writer = ExcelWriter("life_safety_schedule.xlsx")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "Egress Schedule"

        self.writer.format_title_banner(
            title=f"LIFE SAFETY & MEANS OF EGRESS SCHEDULE - {self.res.building_name.upper()}",
            subtitle=f"Code: {self.res.code_used} / NFPA 101 | Total Occupant Load: {self.res.total_building_occupants} Persons | Sprinklered: {'YES' if self.res.is_sprinklered else 'NO'}",
            max_col=8,
        )

        headers = [
            "Zone Name",
            "Area (m²)",
            "Occupant Load",
            "Min Exits",
            "Travel Dist (m)",
            "Door Req / Prov (mm)",
            "Stair Req / Prov (mm)",
            "Status",
        ]
        self.writer.add_table_header(4, headers)

        for idx, z in enumerate(self.res.zones, start=5):
            door_str = f"{z.door_capacity_width_required_mm:.0f} / {z.door_clear_width_provided_mm:.0f}"
            stair_str = f"{z.stair_width_required_mm:.0f} / {z.stair_width_provided_mm:.0f}"
            ws.cell(row=idx, column=1, value=z.zone_name)
            ws.cell(row=idx, column=2, value=z.area_m2)
            ws.cell(row=idx, column=3, value=z.calculated_occupants)
            ws.cell(row=idx, column=4, value=z.min_exits_required)
            ws.cell(row=idx, column=5, value=f"{z.longest_travel_distance_m:.1f} m")
            ws.cell(row=idx, column=6, value=door_str)
            ws.cell(row=idx, column=7, value=stair_str)
            ws.cell(row=idx, column=8, value=z.overall_status)

        self.writer.auto_fit_columns()

        # Tab 2: Remoteness & MEP Fire Safety
        ws_mep = self.writer.create_sheet("Remoteness & MEP Fire Safety")
        self.writer.format_title_banner(
            title="EXIT REMOTENESS & MEP FIRE PROTECTION DIRECTIVES",
            subtitle="Diagonal Rule Separation and Fire Alarm Interface",
            max_col=5,
        )

        headers2 = ["Item", "Parameter / System", "Design Value", "Code Requirement", "Compliance"]
        self.writer.add_table_header(4, headers2)

        data2 = [
            [1, "Building Floor Diagonal", f"{self.res.building_diagonal_m} m", "-", "CALCULATED"],
            [2, "Min Exit Separation Required", f"{self.res.min_exit_separation_required_m} m", "1/3 Diagonal", "MANDATORY"],
            [3, "Actual Exit Separation", f"{self.res.actual_exit_separation_m} m", f">= {self.res.min_exit_separation_required_m} m", "PASS" if self.res.separation_pass else "VIOLATION"],
            [4, "Emergency Exit Signs", "Self-Illuminated (90 min battery)", "Over all exit doors", "REQUIRED"],
            [5, "Fire Alarm Pull Stations", "Within 1.5m of exits", "+1200mm to +1400mm AFF", "REQUIRED"],
            [6, "Fire Sprinkler Density", "0.10 gpm/sq.ft", "NFPA 13 / SBC 801", "COMPLIANT"],
        ]

        for r_idx, row_vals in enumerate(data2, start=5):
            for c_idx, val in enumerate(row_vals, start=1):
                ws_mep.cell(row=r_idx, column=c_idx, value=val)

        self.writer.auto_fit_columns()

        return self.writer.save(filepath)
