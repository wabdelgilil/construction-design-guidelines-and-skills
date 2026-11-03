"""
AutoCAD DXF Exporter for Small Power Socket Circuits.
Generates electrical distribution schematic, socket legends, and circuit schedules.
"""

from pathlib import Path
from ezdxf.enums import TextEntityAlignment
from core.exporters.dxf_writer import DXFWriter
from electrical.power_distribution.sockets.scripts.design_engine import SocketDesignResult


class SocketDXFExporter:
    """Exports Small Power socket layout and circuit schedule to AutoCAD .dxf format."""

    def __init__(self, design_result: SocketDesignResult):
        self.res = design_result
        self.writer = DXFWriter("socket_schematic.dxf")

    def export(self, filepath: Path) -> Path:
        """Generates the drawing and saves to the given path."""
        # 1. Draw Title Block / Header
        self.writer.add_rectangle(0, 0, 1200, 800, layer="S-TITLEBLOCK")
        self.writer.add_text("ELECTRICAL SMALL POWER DISTRIBUTION SCHEMATIC", (30, 750), height=22, layer="E-TEXT")
        self.writer.add_text(f"Design Code: {self.res.code_used} | System: Single-Phase 230V | Circuits: {self.res.total_circuits_count}", (30, 720), height=14, layer="E-TEXT")
        self.writer.add_text(f"Total Connected Load: {self.res.total_connected_watts/1000.0:.2f} kW ({self.res.total_connected_kva:.2f} kVA)", (30, 695), height=14, layer="E-TEXT")

        # 2. Draw Main Distribution Panel (DB)
        db_x, db_y = 60, 620
        db_w, db_h = 100, 40
        self.writer.add_rectangle(db_x, db_y - db_h, db_w, db_h, layer="E-POWR-PANL")
        self.writer.add_text("MAIN DB", (db_x + db_w / 2, db_y - db_h / 2), height=12, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)

        # 3. Draw Busbar and Branch Circuits
        bus_start_y = db_y - db_h - 40
        self.writer.add_line((db_x + db_w / 2, db_y - db_h), (db_x + db_w / 2, bus_start_y), layer="E-POWR-PANL")

        spacing_y = 35
        curr_y = bus_start_y

        for i, ckt in enumerate(self.res.circuits):
            branch_y = curr_y - (i * spacing_y)
            # Circuit breaker representation
            self.writer.add_line((db_x + db_w / 2, branch_y), (db_x + 150, branch_y), layer="E-POWR-CIRC")
            self.writer.add_rectangle(db_x + 150, branch_y - 8, 35, 16, layer="E-POWR-CIRC")
            self.writer.add_text(f"{ckt.breaker_rating_amps}A", (db_x + 167, branch_y), height=7, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)

            # Circuit Cable Run Line
            self.writer.add_line((db_x + 185, branch_y), (db_x + 350, branch_y), layer="E-POWR-CIRC")

            # Outlets symbols & tag
            ckt_label = f"[{ckt.circuit_tag}] {ckt.description} ({ckt.outlet_count}x outlets) - {ckt.cable_size_sqmm}mm2 Cu - VD: {ckt.voltage_drop_pct:.2f}%"
            self.writer.add_text(ckt_label, (db_x + 360, branch_y), height=9, layer="E-TEXT", align=TextEntityAlignment.LEFT)

            # Draw socket symbol
            self.writer.msp.add_circle((db_x + 330, branch_y), radius=5, dxfattribs={"layer": "E-POWR-SCKT"})

        # 4. Draw Legend & Mounting Heights Table
        legend_x, legend_y = 750, 620
        self.writer.add_rectangle(legend_x, legend_y - 250, 400, 250, layer="S-TITLEBLOCK")
        self.writer.add_text("SMALL POWER MOUNTING HEIGHT LEGEND (AFF)", (legend_x + 20, legend_y - 25), height=13, layer="E-TEXT")

        legend_items = [
            ("Standard Convenience Duplex Socket", "+300 mm AFF"),
            ("Kitchen Countertop Socket (Splash-proof)", "+1100 mm AFF"),
            ("Split AC Unit Disconnect Switch", "+2200 mm AFF (Near Indoor Unit)"),
            ("Water Heater Double Pole Switch + Neon", "+1600 mm AFF (Outside Wet Zone)"),
            ("Washing Machine / Dishwasher Socket", "+500 mm AFF"),
            ("Distribution Board (DB-01)", "+1800 mm AFF (Top of Enclosure)"),
        ]

        for idx, (desc, height_aff) in enumerate(legend_items):
            ly = legend_y - 60 - (idx * 30)
            self.writer.msp.add_circle((legend_x + 25, ly), radius=4, dxfattribs={"layer": "E-POWR-SCKT"})
            self.writer.add_text(desc, (legend_x + 40, ly), height=9, layer="E-TEXT", align=TextEntityAlignment.LEFT)
            self.writer.add_text(height_aff, (legend_x + 390, ly), height=9, layer="E-TEXT", align=TextEntityAlignment.RIGHT)

        # 5. Draw Coordination Alerts Box
        coord_x, coord_y = 750, 320
        self.writer.add_rectangle(coord_x, coord_y - 200, 400, 200, layer="S-TITLEBLOCK")
        self.writer.add_text("MANDATORY CROSS-DISCIPLINE COORDINATION", (coord_x + 20, coord_y - 25), height=12, layer="S-REBAR-BOT")

        coord_notes = [
            "1. Coordinate AC isolator location with Mechanical/HVAC shop drawings.",
            "2. Plumbing water heater isolation switch must be outside bathroom Zone 1.",
            "3. Provide RCD 30mA protection for all bathroom & kitchen countertop sockets.",
            "4. Verify conduits in structural columns do not exceed 4% cross-sectional area.",
        ]
        for c_idx, c_note in enumerate(coord_notes):
            cy = coord_y - 60 - (c_idx * 30)
            self.writer.add_text(c_note, (coord_x + 20, cy), height=8, layer="E-TEXT", align=TextEntityAlignment.LEFT)

        return self.writer.save(filepath)
