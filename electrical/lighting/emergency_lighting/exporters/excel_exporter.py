"""
Excel Exporter for Emergency Lighting Schedule and Central Battery System (CBS) Sizing.
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from electrical.lighting.emergency_lighting.scripts.design_engine import EmergencyLightingDesignResult


class EmergencyLightingExcelExporter:
    """Exports emergency lighting schedules and CBS calculation workbooks to Excel."""

    def __init__(self, result: EmergencyLightingDesignResult):
        self.res = result
        self.writer = ExcelWriter("Emergency Lighting")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "Emergency Schedule"

        self.writer.format_title_banner(
            title=f"EMERGENCY & EXIT LIGHTING SCHEDULE - {self.res.project_name.upper()}",
            subtitle=f"Code: {self.res.standard_used} | System: {self.res.system_architecture} | Autonomy: {self.res.autonomy_hours * 60:.0f} Minutes",
            max_col=7,
        )

        headers = [
            "Space / Zone",
            "Typology",
            "Area (m²)",
            "Target Lux",
            "Emergency Lights",
            "Exit Signs",
            "Connected Load (W)",
        ]
        self.writer.add_table_header(4, headers)

        for idx, alloc in enumerate(self.res.allocations, start=5):
            ws.cell(row=idx, column=1, value=alloc.space_name)
            ws.cell(row=idx, column=2, value=alloc.space_type)
            ws.cell(row=idx, column=3, value=alloc.area_m2)
            ws.cell(row=idx, column=4, value=f"{alloc.target_illuminance_lux} Lux")
            ws.cell(row=idx, column=5, value=alloc.emergency_luminaires_count)
            ws.cell(row=idx, column=6, value=alloc.exit_signs_count)
            ws.cell(row=idx, column=7, value=f"{alloc.total_watts:.1f} W")

        self.writer.auto_fit_columns()

        # Tab 2: CBS Central Battery Sizing
        ws_cbs = self.writer.create_sheet("CBS Battery Sizing")
        self.writer.format_title_banner(
            title="CENTRAL BATTERY SYSTEM (CBS) INVERTER & BATTERY PACK",
            subtitle=f"Inverter: {self.res.cbs_inverter_rated_va} VA | Battery: {self.res.cbs_selected_battery_ah} Ah @ {self.res.cbs_battery_dc_bus_v}V DC",
            max_col=5,
        )

        headers2 = ["Item", "CBS Component / Parameter", "Calculated / Specified Value", "Unit", "Engineering Criteria"]
        self.writer.add_table_header(4, headers2)

        data2 = [
            [1, "Total Emergency Lighting Load", f"{self.res.total_emergency_load_watts} W", "Watts", "Sum of all luminaires & exit signs"],
            [2, "Required Autonomy Duration", f"{self.res.autonomy_hours * 60:.0f} Minutes", "Minutes", "NFPA 101 / SBC 801 mandate"],
            [3, "Specified CBS Inverter Rating", f"{self.res.cbs_inverter_rated_va} VA", "VA", "With 25% future growth margin"],
            [4, "DC Battery Bus Voltage", f"{self.res.cbs_battery_dc_bus_v} V DC", "V DC", f"{self.res.cbs_battery_blocks_12v_count}x 12V VRLA Blocks in series"],
            [5, "Calculated Theoretical Battery Capacity", f"{self.res.cbs_calculated_battery_ah} Ah", "Ah", "C = (P*T*1.25)/(eta*V)"],
            [6, "Specified Commercial Battery Pack", f"{self.res.cbs_selected_battery_ah} Ah", "Ah", "10-Year High-Rate VRLA"],
            [7, "Dedicated CBS Branch Circuits", f"{self.res.total_cbs_circuits_count} Circuits", "Nos.", "FP200 Fire-Resistant Cable"],
        ]

        for r_idx, row_vals in enumerate(data2, start=5):
            for c_idx, val in enumerate(row_vals, start=1):
                ws_cbs.cell(row=r_idx, column=c_idx, value=val)

        self.writer.auto_fit_columns()

        return self.writer.save(filepath)
