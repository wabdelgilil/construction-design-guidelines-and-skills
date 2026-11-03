"""
AutoCAD DXF Exporter for Earthing Grid and Lightning Protection Plan.
Generates scaled building perimeter, buried copper ring, earth pits, air terminals, and down conductors.
"""

from pathlib import Path
from ezdxf.enums import TextEntityAlignment
from core.exporters.dxf_writer import DXFWriter
from electrical.earthing.scripts.design_engine import EarthingDesignResult


class EarthingDXFExporter:
    """Exports Earthing Grid and LPS layout to AutoCAD .dxf format."""

    def __init__(
        self,
        result: EarthingDesignResult,
        building_length_m: float = 30.0,
        building_width_m: float = 20.0,
    ):
        self.res = result
        self.l_m = building_length_m
        self.w_m = building_width_m
        self.writer = DXFWriter("earthing_and_lps_layout.dxf")

    def export(self, filepath: Path) -> Path:
        scale = 1000.0  # mm
        l_mm = self.l_m * scale
        w_mm = self.w_m * scale
        margin = 2500.0

        # Sheet Border
        self.writer.add_rectangle(-margin, -margin, l_mm + 2 * margin + 3000, w_mm + 2 * margin, layer="S-TITLEBLOCK")

        # Title Block
        self.writer.add_text("EARTHING GRID & LIGHTNING PROTECTION PLAN", (0, w_mm + 1200), height=200, layer="E-TEXT")
        self.writer.add_text(
            f"Project: {self.res.project_name} | Standards: {self.res.standard_used}",
            (0, w_mm + 850),
            height=130,
            layer="E-TEXT",
        )
        self.writer.add_text(
            f"Target Resistance: <= {self.res.target_resistance_ohms} Ohm | Achieved: {self.res.combined_earthing_resistance_ohms} Ohm ({self.res.earthing_compliance_status}) | LPS Level: {self.res.lps_level} (Sphere Radius = {self.res.rolling_sphere_radius_m}m)",
            (0, w_mm + 550),
            height=110,
            layer="E-TEXT",
        )

        # 1. Building Footprint Walls
        self.writer.add_rectangle(0, 0, l_mm, w_mm, layer="S-COLUMN")
        self.writer.add_text("BUILDING ROOF / FOOTPRINT", (l_mm / 2, w_mm / 2), height=140, layer="S-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)

        # 2. Buried Perimeter Earthing Ring (70mm2 Cu offset 1000mm from building)
        ring_offset = 1000.0
        ring_x = -ring_offset
        ring_y = -ring_offset
        ring_w = l_mm + 2 * ring_offset
        ring_h = w_mm + 2 * ring_offset
        self.writer.add_rectangle(ring_x, ring_y, ring_w, ring_h, layer="S-REBAR-BOT")
        self.writer.add_text("BURIED 70mm2 BARE COPPER EARTHING RING (0.8m DEPTH)", (l_mm / 2, -ring_offset - 150), height=80, layer="E-TEXT", align=TextEntityAlignment.TOP_CENTER)

        # 3. Driven Earth Pits & Rods around ring
        n_rods = self.res.number_of_earth_rods
        # Distribute rods along the ring perimeter
        # Corners first:
        corners = [
            (ring_x, ring_y),
            (ring_x + ring_w, ring_y),
            (ring_x + ring_w, ring_y + ring_h),
            (ring_x, ring_y + ring_h),
        ]

        # Draw 4 corner earth pits
        for c_idx, (cx, cy) in enumerate(corners, 1):
            pit_size = 400.0
            self.writer.add_rectangle(cx - pit_size / 2, cy - pit_size / 2, pit_size, pit_size, layer="E-POWR-PANL")
            self.writer.msp.add_circle((cx, cy), radius=70, dxfattribs={"layer": "S-REBAR-BOT"})
            self.writer.add_text(f"PIT-{c_idx}", (cx, cy + 300), height=70, layer="E-TEXT", align=TextEntityAlignment.BOTTOM_CENTER)

        # 4. Main Earthing Busbar (MEB) inside Substation
        meb_x, meb_y = 1500.0, 1500.0
        self.writer.add_rectangle(meb_x, meb_y, 800.0, 200.0, layer="S-REBAR-BOT")
        self.writer.add_text("MAIN EARTHING BUSBAR (MEB)", (meb_x + 400, meb_y + 100), height=60, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
        # Bond MEB to external earth ring
        self.writer.add_line((meb_x, meb_y + 100), (ring_x, meb_y + 100), layer="S-REBAR-BOT")
        self.writer.add_text("2x 70mm2 Cu Feeders", (meb_x - 500, meb_y + 160), height=55, layer="E-TEXT")

        # 5. Roof Air Terminals (Franklin Rods) & Down Conductors
        # Draw 4 corner air terminals on roof
        roof_corners = [
            (0, 0),
            (l_mm, 0),
            (l_mm, w_mm),
            (0, w_mm),
        ]
        for rc_idx, (rx, ry) in enumerate(roof_corners, 1):
            # Air terminal symbol (small circle with cross)
            self.writer.msp.add_circle((rx, ry), radius=100, dxfattribs={"layer": "E-POWR-SCKT"})
            self.writer.add_line((rx - 120, ry), (rx + 120, ry), layer="E-POWR-SCKT")
            self.writer.add_line((rx, ry - 120), (rx, ry + 120), layer="E-POWR-SCKT")
            self.writer.add_text(f"AT-{rc_idx}", (rx + 150, ry + 150), height=65, layer="E-POWR-SCKT")

            # Down conductor tape to nearest pit
            nearest_pit = corners[rc_idx - 1]
            self.writer.add_line((rx, ry), nearest_pit, layer="E-POWR-CIRC")
            self.writer.add_text("Test Link (+1.5m)", ((rx + nearest_pit[0]) / 2, (ry + nearest_pit[1]) / 2), height=50, layer="S-TEXT")

        # 6. Earthing & LPS Legend & Summary Box
        leg_x = l_mm + 2500.0
        leg_y = w_mm
        self.writer.add_rectangle(leg_x, leg_y - 4500, 2200, 4500, layer="S-TITLEBLOCK")
        self.writer.add_text("EARTHING & LPS SCHEDULE", (leg_x + 100, leg_y - 250), height=110, layer="E-TEXT")

        notes = [
            f"1. Soil Resistivity (rho): {self.res.soil_resistivity_ohm_m} Ohm·m",
            f"2. Earth Rods: {self.res.number_of_earth_rods}x (3/4\" x 3.0m Copper-Bonded)",
            f"3. Target Resistance: <= {self.res.target_resistance_ohms} Ohm",
            f"4. Net Achieved Resistance: {self.res.combined_earthing_resistance_ohms} Ohm ({self.res.earthing_compliance_status})",
            f"5. LPS Level: {self.res.lps_level} (Rolling Sphere r={self.res.rolling_sphere_radius_m}m)",
            f"6. Roof Air Terminals: {self.res.air_terminals_count}x Franklin Rods (H={self.res.air_terminal_height_m}m)",
            f"7. Down Conductors: {self.res.down_conductors_count}x (25x3mm Bare Copper Tape)",
            f"8. Inspection Pits: {self.res.total_earth_pits_count}x Heavy Duty (300x300mm)",
            "9. Ufer Grounding: Foundation rebar bonded via Cadweld",
        ]
        for n_idx, text in enumerate(notes):
            self.writer.add_text(text, (leg_x + 100, leg_y - 650 - (n_idx * 380)), height=75, layer="E-TEXT")

        return self.writer.save(filepath)
