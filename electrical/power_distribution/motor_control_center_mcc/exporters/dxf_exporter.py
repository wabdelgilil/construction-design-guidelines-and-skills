"""
AutoCAD DXF Exporter for Motor Control Center (MCC) Front Elevation and Starter Control Schematics.
"""

from pathlib import Path
from core.exporters.dxf_writer import DXFWriter
from electrical.power_distribution.motor_control_center_mcc.scripts.design_engine import MCCDesignResult


class MCCDXFExporter:
    """Exports MCC physical front elevation and starter wiring schematics to AutoCAD .dxf format."""

    def __init__(self, result: MCCDesignResult):
        self.res = result
        self.writer = DXFWriter("mcc_panel_elevation.dxf")
        self._setup_layers()

    def _setup_layers(self):
        layers = [
            ("E-MCC-FRAME", 8),      # Dark Grey: Panel frame, plinth, column borders
            ("E-MCC-CUBICLE", 6),    # Magenta: Individual starter compartments
            ("E-MCC-DEVICES", 4),    # Cyan: Meters, Pilot Lamps, HOA switches, push buttons
            ("E-MCC-POWER", 1),      # Red: Busbars, power lines, breakers
            ("E-MCC-CONTROL", 3),    # Green: Control circuit wiring, BMS interlocks
            ("E-MCC-DIMS", 2),       # Yellow: Dimensions and annotations
            ("E-MCC-TEXT", 7),       # White: Titles and labels
        ]
        for name, color in layers:
            if name not in self.writer.doc.layers:
                lyr = self.writer.doc.layers.add(name)
                lyr.color = color

    def export(self, filepath: Path) -> Path:
        # Title Block
        self.writer.add_text(
            "MOTOR CONTROL CENTER (MCC) - FRONT ELEVATION & STARTER SCHEMATIC",
            (0, 3100),
            height=120,
            layer="E-MCC-TEXT",
        )
        self.writer.add_text(
            f"Project: {self.res.project_name} | Code: {self.res.standard_used} | Motors: {self.res.total_motors_count} ({self.res.total_connected_kw}kW) | Incomer: {self.res.mcc_main_incomer_rating_a}A (Form 4b)",
            (0, 2950),
            height=70,
            layer="E-MCC-TEXT",
        )

        # -------------------------------------------------------------
        # VIEW 1: MCC Front Elevation (Multi-Column Form 4b Enclosure)
        # -------------------------------------------------------------
        mcc_x = 0.0
        mcc_y = 400.0
        col_w = 700.0    # 700mm column width
        col_h = 2100.0   # 2100mm height
        plinth_h = 100.0 # 100mm base plinth

        num_cols = self.res.total_columns_count
        total_mcc_w = num_cols * col_w

        # Base Plinth
        self.writer.add_rectangle(mcc_x, mcc_y - plinth_h, total_mcc_w, plinth_h, layer="E-MCC-FRAME")
        self.writer.add_text("BASE PLINTH (100mm C-CHANNEL)", (mcc_x + 100, mcc_y - 65), height=35, layer="E-MCC-TEXT")

        # Top Busbar Chamber (Horizontal running across all columns)
        self.writer.add_rectangle(mcc_x, mcc_y + col_h - 250, total_mcc_w, 250, layer="E-MCC-FRAME")
        self.writer.add_text(f"MAIN HORIZONTAL BUSBAR CHAMBER ({self.res.mcc_main_busbar_rating_a}A Cu 50kA/1s)", (mcc_x + 80, mcc_y + col_h - 150), height=35, layer="E-MCC-POWER")

        # Column 1: Incomer & Metering Column
        self.writer.add_rectangle(mcc_x, mcc_y, col_w, col_h - 250, layer="E-MCC-FRAME")
        self.writer.add_text("COLUMN 1: INCOMER", (mcc_x + 150, mcc_y + col_h - 300), height=35, layer="E-MCC-TEXT")

        # Incomer Metering Compartment
        self.writer.add_rectangle(mcc_x + 50, mcc_y + 1100, col_w - 100, 600, layer="E-MCC-CUBICLE")
        # Digital LCD Power Meter
        self.writer.add_rectangle(mcc_x + 200, mcc_y + 1400, 200, 150, layer="E-MCC-DEVICES")
        self.writer.add_text("POWER METER", (mcc_x + 220, mcc_y + 1470), height=25, layer="E-MCC-DEVICES")
        self.writer.add_text("V / I / kW / pf", (mcc_x + 230, mcc_y + 1430), height=20, layer="E-MCC-TEXT")

        # Phase Pilot Lamps (R-Y-B)
        self.writer.msp.add_circle((mcc_x + 150, mcc_y + 1600), 20, dxfattribs={"layer": "E-MCC-POWER"})
        self.writer.msp.add_circle((mcc_x + 300, mcc_y + 1600), 20, dxfattribs={"layer": "E-MCC-DIMS"})
        self.writer.msp.add_circle((mcc_x + 450, mcc_y + 1600), 20, dxfattribs={"layer": "E-MCC-DEVICES"})
        self.writer.add_text("R", (mcc_x + 143, mcc_y + 1590), height=22, layer="E-MCC-TEXT")
        self.writer.add_text("Y", (mcc_x + 293, mcc_y + 1590), height=22, layer="E-MCC-TEXT")
        self.writer.add_text("B", (mcc_x + 443, mcc_y + 1590), height=22, layer="E-MCC-TEXT")

        # Main Incomer ACB Compartment (Bottom of Col 1)
        self.writer.add_rectangle(mcc_x + 50, mcc_y + 100, col_w - 100, 950, layer="E-MCC-CUBICLE")
        self.writer.add_rectangle(mcc_x + 150, mcc_y + 350, 300, 500, layer="E-MCC-POWER")
        self.writer.add_text("MAIN INCOMER", (mcc_x + 200, mcc_y + 650), height=35, layer="E-MCC-TEXT")
        self.writer.add_text(f"{self.res.mcc_main_incomer_rating_a}A 4P ACB", (mcc_x + 210, mcc_y + 580), height=35, layer="E-MCC-POWER")
        self.writer.add_text("Drawout Form 4b", (mcc_x + 210, mcc_y + 510), height=25, layer="E-MCC-DIMS")

        # Feeder Columns (Motor Starter Cubicles)
        col_idx = 1
        curr_col_x = mcc_x + col_w
        curr_y = mcc_y + 100.0

        for m in self.res.motors:
            if curr_y + m.cubicle_height_mm > (mcc_y + col_h - 260):
                # Move to next column
                col_idx += 1
                curr_col_x += col_w
                curr_y = mcc_y + 100.0

            # Draw outer column frame if starting new column
            if curr_y == mcc_y + 100.0:
                self.writer.add_rectangle(curr_col_x, mcc_y, col_w, col_h - 250, layer="E-MCC-FRAME")
                self.writer.add_text(f"COLUMN {col_idx + 1}: STARTERS", (curr_col_x + 100, mcc_y + col_h - 300), height=35, layer="E-MCC-TEXT")

            # Draw Starter Cubicle
            cub_h = m.cubicle_height_mm
            self.writer.add_rectangle(curr_col_x + 40, curr_y, col_w - 80, cub_h - 20, layer="E-MCC-CUBICLE")

            # Cubicle door details: Nameplate, HOA, Run/Trip Lamps, Reset
            self.writer.add_text(f"[{m.tag}] {m.description}", (curr_col_x + 60, curr_y + cub_h - 60), height=25, layer="E-MCC-TEXT")
            self.writer.add_text(f"{m.rated_kw} kW ({m.rated_hp} HP) | {m.starting_method}", (curr_col_x + 60, curr_y + cub_h - 95), height=22, layer="E-MCC-DIMS")
            self.writer.add_text(f"FLA: {m.fla_a}A | Breaker: {m.mcp_breaker_rating_a}A", (curr_col_x + 60, curr_y + cub_h - 130), height=20, layer="E-MCC-DIMS")

            # HOA Selector Switch (Circle)
            self.writer.msp.add_circle((curr_col_x + col_w - 120, curr_y + cub_h - 70), 16, dxfattribs={"layer": "E-MCC-DEVICES"})
            self.writer.add_text("HOA", (curr_col_x + col_w - 135, curr_y + cub_h - 110), height=18, layer="E-MCC-TEXT")

            # Run (Green) and Trip (Red) Pilot Lamps
            self.writer.msp.add_circle((curr_col_x + col_w - 200, curr_y + cub_h - 70), 14, dxfattribs={"layer": "E-MCC-CONTROL"})
            self.writer.msp.add_circle((curr_col_x + col_w - 250, curr_y + cub_h - 70), 14, dxfattribs={"layer": "E-MCC-POWER"})
            self.writer.add_text("RUN", (curr_col_x + col_w - 212, curr_y + cub_h - 110), height=16, layer="E-MCC-TEXT")
            self.writer.add_text("TRIP", (curr_col_x + col_w - 265, curr_y + cub_h - 110), height=16, layer="E-MCC-TEXT")

            curr_y += cub_h

        # -------------------------------------------------------------
        # VIEW 2: Starter Power & Control Schematic (Typical Y-Δ / DOL)
        # -------------------------------------------------------------
        sch_x = total_mcc_w + 300.0
        sch_y = 1200.0

        self.writer.add_text("TYPICAL MOTOR STARTER POWER & CONTROL SCHEMATIC (TYPE 2 COORDINATION)", (sch_x, sch_y + 1400), height=70, layer="E-MCC-TEXT")

        # 3-Phase Busbar at top of schematic
        self.writer.add_line((sch_x, sch_y + 1200), (sch_x + 900, sch_y + 1200), layer="E-MCC-POWER")
        self.writer.add_line((sch_x, sch_y + 1170), (sch_x + 900, sch_y + 1170), layer="E-MCC-POWER")
        self.writer.add_line((sch_x, sch_y + 1140), (sch_x + 900, sch_y + 1140), layer="E-MCC-POWER")
        self.writer.add_text("L1, L2, L3 (400V 3-PHASE BUSBAR)", (sch_x + 20, sch_y + 1230), height=30, layer="E-MCC-POWER")

        # MCP Breaker Symbol
        self.writer.add_rectangle(sch_x + 150, sch_y + 900, 100, 150, layer="E-MCC-POWER")
        self.writer.add_text("MCP BREAKER", (sch_x + 280, sch_y + 980), height=30, layer="E-MCC-TEXT")
        self.writer.add_text("Short-Circuit Protection", (sch_x + 280, sch_y + 930), height=25, layer="E-MCC-DIMS")

        # Main Contactor (KM1)
        self.writer.add_rectangle(sch_x + 150, sch_y + 650, 100, 150, layer="E-MCC-POWER")
        self.writer.add_text("MAIN CONTACTOR (KM1)", (sch_x + 280, sch_y + 730), height=30, layer="E-MCC-TEXT")
        self.writer.add_text("AC-3 Rated Duty", (sch_x + 280, sch_y + 680), height=25, layer="E-MCC-DIMS")

        # Thermal Overload Relay (OL)
        self.writer.add_rectangle(sch_x + 150, sch_y + 400, 100, 150, layer="E-MCC-POWER")
        self.writer.add_text("THERMAL OVERLOAD (OL)", (sch_x + 280, sch_y + 480), height=30, layer="E-MCC-TEXT")
        self.writer.add_text("Class 10 (0.95 - 1.05 FLA)", (sch_x + 280, sch_y + 430), height=25, layer="E-MCC-DIMS")

        # Motor Circle (M 3~)
        self.writer.msp.add_circle((sch_x + 200, sch_y + 180), 90, dxfattribs={"layer": "E-MCC-POWER"})
        self.writer.add_text("M", (sch_x + 180, sch_y + 180), height=60, layer="E-MCC-TEXT")
        self.writer.add_text("3 ~", (sch_x + 180, sch_y + 130), height=40, layer="E-MCC-DIMS")
        self.writer.add_text("INDUCTION MOTOR", (sch_x + 320, sch_y + 180), height=35, layer="E-MCC-TEXT")

        # Vertical Power Lines Connecting Components
        self.writer.add_line((sch_x + 200, sch_y + 1140), (sch_x + 200, sch_y + 1050), layer="E-MCC-POWER")
        self.writer.add_line((sch_x + 200, sch_y + 900), (sch_x + 200, sch_y + 800), layer="E-MCC-POWER")
        self.writer.add_line((sch_x + 200, sch_y + 650), (sch_x + 200, sch_y + 550), layer="E-MCC-POWER")
        self.writer.add_line((sch_x + 200, sch_y + 400), (sch_x + 200, sch_y + 270), layer="E-MCC-POWER")

        # BMS Interface Callouts (Right side of schematic)
        bms_x = sch_x + 850
        self.writer.add_rectangle(bms_x, sch_y + 350, 400, 500, layer="E-MCC-CONTROL")
        self.writer.add_text("BMS INTERFACE TERMINALS", (bms_x + 30, sch_y + 800), height=30, layer="E-MCC-CONTROL")
        self.writer.add_text("• Run Status (Dry Contact NO)", (bms_x + 30, sch_y + 730), height=25, layer="E-MCC-TEXT")
        self.writer.add_text("• Trip Alarm (Dry Contact NC)", (bms_x + 30, sch_y + 660), height=25, layer="E-MCC-TEXT")
        self.writer.add_text("• Remote Start/Stop (DO)", (bms_x + 30, sch_y + 590), height=25, layer="E-MCC-TEXT")
        self.writer.add_text("• HOA Auto Status (DI)", (bms_x + 30, sch_y + 520), height=25, layer="E-MCC-TEXT")
        self.writer.add_text("• Emergency Fire Stop Interlock", (bms_x + 30, sch_y + 450), height=25, layer="E-MCC-DIMS")

        self.writer.save(filepath)
        return filepath
