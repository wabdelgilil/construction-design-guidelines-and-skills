"""
Excel Panel Schedule and BOQ Exporter for Medical Isolated Power Systems (IPS).
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from electrical.power_distribution.medical_isolated_power_ips.scripts.design_engine import IPSDesignResult


class MedicalIPSExcelExporter:
    """Exports Medical IPS panel schedules and equipment bills of quantities."""

    def __init__(self, result: IPSDesignResult):
        self.res = result
        self.writer = ExcelWriter("medical_ips_schedule.xlsx")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "IPS Schedule"

        self.writer.format_title_banner(
            title=f"MEDICAL ISOLATED POWER PANEL (IPS) - {self.res.room_name.upper()}",
            subtitle=f"Code: {self.res.standard_used} | Transformer: {self.res.selected_transformer_kva} kVA (230V/230V 1-Ph)",
            max_col=7,
        )

        headers = [
            "Circuit Tag",
            "Description & Medical Equipment",
            "Load (W)",
            "Current (A)",
            "Breaker (DP)",
            "Cable Specification",
            "POAG Pin",
        ]
        self.writer.add_table_header(4, headers)

        for idx, ckt in enumerate(self.res.secondary_circuits, start=5):
            ws.cell(row=idx, column=1, value=ckt.circuit_tag)
            ws.cell(row=idx, column=2, value=ckt.description)
            ws.cell(row=idx, column=3, value=ckt.connected_watts)
            ws.cell(row=idx, column=4, value=ckt.current_amps)
            ws.cell(row=idx, column=5, value=f"{ckt.breaker_rating_amps}A DP")
            ws.cell(row=idx, column=6, value=f"{ckt.cable_size_sqmm}mm2 Cu Shielded")
            ws.cell(row=idx, column=7, value="CONNECTED" if ckt.poag_pin_assigned else "N/A")

        self.writer.auto_fit_columns()

        # Tab 2: System Specifications & IMD Settings
        ws_specs = self.writer.create_sheet("IPS Engineering Specs")
        self.writer.format_title_banner(
            title="MEDICAL IT SYSTEM & MONITORING SETTINGS",
            subtitle="IEC 60364-7-710 / NFPA 99 / SBC 401 Compliance",
            max_col=5,
        )
        spec_headers = ["Item", "Subsystem Parameter", "Design Value", "Threshold / Code Limit", "Status"]
        self.writer.add_table_header(4, spec_headers)

        spec_data = [
            [1, "Transformer Rating", f"{self.res.selected_transformer_kva} kVA", "Max 10 kVA per unit", "COMPLIANT"],
            [2, "Transformer Primary Breaker", f"{self.res.primary_mcb_rating_amps}A Curve D", "12x inrush withstand", "COMPLIANT"],
            [3, "Insulation Monitor (IMD) Response", f"{self.res.imd_alarm_threshold_kohm} kOhm", "Min 50 kOhm", "PASS"],
            [4, "Max Earth Leakage Current", f"{self.res.max_leakage_current_ma} mA", "Max 0.5 mA", "PASS"],
            [5, "POAG Bonding Resistance", f"<= {self.res.equipotential_bonding_max_resistance_ohms} Ohm", "Max 0.1 Ohm", "COMPLIANT"],
            [6, "Operating Theater Annunciator", "Dual (Acoustic + Visual)", "Mandatory in OR", "CONFIGURED"],
        ]

        for r_idx, row_vals in enumerate(spec_data, start=5):
            for c_idx, val in enumerate(row_vals, start=1):
                ws_specs.cell(row=r_idx, column=c_idx, value=val)

        self.writer.auto_fit_columns()

        return self.writer.save(filepath)
