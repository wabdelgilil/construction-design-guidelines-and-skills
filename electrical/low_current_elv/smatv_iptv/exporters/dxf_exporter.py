"""AutoCAD DXF Exporter for SMATV and IPTV Distribution Systems."""

import math
from typing import Dict, Any
from core.exporters.dxf_writer import DXFWriter


class SMATVIPTVDXFExporter:
    """Exports SMATV / IPTV System Architecture Riser Diagram and Headend details to DXF."""

    def __init__(self):
        self.writer = None

    def export(self, design_data: Dict[str, Any], file_path: str):
        self.writer = DXFWriter()
        self._setup_layers()

        self._draw_riser_diagram(design_data)
        self._draw_headend_dish_details(design_data)
        self._draw_title_block_and_notes(design_data)

        self.writer.save(file_path)

    def _setup_layers(self):
        doc = self.writer.doc
        layers = [
            ("ELV-SAT-DISH", 3),    # Green (Satellite Dishes & RF Horns)
            ("ELV-HEAD-END", 4),    # Cyan (Headend Servers & Launch Amps)
            ("ELV-COAX-TRNK", 1),   # Red (RG-11 Trunk Riser Backbone)
            ("ELV-COAX-DROP", 2),   # Yellow (RG-6 Horizontal Drops)
            ("ELV-MULT-SWT", 6),    # Magenta (Floor Multiswitches)
            ("ELV-IPTV-NETW", 5),   # Blue (IPTV Fiber / Cat6A Ethernet)
            ("E-TEXT-LABEL", 7),    # White (Annotations)
            ("E-DIM-LINE", 8),      # Gray (Dimensions)
        ]
        for name, color in layers:
            if name not in doc.layers:
                doc.layers.add(name, color=color)

    def _draw_riser_diagram(self, data: Dict[str, Any]):
        msp = self.writer.msp
        bldg = data["building_parameters"]
        rf = data["rf_link_budget"]
        hw = data["hardware_sizing"]

        x_base = 50.0
        y_base = 60.0
        floor_h = 18.0

        msp.add_text(
            f"SMATV & IPTV HYBRID SYSTEM RISER DIAGRAM ({bldg['num_floors']} STOREY TOWER)",
            dxfattribs={"layer": "E-TEXT-LABEL", "height": 3.5}
        ).set_placement((x_base, y_base + (bldg['num_floors'] + 2) * floor_h))

        # Roof Level (Headend Room)
        roof_y = y_base + (bldg["num_floors"] + 1) * floor_h
        msp.add_line((x_base - 10, roof_y), (x_base + 120, roof_y), dxfattribs={"layer": "E-DIM-LINE"})
        msp.add_text("ROOF LEVEL (HEADEND & ANTENNA MAST)", dxfattribs={"layer": "E-TEXT-LABEL", "height": 2.0}).set_placement((x_base - 10, roof_y + 3.0))

        # Headend Equipment Rack
        rack_x = x_base + 10
        rack_y = roof_y - 12
        msp.add_lwpolyline(
            [(rack_x, rack_y), (rack_x + 25, rack_y), (rack_x + 25, rack_y + 10), (rack_x, rack_y + 10), (rack_x, rack_y)],
            dxfattribs={"layer": "ELV-HEAD-END"}
        )
        msp.add_text("CENTRAL HEADEND RACK\n(LAUNCH AMPS & IP GATEWAYS)", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.2}).set_placement((rack_x + 1, rack_y + 4))

        # Riser Backbone Line (Vertical RG-11 Coaxial Trunk & Fiber)
        riser_x = x_base + 22
        msp.add_line((riser_x, roof_y - 12), (riser_x, y_base), dxfattribs={"layer": "ELV-COAX-TRNK"})
        msp.add_line((riser_x + 3, roof_y - 12), (riser_x + 3, y_base), dxfattribs={"layer": "ELV-IPTV-NETW"})
        msp.add_text("RG-11 TRUNK & 10G FIBER RISER", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.2}).set_placement((riser_x - 18, y_base - 5))

        # Floors (Show representative top floor, intermediate, and ground)
        for flr_idx in range(1, bldg["num_floors"] + 1):
            fy = y_base + (flr_idx - 1) * floor_h

            # Floor slab line
            msp.add_line((x_base - 10, fy), (x_base + 120, fy), dxfattribs={"layer": "E-DIM-LINE"})
            msp.add_text(f"FLOOR {flr_idx:02d}", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.6}).set_placement((x_base - 10, fy + 2))

            # Floor Multiswitch Box (ELV Telecom Riser Room)
            ms_x = riser_x + 12
            ms_y = fy + 4
            msp.add_lwpolyline(
                [(ms_x, ms_y), (ms_x + 16, ms_y), (ms_x + 16, ms_y + 8), (ms_x, ms_y + 8), (ms_x, ms_y)],
                dxfattribs={"layer": "ELV-MULT-SWT"}
            )
            msp.add_text(f"MULTISWITCH\n(17x16 CAS)", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.1}).set_placement((ms_x + 1, ms_y + 4.5))

            # Tap connection from trunk
            msp.add_line((riser_x, ms_y + 4), (ms_x, ms_y + 4), dxfattribs={"layer": "ELV-COAX-TRNK"})

            # Representative TV Outlet Drop
            drop_x = ms_x + 35
            drop_y = ms_y + 4
            msp.add_line((ms_x + 16, ms_y + 4), (drop_x, drop_y), dxfattribs={"layer": "ELV-COAX-DROP"})

            # Outlet Symbol (Circle with triangle inside)
            msp.add_circle((drop_x + 3, drop_y), radius=2.0, dxfattribs={"layer": "ELV-COAX-DROP"})
            msp.add_text(f"{bldg['outlets_per_floor']}x TV/IPTV OUTLETS\n(68 dBuV TARGET)", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.1}).set_placement((drop_x + 6, drop_y - 1))

    def _draw_headend_dish_details(self, data: Dict[str, Any]):
        msp = self.writer.msp
        dishes = data["satellite_dishes"]

        # Roof Antenna Array Detail (Plan / Elevation View)
        ax = 180.0
        ay = 160.0

        msp.add_text("ROOFTOP PARABOLIC DISH ANTENNA ARRAY", dxfattribs={"layer": "E-TEXT-LABEL", "height": 2.5}).set_placement((ax, ay + 45.0))

        for idx, sat in enumerate(dishes):
            cx = ax + (idx * 30.0)
            cy = ay + 20.0
            r = sat["dish_diameter_m"] * 3.5

            # Dish Parabolic Curve (Arc)
            msp.add_arc((cx, cy), radius=r, start_angle=200, end_angle=340, dxfattribs={"layer": "ELV-SAT-DISH"})
            # Feed Arm & LNB Horn
            msp.add_line((cx, cy - r), (cx, cy), dxfattribs={"layer": "ELV-SAT-DISH"})
            msp.add_circle((cx, cy), radius=1.2, dxfattribs={"layer": "ELV-SAT-DISH"})

            # Labels
            msp.add_text(f"{sat['name']}\nDia: {sat['dish_diameter_m']}m (Gain: {sat['gain_dbi']} dBi)", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.2}).set_placement((cx - 12, cy - r - 8.0))

    def _draw_title_block_and_notes(self, data: Dict[str, Any]):
        msp = self.writer.msp

        nx = 180.0
        ny = 40.0
        notes = [
            "SMATV & IPTV ENGINEERING DESIGN NOTES:",
            "1. SYSTEM FULLY COMPLIANT WITH EN 50083 (CENELEC) AND ITU-T J.83 RECOMMENDATIONS.",
            "2. ALL OUTLETS MUST DELIVER BETWEEN 60.0 AND 77.0 dBuV WITH CARRIER-TO-NOISE (C/N) >= 12 dB.",
            "3. VERTICAL TRUNK BACKBONE IS CLASS A+ RG-11 SHIELDED COAXIAL CABLE WITH COMPRESSION CONNECTORS.",
            "4. HORIZONTAL DROPS ARE LSZH TRIPLE-SHIELDED RG-6 COPPER CABLES NOT EXCEEDING 50 METERS.",
            "5. ROOFTOP SATELLITE DISH MASTS MUST BE BONDED TO THE LIGHTNING PROTECTION SYSTEM (LPS) VIA SPARK GAPS.",
            "6. IPTV GATEWAYS SHALL PROVIDE UNICAST/MULTICAST STREAMING VIA IGMP v2/v3 WITH DEDICATED VLAN.",
            "7. ALL UNUSED MULTISWITCH AND TAP PORTS MUST BE TERMINATED WITH 75-OHM DC-BLOCKED TERMINATORS."
        ]

        for idx, line in enumerate(notes):
            h = 1.6 if idx == 0 else 1.3
            msp.add_text(line, dxfattribs={"layer": "E-TEXT-LABEL", "height": h}).set_placement((nx, ny + (len(notes) - idx) * 4.0))
