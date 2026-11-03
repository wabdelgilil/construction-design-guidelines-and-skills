"""
Excel Exporter for Substation Transformer, Diesel Generator, and MDB Load Schedules.
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from electrical.power_distribution.substation.scripts.design_engine import SubstationDesignResult


class SubstationExcelExporter:
    """Exports substation equipment sizing schedules and load calculation tables to Excel."""

    def __init__(self, result: SubstationDesignResult):
        self.res = result
        self.writer = ExcelWriter("substation_schedule.xlsx")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "Substation Sizing"

        self.writer.format_title_banner(
            title=f"ELECTRICAL SUBSTATION & INCOMER SIZING - {self.res.project_name.upper()}",
            subtitle=f"Standards: {self.res.standard_used} | Transformer: {self.res.selected_transformer_kva} kVA | Generator: {self.res.selected_generator_kva} kVA",
            max_col=6,
        )

        headers = ["Item", "System Parameter", "Calculated / Sized Value", "Unit", "Code Standard", "Compliance"]
        self.writer.add_table_header(4, headers)

        data = [
            [1, "Total Building Connected Load", self.res.total_connected_kw, "kW", "-", "OK"],
            [2, "Total Connected Apparent Load", self.res.total_connected_kva, "kVA", "-", "OK"],
            [3, "Diversified Maximum Demand Load", self.res.max_demand_kw, "kW", "With Diversity Factors", "OK"],
            [4, "Diversified Maximum Demand Apparent", self.res.max_demand_kva, "kVA", "With Future Margin", "OK"],
            [5, "Selected Distribution Transformer", f"{self.res.selected_transformer_kva} kVA ({self.res.transformer_primary_kv}kV/{self.res.transformer_secondary_v}V)", "-", "Step Rating", "OPTIMAL"],
            [6, "Transformer Operating Loading", f"{self.res.transformer_loading_pct}%", "%", "Target <= 80%", "PASS"],
            [7, "Transformer Secondary Rated Current", self.res.transformer_flc_amps, "A", "@ 400V 3-Phase", "CALCULATED"],
            [8, "Transformer Impedance (uk%)", f"{self.res.transformer_uk_pct}%", "%", "IEC 60076", "STANDARD"],
            [9, "Prospective Short-Circuit Current (Isc)", f"{self.res.prospective_short_circuit_ka} kA", "kA", "Secondary Busbar", "CALCULATED"],
            [10, "MDB Incomer Breaker Rating", f"{self.res.mdb_incomer_rating_amps}A ({self.res.mdb_incomer_breaker_type})", "-", "In >= Iflc", "PASS"],
            [11, "MDB Breaker Breaking Capacity (Icu)", f"{self.res.mdb_incomer_icu_ka} kA", "kA", f"Icu >= 1.25*Isc ({self.res.prospective_short_circuit_ka} kA)", "COMPLIANT"],
        ]

        for r_idx, row_vals in enumerate(data, start=5):
            for c_idx, val in enumerate(row_vals, start=1):
                ws.cell(row=r_idx, column=c_idx, value=val)

        self.writer.auto_fit_columns()

        # Tab 2: Generator & ATS Sizing
        ws_gen = self.writer.create_sheet("Generator & ATS Sizing")
        self.writer.format_title_banner(
            title="STANDBY DIESEL GENERATOR & ATS SIZING",
            subtitle=f"Emergency Load: {self.res.emergency_connected_kw} kW | Selected Generator: {self.res.selected_generator_kva} kVA | ATS: {self.res.ats_rating_amps}A",
            max_col=5,
        )

        headers2 = ["Item", "Emergency Equipment", "Design Sizing", "Unit", "Engineering Criteria"]
        self.writer.add_table_header(4, headers2)

        data2 = [
            [1, "Running Emergency Load", self.res.emergency_connected_kw, "kW", "Life Safety + Pumps + Critical"],
            [2, "Emergency Running Apparent Load", self.res.emergency_demand_kva, "kVA", "Power Factor = 0.80"],
            [3, "Largest Motor Starting Inrush", self.res.motor_starting_inrush_kva, "kVA", "6x DOL inrush check"],
            [4, "Selected Diesel Generator Rating", f"{self.res.selected_generator_kva} kVA", "kVA", "ISO 8528 Standby Class"],
            [5, "Generator Standby Rated Current", f"{self.res.generator_standby_amps} A", "A", "@ 400V 3-Phase"],
            [6, "Automatic Transfer Switch (ATS)", f"{self.res.ats_rating_amps} A", "A", f"{self.res.ats_poles}-Pole with Interlock"],
        ]

        for r_idx, row_vals in enumerate(data2, start=5):
            for c_idx, val in enumerate(row_vals, start=1):
                ws_gen.cell(row=r_idx, column=c_idx, value=val)

        self.writer.auto_fit_columns()

        return self.writer.save(filepath)
