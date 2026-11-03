"""
Excel Exporter for HVAC Cooling Load, Equipment Schedule, and MEP Interface.
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from mechanical.hvac.heat_load.scripts.design_engine import HVACDesignResult


class HVACExcelExporter:
    """Exports HVAC design calculation and MEP coordination matrix to Excel."""

    def __init__(self, result: HVACDesignResult):
        self.res = result
        self.writer = ExcelWriter("hvac_design_schedule.xlsx")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "Cooling Load Summary"

        self.writer.format_title_banner(
            title=f"HVAC COOLING LOAD & EQUIPMENT SCHEDULE - {self.res.space_name.upper()}",
            subtitle=f"Governing Standard: {self.res.code_used} / ASHRAE | Sized Capacity: {self.res.selected_unit_tons_tr} TR ({self.res.supply_airflow_cfm} CFM)",
            max_col=6,
        )

        headers = [
            "Item",
            "Heat Gain Component",
            "Sensible (W)",
            "Latent (W)",
            "Total (W)",
            "Percentage",
        ]
        self.writer.add_table_header(4, headers)

        gt = max(self.res.grand_total_heat_w, 1.0)
        breakdown = [
            [1, "Building Envelope Conduction", self.res.envelope_heat_gain_w, 0.0, self.res.envelope_heat_gain_w, f"{self.res.envelope_heat_gain_w/gt*100:.1f}%"],
            [2, "Window Fenestration Solar Gain", self.res.glass_solar_gain_w, 0.0, self.res.glass_solar_gain_w, f"{self.res.glass_solar_gain_w/gt*100:.1f}%"],
            [3, "Occupancy Sensible & Latent Gain", self.res.occupant_sensible_gain_w, self.res.occupant_latent_gain_w, self.res.occupant_sensible_gain_w + self.res.occupant_latent_gain_w, f"{(self.res.occupant_sensible_gain_w + self.res.occupant_latent_gain_w)/gt*100:.1f}%"],
            [4, "Artificial Lighting Heat Gain", self.res.lighting_gain_w, 0.0, self.res.lighting_gain_w, f"{self.res.lighting_gain_w/gt*100:.1f}%"],
            [5, "Office Computers / Equipment Load", self.res.equipment_gain_w, 0.0, self.res.equipment_gain_w, f"{self.res.equipment_gain_w/gt*100:.1f}%"],
            [6, "Fresh Air Ventilation Load", self.res.ventilation_sensible_w, self.res.ventilation_latent_w, self.res.ventilation_sensible_w + self.res.ventilation_latent_w, f"{(self.res.ventilation_sensible_w + self.res.ventilation_latent_w)/gt*100:.1f}%"],
            [7, "TOTAL SPACE COOLING LOAD", self.res.total_sensible_heat_w, self.res.total_latent_heat_w, self.res.grand_total_heat_w, "100.0%"],
        ]

        for r_idx, row_vals in enumerate(breakdown, start=5):
            for c_idx, val in enumerate(row_vals, start=1):
                ws.cell(row=r_idx, column=c_idx, value=val)

        self.writer.auto_fit_columns()

        # Tab 2: Equipment & MEP Coordination Interface
        ws_mep = self.writer.create_sheet("MEP Coordination Interface")
        self.writer.format_title_banner(
            title="HVAC TO ELECTRICAL / CIVIL COORDINATION MATRIX",
            subtitle="Cross-Discipline Demands for Electrical Panel Boards and Architectural Drops",
            max_col=5,
        )

        mep_headers = ["Item", "MEP Interface Target", "Value / Requirement", "Unit", "Discipline Responsible"]
        self.writer.add_table_header(4, mep_headers)

        mep_data = [
            [1, "Indoor / Outdoor Unit Model", self.res.selected_unit_model, "-", "Mechanical"],
            [2, "Required Cooling Tonnage", self.res.selected_unit_tons_tr, "TR", "Mechanical"],
            [3, "Total Supply Airflow", self.res.supply_airflow_cfm, "CFM", "Mechanical"],
            [4, "Supply Air Diffusers", f"{self.res.supply_diffusers_count}x @ {self.res.cfm_per_diffuser} CFM", "Nos.", "Mechanical / Arch"],
            [5, "Return Air Grilles", f"{self.res.return_grilles_count}x Ceiling Grilles", "Nos.", "Mechanical / Arch"],
            [6, "Electrical Connected Load", self.res.equipment_electrical_kw, "kW", "Electrical"],
            [7, "Feeder Operating Voltage", self.res.electrical_voltage_v, "V AC", "Electrical"],
            [8, "Minimum Circuit Ampacity (MCA)", self.res.electrical_mca_amps, "A", "Electrical"],
            [9, "Max Overcurrent Protection (MOP)", f"{self.res.electrical_mop_amps}A MCB", "-", "Electrical"],
            [10, "Digital Room Thermostat Height", f"+{self.res.thermostat_height_aff_m}m AFF", "m", "Electrical & Controls"],
            [11, "Weatherproof Isolator Switch Height", f"+{self.res.isolator_height_aff_m}m AFF", "m", "Electrical & Mechanical"],
            [12, "Condensate Drain Connection", "25mm UPVC Insulated", "-", "Plumbing"],
        ]

        for r_idx, row_vals in enumerate(mep_data, start=5):
            for c_idx, val in enumerate(row_vals, start=1):
                ws_mep.cell(row=r_idx, column=c_idx, value=val)

        self.writer.auto_fit_columns()

        return self.writer.save(filepath)
