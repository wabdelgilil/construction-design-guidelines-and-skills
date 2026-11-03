"""
AutoCAD DXF Exporter for Public Address & Voice Alarm (PA/VA) A/B Interleaved Layout and Rack Schematics.
"""

from pathlib import Path
from core.exporters.dxf_writer import DXFWriter
from electrical.low_current_elv.public_address_pava.scripts.design_engine import PAVADesignResult


class PAVADXFExporter:
    """Exports PA/VA acoustic ceiling layouts, A/B circuits, and rack schematics to AutoCAD .dxf format."""

    def __init__(self, result: PAVADesignResult):
        self.res = result
        self.writer = DXFWriter("pava_acoustic_layout.dxf")
        self._setup_layers()

    def _setup_layers(self):
        layers = [
            ("E-PAVA-WALL", 8),       # Dark Grey: Architectural walls
            ("E-PAVA-CIRCA", 4),      # Cyan: Circuit A Loudspeakers & Wiring
            ("E-PAVA-CIRCB", 6),      # Magenta: Circuit B Loudspeakers & Wiring
            ("E-PAVA-RACK", 7),       # White: 19" Rack Equipment & Controller
            ("E-PAVA-POWER", 1),      # Red: 24V DC Charger & Battery
            ("E-PAVA-DIMS", 2),       # Yellow: Dimensions and SPL marks
            ("E-PAVA-TEXT", 7),       # White: Titles and text labels
        ]
        for name, color in layers:
            if name not in self.writer.doc.layers:
                lyr = self.writer.doc.layers.add(name)
                lyr.color = color

    def export(self, filepath: Path) -> Path:
        # Title Block
        self.writer.add_text(
            "PUBLIC ADDRESS & VOICE ALARM (PA/VA) - A/B DUAL INTERLEAVED LAYOUT & RACK RISER",
            (0, 3100),
            height=120,
            layer="E-PAVA-TEXT",
        )
        self.writer.add_text(
            f"Project: {self.res.project_name} | Code: {self.res.standard_used} | Total Speakers: {self.res.total_speakers_count} | 100V Dual Redundant Line (EN 54-16 / EN 54-24)",
            (0, 2950),
            height=70,
            layer="E-PAVA-TEXT",
        )

        # -------------------------------------------------------------
        # VIEW 1: Zone Ceiling Layout & A/B Interleaving
        # -------------------------------------------------------------
        plan_x = 0.0
        plan_y = 600.0
        plan_w = 12000.0
        plan_h = 2200.0   # Escape Corridor

        self.writer.add_text("TYPICAL EGRESS CORRIDOR - DUAL A/B INTERLEAVED LOUDSPEAKER DISTRIBUTION", (plan_x, plan_y + plan_h + 100), height=60, layer="E-PAVA-TEXT")

        # Corridor Boundary Walls
        self.writer.add_rectangle(plan_x, plan_y, plan_w, plan_h, layer="E-PAVA-WALL")
        self.writer.add_text("EGRESS CORRIDOR (ESCAPE ROUTE - EN 54 COMPLIANT)", (plan_x + 3500, plan_y + 100), height=50, layer="E-PAVA-WALL")

        # Loudspeakers along corridor centerline (y = plan_y + plan_h / 2)
        spk_y = plan_y + plan_h / 2.0
        spacing = 2000.0  # 2m spacing in drawing

        for i in range(6):
            spk_x = plan_x + 1000.0 + i * spacing
            is_circuit_a = (i % 2 == 0)

            if is_circuit_a:
                lyr = "E-PAVA-CIRCA"
                tag = f"A{i//2 + 1}"
            else:
                lyr = "E-PAVA-CIRCB"
                tag = f"B{i//2 + 1}"

            # Outer circle (Loudspeaker grill)
            self.writer.msp.add_circle((spk_x, spk_y), 60, dxfattribs={"layer": lyr})
            # Inner circle (Cone)
            self.writer.msp.add_circle((spk_x, spk_y), 30, dxfattribs={"layer": lyr})
            # Speaker Tag
            self.writer.add_text(tag, (spk_x - 20, spk_y + 80), height=35, layer=lyr)
            self.writer.add_text("3W 100V", (spk_x - 35, spk_y - 110), height=28, layer="E-PAVA-DIMS")

        # Connecting Cable Runs
        # Circuit A Homing line (Cyan)
        self.writer.add_line((plan_x, spk_y + 30), (plan_x + 1000, spk_y + 30), layer="E-PAVA-CIRCA")
        for i in range(0, 5, 2):
            x1 = plan_x + 1000.0 + i * spacing
            x2 = plan_x + 1000.0 + (i + 2) * spacing
            if x2 < plan_x + plan_w:
                self.writer.add_line((x1 + 60, spk_y + 30), (x2 - 60, spk_y + 30), layer="E-PAVA-CIRCA")

        # Circuit B Homing line (Magenta)
        self.writer.add_line((plan_x, spk_y - 30), (plan_x + 3000, spk_y - 30), layer="E-PAVA-CIRCB")
        for i in range(1, 5, 2):
            x1 = plan_x + 1000.0 + i * spacing
            x2 = plan_x + 1000.0 + (i + 2) * spacing
            if x2 < plan_x + plan_w:
                self.writer.add_line((x1 + 60, spk_y - 30), (x2 - 60, spk_y - 30), layer="E-PAVA-CIRCB")

        self.writer.add_text("<-- CIRCUIT A (2x1.5mm2 FP200)", (plan_x - 450, spk_y + 70), height=35, layer="E-PAVA-CIRCA")
        self.writer.add_text("<-- CIRCUIT B (2x1.5mm2 FP200)", (plan_x - 450, spk_y - 100), height=35, layer="E-PAVA-CIRCB")

        # -------------------------------------------------------------
        # VIEW 2: 19" Equipment Rack & Audio System Schematic
        # -------------------------------------------------------------
        rck_x = 13500.0
        rck_y = 400.0
        rck_w = 700.0
        rck_h = 2400.0

        self.writer.add_text("VOICE ALARM SYSTEM RACK & 100V AMPLIFIER SCHEMATIC (EN 54-16)", (rck_x, rck_y + rck_h + 100), height=60, layer="E-PAVA-TEXT")

        # Outer Rack Frame
        self.writer.add_rectangle(rck_x, rck_y, rck_w, rck_h, layer="E-PAVA-RACK")
        self.writer.add_text("19\" PAVA EQUIPMENT RACK", (rck_x + 150, rck_y - 60), height=40, layer="E-PAVA-TEXT")

        # Unit 1: Master Voice Alarm Controller (Top)
        u1_y = rck_y + rck_h - 350
        self.writer.add_rectangle(rck_x + 40, u1_y, rck_w - 80, 280, layer="E-PAVA-RACK")
        self.writer.add_text("EN 54-16 MASTER CONTROLLER", (rck_x + 60, u1_y + 200), height=32, layer="E-PAVA-TEXT")
        self.writer.add_text("Digital Audio Matrix & Message Player", (rck_x + 60, u1_y + 140), height=25, layer="E-PAVA-DIMS")
        self.writer.add_text("FACP Fire Alarm Interface (RS485/Relay)", (rck_x + 60, u1_y + 80), height=25, layer="E-PAVA-POWER")

        # Unit 2: Fireman Emergency Microphone Panel
        u2_y = u1_y - 250
        self.writer.add_rectangle(rck_x + 40, u2_y, rck_w - 80, 200, layer="E-PAVA-RACK")
        self.writer.add_text("EMERGENCY PAGING MICROPHONE", (rck_x + 60, u2_y + 130), height=30, layer="E-PAVA-TEXT")
        self.writer.add_text("Priority 1 Handheld Mic & Zone Keys", (rck_x + 60, u2_y + 70), height=25, layer="E-PAVA-DIMS")

        # Unit 3: Main Class-D Power Amplifiers
        u3_y = u2_y - 350
        self.writer.add_rectangle(rck_x + 40, u3_y, rck_w - 80, 280, layer="E-PAVA-CIRCA")
        self.writer.add_text(f"MAIN POWER AMPLIFIERS ({self.res.main_amplifiers_count}x {self.res.amplifier_rating_per_unit_w}W)", (rck_x + 60, u3_y + 200), height=30, layer="E-PAVA-CIRCA")
        self.writer.add_text("Class-D High Efficiency 100V Channels", (rck_x + 60, u3_y + 140), height=25, layer="E-PAVA-DIMS")
        self.writer.add_text("Pilot-Tone End-of-Line Surveillance", (rck_x + 60, u3_y + 80), height=25, layer="E-PAVA-DIMS")

        # Unit 4: Standby Amplifier (Hot-Standby N+1)
        u4_y = u3_y - 280
        self.writer.add_rectangle(rck_x + 40, u4_y, rck_w - 80, 220, layer="E-PAVA-CIRCB")
        self.writer.add_text(f"HOT-STANDBY AMPLIFIER (1x {self.res.amplifier_rating_per_unit_w}W)", (rck_x + 60, u4_y + 150), height=30, layer="E-PAVA-CIRCB")
        self.writer.add_text("Automatic N+1 Failover Switch (<100ms)", (rck_x + 60, u4_y + 90), height=25, layer="E-PAVA-TEXT")

        # Unit 5: EN 54-4 Battery Charger & Power Supply
        u5_y = u4_y - 300
        self.writer.add_rectangle(rck_x + 40, u5_y, rck_w - 80, 240, layer="E-PAVA-POWER")
        self.writer.add_text("EN 54-4 POWER SUPPLY & CHARGER", (rck_x + 60, u5_y + 170), height=30, layer="E-PAVA-POWER")
        self.writer.add_text("24V DC Regulated Bus (Supervised)", (rck_x + 60, u5_y + 110), height=25, layer="E-PAVA-DIMS")
        self.writer.add_text("230V AC Essential Mains Supply", (rck_x + 60, u5_y + 50), height=25, layer="E-PAVA-TEXT")

        # Unit 6: VRLA Battery Set (Bottom of Rack)
        u6_y = rck_y + 60
        self.writer.add_rectangle(rck_x + 40, u6_y, rck_w - 80, 320, layer="E-PAVA-POWER")
        self.writer.add_text("24V VRLA EMERGENCY BATTERY SET", (rck_x + 60, u6_y + 240), height=30, layer="E-PAVA-POWER")
        self.writer.add_text(f"2x 12V {self.res.selected_battery_ah} Ah in Series", (rck_x + 60, u6_y + 170), height=25, layer="E-PAVA-TEXT")
        self.writer.add_text("24h Standby + 30m Full Alarm Autonomy", (rck_x + 60, u6_y + 100), height=25, layer="E-PAVA-DIMS")

        # -------------------------------------------------------------
        # VIEW 3: Acoustic Legend & Standards Table
        # -------------------------------------------------------------
        tbl_x = 0.0
        tbl_y = -700.0
        self.writer.add_rectangle(tbl_x, tbl_y, 2500, 500, layer="E-PAVA-WALL")
        self.writer.add_text("PUBLIC ADDRESS & VOICE ALARM (PA/VA) DESIGN SPECIFICATIONS", (tbl_x + 50, tbl_y + 440), height=50, layer="E-PAVA-TEXT")

        lines = [
            ("Loudspeaker Line Voltage:", "100V Constant-Voltage Distributed Line with multi-tap matching transformers"),
            ("A/B Circuit Interleaving:", "Adjacent speakers wired to Circuit A and Circuit B to preserve broadcast if one circuit is severed"),
            ("Intelligibility Target (STI):", "Speech Transmission Index STI >= 0.50 (CIS >= 0.70) in all acoustically conditioned areas"),
            ("Amplifier Redundancy:", f"N+1 Hot-Standby amplifier ({self.res.amplifier_rating_per_unit_w}W) with automatic line surveillance and transfer"),
        ]

        for i, (hdr, val) in enumerate(lines):
            row_y = tbl_y + 350 - i * 90
            self.writer.add_text(f"• {hdr}", (tbl_x + 60, row_y), height=35, layer="E-PAVA-TEXT")
            self.writer.add_text(val, (tbl_x + 550, row_y), height=32, layer="E-PAVA-DIMS")

        self.writer.save(filepath)
        return filepath
