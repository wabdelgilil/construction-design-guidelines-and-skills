"""
AutoCAD DXF Exporter for Automatic Power Factor Correction (APFC) Panel Elevation and Single-Line Schematic.
"""

from pathlib import Path
from core.exporters.dxf_writer import DXFWriter
from electrical.power_distribution.power_factor_correction.scripts.design_engine import PFCDesignResult


class PFC_DXFExporter:
    """Exports APFC panel front elevations and step wiring schematics to AutoCAD .dxf format."""

    def __init__(self, result: PFCDesignResult):
        self.res = result
        self.writer = DXFWriter("apfc_panel_elevation.dxf")
        self._setup_layers()

    def _setup_layers(self):
        layers = [
            ("E-PFC-FRAME", 8),      # Dark Grey: Panel frame, plinth, column borders
            ("E-PFC-DEVICES", 4),    # Cyan: APFC controller, contactors, meters
            ("E-PFC-CAPACITOR", 6),  # Magenta: Capacitor cells
            ("E-PFC-REACTOR", 1),    # Red: Detuned iron-core reactors
            ("E-PFC-BUS", 7),        # White: Main copper busbars
            ("E-PFC-DIMS", 2),       # Yellow: Dimensions, step ratings
            ("E-PFC-TEXT", 7),       # White: Titles and annotations
        ]
        for name, color in layers:
            if name not in self.writer.doc.layers:
                lyr = self.writer.doc.layers.add(name)
                lyr.color = color

    def export(self, filepath: Path) -> Path:
        # Title Block
        self.writer.add_text(
            "AUTOMATIC POWER FACTOR CORRECTION (APFC) - PANEL ELEVATION & DETUNED SCHEMATIC",
            (0, 3100),
            height=120,
            layer="E-PFC-TEXT",
        )
        self.writer.add_text(
            f"Project: {self.res.project_name} | Code: {self.res.standard_used} | Bank: {self.res.selected_total_kvar} kVAR ({self.res.step_progression_sequence}) | Reactor: {self.res.detuned_reactor_percent}% ({self.res.tuning_frequency_hz} Hz)",
            (0, 2950),
            height=70,
            layer="E-PFC-TEXT",
        )

        # -------------------------------------------------------------
        # VIEW 1: APFC Free-Standing Panel Front Elevation
        # -------------------------------------------------------------
        pnl_x = 0.0
        pnl_y = 400.0
        pnl_w = 800.0    # 800mm width
        pnl_h = 2100.0   # 2100mm height
        plinth_h = 100.0 # 100mm plinth

        # Plinth
        self.writer.add_rectangle(pnl_x, pnl_y - plinth_h, pnl_w, plinth_h, layer="E-PFC-FRAME")
        self.writer.add_text("BASE PLINTH (100mm)", (pnl_x + 250, pnl_y - 65), height=35, layer="E-PFC-TEXT")

        # Outer Enclosure
        self.writer.add_rectangle(pnl_x, pnl_y, pnl_w, pnl_h, layer="E-PFC-FRAME")

        # Top Control & Metering Door (Top 600mm)
        self.writer.add_rectangle(pnl_x + 40, pnl_y + pnl_h - 600, pnl_w - 80, 560, layer="E-PFC-FRAME")

        # Digital APFC Microprocessor Controller
        self.writer.add_rectangle(pnl_x + 150, pnl_y + pnl_h - 350, 300, 200, layer="E-PFC-DEVICES")
        self.writer.add_text("APFC CONTROLLER", (pnl_x + 190, pnl_y + pnl_h - 220), height=30, layer="E-PFC-DEVICES")
        self.writer.add_text(f"Target pf: {self.res.target_power_factor:.2f}", (pnl_x + 230, pnl_y + pnl_h - 270), height=25, layer="E-PFC-TEXT")
        self.writer.add_text("Automatic 6-12 Step", (pnl_x + 210, pnl_y + pnl_h - 320), height=22, layer="E-PFC-DIMS")

        # Step Status LEDs (Circles along top)
        for i in range(min(self.res.total_steps_count, 8)):
            cx = pnl_x + 500 + (i % 4) * 50
            cy = pnl_y + pnl_h - 230 - (i // 4) * 60
            self.writer.msp.add_circle((cx, cy), 12, dxfattribs={"layer": "E-PFC-DEVICES"})
            self.writer.add_text(f"{i+1}", (cx - 7, cy - 8), height=16, layer="E-PFC-TEXT")

        # Incomer MCCB Rotary Handle
        self.writer.msp.add_circle((pnl_x + pnl_w - 120, pnl_y + pnl_h - 450), 30, dxfattribs={"layer": "E-PFC-BUS"})
        self.writer.add_text("INCOMER", (pnl_x + pnl_w - 160, pnl_y + pnl_h - 520), height=22, layer="E-PFC-TEXT")
        self.writer.add_text(f"{self.res.incomer_mccb_rating_a}A", (pnl_x + pnl_w - 150, pnl_y + pnl_h - 550), height=22, layer="E-PFC-DIMS")

        # Middle Compartment: Switching Contactors & Protection Fuses
        self.writer.add_rectangle(pnl_x + 40, pnl_y + 850, pnl_w - 80, 600, layer="E-PFC-FRAME")
        self.writer.add_text("CAPACITOR CONTACTORS (AC-6b) & STEP PROTECTION", (pnl_x + 60, pnl_y + 1400), height=25, layer="E-PFC-TEXT")

        # Draw contactor blocks
        for s in range(min(self.res.total_steps_count, 6)):
            bx = pnl_x + 70 + (s % 3) * 220
            by = pnl_y + 1150 - (s // 3) * 230
            self.writer.add_rectangle(bx, by, 180, 160, layer="E-PFC-DEVICES")
            self.writer.add_text(f"Step {s+1}: {int(self.res.steps[s].step_kvar)}kVAR", (bx + 15, by + 120), height=20, layer="E-PFC-TEXT")
            self.writer.add_text("AC-6b Contactor", (bx + 15, by + 80), height=18, layer="E-PFC-DIMS")
            self.writer.add_text(f"Fuse: {self.res.steps[s].step_fuse_or_mccb_a}A", (bx + 15, by + 40), height=18, layer="E-PFC-DIMS")

        # Bottom Compartment: Detuned Reactors & Heavy-Duty Capacitors
        self.writer.add_rectangle(pnl_x + 40, pnl_y + 50, pnl_w - 80, 750, layer="E-PFC-FRAME")
        self.writer.add_text(f"7% DETUNED REACTORS & HEAVY-DUTY {self.res.capacitor_rated_voltage_v:.0f}V CAPACITOR CELLS", (pnl_x + 60, pnl_y + 750), height=25, layer="E-PFC-TEXT")

        # Iron-core reactor symbols (Coils)
        for r in range(min(self.res.total_steps_count, 4)):
            rx = pnl_x + 80 + r * 170
            ry = pnl_y + 450
            self.writer.add_rectangle(rx, ry, 130, 200, layer="E-PFC-REACTOR")
            self.writer.add_text("7% REACTOR", (rx + 10, ry + 150), height=18, layer="E-PFC-REACTOR")
            self.writer.add_text(f"{self.res.steps[r].reactor_inductance_mh} mH", (rx + 20, ry + 100), height=18, layer="E-PFC-DIMS")

        # Cylindrical Capacitors (Cans)
        for c in range(min(self.res.total_steps_count, 4)):
            cx = pnl_x + 100 + c * 170
            cy = pnl_y + 200
            self.writer.add_rectangle(cx, cy, 90, 180, layer="E-PFC-CAPACITOR")
            self.writer.add_text("CAPACITOR", (cx + 5, cy + 130), height=16, layer="E-PFC-CAPACITOR")
            self.writer.add_text(f"{self.res.capacitor_rated_voltage_v:.0f}V Cell", (cx + 10, cy + 80), height=16, layer="E-PFC-DIMS")

        # Forced ventilation louvers and roof fan
        self.writer.add_rectangle(pnl_x + 250, pnl_y + pnl_h, 300, 80, layer="E-PFC-FRAME")
        self.writer.add_text("FORCED EXHAUST FAN", (pnl_x + 290, pnl_y + pnl_h + 45), height=25, layer="E-PFC-DEVICES")

        # -------------------------------------------------------------
        # VIEW 2: Single-Line Schematic of Detuned Capacitor Step
        # -------------------------------------------------------------
        sch_x = pnl_w + 300.0
        sch_y = 1000.0

        self.writer.add_text("DETUNED CAPACITOR STEP SINGLE-LINE SCHEMATIC (ANTI-RESONANCE)", (sch_x, sch_y + 1600), height=70, layer="E-PFC-TEXT")

        # 3-Phase Main Busbar
        self.writer.add_line((sch_x, sch_y + 1400), (sch_x + 1000, sch_y + 1400), layer="E-PFC-BUS")
        self.writer.add_line((sch_x, sch_y + 1370), (sch_x + 1000, sch_y + 1370), layer="E-PFC-BUS")
        self.writer.add_line((sch_x, sch_y + 1340), (sch_x + 1000, sch_y + 1340), layer="E-PFC-BUS")
        self.writer.add_text("400V 3-PHASE MAIN BUSBAR", (sch_x + 20, sch_y + 1430), height=30, layer="E-PFC-BUS")

        # Step HRC Fuse / MCCB
        self.writer.add_rectangle(sch_x + 200, sch_y + 1100, 100, 150, layer="E-PFC-DEVICES")
        self.writer.add_text("STEP MCCB/FUSE", (sch_x + 330, sch_y + 1200), height=30, layer="E-PFC-TEXT")
        self.writer.add_text(f"Rating: {self.res.steps[0].step_fuse_or_mccb_a}A HRC", (sch_x + 330, sch_y + 1150), height=25, layer="E-PFC-DIMS")

        # AC-6b Contactor with Early-Make Resistors
        self.writer.add_rectangle(sch_x + 200, sch_y + 800, 100, 180, layer="E-PFC-DEVICES")
        self.writer.add_text("CAPACITOR CONTACTOR (AC-6b)", (sch_x + 330, sch_y + 920), height=30, layer="E-PFC-TEXT")
        self.writer.add_text("Pre-charge Damping Resistors", (sch_x + 330, sch_y + 870), height=25, layer="E-PFC-DIMS")
        self.writer.add_text(f"Current Rating: {self.res.steps[0].contactor_rating_ac6b_a}A", (sch_x + 330, sch_y + 820), height=25, layer="E-PFC-DIMS")

        # 7% Detuned Series Reactor
        self.writer.add_rectangle(sch_x + 200, sch_y + 500, 100, 180, layer="E-PFC-REACTOR")
        self.writer.add_text(f"7% DETUNED REACTOR ({self.res.steps[0].reactor_inductance_mh} mH)", (sch_x + 330, sch_y + 620), height=30, layer="E-PFC-REACTOR")
        self.writer.add_text(f"Tuning Frequency: {self.res.tuning_frequency_hz} Hz", (sch_x + 330, sch_y + 570), height=25, layer="E-PFC-DIMS")
        self.writer.add_text("Class H Iron Core, Cu Winding", (sch_x + 330, sch_y + 520), height=25, layer="E-PFC-DIMS")

        # Heavy-Duty Shunt Capacitor Cell
        self.writer.add_rectangle(sch_x + 200, sch_y + 200, 100, 180, layer="E-PFC-CAPACITOR")
        self.writer.add_text(f"HEAVY-DUTY CAPACITOR ({self.res.capacitor_rated_voltage_v:.0f}V)", (sch_x + 330, sch_y + 320), height=30, layer="E-PFC-CAPACITOR")
        self.writer.add_text(f"Step Output: {self.res.steps[0].effective_kvar} kVAR", (sch_x + 330, sch_y + 270), height=25, layer="E-PFC-DIMS")
        self.writer.add_text("Internal Discharge Resistors (<50V in 60s)", (sch_x + 330, sch_y + 220), height=25, layer="E-PFC-DIMS")

        # Vertical Wiring
        self.writer.add_line((sch_x + 250, sch_y + 1340), (sch_x + 250, sch_y + 1250), layer="E-PFC-BUS")
        self.writer.add_line((sch_x + 250, sch_y + 1100), (sch_x + 250, sch_y + 980), layer="E-PFC-BUS")
        self.writer.add_line((sch_x + 250, sch_y + 800), (sch_x + 250, sch_y + 680), layer="E-PFC-BUS")
        self.writer.add_line((sch_x + 250, sch_y + 500), (sch_x + 250, sch_y + 380), layer="E-PFC-BUS")

        # -------------------------------------------------------------
        # VIEW 3: Engineering Specifications Legend Table
        # -------------------------------------------------------------
        tbl_x = 0.0
        tbl_y = -700.0
        self.writer.add_rectangle(tbl_x, tbl_y, 2500, 500, layer="E-PFC-FRAME")
        self.writer.add_text("APFC SYSTEM DESIGN CRITERIA & INSTALLATION SPECIFICATIONS", (tbl_x + 50, tbl_y + 440), height=50, layer="E-PFC-TEXT")

        lines = [
            ("Power Factor Target:", f"Corrects facility power factor from {self.res.initial_power_factor:.2f} to {self.res.target_power_factor:.2f}, releasing {self.res.apparent_power_released_kva} kVA"),
            ("Anti-Resonance Tuning:", f"{self.res.detuned_reactor_percent}% series reactor creates 227 Hz anti-resonance point safely below 5th harmonic (300 Hz)"),
            ("Capacitor Overvoltage:", f"Fundamental voltage rise Vc = 430V; heavy-duty {self.res.capacitor_rated_voltage_v:.0f}V cells prevent premature dielectric puncture"),
            ("Harmonic Overcurrent:", f"All switchgear, contactors, and internal wiring sized for 1.43 x In under IEC 61921"),
        ]

        for i, (hdr, val) in enumerate(lines):
            row_y = tbl_y + 350 - i * 90
            self.writer.add_text(f"• {hdr}", (tbl_x + 60, row_y), height=35, layer="E-PFC-TEXT")
            self.writer.add_text(val, (tbl_x + 550, row_y), height=32, layer="E-PFC-DIMS")

        self.writer.save(filepath)
        return filepath
