"""
Excel Exporter for Building Management System (BMS) Point Schedules, DDC Panels, and BOQ.
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from electrical.low_current_elv.bms_automation.scripts.design_engine import BMSDesignResult


class BMSExcelExporter:
    """Exports BMS I/O point schedules, DDC panel allocations, and BOQ workbooks to Excel."""

    def __init__(self, result: BMSDesignResult):
        self.res = result
        self.writer = ExcelWriter("BMS Point Schedule")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "MEP IO Point Schedule"

        self.writer.format_title_banner(
            title=f"BMS MEP I/O POINT SCHEDULE - {self.res.project_name.upper()}",
            subtitle=f"Code: {self.res.standard_used} | Active Points: {self.res.grand_total_active_points} | Spare: {self.res.grand_total_spare_points} (20%) | Total Equipped: {self.res.grand_total_equipped_points} | DDC Panels: {self.res.total_ddc_panels_count}",
            max_col=10,
        )

        headers = [
            "Equipment Tag",
            "Description",
            "Location",
            "DI (Status/Alarm)",
            "DO (Command)",
            "AI (Sensors)",
            "AO (Actuators)",
            "Total Hardwired",
            "HLI Integration",
            "I/O Descriptions Summary",
        ]
        self.writer.add_table_header(4, headers)

        for idx, eq in enumerate(self.res.equipment_points, start=5):
            ws.cell(row=idx, column=1, value=eq.equipment_tag)
            ws.cell(row=idx, column=2, value=eq.description)
            ws.cell(row=idx, column=3, value=eq.location)
            ws.cell(row=idx, column=4, value=eq.di_count)
            ws.cell(row=idx, column=5, value=eq.do_count)
            ws.cell(row=idx, column=6, value=eq.ai_count)
            ws.cell(row=idx, column=7, value=eq.ao_count)
            ws.cell(row=idx, column=8, value=eq.total_hardwired_points)
            ws.cell(row=idx, column=9, value=eq.hli_integration_type)
            ws.cell(row=idx, column=10, value="; ".join(eq.point_descriptions[:3]) + "...")

        self.writer.auto_fit_columns()

        # Tab 2: DDC Panel Allocation & Sizing
        ws_pnl = self.writer.create_sheet("DDC Panel Allocation")
        self.writer.format_title_banner(
            title="DIRECT DIGITAL CONTROLLER (DDC) PANEL SIZING & ALLOCATION",
            subtitle="Equipped with 20% Spare I/O Capacity per ASHRAE 135 & SBC 601",
            max_col=9,
        )

        pnl_headers = [
            "Panel Tag",
            "Location",
            "Served Equipment",
            "Active Points",
            "Spare Points (20%)",
            "Equipped Capacity",
            "Base DDC (32-pt)",
            "Exp. Modules (16-pt)",
            "Enclosure Specification",
        ]
        self.writer.add_table_header(4, pnl_headers)

        for idx, p in enumerate(self.res.ddc_panels, start=5):
            ws_pnl.cell(row=idx, column=1, value=p.panel_tag)
            ws_pnl.cell(row=idx, column=2, value=p.panel_location)
            ws_pnl.cell(row=idx, column=3, value=", ".join(p.served_equipment))
            ws_pnl.cell(row=idx, column=4, value=p.active_points)
            ws_pnl.cell(row=idx, column=5, value=p.spare_points)
            ws_pnl.cell(row=idx, column=6, value=p.equipped_capacity_points)
            ws_pnl.cell(row=idx, column=7, value=p.base_ddc_units_count)
            ws_pnl.cell(row=idx, column=8, value=p.expansion_modules_count)
            ws_pnl.cell(row=idx, column=9, value=p.enclosure_size_mm)

        self.writer.auto_fit_columns()

        # Tab 3: Itemized Bill of Quantities (BOQ)
        ws_boq = self.writer.create_sheet("BMS BOQ")
        self.writer.format_title_banner(
            title="BUILDING MANAGEMENT SYSTEM (BMS) BILL OF QUANTITIES",
            subtitle=f"Project: {self.res.project_name} | Scope: DDC Hardware, Field Sensors & Central Server",
            max_col=5,
        )

        boq_headers = ["Item No.", "Equipment Description", "Specification / Rating", "Quantity", "Unit"]
        self.writer.add_table_header(4, boq_headers)

        total_base = sum(p.base_ddc_units_count for p in self.res.ddc_panels)
        total_exp = sum(p.expansion_modules_count for p in self.res.ddc_panels)

        boq_items = [
            ("1.01", "Central BMS Server & Software Suite", "BACnet/IP client, unlimited points license, 3D graphics, alarm logger", 1, "Set"),
            ("1.02", "Operator Workstation Terminal", "Intel Core i7, 32GB RAM, Dual 27-inch 4K LCD displays", 1, "Unit"),
            ("1.03", "Base DDC Controller (BACnet/IP)", "32-Point Universal I/O, 10/100 Ethernet RJ45, 24V AC/DC", total_base, "Units"),
            ("1.04", "DDC Universal Expansion Module", "16-Point UI/O Expansion Module with internal communication bus", total_exp, "Units"),
            ("1.05", "DDC Control Panel Enclosure Assembly", "IP54 sheet steel, 24V DC regulated PSU, terminal blocks, fuse isolator", self.res.total_ddc_panels_count, "Sets"),
            ("1.06", "Immersion Water Temperature Sensors", "Pt1000 Class A RTD, stainless steel thermowell, 0-100°C", sum(e.ai_count for e in self.res.equipment_points if "Temp" in "".join(e.point_descriptions)), "Nos"),
            ("1.07", "Differential Pressure Switches (Air DPS)", "Adjustable 20-300 Pa, gold-plated contacts (Fan/Filter)", sum(e.di_count for e in self.res.equipment_points if "DPS" in "".join(e.point_descriptions)), "Nos"),
            ("1.08", "Water Pressure Transmitters", "4-20 mA output, 0-16 bar range, ceramic measuring cell", sum(e.ai_count for e in self.res.equipment_points if "Pressure" in "".join(e.point_descriptions)), "Nos"),
            ("1.09", "Indoor Air Quality CO2 Transmitters", "NDIR optical sensor, 0-2000 ppm, 0-10V DC output", sum(e.ai_count for e in self.res.equipment_points if "CO2" in "".join(e.point_descriptions)), "Nos"),
            ("1.10", "Online Double-Conversion Rackmount UPS", f"{self.res.recommended_ups_va} VA, 2.0 hours backup autonomy for central server and DDC network", 1, "Unit"),
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
