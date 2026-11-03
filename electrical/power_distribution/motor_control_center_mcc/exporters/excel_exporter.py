"""
Excel Exporter for Motor Control Center (MCC) Schedules, Starters, and BOQ.
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from electrical.power_distribution.motor_control_center_mcc.scripts.design_engine import MCCDesignResult


class MCCExcelExporter:
    """Exports MCC motor schedules, starter ratings, and BOQ workbooks to Excel."""

    def __init__(self, result: MCCDesignResult):
        self.res = result
        self.writer = ExcelWriter("Motor Control Center")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "MCC Motor Schedule"

        self.writer.format_title_banner(
            title=f"MOTOR CONTROL CENTER (MCC) LOAD & STARTER SCHEDULE - {self.res.project_name.upper()}",
            subtitle=f"Code: {self.res.standard_used} | Motors: {self.res.total_motors_count} ({self.res.total_connected_kw} kW / {self.res.total_connected_hp} HP) | Incomer: {self.res.mcc_main_incomer_rating_a}A | Busbar: {self.res.mcc_main_busbar_rating_a}A",
            max_col=13,
        )

        headers = [
            "Tag",
            "Description",
            "Rated kW",
            "Rated HP",
            "FLA (A)",
            "Starter Method",
            "Starting Current (A)",
            "Main Contactor (A)",
            "Overload Setting (A)",
            "Breaker (A)",
            "Feeder Cable (mm²)",
            "Run VD (%)",
            "Start VD (%)",
        ]
        self.writer.add_table_header(4, headers)

        for idx, m in enumerate(self.res.motors, start=5):
            ws.cell(row=idx, column=1, value=m.tag)
            ws.cell(row=idx, column=2, value=m.description)
            ws.cell(row=idx, column=3, value=m.rated_kw)
            ws.cell(row=idx, column=4, value=m.rated_hp)
            ws.cell(row=idx, column=5, value=m.fla_a)
            ws.cell(row=idx, column=6, value=m.starting_method)
            ws.cell(row=idx, column=7, value=m.starting_current_a)
            ws.cell(row=idx, column=8, value=m.contactor_main_ac3_a)
            ws.cell(row=idx, column=9, value=m.overload_setting_a)
            ws.cell(row=idx, column=10, value=m.mcp_breaker_rating_a)
            ws.cell(row=idx, column=11, value=f"{m.feeder_cable_csa_mm2} mm²")
            ws.cell(row=idx, column=12, value=f"{m.run_voltage_drop_pct:.2f}%")
            ws.cell(row=idx, column=13, value=f"{m.start_voltage_drop_pct:.2f}%")

        self.writer.auto_fit_columns()

        # Tab 2: Switchgear & Starter Technical Breakdown
        ws_tech = self.writer.create_sheet("Starters Technical Data")
        self.writer.format_title_banner(
            title="MOTOR STARTERS & CONTACTOR TECHNICAL SPECIFICATIONS",
            subtitle="Type 2 Coordination per IEC 60947-4-1 (Non-destructive clearing)",
            max_col=7,
        )

        tech_headers = ["Tag", "Starter Type", "Main Contactor AC-3", "Delta Contactor", "Star Contactor", "Overload Relay", "Cubicle Height"]
        self.writer.add_table_header(4, tech_headers)

        for idx, m in enumerate(self.res.motors, start=5):
            ws_tech.cell(row=idx, column=1, value=m.tag)
            ws_tech.cell(row=idx, column=2, value=m.starting_method)
            ws_tech.cell(row=idx, column=3, value=f"{m.contactor_main_ac3_a:.1f} A")
            ws_tech.cell(row=idx, column=4, value=f"{m.contactor_delta_ac3_a:.1f} A" if m.contactor_delta_ac3_a else "N/A")
            ws_tech.cell(row=idx, column=5, value=f"{m.contactor_star_ac3_a:.1f} A" if m.contactor_star_ac3_a else "N/A")
            ws_tech.cell(row=idx, column=6, value=f"{m.overload_setting_a:.1f} A (Class 10)")
            ws_tech.cell(row=idx, column=7, value=f"{m.cubicle_height_mm} mm")

        self.writer.auto_fit_columns()

        # Tab 3: Itemized Bill of Quantities (BOQ)
        ws_boq = self.writer.create_sheet("MCC BOQ")
        self.writer.format_title_banner(
            title="MOTOR CONTROL CENTER (MCC) BILL OF QUANTITIES",
            subtitle=f"Project: {self.res.project_name} | Segregation: {self.res.segregation_form}",
            max_col=5,
        )

        boq_headers = ["Item No.", "Equipment Description", "Specification / Rating", "Quantity", "Unit"]
        self.writer.add_table_header(4, boq_headers)

        boq_items = [
            ("1.01", "MCC Enclosure Switchboard Assembly", f"{self.res.total_columns_count} Columns Form 4b, IP54, 400V 60Hz, 50kA/1s", 1, "Set"),
            ("1.02", "Incomer 4-Pole Drawout Circuit Breaker", f"{self.res.mcc_main_incomer_rating_a}A ACB/MCCB, Icu=50kA with Micrologic Unit", 1, "Unit"),
            ("1.03", "Main Tinned Copper Horizontal Busbars", f"{self.res.mcc_main_busbar_rating_a}A rating, 50kA 1s withstand capacity", 1, "Lot"),
            ("1.04", "Direct-On-Line (DOL) Starter Modules", "MCP Breaker + AC-3 Contactor + Thermal Overload + HOA", sum(1 for m in self.res.motors if "DOL" in m.starting_method), "Sets"),
            ("1.05", "Star-Delta (Y-Δ) Starter Modules", "MCP Breaker + 3x Contactors + Timer Relay + Overload", sum(1 for m in self.res.motors if "Star-Delta" in m.starting_method), "Sets"),
            ("1.06", "Variable Frequency Drive (VFD) Cubicles", "IP54 Inverter with 3% Line Choke, Bypass Contactor, Keypad", sum(1 for m in self.res.motors if "VFD" in m.starting_method), "Sets"),
            ("1.07", "Solid-State Soft Starter Modules", "Thyristor-based soft starter with internal bypass contactor", sum(1 for m in self.res.motors if "Soft" in m.starting_method), "Sets"),
            ("1.08", "Multifunction Digital Power Meter", "Incomer LCD meter (V, I, kW, kVA, pf, THD, RS485 Modbus)", 1, "Unit"),
        ]

        for idx, (num, desc, spec, qty, unit) in enumerate(boq_items, start=5):
            ws_boq.cell(row=idx, column=1, value=num)
            ws_boq.cell(row=idx, column=2, value=desc)
            ws_boq.cell(row=idx, column=3, value=spec)
            ws_boq.cell(row=idx, column=4, value=qty)
            ws_boq.cell(row=idx, column=5, value=unit)

        self.writer.auto_fit_columns()
        self.writer.save(filepath)
        return filepath
