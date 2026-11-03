"""
Excel Exporter for Earthing Calculations and Lightning Protection BOQ Schedules.
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from electrical.earthing.scripts.design_engine import EarthingDesignResult


class EarthingExcelExporter:
    """Exports earthing resistance schedules and lightning protection BOQs to Excel."""

    def __init__(self, result: EarthingDesignResult):
        self.res = result
        self.writer = ExcelWriter("earthing_schedule.xlsx")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "Earthing Sizing"

        self.writer.format_title_banner(
            title=f"EARTHING & GROUNDING RESISTANCE ANALYSIS - {self.res.project_name.upper()}",
            subtitle=f"Standard: {self.res.standard_used} | Target: <= {self.res.target_resistance_ohms} Ohm | Achieved: {self.res.combined_earthing_resistance_ohms} Ohm",
            max_col=6,
        )

        headers = ["Item", "System Parameter", "Calculated / Specified Value", "Unit", "Code Limit", "Status"]
        self.writer.add_table_header(4, headers)

        data = [
            [1, "Design Soil Resistivity (rho)", self.res.soil_resistivity_ohm_m, "Ohm·m", "-", "OK"],
            [2, "Single Driven Earth Rod Resistance", self.res.single_rod_resistance_ohms, "Ohm", "Dwight's Equation", "CALCULATED"],
            [3, "Perimeter Buried Ring Length", self.res.perimeter_ring_length_m, "m", "Around Building", "OK"],
            [4, "Perimeter Ring Conductor Resistance", self.res.perimeter_ring_resistance_ohms, "Ohm", "70mm² Cu @ 0.8m", "CALCULATED"],
            [5, "Number of Driven Earth Rods", self.res.number_of_earth_rods, "Nos.", "In Parallel Array", "SIZED"],
            [6, "Combined System Earth Resistance", self.res.combined_earthing_resistance_ohms, "Ohm", f"<= {self.res.target_resistance_ohms} Ohm", self.res.earthing_compliance_status],
            [7, "Total Earth Inspection Pits", self.res.total_earth_pits_count, "Nos.", "One per rod location", "SPECIFIED"],
        ]

        for r_idx, row_vals in enumerate(data, start=5):
            for c_idx, val in enumerate(row_vals, start=1):
                ws.cell(row=r_idx, column=c_idx, value=val)

        self.writer.auto_fit_columns()

        # Tab 2: Lightning Protection & BOQ
        ws_lps = self.writer.create_sheet("Lightning Protection & BOQ")
        self.writer.format_title_banner(
            title="LIGHTNING PROTECTION SYSTEM (LPS) & MATERIAL BOQ",
            subtitle=f"Level: {self.res.lps_level} | Rolling Sphere: {self.res.rolling_sphere_radius_m}m | Down Conductors: {self.res.down_conductors_count}",
            max_col=5,
        )

        headers2 = ["Item", "Component / Material", "Quantity", "Unit", "Purpose"]
        self.writer.add_table_header(4, headers2)

        data2 = [
            [1, "LPS Protection Classification", self.res.lps_level, "-", "IEC 62305 Risk Category"],
            [2, "Rolling Sphere Radius", f"{self.res.rolling_sphere_radius_m} m", "m", "Protection Envelope"],
            [3, "Air Terminals (Franklin Rods)", self.res.air_terminals_count, "Nos.", f"Height = {self.res.air_terminal_height_m}m above roof"],
            [4, "Down Conductors", self.res.down_conductors_count, "Nos.", f"Max spacing <= {self.res.down_conductor_max_spacing_m}m"],
            [5, "Test Links (Disconnecting)", self.res.test_links_count, "Nos.", "Mounted at +1.5m AFF"],
            [6, "70 mm² Bare Stranded Copper", self.res.total_70mm2_bare_copper_m, "m", "Buried Earth Loop"],
            [7, "25 x 3 mm Bare Copper Tape", self.res.total_25x3mm_copper_tape_m, "m", "Down Conductors & Roof Mesh"],
            [8, "Earth Inspection Test Pits", self.res.total_earth_pits_count, "Nos.", "Heavy Duty 300x300mm"],
        ]

        for r_idx, row_vals in enumerate(data2, start=5):
            for c_idx, val in enumerate(row_vals, start=1):
                ws_lps.cell(row=r_idx, column=c_idx, value=val)

        self.writer.auto_fit_columns()

        return self.writer.save(filepath)
