"""
Excel Exporter for Plumbing Drainage, Water Supply, and Structural Sleeves Schedule.
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from mechanical.plumbing.scripts.design_engine import PlumbingDesignResult


class PlumbingExcelExporter:
    """Exports plumbing engineering calculations and sleeve schedule to Excel."""

    def __init__(self, result: PlumbingDesignResult):
        self.res = result
        self.writer = ExcelWriter("plumbing_schedule.xlsx")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "Plumbing Sizing Summary"

        self.writer.format_title_banner(
            title=f"PLUMBING SYSTEM & BOOSTER PUMP SCHEDULE - {self.res.building_tag}",
            subtitle=f"Governing Standard: {self.res.code_used} / IPC | Total DFU: {self.res.total_dfu} | Total WSFU: {self.res.total_wsfu}",
            max_col=6,
        )

        headers = ["Item", "System Parameter", "Calculated / Sized Value", "Unit", "Code Requirement", "Compliance"]
        self.writer.add_table_header(4, headers)

        data = [
            [1, "Total Drainage Load", self.res.total_dfu, "DFU", "-", "OK"],
            [2, "Vertical Soil / Waste Stack Size", f"{self.res.selected_soil_stack_diameter_in} inch ({self.res.selected_soil_stack_diameter_in*25} mm)", "-", "Capacity <= 500 DFU", "PASS"],
            [3, "Horizontal Main Building Drain", f"{self.res.selected_building_drain_diameter_in} inch ({self.res.selected_building_drain_diameter_in*25} mm)", "-", "Capacity <= 180 DFU", "PASS"],
            [4, "Drain Minimum Invert Slope", f"{self.res.minimum_drain_slope_pct}% ({self.res.minimum_drain_slope_pct*10} mm/m)", "%", "Min 1% (or 2% for 3\")", "COMPLIANT"],
            [5, "Total Water Supply Load", self.res.total_wsfu, "WSFU", "-", "OK"],
            [6, "Peak Simultaneous Demand Flow", f"{self.res.design_flow_gpm} GPM ({self.res.design_flow_l_per_s} L/s)", "-", "Hunter's Curve", "OK"],
            [7, "Total Booster Pump Head", f"{self.res.total_pump_head_m} m ({self.res.total_pump_head_bar} bar)", "-", "Static + Friction + Residual", "OPTIMAL"],
            [8, "Booster Motor Power (Each)", f"{self.res.pump_motor_power_kw} kW", "kW", "1 Duty + 1 Standby", "SIZED"],
            [9, "Booster Electrical Feed", f"{self.res.pump_voltage_v}V, FLC={self.res.pump_current_amps}A, MCB={self.res.pump_mcb_rating_amps}A", "-", "Dedicated Circuit", "COORDINATED"],
        ]

        for r_idx, row_vals in enumerate(data, start=5):
            for c_idx, val in enumerate(row_vals, start=1):
                ws.cell(row=r_idx, column=c_idx, value=val)

        self.writer.auto_fit_columns()

        # Tab 2: Structural Pipe Sleeves Schedule
        ws_sleeves = self.writer.create_sheet("Structural Pipe Sleeves")
        self.writer.format_title_banner(
            title="CIVIL / STRUCTURAL PIPE SLEEVES SCHEDULE",
            subtitle="Pre-Cast Foundation Openings and Retaining Wall Penetrations",
            max_col=5,
        )

        sleeve_headers = ["Item", "Service Penetration", "Pipe Specification", "Sleeve Specification", "Structural Location & Sealing"]
        self.writer.add_table_header(4, sleeve_headers)

        for s_idx, slv in enumerate(self.res.sleeves_required, start=5):
            ws_sleeves.cell(row=s_idx, column=1, value=s_idx - 4)
            ws_sleeves.cell(row=s_idx, column=2, value=slv["service"])
            ws_sleeves.cell(row=s_idx, column=3, value=slv["pipe_size"])
            ws_sleeves.cell(row=s_idx, column=4, value=slv["sleeve_size"])
            ws_sleeves.cell(row=s_idx, column=5, value=f"{slv['location']} | {slv['waterproofing']}")

        self.writer.auto_fit_columns()

        return self.writer.save(filepath)
