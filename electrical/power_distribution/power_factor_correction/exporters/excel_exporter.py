"""
Excel Exporter for Automatic Power Factor Correction (APFC) Schedules, Step Details, and BOQ.
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from electrical.power_distribution.power_factor_correction.scripts.design_engine import PFCDesignResult


class PFCExcelExporter:
    """Exports APFC capacitor bank schedules, detuned reactor parameters, and BOQ workbooks to Excel."""

    def __init__(self, result: PFCDesignResult):
        self.res = result
        self.writer = ExcelWriter("Power Factor Correction")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "APFC Steps Schedule"

        self.writer.format_title_banner(
            title=f"AUTOMATIC POWER FACTOR CORRECTION (APFC) SCHEDULE - {self.res.project_name.upper()}",
            subtitle=f"Code: {self.res.standard_used} | Bank: {self.res.selected_total_kvar} kVAR ({self.res.step_progression_sequence}) | Reactor: {self.res.detuned_reactor_percent}% ({self.res.tuning_frequency_hz} Hz) | Incomer: {self.res.incomer_mccb_rating_a}A",
            max_col=10,
        )

        headers = [
            "Step No.",
            "Step kVAR",
            "Effective kVAR",
            "Capacitor Voltage (V)",
            "Nominal Current (A)",
            "Design Current (A)",
            "Contactor Type",
            "Contactor AC-6b (A)",
            "Step Breaker (A)",
            "Reactor L (mH)",
        ]
        self.writer.add_table_header(4, headers)

        for idx, s in enumerate(self.res.steps, start=5):
            ws.cell(row=idx, column=1, value=f"Step {s.step_number:02d}")
            ws.cell(row=idx, column=2, value=s.step_kvar)
            ws.cell(row=idx, column=3, value=s.effective_kvar)
            ws.cell(row=idx, column=4, value=f"{s.rated_voltage_v:.0f} V")
            ws.cell(row=idx, column=5, value=s.step_nominal_current_a)
            ws.cell(row=idx, column=6, value=s.step_design_current_a)
            ws.cell(row=idx, column=7, value=s.switching_contactor_type)
            ws.cell(row=idx, column=8, value=s.contactor_rating_ac6b_a)
            ws.cell(row=idx, column=9, value=s.step_fuse_or_mccb_a)
            ws.cell(row=idx, column=10, value=s.reactor_inductance_mh)

        self.writer.auto_fit_columns()

        # Tab 2: System Benefits & Improvement Metrics
        ws_ben = self.writer.create_sheet("Power Quality Metrics")
        self.writer.format_title_banner(
            title="FACILITY POWER FACTOR & CAPACITY IMPROVEMENT METRICS",
            subtitle=f"pf Improvement: {self.res.initial_power_factor:.2f} -> {self.res.target_power_factor:.2f} | Released: {self.res.apparent_power_released_kva} kVA | Current Saved: {self.res.line_current_reduction_a} A",
            max_col=4,
        )

        metric_headers = ["Engineering Parameter", "Before APFC Installation", "After APFC Installation", "Net Benefit / Savings"]
        self.writer.add_table_header(4, metric_headers)

        rows = [
            ("Facility Active Load (P)", f"{self.res.active_power_kw:.1f} kW", f"{self.res.active_power_kw:.1f} kW", "Maintained Constant"),
            ("Operating Power Factor (cos φ)", f"{self.res.initial_power_factor:.2f}", f"{self.res.target_power_factor:.2f}", f"+{(self.res.target_power_factor - self.res.initial_power_factor):.2f} Improvement"),
            ("Apparent Power Demand (S)", f"{self.res.apparent_power_initial_kva:.1f} kVA", f"{self.res.apparent_power_corrected_kva:.1f} kVA", f"-{self.res.apparent_power_released_kva:.1f} kVA (Released Capacity)"),
            ("Main Feeder Line Current", f"{(self.res.apparent_power_initial_kva*1000)/(1.732*self.res.nominal_voltage_v):.1f} A", f"{(self.res.apparent_power_corrected_kva*1000)/(1.732*self.res.nominal_voltage_v):.1f} A", f"-{self.res.line_current_reduction_a:.1f} A Line Reduction"),
            ("Harmonic Resonance Status", "High Risk of 5th/7th Resonance", f"Protected by {self.res.detuned_reactor_percent}% Detuning", f"Tuned at {self.res.tuning_frequency_hz} Hz (Anti-Resonant)"),
            ("Utility Power Factor Penalty", "Subject to SEC Penalty Tariffs", "Zero Penalty (Compliance Achieved)", "100% Billing Surcharge Elimination"),
        ]

        for idx, (param, bef, aft, ben) in enumerate(rows, start=5):
            ws_ben.cell(row=idx, column=1, value=param)
            ws_ben.cell(row=idx, column=2, value=bef)
            ws_ben.cell(row=idx, column=3, value=aft)
            ws_ben.cell(row=idx, column=4, value=ben)

        self.writer.auto_fit_columns()

        # Tab 3: Itemized Bill of Quantities (BOQ)
        ws_boq = self.writer.create_sheet("APFC BOQ")
        self.writer.format_title_banner(
            title="AUTOMATIC POWER FACTOR CORRECTION PANEL BILL OF QUANTITIES",
            subtitle=f"Project: {self.res.project_name} | Scope: Factory-Assembled Detuned APFC Switchboard",
            max_col=5,
        )

        boq_headers = ["Item No.", "Equipment Description", "Specification / Rating", "Quantity", "Unit"]
        self.writer.add_table_header(4, boq_headers)

        boq_items = [
            ("1.01", "Free-Standing Modular APFC Enclosure", f"IP54 Indoor Sheet Steel Panel with Forced Cooling, Form 2b", 1, "Unit"),
            ("1.02", "Digital Microprocessor APFC Controller", "6-12 Stage Automatic Step Controller with THD-V/I Monitoring", 1, "Unit"),
            ("1.03", "Main Incomer 4-Pole Circuit Breaker", f"{self.res.incomer_mccb_rating_a}A MCCB, Icu=36kA, Electronic Trip Unit", 1, "Unit"),
            ("1.04", "Three-Phase Detuned Filter Reactors", f"{self.res.detuned_reactor_percent}% p-factor ({self.res.tuning_frequency_hz} Hz), Class H copper winding", self.res.total_steps_count, "Units"),
            ("1.05", "Heavy-Duty Shunt Power Capacitors", f"Dry type, metallized polypropylene, {self.res.capacitor_rated_voltage_v:.0f}V continuous rating", self.res.total_steps_count, "Units"),
            ("1.06", "Capacitor Switching Contactors", "AC-6b with early-make inrush damping resistors", self.res.total_steps_count, "Units"),
            ("1.07", "Step Protection High-Breaking Fuses/MCCBs", "High breaking capacity HRC cylindrical fuses / MCCBs", self.res.total_steps_count, "Sets"),
            ("1.08", "Thermostatically Controlled Cooling Fans", "Roof/Door mounted exhaust fans with washable air filters", 2, "Sets"),
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
