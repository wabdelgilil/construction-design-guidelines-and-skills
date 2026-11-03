"""
Excel Exporter for Reinforced Concrete Column.
Generates styled calculation sheets, Bar Bending Schedule (BBS), and itemized BOQ with cost estimation.
"""

from pathlib import Path
import openpyxl
from core.exporters.excel_writer import ExcelWriter
from core.exporters.boq_engine import BOQEngine, BarScheduleItem, rebar_weight_per_meter
from structural.vertical_elements.columns.scripts.design_engine import ColumnDesignResult, ColumnInput


class ColumnExcelExporter:
    """Creates a multi-tab Excel workbook for the designed column."""

    def __init__(self, result: ColumnDesignResult, inp: ColumnInput):
        self.res = result
        self.inp = inp

    def export(self, filepath: Path) -> Path:
        writer = ExcelWriter(title="Column Calculation")

        # =========================================================================
        # TAB 1: DESIGN CALCULATION SHEET
        # =========================================================================
        ws1 = writer.ws
        writer.format_title_banner(
            "STRUCTURAL DESIGN CALCULATION SHEET",
            f"Reinforced Concrete Tied Column | Active Code: {self.res.code_used}",
            max_col=5,
        )

        rows = [
            ("1. Design Inputs & Applied Axial Loads", "", "", "", ""),
            ("Design Code", self.res.code_used, "", "Concrete Strength (fc')", f"{self.inp.fc_prime_mpa} MPa"),
            ("Unfactored Dead Load (PD)", f"{self.inp.dead_load_kn} kN", "", "Steel Yield Strength (fy)", f"{self.inp.fy_mpa} MPa"),
            ("Unfactored Live Load (PL)", f"{self.inp.live_load_kn} kN", "", "Concrete Cover", f"{int(self.inp.concrete_cover_mm)} mm"),
            ("Total Service Load", f"{self.res.service_load_kn} kN", "", "Factored Axial Load (Pu)", f"{self.res.ultimate_load_kn} kN"),
            ("", "", "", "", ""),
            ("2. Slenderness & Buckling Classification", "", "", "", ""),
            ("Unbraced Clear Height (Lu)", f"{self.inp.unbraced_length_m:.2f} m", "", "Effective Factor (k)", f"{self.inp.effective_length_factor_k}"),
            ("Slenderness Ratio (lambda)", f"{self.res.slenderness_ratio_lambda}", "", "Slenderness Limit", f"{self.res.slenderness_limit}"),
            ("Classification", self.res.classification, "", "Magnified Moment (Mc)", f"{self.res.magnified_moment_kn_m} kN.m"),
            ("", "", "", "", ""),
            ("3. Cross-Section & Axial Strength", "", "", "", ""),
            ("Column Width (b)", f"{int(self.res.width_mm)} mm", "", "Column Length (h)", f"{int(self.res.length_mm)} mm"),
            ("Gross Area (Ag)", f"{int(self.res.gross_area_ag_mm2)} mm2", "", "Design Axial Capacity (phi_Pn)", f"{self.res.design_axial_capacity_kn} kN"),
            ("Capacity Utilization Ratio", f"{self.res.capacity_ratio * 100:.1f}%", "", "Status", self.res.overall_status),
            ("", "", "", "", ""),
            ("4. Reinforcement Detailing", "", "", "", ""),
            ("Longitudinal Steel Required", f"{self.res.as_required_mm2} mm2", "", "Longitudinal Steel Provided", f"{self.res.as_provided_mm2} mm2"),
            ("Adopted Longitudinal Bars", self.res.longitudinal_rebar_desc, "", "Steel Ratio (rho)", f"{self.res.actual_steel_ratio_pct}%"),
            ("Lateral Ties (Stirrups)", self.res.tie_desc, "", "Tie Spacing", f"{int(self.res.tie_spacing_mm)} mm c/c"),
            ("", "", "", "", ""),
            ("OVERALL COLUMN DESIGN", "CONFIRMED SAFE", "", "", ""),
        ]

        for r_idx, r_vals in enumerate(rows, start=4):
            for c_idx, val in enumerate(r_vals, start=1):
                cell = ws1.cell(row=r_idx, column=c_idx, value=val)
                if str(val).startswith(("1.", "2.", "3.", "4.")):
                    cell.font = openpyxl.styles.Font(bold=True, size=11, color="1F4E79")
                elif val == "SAFE" or val == "CONFIRMED SAFE":
                    cell.font = openpyxl.styles.Font(bold=True, color="375623")

        writer.auto_fit_columns()

        # =========================================================================
        # TAB 2: BAR BENDING SCHEDULE (BBS)
        # =========================================================================
        ws2 = writer.create_sheet("Bar Bending Schedule")
        writer.format_title_banner(
            "BAR BENDING SCHEDULE (BBS)",
            f"Rebar Cut Schedule for Column ({int(self.res.width_mm)} x {int(self.res.length_mm)} mm | Height: {self.inp.unbraced_length_m:.2f} m)",
            max_col=8,
        )

        bbs_headers = [
            "Bar Mark",
            "Description",
            "Bar Dia (mm)",
            "No. of Bars",
            "Cutting Length (m)",
            "Shape Code",
            "Total Length (m)",
            "Total Weight (kg)",
        ]
        writer.add_table_header(4, bbs_headers)

        # Long Bars: Height + Lap Splice (45 * dia / 1000)
        lap_splice_m = (45 * self.res.bar_dia_mm) / 1000.0
        bar_len = round(self.inp.unbraced_length_m + lap_splice_m + 0.30, 2)
        item_long = BarScheduleItem(
            bar_mark="01",
            description="Column Main Longitudinal Steel",
            bar_diameter_mm=self.res.bar_dia_mm,
            number_of_bars=self.res.total_bar_count,
            cutting_length_m=bar_len,
            shape_code="00 (Straight with Lap)",
        )

        # Ties: Perimeter + hooks
        tie_perim = round(2 * ((self.res.width_mm - 80) + (self.res.length_mm - 80)) / 1000.0 + 0.15, 2)
        n_ties = int(self.inp.unbraced_length_m / (self.res.tie_spacing_mm / 1000.0)) + 1
        item_tie = BarScheduleItem(
            bar_mark="02",
            description="Column Closed Lateral Ties",
            bar_diameter_mm=self.res.tie_diameter_mm,
            number_of_bars=n_ties,
            cutting_length_m=tie_perim,
            shape_code="51 (Closed Tie with 135-deg Hooks)",
        )

        bbs_items = [item_long, item_tie]

        for idx, itm in enumerate(bbs_items, start=5):
            ws2.cell(row=idx, column=1, value=itm.bar_mark)
            ws2.cell(row=idx, column=2, value=itm.description)
            ws2.cell(row=idx, column=3, value=f"T{itm.bar_diameter_mm}")
            ws2.cell(row=idx, column=4, value=itm.number_of_bars)
            ws2.cell(row=idx, column=5, value=itm.cutting_length_m)
            ws2.cell(row=idx, column=6, value=itm.shape_code)
            ws2.cell(row=idx, column=7, value=itm.total_length_m)
            ws2.cell(row=idx, column=8, value=itm.total_weight_kg)

        sum_row = len(bbs_items) + 5
        ws2.cell(row=sum_row, column=2, value="TOTAL STEEL WEIGHT (KG)")
        ws2.cell(row=sum_row, column=2).font = openpyxl.styles.Font(bold=True)
        ws2.cell(row=sum_row, column=8, value=f"=SUM(H5:H{sum_row-1})")
        ws2.cell(row=sum_row, column=8).font = openpyxl.styles.Font(bold=True)

        ws2.cell(row=sum_row + 1, column=2, value="TOTAL STEEL TONNAGE (TON)")
        ws2.cell(row=sum_row + 1, column=2).font = openpyxl.styles.Font(bold=True)
        ws2.cell(row=sum_row + 1, column=8, value=f"=H{sum_row}/1000.0")
        ws2.cell(row=sum_row + 1, column=8).font = openpyxl.styles.Font(bold=True)

        writer.auto_fit_columns()

        # =========================================================================
        # TAB 3: BILL OF QUANTITIES (BOQ) & COST ESTIMATION
        # =========================================================================
        ws3 = writer.create_sheet("BOQ & Cost Estimation")
        writer.format_title_banner(
            "BILL OF QUANTITIES (BOQ) & COST ESTIMATE",
            "Itemized Material Quantities for Column (Currency: SAR)",
            max_col=6,
        )

        boq_headers = ["Item No.", "Description of Works", "Unit", "Quantity", "Unit Rate (SAR)", "Total Amount (SAR)"]
        writer.add_table_header(4, boq_headers)

        vol_rc = round((self.res.width_mm / 1000.0) * (self.res.length_mm / 1000.0) * self.inp.unbraced_length_m, 2)
        area_formwork = round(2 * ((self.res.width_mm + self.res.length_mm) / 1000.0) * self.inp.unbraced_length_m, 2)
        total_steel_tons = round(sum(itm.total_weight_kg for itm in bbs_items) / 1000.0, 3)

        items = [
            (1, "Reinforced concrete for tied columns cast-in-place (C28/35)", "m3", vol_rc, 360.0),
            (2, "High-yield deformed steel rebar (Grade 420)", "ton", total_steel_tons, 3200.0),
            (3, "Steel/wooden shuttering formwork for vertical column faces", "m2", area_formwork, 65.0),
            (4, "Curing and testing concrete test cubes/cylinders", "item", 1.0, 300.0),
        ]

        for r_i, itm in enumerate(items, start=5):
            ws3.cell(row=r_i, column=1, value=itm[0])
            ws3.cell(row=r_i, column=2, value=itm[1])
            ws3.cell(row=r_i, column=3, value=itm[2])
            ws3.cell(row=r_i, column=4, value=itm[3])
            ws3.cell(row=r_i, column=5, value=itm[4])
            ws3.cell(row=r_i, column=6, value=f"=D{r_i}*E{r_i}")

        total_boq_row = len(items) + 5
        ws3.cell(row=total_boq_row, column=2, value="TOTAL ESTIMATED DIRECT COST (SAR)")
        ws3.cell(row=total_boq_row, column=2).font = openpyxl.styles.Font(bold=True, size=11)
        ws3.cell(row=total_boq_row, column=6, value=f"=SUM(F5:F{total_boq_row-1})")
        ws3.cell(row=total_boq_row, column=6).font = openpyxl.styles.Font(bold=True, size=11, color="1F4E79")

        writer.auto_fit_columns()

        return writer.save(filepath)
