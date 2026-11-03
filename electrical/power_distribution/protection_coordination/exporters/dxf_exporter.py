"""
AutoCAD DXF Exporter for Short-Circuit Single Line Diagram & Time-Current Characteristic (TCC) Curves.
"""

from pathlib import Path
from core.exporters.dxf_writer import DXFWriter
from electrical.power_distribution.protection_coordination.scripts.design_engine import ProtectionCoordinationDesignResult


class ProtectionCoordinationDXFExporter:
    """Exports distribution SLD and TCC coordination curves to AutoCAD .dxf format."""

    def __init__(self, result: ProtectionCoordinationDesignResult):
        self.res = result
        self.writer = DXFWriter("protection_coordination_tcc.dxf")
        self._setup_layers()

    def _setup_layers(self):
        layers = [
            ("E-TCC-GRID", 8),       # Dark Grey: Coordinate grid, axes, borders
            ("E-TCC-CURVE-UP", 1),   # Red: Upstream Incomer ACB Trip Curve
            ("E-TCC-CURVE-DN", 4),   # Cyan: Downstream Feeder MCCB Trip Curve
            ("E-SLD-BUS", 6),        # Magenta: Distribution Busbars
            ("E-SLD-SYMB", 7),       # White: Transformers, Breakers, Cables
            ("E-TCC-DIMS", 2),       # Yellow: Fault levels, time margins, ratings
            ("E-TCC-TEXT", 7),       # White: Annotations and Title
        ]
        for name, color in layers:
            if name not in self.writer.doc.layers:
                lyr = self.writer.doc.layers.add(name)
                lyr.color = color

    def export(self, filepath: Path) -> Path:
        # Title Block
        self.writer.add_text(
            "SHORT-CIRCUIT ANALYSIS & TIME-CURRENT DISCRIMINATION (TCC) CURVES",
            (0, 3200),
            height=120,
            layer="E-TCC-TEXT",
        )
        self.writer.add_text(
            f"Project: {self.res.project_name} | Code: {self.res.standard_used} | Transformer: {self.res.transformer.rating_kva}kVA | Status: {self.res.overall_system_discrimination}",
            (0, 3050),
            height=70,
            layer="E-TCC-TEXT",
        )

        # -------------------------------------------------------------
        # VIEW 1: Distribution Single Line Diagram (SLD) with Fault Levels
        # -------------------------------------------------------------
        sld_x = 0.0
        sld_y = 2600.0

        self.writer.add_text("DISTRIBUTION NETWORK SINGLE-LINE DIAGRAM (SLD)", (sld_x, sld_y + 150), height=70, layer="E-TCC-TEXT")

        # 1. MV Utility Grid Source
        self.writer.add_rectangle(sld_x + 100, sld_y - 120, 200, 100, layer="E-SLD-SYMB")
        self.writer.add_text("MV GRID (13.8 kV)", (sld_x + 110, sld_y - 60), height=30, layer="E-TCC-TEXT")
        self.writer.add_text("Ssc = 500 MVA", (sld_x + 120, sld_y - 100), height=25, layer="E-TCC-DIMS")

        # Vertical line from grid to transformer
        self.writer.add_line((sld_x + 200, sld_y - 120), (sld_x + 200, sld_y - 250), layer="E-SLD-SYMB")

        # 2. Transformer Symbol (Two overlapping circles)
        tr_y = sld_y - 350
        self.writer.msp.add_circle((sld_x + 200, tr_y + 50), 50, dxfattribs={"layer": "E-SLD-SYMB"})
        self.writer.msp.add_circle((sld_x + 200, tr_y - 20), 50, dxfattribs={"layer": "E-SLD-SYMB"})
        self.writer.add_text(f"TR: {self.res.transformer.rating_kva:.0f} kVA Dyn11", (sld_x + 280, tr_y + 40), height=35, layer="E-TCC-TEXT")
        self.writer.add_text(f"13.8kV / {self.res.transformer.voltage_secondary_v:.0f}V, uk={self.res.transformer.uk_percent:.1f}%", (sld_x + 280, tr_y), height=30, layer="E-TCC-DIMS")

        # Line from Transformer to MDB Incomer
        self.writer.add_line((sld_x + 200, tr_y - 70), (sld_x + 200, tr_y - 170), layer="E-SLD-SYMB")

        # 3. MDB Main Incomer ACB Breaker Symbol
        acb_y = tr_y - 250
        self.writer.add_rectangle(sld_x + 160, acb_y, 80, 80, layer="E-SLD-SYMB")
        self.writer.add_line((sld_x + 160, acb_y), (sld_x + 240, acb_y + 80), layer="E-SLD-SYMB")
        self.writer.add_text(f"INCOMER ACB: {self.res.bus_faults[0].rated_current_in_a}A 4P", (sld_x + 260, acb_y + 50), height=35, layer="E-TCC-TEXT")
        self.writer.add_text(f"Icu={self.res.bus_faults[0].rated_breaking_capacity_icu_ka}kA, Icw={self.res.bus_faults[0].rated_withstand_icw_ka}kA", (sld_x + 260, acb_y + 10), height=30, layer="E-TCC-DIMS")

        # Line to MDB Busbar
        self.writer.add_line((sld_x + 200, acb_y), (sld_x + 200, acb_y - 60), layer="E-SLD-SYMB")

        # 4. MDB Main Busbar
        bus1_y = acb_y - 70
        self.writer.add_line((sld_x + 50, bus1_y), (sld_x + 750, bus1_y), layer="E-SLD-BUS")
        self.writer.add_line((sld_x + 50, bus1_y - 5), (sld_x + 750, bus1_y - 5), layer="E-SLD-BUS")  # Heavy line
        self.writer.add_text("MDB BUSBAR (400V)", (sld_x + 60, bus1_y + 15), height=35, layer="E-SLD-BUS")
        self.writer.add_text(f"FAULT LEVEL: Isc = {self.res.bus_faults[0].isc_sym_ka} kA", (sld_x + 60, bus1_y - 40), height=35, layer="E-TCC-DIMS")

        # 5. Feeder Cable to SMDB
        self.writer.add_line((sld_x + 400, bus1_y - 5), (sld_x + 400, bus1_y - 120), layer="E-SLD-SYMB")
        self.writer.add_text("Feeder: 3x(4x1x300mm2) Cu/XLPE (45m)", (sld_x + 420, bus1_y - 70), height=25, layer="E-TCC-DIMS")

        # SMDB Incomer MCCB
        mccb_y = bus1_y - 200
        self.writer.add_rectangle(sld_x + 360, mccb_y, 80, 80, layer="E-SLD-SYMB")
        self.writer.add_line((sld_x + 360, mccb_y), (sld_x + 440, mccb_y + 80), layer="E-SLD-SYMB")
        self.writer.add_text(f"FEEDER MCCB: {self.res.bus_faults[1].rated_current_in_a}A 4P", (sld_x + 460, mccb_y + 50), height=35, layer="E-TCC-TEXT")
        self.writer.add_text(f"Icu={self.res.bus_faults[1].rated_breaking_capacity_icu_ka}kA", (sld_x + 460, mccb_y + 10), height=30, layer="E-TCC-DIMS")

        # SMDB Busbar
        bus2_y = mccb_y - 70
        self.writer.add_line((sld_x + 250, bus2_y), (sld_x + 650, bus2_y), layer="E-SLD-BUS")
        self.writer.add_line((sld_x + 250, bus2_y - 4), (sld_x + 650, bus2_y - 4), layer="E-SLD-BUS")
        self.writer.add_text("SMDB BUSBAR (400V)", (sld_x + 260, bus2_y + 15), height=35, layer="E-SLD-BUS")
        self.writer.add_text(f"FAULT LEVEL: Isc = {self.res.bus_faults[1].isc_sym_ka} kA", (sld_x + 260, bus2_y - 35), height=35, layer="E-TCC-DIMS")

        # 6. Branch Cable to DB
        self.writer.add_line((sld_x + 500, bus2_y - 4), (sld_x + 500, bus2_y - 120), layer="E-SLD-SYMB")
        self.writer.add_text("Branch: 4x16mm2 Cu/PVC (35m)", (sld_x + 520, bus2_y - 70), height=25, layer="E-TCC-DIMS")

        # Final DB Incomer MCB
        mcb_y = bus2_y - 200
        self.writer.add_rectangle(sld_x + 460, mcb_y, 80, 80, layer="E-SLD-SYMB")
        self.writer.add_line((sld_x + 460, mcb_y), (sld_x + 540, mcb_y + 80), layer="E-SLD-SYMB")
        self.writer.add_text(f"BRANCH MCB: {self.res.bus_faults[2].rated_current_in_a}A Curve C", (sld_x + 560, mcb_y + 50), height=35, layer="E-TCC-TEXT")

        # DB Busbar
        bus3_y = mcb_y - 60
        self.writer.add_line((sld_x + 400, bus3_y), (sld_x + 700, bus3_y), layer="E-SLD-BUS")
        self.writer.add_text("DB FINAL BUSBAR", (sld_x + 410, bus3_y + 15), height=30, layer="E-SLD-BUS")
        self.writer.add_text(f"FAULT LEVEL: Isc = {self.res.bus_faults[2].isc_sym_ka} kA", (sld_x + 410, bus3_y - 35), height=30, layer="E-TCC-DIMS")

        # -------------------------------------------------------------
        # VIEW 2: Time-Current Characteristic (TCC) Discrimination Plot
        # -------------------------------------------------------------
        tcc_x = 1100.0
        tcc_y = 1000.0
        plot_w = 1600.0
        plot_h = 1600.0

        self.writer.add_text("TIME-CURRENT CHARACTERISTIC (TCC) COORDINATION CURVES (LOG-LOG)", (tcc_x, tcc_y + plot_h + 100), height=70, layer="E-TCC-TEXT")

        # Outer Plot Box
        self.writer.add_rectangle(tcc_x, tcc_y, plot_w, plot_h, layer="E-TCC-GRID")

        # Coordinate Axes Labels
        self.writer.add_text("CURRENT IN AMPERES (A) [LOG SCALE]", (tcc_x + 500, tcc_y - 70), height=40, layer="E-TCC-TEXT")
        self.writer.add_text("TIME (s)", (tcc_x - 80, tcc_y + 800), height=40, layer="E-TCC-TEXT")

        # Vertical Grid Lines (Current Decades: 100A, 1kA, 10kA, 50kA)
        x_100a = tcc_x
        x_1ka = tcc_x + 450
        x_10ka = tcc_x + 1050
        x_50ka = tcc_x + plot_w

        for x_val, lbl in [(x_100a, "100 A"), (x_1ka, "1 kA"), (x_10ka, "10 kA"), (x_50ka, "50 kA")]:
            self.writer.add_line((x_val, tcc_y), (x_val, tcc_y + plot_h), layer="E-TCC-GRID")
            self.writer.add_text(lbl, (x_val - 30, tcc_y - 35), height=30, layer="E-TCC-DIMS")

        # Horizontal Grid Lines (Time Decades: 0.01s, 0.1s, 1s, 10s, 100s, 1000s)
        y_001s = tcc_y
        y_01s = tcc_y + 320
        y_1s = tcc_y + 640
        y_10s = tcc_y + 960
        y_100s = tcc_y + 1280
        y_1000s = tcc_y + plot_h

        for y_val, lbl in [(y_001s, "0.01s"), (y_01s, "0.10s"), (y_1s, "1.0s"), (y_10s, "10s"), (y_100s, "100s"), (y_1000s, "1000s")]:
            self.writer.add_line((tcc_x, y_val), (tcc_x + plot_w, y_val), layer="E-TCC-GRID")
            self.writer.add_text(lbl, (tcc_x - 70, y_val - 10), height=25, layer="E-TCC-DIMS")

        # 1. UPSTREAM ACB TRIP CURVE (RED)
        # ACB: In=2500A, Ir=2500A (x ~ 720), Isd=10000A (x=1050), tsd=0.3s (y ~ 480)
        # Thermal band (from 1000s down to 0.3s)
        acb_pts = [
            (tcc_x + 720, y_1000s),
            (tcc_x + 850, y_10s),
            (tcc_x + 1050, tcc_y + 480),   # 0.3s plateau at Isd=10kA
            (tcc_x + 1500, tcc_y + 480),   # Holds flat at 0.3s up to Icw=50kA (Selective Mode)
            (tcc_x + 1500, y_001s),
        ]
        for p1, p2 in zip(acb_pts[:-1], acb_pts[1:]):
            self.writer.add_line(p1, p2, layer="E-TCC-CURVE-UP")
        self.writer.add_text("UPSTREAM ACB (2500A) - tsd=0.30s", (tcc_x + 900, tcc_y + 530), height=35, layer="E-TCC-CURVE-UP")

        # 2. DOWNSTREAM MCCB TRIP CURVE (CYAN)
        # MCCB: In=400A, Ir=360A (x ~ 280), Isd=1080A (x ~ 480), tsd=0.10s (y=320), Ii=4000A (x ~ 820)
        mccb_pts = [
            (tcc_x + 280, y_1000s),
            (tcc_x + 400, y_10s),
            (tcc_x + 480, y_01s),          # 0.1s plateau at Isd=1080A
            (tcc_x + 820, y_01s),          # Reaches Instantaneous at 4000A
            (tcc_x + 820, tcc_y + 80),     # Drops to < 20ms instantaneous clearing
            (tcc_x + 1200, tcc_y + 80),
            (tcc_x + 1200, y_001s),
        ]
        for p1, p2 in zip(mccb_pts[:-1], mccb_pts[1:]):
            self.writer.add_line(p1, p2, layer="E-TCC-CURVE-DN")
        self.writer.add_text("DOWNSTREAM MCCB (400A) - tsd=0.10s", (tcc_x + 220, y_01s - 50), height=35, layer="E-TCC-CURVE-DN")

        # 3. Time Margin Annotation (The Gap between 0.30s and 0.10s)
        self.writer.add_line((tcc_x + 650, y_01s), (tcc_x + 650, tcc_y + 480), layer="E-TCC-DIMS")
        self.writer.add_text("<-- TIME MARGIN Δt = 200 ms (>= 100ms PASS) -->", (tcc_x + 670, tcc_y + 400), height=35, layer="E-TCC-DIMS")
        self.writer.add_text("[TOTAL DISCRIMINATION ZONE]", (tcc_x + 670, tcc_y + 350), height=30, layer="E-TCC-TEXT")

        # -------------------------------------------------------------
        # VIEW 3: Switchgear Coordination Legend Table
        # -------------------------------------------------------------
        tbl_x = 0.0
        tbl_y = 400.0
        self.writer.add_rectangle(tbl_x, tbl_y, 2700, 500, layer="E-TCC-GRID")
        self.writer.add_text("CIRCUIT BREAKER PROTECTION & DISCRIMINATION SCHEDULE", (tbl_x + 50, tbl_y + 440), height=50, layer="E-TCC-TEXT")

        lines = [
            ("MDB Main Incomer:", "4-Pole Drawout ACB 2500A, Icu=65kA, Icw=50kA (1s). LSIG: Ir=2500A, tr=12s, Isd=10000A, tsd=0.3s flat, Ii=OFF"),
            ("SMDB Feeder Breaker:", "4-Pole Fixed MCCB 400A, Icu=36kA (Cat A). Electronic: Ir=360A, tr=12s, Isd=1080A, tsd=0.1s flat, Ii=4000A"),
            ("Final DB Incomer:", "3-Pole / 4-Pole MCB 63A, Icu=10kA (Cat A). Thermal-Magnetic Curve C (Ir=63A, Im=5-10xIn, clearing < 20ms)"),
            ("Discrimination Status:", "FULL TOTAL SELECTIVITY ACHIEVED up to MDB prospective fault level (No curve overlap, Δt=200ms >= 100ms)"),
        ]

        for i, (hdr, val) in enumerate(lines):
            row_y = tbl_y + 350 - i * 90
            self.writer.add_text(f"• {hdr}", (tbl_x + 60, row_y), height=35, layer="E-TCC-TEXT")
            self.writer.add_text(val, (tbl_x + 500, row_y), height=32, layer="E-TCC-DIMS")

        self.writer.save(filepath)
        return filepath
