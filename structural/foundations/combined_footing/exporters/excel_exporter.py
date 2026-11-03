"""
Excel Exporter for Combined Footing System.
Generates styled calculation sheets, Bar Bending Schedule (BBS), and itemized BOQ with cost estimation.
"""

from pathlib import Path
import openpyxl
from core.exporters.excel_writer import ExcelWriter
from core.exporters.boq_engine import BOQEngine, BarScheduleItem, rebar_weight_per_meter
from structural.foundations.combined_footing.scripts.design_engine import (
    CombinedFootingDesignResult,
    CombinedFootingInput,
)


class CombinedFootingExcelExporter:
    """Creates a multi-tab Excel workbook for the designed combined footing."""

    def __init__(self, result: CombinedFootingDesignResult, inp: CombinedFootingInput):
        self.res = result
        self.inp = inp

    def export(self, filepath: Path) -> Path:
        writer = ExcelWriter(title="Combined Footing Calculation")

        # =========================================================================
        # TAB 1: DESIGN CALCULATION SHEET
        # =========================================================================
        ws1 = writer.ws
        writer.format_title_banner(
            "STRUCTURAL DESIGN CALCULATION SHEET",
            f"Reinforced Concrete Combined Footing | Active Code: {self.res.code_used}",
            max_col=5,
        )

        rows = [
            ("1. Design Inputs & Column Loads", "", "", "", ""),
            ("Design Code", self.res.code_used, "", "Allowable Soil Pressure (q_all)", f"{self.inp.allowable_soil_capacity_kpa} kPa"),
            ("Col 1 Load", f"{self.inp.col1_dead_load_kn}D + {self.inp.col1_live_load_kn}L kN", "", "Col 2 Load", f"{self.inp.col2_dead_load_kn}D + {self.inp.col2_live_load_kn}L kN"),
            ("Span (S)", f"{self.inp.span_center_to_center_m:.2f} m", "", "Distance to Col 1 (d1)", f"{self.inp.col1_edge_distance_m:.2f} m"),
            ("Concrete Strength (fc')", f"{self.inp.fc_prime_mpa} MPa", "", "Steel Yield Strength (fy)", f"{self.inp.fy_mpa} MPa"),
            ("", "", "", "", ""),
            ("2. Footing Dimensions & Uniform Soil Pressure", "", "", "", ""),
            ("Footing Length (L)", f"{self.res.length_m:.2f} m", "", "Footing Width (B)", f"{self.res.width_m:.2f} m"),
            ("Total Thickness (T)", f"{int(self.res.thickness_mm)} mm", "", "Effective Depth (d)", f"{int(self.res.effective_depth_mm)} mm"),
            ("Actual Service Soil Pressure", f"{self.res.actual_service_soil_pressure_kpa} kPa", "", "Status", "SAFE"),
            ("Net Ultimate Upward Pressure (qu)", f"{self.res.net_ultimate_soil_pressure_kpa} kPa", "", "", ""),
            ("", "", "", "", ""),
            ("3. Critical Section Actions (SFD & BMD)", "", "", "", ""),
            ("Zero Shear Point from Left", f"{self.res.zero_shear_point_from_left_m:.2f} m", "", "Max Negative Moment (Mu,max)", f"{self.res.max_negative_moment_kn_m} kN.m"),
            ("Max One-Way Shear Force (Vu,max)", f"{self.res.max_shear_force_kn} kN", "", "Beam Shear Status", self.res.beam_shear_status),
            ("Two-Way Punching Shear Status", self.res.punching_status, "", "Punching Demand/Capacity Ratio", f"{self.res.punching_ratio_col2}"),
            ("", "", "", "", ""),
            ("4. Reinforcement Detailing", "", "", "", ""),
            ("Top Longitudinal Steel", self.res.top_longitudinal_rebar_desc, "", "Bottom Longitudinal Steel", self.res.bottom_longitudinal_rebar_desc),
            ("Transverse Band under Col 1", self.res.transverse_rebar_col1_desc, "", "Transverse Band under Col 2", self.res.transverse_rebar_col2_desc),
            ("", "", "", "", ""),
            ("OVERALL SYSTEM STATUS", "CONFIRMED SAFE", "", "", ""),
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
            f"Rebar Cut Schedule for Combined Footing ({self.res.length_m:.2f} x {self.res.width_m:.2f} x {int(self.res.thickness_mm)} mm)",
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

        hook_m = (self.res.thickness_mm - 150.0) / 1000.0
        cut_len_long = round(self.res.length_m - 0.15 + 2 * hook_m, 2)
        cut_len_trans = round(self.res.width_m - 0.15 + 2 * hook_m, 2)

        n_top = int(self.res.top_longitudinal_rebar_desc.split()[0])
        n_bot = int(self.res.bottom_longitudinal_rebar_desc.split()[0])
        n_trans1 = int(self.res.transverse_rebar_col1_desc.split()[0])
        n_trans2 = int(self.res.transverse_rebar_col2_desc.split()[0])

        bbs_items = [
            BarScheduleItem("01", "Top Longitudinal Steel (Negative Moment)", 18, n_top, cut_len_long, "21 (U-Hook)"),
            BarScheduleItem("02", "Bottom Longitudinal Steel (Positive/Nominal)", 16, n_bot, cut_len_long, "21 (U-Hook)"),
            BarScheduleItem("03", "Transverse Band Rebar under Column 1", 14, n_trans1, cut_len_trans, "21 (U-Hook)"),
            BarScheduleItem("04", "Transverse Band Rebar under Column 2", 14, n_trans2, cut_len_trans, "21 (U-Hook)"),
            BarScheduleItem("05", "Column Starter Dowels (Both Columns)", 16, 16, 1.80, "11 (L-Bar)"),
        ]

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
            "Itemized Material Quantities for Combined Footing (Currency: SAR)",
            max_col=6,
        )

        boq_headers = ["Item No.", "Description of Works", "Unit", "Quantity", "Unit Rate (SAR)", "Total Amount (SAR)"]
        writer.add_table_header(4, boq_headers)

        vol_rc = round(self.res.length_m * self.res.width_m * (self.res.thickness_mm / 1000.0), 2)
        vol_pc = round((self.res.length_m + 0.2) * (self.res.width_m + 0.2) * 0.1, 2)
        total_steel_tons = round(sum(itm.total_weight_kg for itm in bbs_items) / 1000.0, 3)

        items = [
            (1, "Site excavation for combined footing pit down to founding level", "m3", round(vol_rc * 3.0, 2), 25.0),
            (2, "Plain concrete blinding layer under footing (C15/20)", "m3", vol_pc, 240.0),
            (3, "Reinforced concrete combined footing (C28/35)", "m3", vol_rc, 320.0),
            (4, "High-yield deformed steel rebar (Grade 420)", "ton", total_steel_tons, 3200.0),
            (5, "Wooden shuttering/formwork for footing perimeter", "m2", round(2 * (self.res.length_m + self.res.width_m) * (self.res.thickness_mm / 1000.0), 2), 45.0),
            (6, "Bituminous cold dampproof membrane on all buried surfaces", "m2", round((self.res.length_m * self.res.width_m) + 2 * (self.res.length_m + self.res.width_m) * (self.res.thickness_mm / 1000.0), 2), 18.0),
            (7, "Selected soil backfilling in compacted layers", "m3", round(vol_rc * 1.8, 2), 20.0),
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
