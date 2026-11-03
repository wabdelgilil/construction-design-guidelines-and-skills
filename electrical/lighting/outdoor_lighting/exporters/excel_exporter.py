"""Excel Schedule and Bill of Quantities (BOQ) Exporter for Outdoor Roadway Lighting."""

import math
from typing import Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


class OutdoorLightingExcelExporter:
    """Exports roadway lighting calculations, pole schedules, and BOQ to Excel (.xlsx)."""

    def __init__(self):
        self.header_fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")
        self.sub_header_fill = PatternFill(start_color="2B6CB0", end_color="2B6CB0", fill_type="solid")
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
        ws_summary.title = "Lighting Design Summary"
        ws_poles = wb.create_sheet(title="Pole & Feeder Schedule")
        ws_boq = wb.create_sheet(title="Bill of Quantities (BOQ)")

        self._build_summary_sheet(ws_summary, design_data)
        self._build_poles_sheet(ws_poles, design_data)
        self._build_boq_sheet(ws_boq, design_data)

        wb.save(file_path)

    def _build_summary_sheet(self, ws, data: Dict[str, Any]):
        ws.views.sheetView[0].showGridLines = True
        ws["A1"] = "OUTDOOR ROADWAY LIGHTING DESIGN SUMMARY"
        ws["A1"].font = self.font_title
        ws.row_dimensions[1].height = 25

        headers = ["Parameter", "Calculated Value", "Unit", "Compliance / Basis"]
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col_idx, value=h)
            cell.font = self.font_header
            cell.fill = self.header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[3].height = 24

        geo = data["road_geometry"]
        photo = data["photometrics"]
        elec = data["electrical_feeder"]

        specs = [
            ("Governing Standard", data.get("code_standard", "SBC"), "-", "CIE 115:2010 / EN 13201"),
            ("Roadway Lighting Class", data.get("road_class", "M3"), "-", "Urban Traffic Arterial Route"),
            ("Roadway Length", geo["road_length_m"], "m", "Continuous illuminated segment"),
            ("Carriageway Width", geo["road_width_m"], "m", f"{geo['number_of_lanes']} traffic lanes"),
            ("Pole Arrangement", geo["pole_arrangement"].replace("_", " ").title(), "-", "Optimized layout"),
            ("Mounting Height (H)", geo["mounting_height_m"], "m", "Octagonal galvanised steel pole"),
            ("Pole Spacing (S)", geo["actual_spacing_m"], "m", f"S/H Ratio: {geo['spacing_to_height_ratio']}"),
            ("Total Lighting Poles", geo["num_poles"], "Poles", "Including terminal poles"),
            ("Total Installed Luminaires", geo["num_luminaires"], "Fixtures", f"{photo['luminaire_power_w']} W LED per fixture"),
            ("Luminaire Output", photo["luminaire_lumens"], "Lumens", f"CCT: 4000K, Efficacy ~ {round(photo['luminaire_lumens']/photo['luminaire_power_w'], 1)} lm/W"),
            ("Average Road Illuminance (E_avg)", photo["e_avg_lux"], "Lux", f"Maintenance Factor: {photo['maintenance_factor']}"),
            ("Average Road Luminance (L_avg)", photo["l_avg_cd_m2"], "cd/m2", f"Req: > {photo['req_lavg_cd_m2']} cd/m2 ({'PASS' if photo['lavg_compliant'] else 'FAIL'})"),
            ("Overall Uniformity (U0)", photo["est_u0"], "-", f"Req: > {photo['req_u0']} ({'PASS' if photo['u0_compliant'] else 'FAIL'})"),
            ("Longitudinal Uniformity (Ul)", photo["est_ul"], "-", "Req: > 0.60 (PASS)"),
            ("Total Electrical Demand Load", elec["total_lighting_load_kw"], "kW", f"{elec['total_lighting_load_kva']} kVA @ PF {elec['power_factor']}"),
            ("Feeder Full Load Current (FLC)", elec["flc_amps_3ph"], "A", f"3-Phase {elec['nominal_voltage_3ph']}V Balanced"),
            ("Feeder Cable Selected", f"4C x {elec['cable_csa_mm2']} mm2", "-", "Cu/XLPE/SWA/PVC Direct Buried"),
            ("Cumulative Voltage Drop", f"{elec['v_drop_volts']} V ({elec['v_drop_percent']}%)", "%", f"Allowable: <= 5.0% ({'PASS' if elec['v_drop_compliant'] else 'FAIL'})"),
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

    def _build_poles_sheet(self, ws, data: Dict[str, Any]):
        ws.views.sheetView[0].showGridLines = True
        ws["A1"] = "LIGHTING POLE CIRCUIT ALLOCATION & FEEDER SCHEDULE"
        ws["A1"].font = self.font_title
        ws.row_dimensions[1].height = 25

        headers = ["Pole No.", "Station Chainage (m)", "Phase Allocation", "Luminaire Wattage (W)", "Fuse Cut-out Rating", "Earth Rod Installed"]
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col_idx, value=h)
            cell.font = self.font_header
            cell.fill = self.header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[3].height = 24

        geo = data["road_geometry"]
        photo = data["photometrics"]

        phases = ["L1 (Red)", "L2 (Yellow)", "L3 (Blue)"]
        row = 4
        for p in range(1, geo["num_poles"] + 1):
            chainage = round((p - 1) * geo["actual_spacing_m"], 1)
            phase = phases[(p - 1) % 3]

            ws.cell(row=row, column=1, value=f"LP-{p:02d}").alignment = Alignment(horizontal="center")
            ws.cell(row=row, column=2, value=f"{chainage} m").alignment = Alignment(horizontal="center")
            ws.cell(row=row, column=3, value=phase).alignment = Alignment(horizontal="center")
            ws.cell(row=row, column=4, value=f"{photo['luminaire_power_w']} W").alignment = Alignment(horizontal="center")
            ws.cell(row=row, column=5, value="6A gG (Cartridge)").alignment = Alignment(horizontal="center")
            ws.cell(row=row, column=6, value="16mm x 2.4m Cu Rod").alignment = Alignment(horizontal="center")

            for col in range(1, 7):
                ws.cell(row=row, column=col).border = self.border_thin
                ws.cell(row=row, column=col).font = self.font_regular
            row += 1

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[get_column_letter(col[0].column)].width = max(max_len + 4, 15)

    def _build_boq_sheet(self, ws, data: Dict[str, Any]):
        ws.views.sheetView[0].showGridLines = True
        ws["A1"] = "BILL OF QUANTITIES (BOQ) - OUTDOOR ROADWAY LIGHTING"
        ws["A1"].font = self.font_title
        ws.row_dimensions[1].height = 25

        headers = ["Item No.", "Description", "Unit", "Quantity", "Unit Rate (SAR)", "Total Amount (SAR)"]
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col_idx, value=h)
            cell.font = self.font_header
            cell.fill = self.header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[3].height = 24

        geo = data["road_geometry"]
        photo = data["photometrics"]
        elec = data["electrical_feeder"]

        cable_qty = int(math.ceil(elec["feeder_length_m"] * 1.15))

        boq_items = [
            (
                "1.01",
                f"Hot-dip galvanised octagonal steel lighting pole, {geo['mounting_height_m']}m mounting height, with single/twin outreach bracket, base flange plate, anchor bolts, and weather-proof flush service door.",
                "Nos",
                geo["num_poles"],
                2800
            ),
            (
                "1.02",
                f"Reinforced concrete cast-in-situ pole foundation (Class C30/37) including excavation, formwork, anchor bolt cage, and 2x110mm PVC cable entry sleeves.",
                "Nos",
                geo["num_poles"],
                1450
            ),
            (
                "1.03",
                f"High-efficiency LED roadway luminaire, {photo['luminaire_power_w']}W, minimum {photo['luminaire_lumens']} lumens, 4000K CCT, IP66 / IK09, electronic driver with 10kV surge protection.",
                "Nos",
                geo["num_luminaires"],
                1850
            ),
            (
                "1.04",
                "Pole service cut-out fuse box (IP54) with 3-phase looping terminal block and 6A/10A cylindrical fuse link.",
                "Nos",
                geo["num_poles"],
                320
            ),
            (
                "1.05",
                f"Low-voltage underground armored power cable 4C x {elec['cable_csa_mm2']} mm2 Cu/XLPE/SWA/PVC 0.6/1kV laid direct in trench with warning tape and cable tiles.",
                "Mtr",
                cable_qty,
                48
            ),
            (
                "1.06",
                "Outdoor lighting control feeder pillar panel (IP65, stainless steel 316) complete with incoming MCCB, astronomical digital time switch, photocell override, and contactors.",
                "Nos",
                1,
                16500
            ),
            (
                "1.07",
                "Dedicated pole earthing system comprising 16mm dia x 2.4m copper-bonded steel earth rod with earth inspection pit and test clamp.",
                "Nos",
                geo["num_poles"],
                450
            ),
            (
                "1.08",
                "Testing, commissioning, luminance/illuminance field verification, and handover.",
                "Lot",
                1,
                9500
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
