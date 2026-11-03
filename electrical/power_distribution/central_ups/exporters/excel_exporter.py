"""Excel Schedule and Bill of Quantities (BOQ) Exporter for Central UPS Systems."""

import math
from typing import Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


class CentralUPSExcelExporter:
    """Exports UPS sizing results, battery schedules, and complete BOQ to Excel (.xlsx)."""

    def __init__(self):
        self.header_fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")  # Navy
        self.sub_header_fill = PatternFill(start_color="2B6CB0", end_color="2B6CB0", fill_type="solid") # Steel Blue
        self.accent_fill = PatternFill(start_color="EBF8FF", end_color="EBF8FF", fill_type="solid")
        self.total_fill = PatternFill(start_color="CBD5E0", end_color="CBD5E0", fill_type="solid")

        self.font_title = Font(name="Calibri", size=16, bold=True, color="1A365D")
        self.font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        self.font_bold = Font(name="Calibri", size=11, bold=True)
        self.font_regular = Font(name="Calibri", size=11)

        thin_border = Side(style="thin", color="CBD5E0")
        self.border_thin = Border(left=thin_border, right=thin_border, top=thin_border, bottom=thin_border)
        double_bottom = Side(style="double", color="1A365D")
        self.border_total = Border(top=thin_border, bottom=double_bottom, left=thin_border, right=thin_border)

    def export(self, design_data: Dict[str, Any], file_path: str):
        wb = openpyxl.Workbook()
        ws_summary = wb.active
        ws_summary.title = "UPS System Summary"
        ws_loads = wb.create_sheet(title="Load Schedule")
        ws_boq = wb.create_sheet(title="Bill of Quantities (BOQ)")

        self._build_summary_sheet(ws_summary, design_data)
        self._build_load_sheet(ws_loads, design_data)
        self._build_boq_sheet(ws_boq, design_data)

        wb.save(file_path)

    def _build_summary_sheet(self, ws, data: Dict[str, Any]):
        ws.views.sheetView[0].showGridLines = True
        ws["A1"] = "CENTRAL UPS & DC BATTERY PLANT SPECIFICATION"
        ws["A1"].font = self.font_title
        ws.row_dimensions[1].height = 25

        headers = ["Parameter", "Engineering Design Value", "Unit", "Governing Standard / Basis"]
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col_idx, value=h)
            cell.font = self.font_header
            cell.fill = self.header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[3].height = 24

        ups = data["ups_module"]
        batt = data["battery_plant"]
        loads = data["loads_summary"]
        brk = data["breakers"]
        vent = data["ventilation"]

        specs = [
            ("Governing Standard", data.get("code_standard", "SBC"), "-", "IEC 62040-3 / IEEE 485 / NFPA 111"),
            ("Nominal System Voltage (AC)", data.get("nominal_voltage_ac", 400.0), "V AC (3-Phase)", "Grid Nominal Frequency: {} Hz".format(data.get("frequency_hz", 60.0))),
            ("UPS Topology", "Online Double-Conversion (VFI-SS-111)", "-", "IGBT Rectifier & Inverter with Static Bypass"),
            ("UPS Redundancy Configuration", data.get("redundancy_type", "N+1"), "-", "Parallel redundant architecture"),
            ("Connected Load", loads["total_connected_kw"], "kW", f"{loads['total_connected_kva']} kVA @ PF {loads['overall_pf']}"),
            ("Design Load with Growth Margin", loads["design_load_kw"], "kW", f"{loads['design_load_kva']} kVA (20% future growth allowance)"),
            ("Selected UPS Unit Rating", ups["selected_module_kva"], "kVA", "Standard industrial modular tier"),
            ("Total Installed UPS Modules", f"{ups['total_modules']} Units ({ups['n_modules']} Active + 1 Redundant)", "Units", f"Total System: {ups['total_system_kva']} kVA"),
            ("Module AC Full Load Current (FLC)", ups["module_flc_ac"], "A", "Per UPS module at nominal 400V"),
            ("Battery Nominal DC Bus Voltage", batt["nominal_dc_bus_v"], "V DC", f"{batt['total_cells']} Cells @ 2.0 V/cell nominal"),
            ("End of Discharge Voltage (EOD)", batt["min_dc_bus_voltage"], "V DC", f"{batt['cell_eod_v']} V/cell cutoff threshold"),
            ("Battery Technology", "Sealed Maintenance-Free VRLA (AGM)", "-", "Flame retardant UL94-V0 jars"),
            ("Required Autonomy Time", data.get("backup_time_min", 30.0), "Minutes", "Full design load continuous discharge"),
            ("Calculated Constant DC Power", batt["dc_power_kw"], "kW", f"Inverter Efficiency: {ups['inverter_efficiency']*100:.1f}%"),
            ("Design Watts per Cell (IEEE 485)", batt["req_watts_per_cell"], "W/cell", f"Aging Factor: {batt['aging_factor']}"),
            ("Maximum DC Discharge Current", batt["i_dc_max"], "A", f"At EOD cutoff {batt['min_dc_bus_voltage']} V DC"),
            ("Battery Strings & Blocks", f"{batt['num_parallel_strings']} string(s) x {batt['blocks_per_string']} blocks", "Blocks", f"Total {batt['total_battery_blocks']} monoblocs (12V)"),
            ("Total Battery Plant Capacity", batt["actual_installed_ah"], "Ah", "C10 rated capacity"),
            ("Rectifier Input Breaker", brk["rectifier_input_breaker_a"], "A", "3P MCCB / ACB (1.25 x FLC)"),
            ("Inverter Output Breaker", brk["inverter_output_breaker_a"], "A", "3P MCCB / ACB (1.15 x FLC)"),
            ("Static Bypass Switch Breaker", brk["static_bypass_breaker_a"], "A", "3P MCCB / ACB with electronic trip"),
            ("Battery DC Protection Breaker", brk["battery_dc_breaker_a"], "A", "2P DC MCCB with shunt trip & UVR"),
            ("Battery Room Hydrogen Gen. Rate", vent["h2_generation_m3_per_hr"], "m3/h", "IEEE 484 boost-charge formulation"),
            ("Battery Room Exhaust Fan Capacity", vent["design_exhaust_airflow_m3_per_hr"], "m3/h", f"{vent['design_exhaust_airflow_cfm']} CFM (Dedicated Spark-proof Fan)"),
        ]

        row = 4
        for item, val, unit, basis in specs:
            ws.cell(row=row, column=1, value=item).font = self.font_bold
            c_val = ws.cell(row=row, column=2, value=val)
            c_val.font = self.font_regular
            c_val.alignment = Alignment(horizontal="center")
            c_u = ws.cell(row=row, column=3, value=unit)
            c_u.font = self.font_regular
            c_u.alignment = Alignment(horizontal="center")
            c_b = ws.cell(row=row, column=4, value=basis)
            c_b.font = self.font_regular

            for col in range(1, 5):
                ws.cell(row=row, column=col).border = self.border_thin
            row += 1

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[get_column_letter(col[0].column)].width = max(max_len + 4, 15)

    def _build_load_sheet(self, ws, data: Dict[str, Any]):
        ws.views.sheetView[0].showGridLines = True
        ws["A1"] = "CONNECTED CRITICAL LOAD SCHEDULE"
        ws["A1"].font = self.font_title
        ws.row_dimensions[1].height = 25

        headers = ["Load ID", "Load Name / Description", "Active Power (kW)", "Power Factor", "Apparent Power (kVA)", "Reactive Power (kVAR)"]
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col_idx, value=h)
            cell.font = self.font_header
            cell.fill = self.header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[3].height = 24

        row = 4
        total_kw = 0.0
        total_kvar = 0.0
        for load in data.get("loads_detail", []):
            kw = load.get("load_kw", 0.0)
            pf = load.get("pf", 0.90)
            kva = kw / pf if pf > 0 else kw
            kvar = kw * math.tan(math.acos(pf)) if pf < 1.0 else 0.0

            total_kw += kw
            total_kvar += kvar

            ws.cell(row=row, column=1, value=load.get("id", f"L-{row-3}")).alignment = Alignment(horizontal="center")
            ws.cell(row=row, column=2, value=load.get("name", "Critical Load"))
            ws.cell(row=row, column=3, value=round(kw, 2)).alignment = Alignment(horizontal="right")
            ws.cell(row=row, column=4, value=round(pf, 2)).alignment = Alignment(horizontal="center")
            ws.cell(row=row, column=5, value=round(kva, 2)).alignment = Alignment(horizontal="right")
            ws.cell(row=row, column=6, value=round(kvar, 2)).alignment = Alignment(horizontal="right")

            for col in range(1, 7):
                ws.cell(row=row, column=col).border = self.border_thin
                ws.cell(row=row, column=col).font = self.font_regular
            row += 1

        total_kva = math.sqrt(total_kw**2 + total_kvar**2)
        total_pf = total_kw / total_kva if total_kva > 0 else 1.0

        # Totals Row
        ws.cell(row=row, column=1, value="TOTAL")
        ws.cell(row=row, column=2, value="Connected Total Demand")
        ws.cell(row=row, column=3, value=round(total_kw, 2))
        ws.cell(row=row, column=4, value=round(total_pf, 3))
        ws.cell(row=row, column=5, value=round(total_kva, 2))
        ws.cell(row=row, column=6, value=round(total_kvar, 2))

        for col in range(1, 7):
            c = ws.cell(row=row, column=col)
            c.font = self.font_bold
            c.fill = self.total_fill
            c.border = self.border_total
            if col in [3, 5, 6]:
                c.alignment = Alignment(horizontal="right")
            elif col in [1, 4]:
                c.alignment = Alignment(horizontal="center")

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[get_column_letter(col[0].column)].width = max(max_len + 4, 15)

    def _build_boq_sheet(self, ws, data: Dict[str, Any]):
        ws.views.sheetView[0].showGridLines = True
        ws["A1"] = "BILL OF QUANTITIES (BOQ) - CENTRAL UPS & BATTERY PLANT"
        ws["A1"].font = self.font_title
        ws.row_dimensions[1].height = 25

        headers = ["Item No.", "Description", "Unit", "Quantity", "Unit Rate (SAR)", "Total Amount (SAR)"]
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col_idx, value=h)
            cell.font = self.font_header
            cell.fill = self.header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[3].height = 24

        ups = data["ups_module"]
        batt = data["battery_plant"]
        brk = data["breakers"]
        vent = data["ventilation"]

        boq_items = [
            (
                "1.01",
                f"True Online Double-Conversion UPS Module, {ups['selected_module_kva']} kVA / {int(ups['selected_module_kva']*0.9)} kW, 400V 3Ph 50/60Hz, IGBT Rectifier & Inverter, THDi < 3%, with built-in Static Bypass and SNMP network management card.",
                "Set",
                ups["total_modules"],
                65000 + ups["selected_module_kva"] * 350
            ),
            (
                "1.02",
                f"External Maintenance Bypass Panel (MBP) rated {ups['total_system_kva']} kVA with make-before-break interlocked rotary switch and Kirk-key mechanical interlocking system.",
                "Lot",
                1,
                18500
            ),
            (
                "1.03",
                f"Valve Regulated Lead-Acid (VRLA) AGM Battery Monobloc, 12V DC, {batt['selected_block_ah']} Ah @ 10-hr rate, flame-retardant UL94-V0 container, 10-year design life.",
                "Nos",
                batt["total_battery_blocks"],
                1250
            ),
            (
                "1.04",
                f"Seismic Tier Battery Rack (Heavy-duty steel, epoxy acid-resistant coated) complete with insulated inter-tier copper busbars and protective covers for {batt['total_battery_blocks']} blocks.",
                "Set",
                batt["num_parallel_strings"],
                8500
            ),
            (
                "1.05",
                f"DC Battery Protection Panel equipped with 2-Pole DC MCCB rated {brk['battery_dc_breaker_a']} A, with auxiliary contact, shunt-trip coil, and integrated micro-switch for door interlock.",
                "Nos",
                batt["num_parallel_strings"],
                9500
            ),
            (
                "1.06",
                "Battery Monitoring System (BMS) with individual block voltage, internal resistance, and string temperature sensors with Modbus/BACnet interface.",
                "Lot",
                1,
                15000
            ),
            (
                "1.07",
                f"Spark-Proof (ATEX / IECEx rated) Battery Room Hydrogen Exhaust Fan, capacity {vent['design_exhaust_airflow_m3_per_hr']} m3/h, with air-flow switch and hydrogen sensor interlock.",
                "Nos",
                2,  # 1 Duty + 1 Standby
                7500
            ),
            (
                "1.08",
                "Wall-mounted Emergency Eye-Wash and Safety Shower Station with acid-neutralizing spill kit.",
                "Set",
                1,
                4200
            ),
            (
                "1.09",
                "Testing, commissioning, full-load bank burn-in test (4 hours), and training.",
                "Lot",
                1,
                22000
            ),
        ]

        row = 4
        subtotal = 0.0
        for item_no, desc, unit, qty, rate in boq_items:
            amount = qty * rate
            subtotal += amount

            ws.cell(row=row, column=1, value=item_no).alignment = Alignment(horizontal="center")
            ws.cell(row=row, column=2, value=desc)
            ws.cell(row=row, column=3, value=unit).alignment = Alignment(horizontal="center")
            ws.cell(row=row, column=4, value=qty).alignment = Alignment(horizontal="center")
            c_rate = ws.cell(row=row, column=5, value=rate)
            c_rate.alignment = Alignment(horizontal="right")
            c_rate.number_format = "#,##0.00"
            c_amt = ws.cell(row=row, column=6, value=amount)
            c_amt.alignment = Alignment(horizontal="right")
            c_amt.number_format = "#,##0.00"

            for col in range(1, 7):
                ws.cell(row=row, column=col).border = self.border_thin
                ws.cell(row=row, column=col).font = self.font_regular
            row += 1

        vat = subtotal * 0.15
        grand_total = subtotal + vat

        # Subtotal
        ws.cell(row=row, column=1, value="")
        ws.cell(row=row, column=2, value="SUBTOTAL")
        ws.cell(row=row, column=6, value=subtotal).number_format = "#,##0.00"
        for col in range(1, 7):
            c = ws.cell(row=row, column=col)
            c.font = self.font_bold
            c.fill = self.accent_fill
            c.border = self.border_thin

        # VAT 15%
        row += 1
        ws.cell(row=row, column=1, value="")
        ws.cell(row=row, column=2, value="VALUE ADDED TAX (VAT 15%)")
        ws.cell(row=row, column=6, value=vat).number_format = "#,##0.00"
        for col in range(1, 7):
            c = ws.cell(row=row, column=col)
            c.font = self.font_bold
            c.fill = self.accent_fill
            c.border = self.border_thin

        # Grand Total
        row += 1
        ws.cell(row=row, column=1, value="")
        ws.cell(row=row, column=2, value="GRAND TOTAL (SAR)")
        ws.cell(row=row, column=6, value=grand_total).number_format = "#,##0.00"
        for col in range(1, 7):
            c = ws.cell(row=row, column=col)
            c.font = self.font_bold
            c.fill = self.total_fill
            c.border = self.border_total

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[get_column_letter(col[0].column)].width = max(max_len + 4, 15)
        ws.column_dimensions["B"].width = 65
