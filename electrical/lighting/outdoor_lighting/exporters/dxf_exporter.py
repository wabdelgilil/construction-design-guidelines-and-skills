"""AutoCAD DXF Exporter for Outdoor Roadway Lighting."""

import math
from typing import Dict, Any
from core.exporters.dxf_writer import DXFWriter


class OutdoorLightingDXFExporter:
    """Exports 2D Roadway lighting layout, pole spacing, and feeder routing to DXF."""

    def __init__(self):
        self.writer = None

    def export(self, design_data: Dict[str, Any], file_path: str):
        self.writer = DXFWriter()
        self._setup_layers()

        self._draw_roadway_lighting_layout(design_data)
        self._draw_pole_detail(design_data)
        self._draw_title_block_and_notes(design_data)

        self.writer.save(file_path)

    def _setup_layers(self):
        doc = self.writer.doc
        layers = [
            ("C-ROAD-CURB", 8),      # Dark Gray (Curb lines & edge of pavement)
            ("C-ROAD-CLINE", 2),     # Yellow (Road Centerline dashed)
            ("E-LITE-POLE", 3),      # Green (Lighting Poles)
            ("E-LITE-FIXT", 4),      # Cyan (LED Fixture symbols)
            ("E-POWR-CABL", 1),      # Red (Underground Armored Feeder Cable)
            ("E-POWR-PILL", 6),      # Magenta (Feeder Pillar Control Panel)
            ("E-ERTH-ROD", 5),       # Blue (Earthing rods & pits)
            ("E-TEXT-LABEL", 7),     # White (Annotations)
            ("E-DIM-LINE", 9),       # Gray (Dimensions)
        ]
        for name, color in layers:
            if name not in doc.layers:
                doc.layers.add(name, color=color)

    def _draw_roadway_lighting_layout(self, data: Dict[str, Any]):
        msp = self.writer.msp
        geo = data["road_geometry"]
        photo = data["photometrics"]
        elec = data["electrical_feeder"]

        # Scale coordinates for CAD representation
        # Road runs horizontally from X = 50.0 to X = 50.0 + (road_length * scale)
        # To make it fit standard drawing view, scale 1 meter = 0.5 CAD units
        scale = 0.5
        x0 = 50.0
        y_center = 150.0
        r_len = geo["road_length_m"] * scale
        r_width = geo["road_width_m"] * scale
        half_w = r_width / 2.0

        msp.add_text(
            f"ROADWAY LIGHTING LAYOUT - CLASS {data.get('road_class', 'M3')} ({geo['pole_arrangement'].upper()} ARRANGEMENT)",
            dxfattribs={"layer": "E-TEXT-LABEL", "height": 3.5}
        ).set_placement((x0, y_center + half_w + 25.0))

        # Road boundaries (Curbs)
        msp.add_line((x0, y_center + half_w), (x0 + r_len, y_center + half_w), dxfattribs={"layer": "C-ROAD-CURB"})
        msp.add_line((x0, y_center - half_w), (x0 + r_len, y_center - half_w), dxfattribs={"layer": "C-ROAD-CURB"})

        # Centerline
        msp.add_line((x0, y_center), (x0 + r_len, y_center), dxfattribs={"layer": "C-ROAD-CLINE"})

        # Feeder Pillar (FP) Panel at start of road
        fp_x = x0 - 15.0
        fp_y = y_center + half_w + 10.0
        msp.add_lwpolyline(
            [(fp_x, fp_y), (fp_x + 8, fp_y), (fp_x + 8, fp_y + 12), (fp_x, fp_y + 12), (fp_x, fp_y)],
            dxfattribs={"layer": "E-POWR-PILL"}
        )
        msp.add_text("FEEDER PILLAR (FP-01)", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.4}).set_placement((fp_x - 5, fp_y + 14))

        # Cable Trench Line
        cable_y = y_center + half_w + 4.0
        msp.add_line((fp_x + 4, fp_y), (x0, cable_y), dxfattribs={"layer": "E-POWR-CABL"})

        # Draw Poles and Fixtures
        pole_spacing_cad = geo["actual_spacing_m"] * scale
        pole_y = y_center + half_w + 4.0

        last_px = None
        phases = ["L1", "L2", "L3"]
        for p in range(geo["num_poles"]):
            px = x0 + p * pole_spacing_cad
            phase_tag = phases[p % 3]

            # Connect cable between poles
            if last_px is not None:
                msp.add_line((last_px, pole_y), (px, pole_y), dxfattribs={"layer": "E-POWR-CABL"})
            else:
                msp.add_line((x0, cable_y), (px, pole_y), dxfattribs={"layer": "E-POWR-CABL"})
            last_px = px

            # Pole base (Circle + Cross)
            msp.add_circle((px, pole_y), radius=1.5, dxfattribs={"layer": "E-LITE-POLE"})
            msp.add_line((px - 1.2, pole_y - 1.2), (px + 1.2, pole_y + 1.2), dxfattribs={"layer": "E-LITE-POLE"})
            msp.add_line((px - 1.2, pole_y + 1.2), (px + 1.2, pole_y - 1.2), dxfattribs={"layer": "E-LITE-POLE"})

            # Luminaire Arm extending into roadway
            arm_reach = half_w * 0.4
            fixt_y = pole_y - arm_reach
            msp.add_line((px, pole_y), (px, fixt_y), dxfattribs={"layer": "E-LITE-FIXT"})
            # LED Head symbol
            msp.add_lwpolyline(
                [(px - 1.2, fixt_y - 1.8), (px + 1.2, fixt_y - 1.8), (px + 0.8, fixt_y + 0.5), (px - 0.8, fixt_y + 0.5), (px - 1.2, fixt_y - 1.8)],
                dxfattribs={"layer": "E-LITE-FIXT"}
            )

            # Earth Pit symbol
            msp.add_circle((px + 3.0, pole_y + 3.0), radius=0.8, dxfattribs={"layer": "E-ERTH-ROD"})

            # Labels
            msp.add_text(f"LP-{p+1:02d} ({phase_tag})", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.2}).set_placement((px - 3.5, pole_y + 5.0))

        # Dimension Line for Spacing
        if geo["num_poles"] >= 2:
            dim_y = pole_y + 12.0
            p1_x = x0
            p2_x = x0 + pole_spacing_cad
            msp.add_line((p1_x, dim_y), (p2_x, dim_y), dxfattribs={"layer": "E-DIM-LINE"})
            msp.add_line((p1_x, dim_y - 1.5), (p1_x, dim_y + 1.5), dxfattribs={"layer": "E-DIM-LINE"})
            msp.add_line((p2_x, dim_y - 1.5), (p2_x, dim_y + 1.5), dxfattribs={"layer": "E-DIM-LINE"})
            msp.add_text(f"SPACING S = {geo['actual_spacing_m']} m", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.3}).set_placement((p1_x + 2.0, dim_y + 1.5))

    def _draw_pole_detail(self, data: Dict[str, Any]):
        msp = self.writer.msp
        geo = data["road_geometry"]
        photo = data["photometrics"]

        # Detail Elevation of Pole & Concrete Base
        dx = 50.0
        dy = 40.0
        h_cad = 40.0

        msp.add_text("STANDARD OCTAGONAL LIGHTING POLE ELEVATION & FOUNDATION DETAIL", dxfattribs={"layer": "E-TEXT-LABEL", "height": 2.5}).set_placement((dx, dy + h_cad + 15.0))

        # Ground line
        msp.add_line((dx - 15, dy), (dx + 25, dy), dxfattribs={"layer": "C-ROAD-CURB"})
        msp.add_text("FINISHED ROAD FINISH LEVEL (FRL)", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.1}).set_placement((dx - 15, dy - 2.5))

        # Concrete Foundation
        msp.add_lwpolyline(
            [(dx - 8, dy), (dx + 8, dy), (dx + 8, dy - 18), (dx - 8, dy - 18), (dx - 8, dy)],
            dxfattribs={"layer": "C-ROAD-CURB"}
        )
        msp.add_text("REINFORCED CONCRETE CLASS C30/37", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.1}).set_placement((dx - 7, dy - 10))

        # Pole Shaft (Tapered)
        msp.add_line((dx - 1.8, dy), (dx - 0.9, dy + h_cad), dxfattribs={"layer": "E-LITE-POLE"})
        msp.add_line((dx + 1.8, dy), (dx + 0.9, dy + h_cad), dxfattribs={"layer": "E-LITE-POLE"})

        # Service Door & Fuse Cutout
        msp.add_lwpolyline(
            [(dx - 1.2, dy + 3), (dx + 1.2, dy + 3), (dx + 1.2, dy + 8), (dx - 1.2, dy + 8), (dx - 1.2, dy + 3)],
            dxfattribs={"layer": "E-LITE-POLE"}
        )
        msp.add_text("SERVICE DOOR & CUT-OUT", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.0}).set_placement((dx + 3, dy + 5))

        # Bracket Arm & LED Fixture
        arm_end_x = dx + 12.0
        arm_end_y = dy + h_cad + 4.0
        msp.add_line((dx, dy + h_cad), (arm_end_x, arm_end_y), dxfattribs={"layer": "E-LITE-FIXT"})
        msp.add_lwpolyline(
            [(arm_end_x - 1, arm_end_y - 2), (arm_end_x + 3, arm_end_y - 2), (arm_end_x + 2, arm_end_y), (arm_end_x - 1, arm_end_y), (arm_end_x - 1, arm_end_y - 2)],
            dxfattribs={"layer": "E-LITE-FIXT"}
        )
        msp.add_text(f"LED ROADWAY LUMINAIRE {photo['luminaire_power_w']}W (IP66)", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.2}).set_placement((arm_end_x + 4, arm_end_y - 1))

        # Height dimension
        msp.add_line((dx - 10, dy), (dx - 10, dy + h_cad), dxfattribs={"layer": "E-DIM-LINE"})
        msp.add_text(f"H = {geo['mounting_height_m']} m", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.4}).set_placement((dx - 18, dy + h_cad / 2.0))

    def _draw_title_block_and_notes(self, data: Dict[str, Any]):
        msp = self.writer.msp

        nx = 180.0
        ny = 35.0
        notes = [
            "ROADWAY LIGHTING DESIGN NOTES:",
            f"1. LIGHTING DESIGN COMPLIES WITH CIE 115 AND EN 13201 CLASS {data.get('road_class', 'M3')}.",
            "2. ALL POLES ARE HOT-DIP GALVANIZED ACCORDING TO ASTM A123 / BS EN ISO 1461.",
            "3. UNDERGROUND POWER CABLE IS 4-CORE ARMORED COPPER (Cu/XLPE/SWA/PVC 0.6/1kV).",
            "4. POLES SHALL BE BALANCED IN CYCLIC ORDER (L1 - L2 - L3) TO PREVENT NEUTRAL UNBALANCE.",
            "5. INDIVIDUAL POLE EARTH RESISTANCE SHALL NOT EXCEED 10 OHMS (DEDICATED EARTH ROD).",
            "6. LIGHTING CONTROLS VIA ASTRONOMICAL TIMER AND DUSK-TO-DAWN PHOTOELECTRIC SENSOR.",
            "7. CABLE SLACK OF 1.0 METER TO BE LEFT IN EACH POLE BASE LOOP BOX."
        ]

        for idx, line in enumerate(notes):
            h = 1.6 if idx == 0 else 1.3
            msp.add_text(line, dxfattribs={"layer": "E-TEXT-LABEL", "height": h}).set_placement((nx, ny + (len(notes) - idx) * 4.0))
