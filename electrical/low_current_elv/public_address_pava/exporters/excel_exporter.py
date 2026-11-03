"""
Excel Exporter for Public Address & Voice Alarm (PA/VA) Schedules, Amplifiers, and BOQ.
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from electrical.low_current_elv.public_address_pava.scripts.design_engine import PAVADesignResult


class PAVAExcelExporter:
    """Exports PA/VA acoustic schedules, amplifier budgets, and BOQ workbooks to Excel."""

    def __init__(self, result: PAVADesignResult):
        self.res = result
        self.writer = ExcelWriter("PAVA Schedule")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "Acoustic & Speaker Schedule"

        self.writer.format_title_banner(
            title=f"PA/VA VOICE EVACUATION ACOUSTIC & SPEAKER SCHEDULE - {self.res.project_name.upper()}",
            subtitle=f"Code: {self.res.standard_used} | Zones: {self.res.total_zones_count} | Speakers: {self.res.total_speakers_count} (A={self.res.total_circuit_a_speakers}, B={self.res.total_circuit_b_speakers}) | Audio Load: {self.res.grand_total_audio_load_w} W",
            max_col=13,
        )

        headers = [
            "Zone Tag / Name",
            "Category",
            "Area (m²)",
            "Ambient Noise (dBA)",
            "Target SPL (dBA)",
            "Speaker Type",
            "Tapping (W)",
            "Total Qty",
            "Circuit A",
            "Circuit B",
            "Ear SPL (dBA)",
            "SNR (dBA)",
            "Est. STI",
        ]
        self.writer.add_table_header(4, headers)

        for idx, z in enumerate(self.res.zones, start=5):
            ws.cell(row=idx, column=1, value=z.zone_name)
            ws.cell(row=idx, column=2, value=z.zone_category)
            ws.cell(row=idx, column=3, value=z.area_m2)
            ws.cell(row=idx, column=4, value=z.ambient_noise_dba)
            ws.cell(row=idx, column=5, value=z.target_spl_dba)
            ws.cell(row=idx, column=6, value=z.speaker_type)
            ws.cell(row=idx, column=7, value=z.tapping_watts)
            ws.cell(row=idx, column=8, value=z.speakers_count)
            ws.cell(row=idx, column=9, value=z.circuit_a_count)
            ws.cell(row=idx, column=10, value=z.circuit_b_count)
            ws.cell(row=idx, column=11, value=z.calculated_spl_at_ear_dba)
            ws.cell(row=idx, column=12, value=z.snr_achieved_dba)
            ws.cell(row=idx, column=13, value=z.sti_estimate)

        self.writer.auto_fit_columns()

        # Tab 2: Amplifier Capacity & 24h+30m Battery Sizing
        ws_amp = self.writer.create_sheet("Amplifier & Battery Sizing")
        self.writer.format_title_banner(
            title="CLASS-D AMPLIFIER SIZING (N+1) & EMERGENCY 24V DC BATTERY CALCULATION",
            subtitle=f"Load: {self.res.grand_total_audio_load_w} W | Installed Capacity: {self.res.grand_total_amplifier_capacity_w} W | Battery: {self.res.selected_battery_ah} Ah @ 24V DC",
            max_col=4,
        )

        amp_headers = ["Engineering Parameter", "Calculated Value", "Selected Unit / Equipment", "Design Standard / Basis"]
        self.writer.add_table_header(4, amp_headers)

        rows = [
            ("Total 100V Loudspeaker Load", f"{self.res.grand_total_audio_load_w:.1f} W", f"{self.res.grand_total_audio_load_w:.1f} W", "Sum of all zone speaker tappings"),
            ("Amplifier Headroom & Cable Factor", "1.20 (20% margin)", "1.20 Multiplier", "EN 54-16 Line loss & dynamic headroom"),
            ("Required Net Audio Amplification", f"{self.res.grand_total_audio_load_w * 1.20:.1f} W", f"{self.res.main_amplifiers_count * self.res.amplifier_rating_per_unit_w} W", f"{self.res.main_amplifiers_count}x {self.res.amplifier_rating_per_unit_w}W Class-D Channels"),
            ("Hot-Standby Redundancy (N+1)", "1 Dedicated Spare Channel", f"1x {self.res.amplifier_rating_per_unit_w}W Hot-Standby", "Automatic pilot-tone failover (<100ms)"),
            ("Total Installed Amplifier Rating", f"{self.res.grand_total_amplifier_capacity_w} W", f"{(self.res.main_amplifiers_count + self.res.standby_amplifiers_count)}x {self.res.amplifier_rating_per_unit_w}W Units", "19-inch Rackmount Chassis"),
            ("Quiescent Standby Current (24h)", f"{self.res.quiescent_current_dc_a:.2f} A", f"{self.res.quiescent_current_dc_a:.2f} A @ 24V DC", "Controller + preamps + idle amps"),
            ("Full Evacuation Alarm Current (30m)", f"{self.res.alarm_current_dc_a:.2f} A", f"{self.res.alarm_current_dc_a:.2f} A @ 24V DC", "Full rated speech output into load"),
            ("Calculated Standby Battery Ah", f"{self.res.calculated_battery_ah:.2f} Ah", f"{self.res.selected_battery_ah:.1f} Ah", "BS 5839-8 (24h standby + 30m alarm) x 1.25 aging"),
            ("Selected VRLA Battery Set", "2x 12V Blocks in series", f"1x Set {self.res.selected_battery_ah} Ah @ 24V", "Enclosed in PA/VA Rack Battery Tray"),
        ]

        for idx, (param, calc, sel, basis) in enumerate(rows, start=5):
            ws_amp.cell(row=idx, column=1, value=param)
            ws_amp.cell(row=idx, column=2, value=calc)
            ws_amp.cell(row=idx, column=3, value=sel)
            ws_amp.cell(row=idx, column=4, value=basis)

        self.writer.auto_fit_columns()

        # Tab 3: Itemized Bill of Quantities (BOQ)
        ws_boq = self.writer.create_sheet("PAVA BOQ")
        self.writer.format_title_banner(
            title="PUBLIC ADDRESS & VOICE ALARM (PA/VA) BILL OF QUANTITIES",
            subtitle=f"Project: {self.res.project_name} | Scope: EN 54 Certified Voice Evacuation System",
            max_col=5,
        )

        boq_headers = ["Item No.", "Equipment Description", "Specification / Rating", "Quantity", "Unit"]
        self.writer.add_table_header(4, boq_headers)

        ceiling_spk_cnt = sum(z.speakers_count for z in self.res.zones if z.speaker_type == "ceiling")
        projector_cnt = sum(z.speakers_count for z in self.res.zones if z.speaker_type == "wall_projector")
        horn_cnt = sum(z.speakers_count for z in self.res.zones if z.speaker_type == "weatherproof_horn")

        boq_items = [
            ("1.01", "Master PA/VA System Controller", "EN 54-16 Certified, digital audio matrix, message player", 1, "Unit"),
            ("1.02", "Modular Class-D Power Amplifier (Main)", f"{self.res.amplifier_rating_per_unit_w}W 100V channel with line surveillance", self.res.main_amplifiers_count, "Units"),
            ("1.03", "Modular Class-D Power Amplifier (Standby)", f"{self.res.amplifier_rating_per_unit_w}W Hot-Standby Channel (N+1 failover)", self.res.standby_amplifiers_count, "Unit"),
            ("1.04", "EN 54-4 Power Supply & Charger Unit", "24V DC regulated with automatic battery switchover", 1, "Unit"),
            ("1.05", "Sealed Lead-Acid (VRLA) Battery Set", f"2x 12V {self.res.selected_battery_ah} Ah (24V DC emergency autonomy)", 2, "Nos"),
            ("1.06", "Ceiling Loudspeakers with Steel Fire Dome", "EN 54-24 certified, 6W/3W/1.5W 100V multi-tap, ceramic block", ceiling_spk_cnt, "Nos"),
            ("1.07", "Bidirectional Sound Projector Loudspeakers", "EN 54-24 certified, 6W/3W 100V, aluminum enclosure", projector_cnt, "Nos"),
            ("1.08", "High-Efficiency Weatherproof Horn Speakers", "EN 54-24 certified, IP66, 15W/7.5W 100V line, 105 dBA", horn_cnt, "Nos"),
            ("1.09", "Emergency Fireman Paging Microphone Station", "EN 54-16 monitored goose-neck microphone with zone keys", 1, "Unit"),
            ("1.10", "Fire-Resistant Speaker Cable (2x1.5mm²)", "FP200 Gold / PH120 fire resistant, twisted pair (Red/White)", 12, "Reels"),
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
