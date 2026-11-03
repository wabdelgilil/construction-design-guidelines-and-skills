"""
Excel Exporter for Addressable Fire Alarm Device Schedule, Loop Loading, and Battery Calculations.
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from electrical.low_current_elv.fire_alarm.scripts.design_engine import FireAlarmDesignResult


class FireAlarmExcelExporter:
    """Exports fire alarm system schedules and battery sizing calculations to Excel."""

    def __init__(self, result: FireAlarmDesignResult):
        self.res = result
        self.writer = ExcelWriter("fire_alarm_schedule.xlsx")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "Device Schedule"

        self.writer.format_title_banner(
            title=f"ADDRESSABLE FIRE ALARM DEVICE SCHEDULE - {self.res.project_name.upper()}",
            subtitle=f"Code: {self.res.standard_used} | Total Addressable Points: {self.res.grand_total_addressable_devices} | Loops: {self.res.total_loops_required}",
            max_col=8,
        )

        headers = [
            "Space Name",
            "Area (m²)",
            "Detector Type",
            "Detectors",
            "MCPs",
            "Sounders/Strobes",
            "Strobe Candela",
            "Interface Modules",
        ]
        self.writer.add_table_header(4, headers)

        for idx, alloc in enumerate(self.res.allocations, start=5):
            mod_str = ", ".join(alloc.interface_modules) if alloc.interface_modules else "None"
            ws.cell(row=idx, column=1, value=alloc.space_name)
            ws.cell(row=idx, column=2, value=alloc.area_m2)
            ws.cell(row=idx, column=3, value=alloc.detector_type)
            ws.cell(row=idx, column=4, value=alloc.detector_count)
            ws.cell(row=idx, column=5, value=alloc.mcp_count)
            ws.cell(row=idx, column=6, value=alloc.sounder_strobe_count)
            ws.cell(row=idx, column=7, value=f"{alloc.strobe_candela_cd} cd")
            ws.cell(row=idx, column=8, value=mod_str)

        self.writer.auto_fit_columns()

        # Tab 2: Loop Loading & Battery Calculations
        ws_batt = self.writer.create_sheet("Loop & Battery Sizing")
        self.writer.format_title_banner(
            title="NFPA 72 BATTERY CALCULATION & LOOP LOADING",
            subtitle=f"Specified Battery: {self.res.selected_battery_rating_ah} Ah (24V DC) | Spare: {self.res.loop_spare_capacity_pct}%",
            max_col=5,
        )

        headers2 = ["Item", "System Parameter", "Calculated / Sized Value", "Unit", "Code Standard"]
        self.writer.add_table_header(4, headers2)

        data2 = [
            [1, "Total Addressable Devices", self.res.grand_total_addressable_devices, "Points", "All loops combined"],
            [2, "Required Addressable Loops", self.res.total_loops_required, "Loops", "Max 127 devices per loop"],
            [3, "Loop Spare Margin", f"{self.res.loop_spare_capacity_pct}%", "%", "Min 20% future spare"],
            [4, "FACP Standby Quiescent Current", self.res.facp_quiescent_current_amps, "A", "Base panel + quiescent points"],
            [5, "FACP Full Alarm Current", self.res.facp_alarm_current_amps, "A", "Active alarm points + sounders"],
            [6, "Standby Duration", self.res.standby_duration_hours, "Hours", "NFPA 72 mandate (24h)"],
            [7, "Alarm Evacuation Duration", self.res.alarm_duration_minutes, "Minutes", "NFPA 72 mandate (15 min)"],
            [8, "Calculated Theoretical Battery Capacity", self.res.calculated_battery_capacity_ah, "Ah", "C = 1.25 * (Iq*24 + Ia*0.25)"],
            [9, "Selected Commercial Battery Pack", f"{self.res.selected_battery_rating_ah} Ah ({self.res.battery_voltage_vdc}V DC)", "-", "SLA Maintenance-Free"],
        ]

        for r_idx, row_vals in enumerate(data2, start=5):
            for c_idx, val in enumerate(row_vals, start=1):
                ws_batt.cell(row=r_idx, column=c_idx, value=val)

        self.writer.auto_fit_columns()

        return self.writer.save(filepath)
