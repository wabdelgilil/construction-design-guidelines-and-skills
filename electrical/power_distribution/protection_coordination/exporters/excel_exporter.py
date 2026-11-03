"""
Excel Exporter for Short-Circuit Calculations, Breaker Schedules, and Protection Selectivity.
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from electrical.power_distribution.protection_coordination.scripts.design_engine import ProtectionCoordinationDesignResult


class ProtectionCoordinationExcelExporter:
    """Exports short-circuit calculations, LSIG settings, and TCC discrimination schedules to Excel."""

    def __init__(self, result: ProtectionCoordinationDesignResult):
        self.res = result
        self.writer = ExcelWriter("Protection Coordination")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "Short-Circuit Calculations"

        self.writer.format_title_banner(
            title=f"SHORT-CIRCUIT ANALYSIS & FAULT LEVELS (IEC 60909) - {self.res.project_name.upper()}",
            subtitle=f"Standards: {self.res.standard_used} | Transformer: {self.res.transformer.rating_kva} kVA ({self.res.transformer.voltage_secondary_v}V, uk={self.res.transformer.uk_percent}%) | Overall: {self.res.overall_system_discrimination}",
            max_col=10,
        )

        headers = [
            "Bus Tag",
            "Hierarchy Level",
            "Nominal V",
            "R (mΩ)",
            "X (mΩ)",
            "Z (mΩ)",
            "Prospective Isc (kA)",
            "Selected Breaker",
            "In (A)",
            "Icu (kA)",
        ]
        self.writer.add_table_header(4, headers)

        for idx, b in enumerate(self.res.bus_faults, start=5):
            ws.cell(row=idx, column=1, value=b.bus_name)
            ws.cell(row=idx, column=2, value=b.hierarchy_level)
            ws.cell(row=idx, column=3, value=f"{b.nominal_voltage_v:.0f} V")
            ws.cell(row=idx, column=4, value=b.r_mohm)
            ws.cell(row=idx, column=5, value=b.x_mohm)
            ws.cell(row=idx, column=6, value=b.z_mohm)
            ws.cell(row=idx, column=7, value=b.isc_sym_ka)
            ws.cell(row=idx, column=8, value=b.selected_breaker_type)
            ws.cell(row=idx, column=9, value=b.rated_current_in_a)
            ws.cell(row=idx, column=10, value=b.rated_breaking_capacity_icu_ka)

        self.writer.auto_fit_columns()

        # Tab 2: Switchgear Schedule & Trip Settings (LSIG)
        ws_lsig = self.writer.create_sheet("LSIG Trip Settings")
        self.writer.format_title_banner(
            title="CIRCUIT BREAKER ELECTRONIC TRIP UNIT (LSIG) CONFIGURATION SCHEDULE",
            subtitle="IEEE 242 Protection Settings for Symmetrical Overload, Short-Time & Ground Fault Protection",
            max_col=6,
        )

        lsig_headers = [
            "Bus Location",
            "Breaker Type",
            "Rated In (A)",
            "Breaking Icu (kA)",
            "Withstand Icw (kA)",
            "Configured Trip Parameters (LSIG)",
        ]
        self.writer.add_table_header(4, lsig_headers)

        for idx, b in enumerate(self.res.bus_faults, start=5):
            ws_lsig.cell(row=idx, column=1, value=b.bus_name)
            ws_lsig.cell(row=idx, column=2, value=b.selected_breaker_type)
            ws_lsig.cell(row=idx, column=3, value=b.rated_current_in_a)
            ws_lsig.cell(row=idx, column=4, value=b.rated_breaking_capacity_icu_ka)
            ws_lsig.cell(row=idx, column=5, value=b.rated_withstand_icw_ka if b.rated_withstand_icw_ka else "N/A (Cat A)")
            ws_lsig.cell(row=idx, column=6, value=b.tripping_lsig_summary)

        self.writer.auto_fit_columns()

        # Tab 3: Selectivity & Discrimination Matrix
        ws_sel = self.writer.create_sheet("Discrimination Matrix")
        self.writer.format_title_banner(
            title="TIME-CURRENT CHARACTERISTIC (TCC) DISCRIMINATION EVALUATION",
            subtitle=f"Criteria: Time Margin Δt >= 100ms | Current Ratio >= 1.5x | Status: {self.res.overall_system_discrimination}",
            max_col=7,
        )

        sel_headers = [
            "Upstream Device",
            "Downstream Device",
            "Upstream Delay tsd",
            "Downstream Clearing",
            "Time Margin Δt (ms)",
            "Selectivity Status",
            "Engineering Evaluation",
        ]
        self.writer.add_table_header(4, sel_headers)

        for idx, pair in enumerate(self.res.selectivity_pairs, start=5):
            ws_sel.cell(row=idx, column=1, value=pair.upstream_device)
            ws_sel.cell(row=idx, column=2, value=pair.downstream_device)
            ws_sel.cell(row=idx, column=3, value=f"{pair.upstream_tsd_s:.2f} s")
            ws_sel.cell(row=idx, column=4, value=f"{pair.downstream_clear_time_s:.2f} s")
            ws_sel.cell(row=idx, column=5, value=f"{pair.time_margin_ms:.0f} ms")
            ws_sel.cell(row=idx, column=6, value=pair.selectivity_status)
            ws_sel.cell(row=idx, column=7, value=pair.notes)

        self.writer.auto_fit_columns()

        # Tab 4: Switchgear Bill of Quantities (BOQ)
        ws_boq = self.writer.create_sheet("Switchgear BOQ")
        self.writer.format_title_banner(
            title="MAIN SWITCHGEAR & CIRCUIT BREAKERS BILL OF QUANTITIES",
            subtitle=f"Project: {self.res.project_name} | Scope: Incomer ACB, Sub-Main MCCBs, and Protection Units",
            max_col=5,
        )

        boq_headers = ["Item No.", "Equipment Description", "Specification / Rating", "Quantity", "Unit"]
        self.writer.add_table_header(4, boq_headers)

        boq_items = [
            ("1.01", "Air Circuit Breaker (ACB) Incomer", f"{self.res.bus_faults[0].rated_current_in_a}A, 4P, Drawout, Icu={self.res.bus_faults[0].rated_breaking_capacity_icu_ka}kA, Icw={self.res.bus_faults[0].rated_withstand_icw_ka}kA with LSIG Unit", 1, "Unit"),
            ("1.02", "Molded Case Circuit Breaker (MCCB) Outgoing", f"{self.res.bus_faults[1].rated_current_in_a}A, 4P, Fixed, Icu={self.res.bus_faults[1].rated_breaking_capacity_icu_ka}kA with Electronic Trip Unit", 4, "Sets"),
            ("1.03", "Final Sub-Distribution Board (DB)", f"12-Way 3-Phase DB with {self.res.bus_faults[2].rated_current_in_a}A Incomer, Icu={self.res.bus_faults[2].rated_breaking_capacity_icu_ka}kA", 8, "Sets"),
            ("1.04", "Digital Power Quality & Metering Unit", "Multifunction LCD meter (V, I, kW, kVA, THD, RS485 Modbus)", 5, "Units"),
            ("1.05", "Surge Protection Device (SPD)", "Type 1+2 Combined Lightning/Surge Arrester, Iimp=25kA, In=40kA", 2, "Sets"),
        ]

        for idx, (num, desc, spec, qty, unit) in enumerate(boq_items, start=5):
            ws_boq.cell(row=idx, column=1, value=num)
            ws_boq.cell(row=idx, column=2, value=desc)
            ws_boq.cell(row=idx, column=3, value=spec)
            ws_boq.cell(row=idx, column=4, value=qty)
            ws_boq.cell(row=idx, column=5, value=unit)

        self.writer.auto_fit_columns()
        self.writer.save(filepath)
        return filepath
