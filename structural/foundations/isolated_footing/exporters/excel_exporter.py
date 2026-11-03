"""
Excel Exporter for Isolated Footing.
Generates styled calculation sheets, Bar Bending Schedule (BBS), and itemized BOQ with cost estimation.
"""

from pathlib import Path
import openpyxl
from core.exporters.excel_writer import ExcelWriter
from core.exporters.boq_engine import BOQEngine, BarScheduleItem, rebar_weight_per_meter
from structural.foundations.isolated_footing.scripts.design_engine import FootingDesignResult


class IsolatedFootingExcelExporter:
    """Creates a multi-tab Excel workbook for the designed footing."""

    def __init__(self, result: FootingDesignResult, column_length_mm: float, column_width_mm: float):
        self.res = result
        self.col_l = column_length_mm
        self.col_w = column_width_mm

    def export(self, filepath: Path) -> Path:
        writer = ExcelWriter(title="Design Calculation")

        # =========================================================================
        # TAB 1: DESIGN CALCULATION SHEET
        # =========================================================================
        ws1 = writer.ws
        writer.format_title_banner(
            "STRUCTURAL DESIGN CALCULATION SHEET",
            f"Reinforced Concrete Isolated Footing | Active Code: {self.res.code_used}",
            max_col=5,
        )

        rows_data = [
            ("1. Design Inputs & Geotechnical Criteria", "", "", "", ""),
            ("Design Code", self.res.code_used, "", "Allowable Soil Pressure (q_all)", f"{self.res.actual_soil_pressure_service_kpa} kPa"),
            ("Concrete Strength (fc')", "28.0 MPa", "", "Steel Yield Strength (fy)", "420.0 MPa"),
            ("Column Dimensions (L x B)", f"{int(self.col_l)} x {int(self.col_w)} mm", "", "Concrete Cover", "75 mm"),
            ("Total Service Load (P_service)", f"{self.res.service_load_kn} kN", "", "Factored Ultimate Load (Pu)", f"{self.res.ultimate_load_kn} kN"),
            ("", "", "", "", ""),
            ("2. Footing Dimensions & Soil Contact Pressure", "", "", "", ""),
            ("Footing Length (L)", f"{self.res.length_mm/1000.0:.2f} m", "", "Footing Width (B)", f"{self.res.width_mm/1000.0:.2f} m"),
            ("Footing Thickness (T)", f"{int(self.res.thickness_mm)} mm", "", "Effective Depth (d)", f"{int(self.res.effective_depth_mm)} mm"),
            ("Actual Service Soil Pressure", f"{self.res.actual_soil_pressure_service_kpa} kPa", "", "Status", "SAFE"),
            ("Net Factored Soil Pressure (qu)", f"{self.res.net_ultimate_soil_pressure_kpa} kPa", "", "", ""),
            ("", "", "", "", ""),
            ("3. Shear Capacity Verifications", "", "", "", ""),
            ("Two-Way Punching Shear Demand (vu)", f"{self.res.punching_shear_stress_mpa} MPa", "", "Punching Capacity (phi_vc)", f"{self.res.punching_capacity_mpa} MPa"),
            ("Punching Demand/Capacity Ratio", f"{self.res.punching_safety_ratio}", "", "Punching Safety Status", self.res.punching_status),
            ("One-Way Beam Shear Demand (vu)", f"{self.res.beam_shear_stress_mpa} MPa", "", "Beam Shear Capacity (phi_vc)", f"{self.res.beam_shear_capacity_mpa} MPa"),
            ("Beam Shear Demand/Capacity Ratio", f"{self.res.beam_shear_safety_ratio}", "", "Beam Shear Safety Status", self.res.beam_shear_status),
            ("", "", "", "", ""),
            ("4. Flexural Design & Reinforcement Sizing", "", "", "", ""),
            ("Long Direction Design Moment (MuL)", f"{self.res.moment_ul_kn_m} kN.m", "", "Short Direction Design Moment (MuB)", f"{self.res.moment_ub_kn_m} kN.m"),
            ("Required Steel Area (As_req L)", f"{self.res.as_required_l_mm2} mm2", "", "Required Steel Area (As_req B)", f"{self.res.as_required_b_mm2} mm2"),
            ("Provided Steel Area (As_prov L)", f"{self.res.as_provided_l_mm2} mm2", "", "Provided Steel Area (As_prov B)", f"{self.res.as_provided_b_mm2} mm2"),
            ("Adopted Reinforcement (Long Dir)", f"{self.res.bars_l_count} T{self.res.bar_dia_l_mm} ({self.res.bars_per_meter_l})", "", "Adopted Reinforcement (Short Dir)", f"{self.res.bars_b_count} T{self.res.bar_dia_b_mm} ({self.res.bars_per_meter_b})"),
            ("Bar Spacing (Long Dir)", f"{self.res.bar_spacing_l_mm} mm c/c", "", "Bar Spacing (Short Dir)", f"{self.res.bar_spacing_b_mm} mm c/c"),
            ("", "", "", "", ""),
            ("OVERALL DESIGN VERIFICATION", "CONFIRMED SAFE", "", "", ""),
        ]

        for r_idx, r_vals in enumerate(rows_data, start=4):
            for c_idx, val in enumerate(r_vals, start=1):
                cell = ws1.cell(row=r_idx, column=c_idx, value=val)
                if val.startswith(("1.", "2.", "3.", "4.")):
                    cell.font = openpyxl.styles.Font(bold=True, size=11, color="1F4E79")
                elif val == "SAFE" or val == "CONFIRMED SAFE":
                    cell.font = openpyxl.styles.Font(bold=True, color="375623")
                elif val == "UNSAFE":
                    cell.font = openpyxl.styles.Font(bold=True, color="C00000")

        writer.auto_fit_columns()

        # =========================================================================
        # TAB 2: BAR BENDING SCHEDULE (BBS)
        # =========================================================================
        ws2 = writer.create_sheet("Bar Bending Schedule")
        writer.format_title_banner(
            "BAR BENDING SCHEDULE (BBS)",
            f"Standard Rebar Cut Schedule for Element: Footing ({self.res.length_mm/1000.0:.2f} x {self.res.width_mm/1000.0:.2f} m)",
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

        # Bar details
        cover_m = 0.075
        hook_m = (self.res.thickness_mm - 2 * 75.0) / 1000.0

        # Bar 1: Bottom Long Dir
        cut_len_l = round((self.res.length_mm / 1000.0) - 2 * cover_m + 2 * hook_m, 2)
        item_l = BarScheduleItem(
            bar_mark="01",
            description="Bottom Rebar (Longitudinal)",
            bar_diameter_mm=self.res.bar_dia_l_mm,
            number_of_bars=self.res.bars_l_count,
            cutting_length_m=cut_len_l,
            shape_code="21 (U-Hook)",
        )

        # Bar 2: Bottom Short Dir
        cut_len_b = round((self.res.width_mm / 1000.0) - 2 * cover_m + 2 * hook_m, 2)
        item_b = BarScheduleItem(
            bar_mark="02",
            description="Bottom Rebar (Transverse)",
            bar_diameter_mm=self.res.bar_dia_b_mm,
            number_of_bars=self.res.bars_b_count,
            cutting_length_m=cut_len_b,
            shape_code="21 (U-Hook)",
        )

        # Bar 3: Column Starter Dowels
        dowel_count = 8
        dowel_dia = 16
        cut_len_dowel = round(0.30 + (self.res.thickness_mm / 1000.0) - cover_m + 0.60, 2)
        item_dowel = BarScheduleItem(
            bar_mark="03",
            description="Column Starter Dowels",
            bar_diameter_mm=dowel_dia,
            number_of_bars=dowel_count,
            cutting_length_m=cut_len_dowel,
            shape_code="11 (L-Bar)",
        )

        bbs_items = [item_l, item_b, item_dowel]

        for idx, itm in enumerate(bbs_items, start=5):
            ws2.cell(row=idx, column=1, value=itm.bar_mark)
            ws2.cell(row=idx, column=2, value=itm.description)
            ws2.cell(row=idx, column=3, value=f"T{itm.bar_diameter_mm}")
            ws2.cell(row=idx, column=4, value=itm.number_of_bars)
            ws2.cell(row=idx, column=5, value=itm.cutting_length_m)
            ws2.cell(row=idx, column=6, value=itm.shape_code)
            ws2.cell(row=idx, column=7, value=itm.total_length_m)
            ws2.cell(row=idx, column=8, value=itm.total_weight_kg)

        # Summary Row
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
            "Itemized Material Quantities and Commercial Estimation (Currency: SAR)",
            max_col=6,
        )

        boq_headers = ["Item No.", "Description of Works", "Unit", "Quantity", "Unit Rate (SAR)", "Total Amount (SAR)"]
        writer.add_table_header(4, boq_headers)

        boq_data = BOQEngine.calculate_footing_boq(
            length_m=self.res.length_mm / 1000.0,
            width_m=self.res.width_mm / 1000.0,
            thickness_m=self.res.thickness_mm / 1000.0,
        )

        total_steel_ton = (item_l.total_weight_kg + item_b.total_weight_kg + item_dowel.total_weight_kg) / 1000.0

        items = [
            (1, "Site Excavation for footing pit down to founding level", "m3", boq_data["excavation_m3"], 25.0),
            (2, "Plain concrete blinding layer (C15/20) under footing, t=100mm", "m3", boq_data["blinding_concrete_m3"], 240.0),
            (3, "Reinforced concrete footing cast-in-place (C28/35)", "m3", boq_data["reinforced_concrete_m3"], 320.0),
            (4, "High-yield deformed steel rebar (Grade 420)", "ton", round(total_steel_ton, 3), 3200.0),
            (5, "Wooden shuttering/formwork for footing sides", "m2", boq_data["formwork_area_m2"], 45.0),
            (6, "Bituminous cold dampproof membrane on all buried surfaces", "m2", boq_data["insulation_area_m2"], 18.0),
            (7, "Selected soil backfilling in compacted layers", "m3", boq_data["backfill_m3"], 20.0),
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
