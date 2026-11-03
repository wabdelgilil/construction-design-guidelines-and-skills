"""
Excel Exporter for Access Control Door Hardware, Power Budget, and Battery Sizing.
"""

from pathlib import Path
import math
from core.exporters.excel_writer import ExcelWriter
from electrical.low_current_elv.access_control.scripts.design_engine import AccessControlDesignResult


class AccessControlExcelExporter:
    """Exports Access Control schedules, power budgets, and battery calculations to Excel."""

    def __init__(self, result: AccessControlDesignResult):
        self.res = result
        self.writer = ExcelWriter("Access Control")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "Door Hardware Schedule"

        self.writer.format_title_banner(
            title=f"ACCESS CONTROL DOOR HARDWARE SCHEDULE - {self.res.project_name.upper()}",
            subtitle=f"Code: {self.res.standard_used} | Doors: {self.res.total_doors_count} | Operating: {self.res.dc_operating_voltage_v}V DC | Autonomy: 4.0 Hours",
            max_col=10,
        )

        headers = [
            "Door Tag",
            "Door Description",
            "Lock Type",
            "Qty",
            "Holding Force (N)",
            "Reader Type",
            "Lock Current (mA)",
            "Periph Current (mA)",
            "Total Current (mA)",
            "Power (W)",
        ]
        self.writer.add_table_header(4, headers)

        for idx, d in enumerate(self.res.doors, start=5):
            ws.cell(row=idx, column=1, value=d.door_tag)
            ws.cell(row=idx, column=2, value=d.door_name)
            ws.cell(row=idx, column=3, value=d.lock_type)
            ws.cell(row=idx, column=4, value=d.lock_count)
            ws.cell(row=idx, column=5, value=f"{d.lock_holding_force_n} N")
            ws.cell(row=idx, column=6, value=d.reader_type)
            ws.cell(row=idx, column=7, value=d.lock_current_ma)
            ws.cell(row=idx, column=8, value=d.peripherals_current_ma)
            ws.cell(row=idx, column=9, value=d.total_door_current_ma)
            ws.cell(row=idx, column=10, value=d.power_watts)

        self.writer.auto_fit_columns()

        # Tab 2: PSU & Standby Battery Sizing
        ws_psu = self.writer.create_sheet("PSU & Battery Sizing")
        self.writer.format_title_banner(
            title="ACCESS CONTROL POWER SUPPLY & 4-HOUR STANDBY BATTERY SIZING",
            subtitle=f"System Load: {self.res.total_system_current_a} A ({self.res.total_system_power_watts} W) | Selected PSU: {self.res.recommended_psu_current_a} A | Battery: {self.res.selected_battery_ah} Ah",
            max_col=4,
        )

        psu_headers = ["Engineering Parameter", "Calculated Value", "Selected Unit / Rating", "Engineering Basis"]
        self.writer.add_table_header(4, psu_headers)

        rows = [
            ("Operating DC Voltage", f"{self.res.dc_operating_voltage_v} V DC", f"{self.res.dc_operating_voltage_v} V DC", "Auxiliary ELV Bus"),
            ("Total Continuous System Current", f"{self.res.total_system_current_a} A", f"{self.res.total_system_current_ma} mA", "Sum of Locks, Readers, Controllers"),
            ("Total Continuous Power Draw", f"{self.res.total_system_power_watts} W", f"{self.res.total_system_power_watts} W", "P = V x I"),
            ("Minimum Power Supply Rating", f"{self.res.total_system_current_a * 1.25:.2f} A", f"{self.res.recommended_psu_current_a} A", "1.25 Continuous Service Factor"),
            ("Selected PSU Power Output", f"{self.res.recommended_psu_rating_w} W", f"{self.res.recommended_psu_rating_w} W", "Regulated 12V DC Switch-Mode PSU"),
            ("Required Standby Autonomy", "4.0 Hours", "4.0 Hours", "NFPA 101 / SBC 801 Emergency Standby"),
            ("Calculated Battery Capacity", f"{self.res.calculated_battery_ah} Ah", f"{self.res.selected_battery_ah} Ah", "C = I x t x 1.25 aging factor"),
            ("Selected Battery Configuration", f"1x {self.res.selected_battery_ah} Ah @ 12V", "Sealed Lead Acid (VRLA)", "Internal PSU Battery Tray"),
            ("Fire Alarm Egress Interlock", "Normally Closed (NC) Relay", "Fail-Safe Dropout", "NFPA 101 Mandatory Life Safety"),
        ]

        for idx, (param, calc, sel, basis) in enumerate(rows, start=5):
            ws_psu.cell(row=idx, column=1, value=param)
            ws_psu.cell(row=idx, column=2, value=calc)
            ws_psu.cell(row=idx, column=3, value=sel)
            ws_psu.cell(row=idx, column=4, value=basis)

        self.writer.auto_fit_columns()

        # Tab 3: Itemized Bill of Quantities (BOQ)
        ws_boq = self.writer.create_sheet("Access Control BOQ")
        self.writer.format_title_banner(
            title="ACCESS CONTROL SYSTEM BILL OF QUANTITIES (BOQ)",
            subtitle=f"Project: {self.res.project_name} | Scope: Supply, Installation, Testing & Commissioning",
            max_col=5,
        )

        boq_headers = ["Item No.", "Equipment Description", "Specification / Rating", "Quantity", "Unit"]
        self.writer.add_table_header(4, boq_headers)

        boq_items = [
            ("1.01", "Intelligent TCP/IP Network Door Controller", self.res.controller_type, self.res.total_controllers_count, "Unit"),
            ("1.02", "Regulated Linear/Switching Power Supply Unit", f"{self.res.recommended_psu_current_a}A @ 12V DC with Fire Relay", max(math.ceil(self.res.total_controllers_count / 2.0), 1), "Unit"),
            ("1.03", "Sealed VRLA Rechargeable Standby Battery", f"{self.res.selected_battery_ah} Ah, 12V DC (4-Hour Backup)", max(math.ceil(self.res.total_controllers_count / 2.0), 1), "Unit"),
            ("1.04", "Proximity Smart Card / BLE Readers", "Mifare Desfire EV2 / OSDP v2 protocol", sum(1 for d in self.res.doors if d.reader_type == 'card_reader'), "Nos"),
            ("1.05", "Biometric Fingerprint / Face Recognition Reader", "IP65 Optical/Thermal sensor with OSDP", sum(1 for d in self.res.doors if d.reader_type == 'biometric_reader'), "Nos"),
            ("1.06", "Electromagnetic Lock (600 lbs)", "Fail-Safe 2700N, 12V DC, with Hall-effect sensor", sum(d.lock_count for d in self.res.doors if '600lbs' in d.lock_type), "Sets"),
            ("1.07", "Electromagnetic Lock (1200 lbs)", "Fail-Safe 5300N, 12V DC, heavy-duty perimeter", sum(d.lock_count for d in self.res.doors if '1200lbs' in d.lock_type), "Sets"),
            ("1.08", "Electric Door Strike", "Fail-Safe / Fail-Secure reversible, 12V DC", sum(d.lock_count for d in self.res.doors if 'strike' in d.lock_type), "Sets"),
            ("1.09", "Passive Infrared Request-to-Exit (REX) Sensor", "Ceiling/Header mount, adjustable latch timer", self.res.total_doors_count, "Nos"),
            ("1.10", "Emergency Break Glass Unit (BGU)", "Green casing, double-pole, marked EMERGENCY EXIT", self.res.total_doors_count, "Nos"),
            ("1.11", "Concealed Magnetic Door Contact (DPS)", "High security reed contact with tamper loop", self.res.total_doors_count, "Nos"),
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
