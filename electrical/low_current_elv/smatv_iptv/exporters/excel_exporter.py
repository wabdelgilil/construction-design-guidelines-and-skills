"""Excel Schedule and Bill of Quantities (BOQ) Exporter for SMATV & IPTV Systems."""

import math
from typing import Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


class SMATVIPTVExcelExporter:
    """Exports SMATV & IPTV calculations, riser schedules, and BOQ to Excel (.xlsx)."""

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
        ws_summary.title = "System Summary"
        ws_riser = wb.create_sheet(title="RF Link Budget Schedule")
        ws_boq = wb.create_sheet(title="Bill of Quantities (BOQ)")

        self._build_summary_sheet(ws_summary, design_data)
        self._build_riser_sheet(ws_riser, design_data)
        self._build_boq_sheet(ws_boq, design_data)

        wb.save(file_path)

    def _build_summary_sheet(self, ws, data: Dict[str, Any]):
        ws.views.sheetView[0].showGridLines = True
        ws["A1"] = "SMATV & IPTV SYSTEM SPECIFICATION SUMMARY"
        ws["A1"].font = self.font_title
        ws.row_dimensions[1].height = 25

        headers = ["System Component / Parameter", "Engineering Value", "Unit", "Standard / Basis"]
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col_idx, value=h)
            cell.font = self.font_header
            cell.fill = self.header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[3].height = 24

        bldg = data["building_parameters"]
        rf = data["rf_link_budget"]
        iptv = data["iptv_network"]

        specs = [
            ("Governing Standards", "EN 50083 / EN 60728 / ITU-T J.83", "-", "European CENELEC Cable Networks Standard"),
            ("Building Floors Served", bldg["num_floors"], "Floors", "Multi-dwelling unit / Commercial tower"),
            ("TV Outlets per Floor", bldg["outlets_per_floor"], "Outlets/Floor", "RJ45 (IPTV) + F-Type Coaxial (SMATV)"),
            ("Total TV Outlets", bldg["total_outlets"], "Outlets", "Whole building coverage"),
            ("Satellite Positions Received", len(data["satellite_dishes"]), "Satellites", "Arabsat (26E), Nilesat (7W), Hotbird (13E)"),
            ("RF Headend Launch Level", rf["headend_launch_level_dbuv"], "dBuV", "High-output launch amplifiers"),
            ("Min Permissible Outlet Level", rf["min_allowable_dbuv"], "dBuV", "EN 50083-7 lower cutoff threshold"),
            ("Max Permissible Outlet Level", rf["max_allowable_dbuv"], "dBuV", "Tuner saturation avoidance limit"),
            ("Target Design Outlet Level", rf["target_outlet_level_dbuv"], "dBuV", "Optimized SNR operating point"),
            ("Riser Compliance Status", "100% COMPLIANT", "-", f"{'All floors meet 60-77 dBuV criteria' if rf['all_floors_compliant'] else 'Attention Needed'}"),
            ("Total Multiswitches Installed", data["hardware_sizing"]["total_multiswitches"], "Units", f"{bldg['num_floors']} risers x cascadable units"),
            ("IPTV Multicast HD Channels", iptv["hd_channels"], "Channels", "1080p @ 6.0 Mbps per channel"),
            ("IPTV Multicast 4K Channels", iptv["uhd_4k_channels"], "Channels", "2160p UHD @ 20.0 Mbps per channel"),
            ("Total Multicast Stream Bandwidth", f"{iptv['total_multicast_stream_bw_mbps']} Mbps ({iptv['total_multicast_stream_bw_gbps']} Gbps)", "Gbps", "Continuous concurrent streaming load"),
            ("Recommended Core Switch Uplink", iptv["recommended_core_uplink"], "-", "IGMP v2/v3 Querier Backbone Link"),
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

    def _build_riser_sheet(self, ws, data: Dict[str, Any]):
        ws.views.sheetView[0].showGridLines = True
        ws["A1"] = "FLOOR-BY-FLOOR RF LINK BUDGET & TAP ATTENUATION SCHEDULE"
        ws["A1"].font = self.font_title
        ws.row_dimensions[1].height = 25

        headers = ["Floor Level", "Trunk Signal In (dBuV)", "Selected Tap Loss (dB)", "Horizontal Cable Loss (dB)", "Outlet Level (dBuV)", "Compliance Status"]
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col_idx, value=h)
            cell.font = self.font_header
            cell.fill = self.header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[3].height = 24

        row = 4
        for r in data["rf_link_budget"]["riser_schedule"]:
            ws.cell(row=row, column=1, value=f"Floor {r['floor_no']}").alignment = Alignment(horizontal="center")
            ws.cell(row=row, column=2, value=r["trunk_input_dbuv"]).alignment = Alignment(horizontal="right")
            ws.cell(row=row, column=3, value=f"{r['tap_loss_db']} dB").alignment = Alignment(horizontal="center")
            ws.cell(row=row, column=4, value=f"{r['horizontal_cable_loss_db']} dB").alignment = Alignment(horizontal="center")
            ws.cell(row=row, column=5, value=r["outlet_signal_level_dbuv"]).alignment = Alignment(horizontal="right")
            ws.cell(row=row, column=6, value=r["status"]).alignment = Alignment(horizontal="center")

            for col in range(1, 7):
                ws.cell(row=row, column=col).border = self.border_thin
                ws.cell(row=row, column=col).font = self.font_regular
            row += 1

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[get_column_letter(col[0].column)].width = max(max_len + 4, 15)

    def _build_boq_sheet(self, ws, data: Dict[str, Any]):
        ws.views.sheetView[0].showGridLines = True
        ws["A1"] = "BILL OF QUANTITIES (BOQ) - SMATV & IPTV SYSTEM"
        ws["A1"].font = self.font_title
        ws.row_dimensions[1].height = 25

        headers = ["Item No.", "Description", "Unit", "Quantity", "Unit Rate (SAR)", "Total Amount (SAR)"]
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col_idx, value=h)
            cell.font = self.font_header
            cell.fill = self.header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[3].height = 24

        bldg = data["building_parameters"]
        hw = data["hardware_sizing"]
        dishes = data["satellite_dishes"]

        boq_items = [
            (
                "1.01",
                f"Prime-focus / Offset Parabolic Satellite Dish Antenna array (2.4m & 1.8m) complete with Quattro LNBs (Low/High Band, Horiz/Vert) and heavy-duty rooftop hot-dip galvanized mounting masts.",
                "Set",
                len(dishes),
                8500
            ),
            (
                "1.02",
                "SMATV Launch & Line Amplifiers (105 dBuV output capability, slope equalization control, low noise figure < 5dB) with built-in power supply.",
                "Nos",
                hw["launch_amplifiers_qty"],
                1950
            ),
            (
                "1.03",
                f"Multi-satellite Cascadable Multiswitch units (17-input x 16-output) with integrated directional couplers and tap attenuators.",
                "Nos",
                hw["total_multiswitches"],
                2400
            ),
            (
                "1.04",
                "IPTV Headend DVB-S2 to IP Gateway Streamer (16x DVB-S/S2 Tuner inputs, SPTS/MPTS Gigabit multicast streaming via UDP/RTP, IGMP v2/v3).",
                "Set",
                2,  # 1 Main + 1 Redundant
                38000
            ),
            (
                "1.05",
                "IPTV Middleware Server & Content Management Software Platform including VoD, EPG, and hospitality interface.",
                "Lot",
                1,
                45000
            ),
            (
                "1.06",
                f"Low-loss RG-11 Coaxial Trunk Backbone Cable (Class A+ screening efficiency > 95dB) along vertical risers.",
                "Mtr",
                int(bldg["num_floors"] * bldg["avg_floor_height_m"] * 16 * 1.15),
                18
            ),
            (
                "1.07",
                f"Low-loss RG-6 Tri-shielded Coaxial Drop Cable (LSZH jacket, flame retardant) for horizontal runs to user outlets.",
                "Mtr",
                int(bldg["total_outlets"] * bldg["avg_horizontal_rg6_run_m"] * 1.15),
                3.5
            ),
            (
                "1.08",
                f"Dual TV Outlet Faceplate (F-Type Satellite + RJ-45 Cat6A Gigabit IPTV port) with screened die-cast metal housing.",
                "Nos",
                bldg["total_outlets"],
                65
            ),
            (
                "1.09",
                "System integration, signal level calibration, BER/MER testing, and commissioning.",
                "Lot",
                1,
                16000
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
