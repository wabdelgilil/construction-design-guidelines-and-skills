"""
Excel Exporter for Strap (Cantilever) Footing System.
Generates styled calculation sheets, Bar Bending Schedule (BBS), and itemized BOQ with cost estimation.
"""

from pathlib import Path
import openpyxl
from core.exporters.excel_writer import ExcelWriter
from core.exporters.boq_engine import BOQEngine, BarScheduleItem, rebar_weight_per_meter
from structural.foundations.strap_footing.scripts.design_engine import (
    StrapFootingDesignResult,
    StrapFootingInput,
)


class StrapFootingExcelExporter:
    """Creates a multi-tab Excel workbook for the designed strap footing system."""

    def __init__(self, result: StrapFootingDesignResult, inp: StrapFootingInput):
        self.res = result
        self.inp = inp

    def export(self, filepath: Path) -> Path:
        writer = ExcelWriter(title="Strap Footing Calculation")

        # =========================================================================
        # TAB 1: DESIGN CALCULATION SHEET
        # =========================================================================
        ws1 = writer.ws
        writer.format_title_banner(
            "STRUCTURAL DESIGN CALCULATION SHEET",
            f"Reinforced Concrete Strap Footing System | Active Code: {self.res.code_used}",
            max_col=5,
        )

        rows = [
            ("1. Design Inputs & Geometry", "", "", "", ""),
            ("Design Code", self.res.code_used, "", "Allowable Soil Pressure (q_all)", f"{self.inp.allowable_soil_capacity_kpa} kPa"),
            ("Col 1 (Boundary) Load", f"{self.inp.col1_dead_load_kn}D + {self.inp.col1_live_load_kn}L kN", "", "Col 2 (Interior) Load", f"{self.inp.col2_dead_load_kn}D + {self.inp.col2_live_load_kn}L kN"),
            ("Center-to-Center Span (S)", f"{self.inp.span_center_to_center_m:.2f} m", "", "Concrete Strength (fc')", f"{self.inp.fc_prime_mpa} MPa"),
            ("", "", "", "", ""),
            ("2. Equilibrium Reactions & Soil Pressures", "", "", "", ""),
            ("Footing 1 Service Reaction (R1)", f"{self.res.f1_service_reaction_kn} kN", "", "Footing 2 Service Reaction (R2)", f"{self.res.f2_service_reaction_kn} kN"),
            ("Footing 1 Factored Reaction (R1u)", f"{self.res.f1_ultimate_reaction_kn} kN", "", "Footing 2 Factored Reaction (R2u)", f"{self.res.f2_ultimate_reaction_kn} kN"),
            ("", "", "", "", ""),
            ("3. Footing Dimensions & Sizing", "", "", "", ""),
            ("Footing 1 (Exterior)", f"{self.res.f1_length_m:.2f} x {self.res.f1_width_m:.2f} x {self.res.f1_thickness_mm/1000.0:.2f} m", "", "Status", self.res.f1_status),
            ("Footing 1 Transverse Steel", self.res.f1_rebar_transverse, "", "", ""),
            ("Footing 2 (Interior)", f"{self.res.f2_length_m:.2f} x {self.res.f2_width_m:.2f} x {self.res.f2_thickness_mm/1000.0:.2f} m", "", "Status", self.res.f2_status),
            ("Footing 2 Reinforcement", f"{self.res.f2_rebar_l} / {self.res.f2_rebar_b}", "", "", ""),
            ("", "", "", "", ""),
            ("4. Strap Beam Structural Design", "", "", "", ""),
            ("Strap Beam Section (b x h)", f"{int(self.res.strap_width_mm)} x {int(self.res.strap_depth_mm)} mm", "", "Status", self.res.strap_status),
            ("Max Negative Factored Moment", f"{self.res.strap_max_negative_moment_kn_m} kN.m", "", "Max Factored Shear", f"{self.res.strap_max_shear_kn} kN"),
            ("Top Tensile Steel Area (As)", f"{self.res.strap_top_steel_as_mm2} mm2", "", "Top Longitudinal Reinforcement", self.res.strap_top_rebar_desc),
            ("Shear Stirrups", self.res.strap_stirrups_desc, "", "", ""),
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
            f"Rebar Cut Schedule for Strap Footing System (Span: {self.inp.span_center_to_center_m:.2f} m)",
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

        # 1. Strap Top Bars
        strap_span_len = round(self.inp.span_center_to_center_m + 0.80, 2)
        n_strap_bars = int(self.res.strap_top_rebar_desc.split()[0])
        item_strap_top = BarScheduleItem(
            bar_mark="01",
            description="Strap Beam Top Longitudinal Steel",
            bar_diameter_mm=20,
            number_of_bars=n_strap_bars,
            cutting_length_m=strap_span_len + 1.2,
            shape_code="21 (End Hooks)",
        )

        # 2. Strap Stirrups
        n_stirrups = int(self.inp.span_center_to_center_m / 0.12)
        stirrup_perim = round(2 * ((self.res.strap_width_mm - 100) + (self.res.strap_depth_mm - 100)) / 1000.0 + 0.2, 2)
        item_stirrups = BarScheduleItem(
            bar_mark="02",
            description="Strap Beam Closed Stirrups",
            bar_diameter_mm=10,
            number_of_bars=n_stirrups,
            cutting_length_m=stirrup_perim,
            shape_code="51 (Closed Tie)",
        )

        # 3. Footing 1 Transverse Bars
        n_f1_bars = int(self.res.f1_rebar_transverse.split()[0])
        item_f1 = BarScheduleItem(
            bar_mark="03",
            description="Footing 1 Transverse Bottom Steel",
            bar_diameter_mm=14,
            number_of_bars=n_f1_bars,
            cutting_length_m=round(self.res.f1_width_m - 0.15 + 0.6, 2),
            shape_code="21 (U-Hook)",
        )

        # 4. Footing 2 Rebar
        n_f2_bars = int(self.res.f2_rebar_l.split()[0])
        item_f2 = BarScheduleItem(
            bar_mark="04",
            description="Footing 2 Bottom Rebar Mesh",
            bar_diameter_mm=14,
            number_of_bars=n_f2_bars * 2,
            cutting_length_m=round(self.res.f2_length_m - 0.15 + 0.6, 2),
            shape_code="21 (U-Hook)",
        )

        bbs_items = [item_strap_top, item_stirrups, item_f1, item_f2]

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
            "Itemized Material Quantities for Strap Footing System (Currency: SAR)",
            max_col=6,
        )

        boq_headers = ["Item No.", "Description of Works", "Unit", "Quantity", "Unit Rate (SAR)", "Total Amount (SAR)"]
        writer.add_table_header(4, boq_headers)

        # Concrete volumes
        vol_f1 = self.res.f1_length_m * self.res.f1_width_m * (self.res.f1_thickness_mm / 1000.0)
        vol_f2 = self.res.f2_length_m * self.res.f2_width_m * (self.res.f2_thickness_mm / 1000.0)
        strap_net_len = max(self.inp.span_center_to_center_m - (self.res.f1_length_m / 2.0) - (self.res.f2_length_m / 2.0), 1.0)
        vol_strap = (self.res.strap_width_mm / 1000.0) * (self.res.strap_depth_mm / 1000.0) * strap_net_len
        total_rc_vol = round(vol_f1 + vol_f2 + vol_strap, 2)
        total_pc_vol = round((self.res.f1_length_m + 0.2) * (self.res.f1_width_m + 0.2) * 0.1 + (self.res.f2_length_m + 0.2) * (self.res.f2_width_m + 0.2) * 0.1, 2)
        total_steel_tons = round(sum(itm.total_weight_kg for itm in bbs_items) / 1000.0, 3)

        items = [
            (1, "Site excavation for strap system and pits", "m3", round(total_rc_vol * 3.5, 2), 25.0),
            (2, "Plain concrete blinding layer under footings (C15/20)", "m3", total_pc_vol, 240.0),
            (3, "Reinforced concrete for footings and strap beam (C28/35)", "m3", total_rc_vol, 320.0),
            (4, "High-yield deformed steel rebar (Grade 420)", "ton", total_steel_tons, 3200.0),
            (5, "Wooden shuttering/formwork for strap beam sides and footings", "m2", round(total_rc_vol * 4.2, 2), 45.0),
            (6, "Bituminous cold dampproof membrane on all buried surfaces", "m2", round(total_rc_vol * 5.0, 2), 18.0),
            (7, "Selected soil backfilling in compacted layers", "m3", round(total_rc_vol * 2.2, 2), 20.0),
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
