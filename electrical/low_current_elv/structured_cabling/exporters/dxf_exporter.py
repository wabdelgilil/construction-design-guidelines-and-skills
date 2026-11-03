"""
AutoCAD DXF Exporter for 42U Telecom Equipment Rack Elevation and Optical Fiber Backbone Riser.
"""

from pathlib import Path
from core.exporters.dxf_writer import DXFWriter
from electrical.low_current_elv.structured_cabling.scripts.design_engine import StructuredCablingDesignResult


class StructuredCablingDXFExporter:
    """Exports 42U equipment rack elevations and fiber riser schematics to AutoCAD .dxf format."""

    def __init__(self, result: StructuredCablingDesignResult):
        self.res = result
        self.writer = DXFWriter("telecom_rack_elevation.dxf")
        self._setup_layers()

    def _setup_layers(self):
        layers = [
            ("E-RACK-FRAME", 8),    # Dark Grey: 42U Cabinet & 19" Rails
            ("E-RACK-PASSIVE", 4),  # Cyan: Patch Panels, Cable Managers, LIU
            ("E-RACK-ACTIVE", 1),   # Red: Managed PoE Switches, Network Hardware
            ("E-RACK-POWER", 6),    # Magenta: UPS & PDUs
            ("E-RACK-DIMS", 2),     # Yellow: U-Marks, Dimensions
            ("E-RACK-TEXT", 7),     # White: Equipment Labels & Titles
        ]
        for name, color in layers:
            if name not in self.writer.doc.layers:
                lyr = self.writer.doc.layers.add(name)
                lyr.color = color

    def export(self, filepath: Path) -> Path:
        # Drawing Title
        self.writer.add_text(
            "TELECOMMUNICATIONS 42U EQUIPMENT RACK ELEVATION & OPTICAL FIBER RISER",
            (0, 3100),
            height=120,
            layer="E-RACK-TEXT",
        )
        self.writer.add_text(
            f"Project: {self.res.project_name} | Code: {self.res.standard_used} | Used: {self.res.total_u_utilized}U / 42U | Spare: {self.res.spare_u_percentage}% | UPS: {self.res.recommended_ups_va}VA",
            (0, 2950),
            height=70,
            layer="E-RACK-TEXT",
        )

        # -------------------------------------------------------------
        # VIEW 1: 42U Equipment Rack Front Elevation
        # -------------------------------------------------------------
        rack_x = 0.0
        rack_y = 0.0
        rack_w = 800.0   # 800mm wide enclosure
        rack_h = 2100.0  # 2100mm height
        rail_w = 482.6   # 19 inch standard equipment mounting width (482.6mm)
        rail_margin = (rack_w - rail_w) / 2.0  # ~158.7mm side cable channel on each side

        # Outer Cabinet Frame
        self.writer.add_rectangle(rack_x, rack_y, rack_w, rack_h, layer="E-RACK-FRAME")
        # Rack Base Plinth
        self.writer.add_rectangle(rack_x + 50, rack_y - 80, rack_w - 100, 80, layer="E-RACK-FRAME")
        self.writer.add_text("42U FLOOR-STANDING ENCLOSURE (800W x 1000D)", (rack_x + 80, rack_y - 60), height=40, layer="E-RACK-TEXT")

        # 19" Inner Equipment Channel
        equip_x = rack_x + rail_margin
        u_height_mm = 44.45  # 1U = 44.45mm
        u_base_y = rack_y + 100.0  # 100mm clearance from bottom

        # Draw left and right vertical mounting rail posts
        self.writer.add_rectangle(equip_x - 30, u_base_y, 30, 42 * u_height_mm, layer="E-RACK-FRAME")
        self.writer.add_rectangle(equip_x + rail_w, u_base_y, 30, 42 * u_height_mm, layer="E-RACK-FRAME")

        # Draw each U tick mark and unit label
        for u in range(1, 43):
            y_u = u_base_y + (u - 1) * u_height_mm
            # Tick mark
            self.writer.add_line((equip_x - 25, y_u), (equip_x - 5, y_u), layer="E-RACK-DIMS")
            self.writer.add_line((equip_x + rail_w + 5, y_u), (equip_x + rail_w + 25, y_u), layer="E-RACK-DIMS")
            # Label every 2U
            if u % 2 == 1 or u == 42:
                self.writer.add_text(f"U{u:02d}", (equip_x - 110, y_u + 10), height=25, layer="E-RACK-DIMS")

        # Draw Installed Equipment Items
        for item in self.res.rack_items:
            item_y = u_base_y + (item.u_position - 1) * u_height_mm
            h_mm = item.u_height * u_height_mm

            if item.category in ("PatchPanel", "FiberLIU"):
                lyr = "E-RACK-PASSIVE"
            elif item.category == "Switch":
                lyr = "E-RACK-ACTIVE"
            elif item.category in ("UPS", "PDU"):
                lyr = "E-RACK-POWER"
            else:
                lyr = "E-RACK-PASSIVE"

            # Outer equipment chassis
            self.writer.add_rectangle(equip_x, item_y, rail_w, h_mm, layer=lyr)
            # Mounting ear screws
            self.writer.msp.add_circle((equip_x + 10, item_y + h_mm / 2), 4, dxfattribs={"layer": "E-RACK-FRAME"})
            self.writer.msp.add_circle((equip_x + rail_w - 10, item_y + h_mm / 2), 4, dxfattribs={"layer": "E-RACK-FRAME"})

            # Equipment description text
            self.writer.add_text(item.device_name, (equip_x + 25, item_y + h_mm / 2 - 12), height=24, layer="E-RACK-TEXT")

        # Side Cable Managers (Vertical channels)
        self.writer.add_text("VERTICAL CABLE ORGANIZER", (rack_x + 15, u_base_y + 1000), height=25, layer="E-RACK-PASSIVE")
        self.writer.add_text("VERTICAL CABLE ORGANIZER", (equip_x + rail_w + 40, u_base_y + 1000), height=25, layer="E-RACK-PASSIVE")

        # -------------------------------------------------------------
        # VIEW 2: Optical Fiber Backbone Riser (MDF Server to Floor IDF)
        # -------------------------------------------------------------
        riser_x = 1300.0
        riser_y = 600.0

        self.writer.add_text("OPTICAL FIBER BACKBONE & NETWORK RISER SCHEMATIC", (riser_x, riser_y + 1600), height=80, layer="E-RACK-TEXT")

        # Main Server Room (MDF) Enclosure
        self.writer.add_rectangle(riser_x, riser_y, 600, 450, layer="E-RACK-ACTIVE")
        self.writer.add_text("MAIN DATA CENTER / MDF", (riser_x + 60, riser_y + 390), height=40, layer="E-RACK-TEXT")
        self.writer.add_text("Core Switch (10G/40G)", (riser_x + 60, riser_y + 320), height=35, layer="E-RACK-ACTIVE")
        self.writer.add_text("Master Optical LIU (24-Core)", (riser_x + 60, riser_y + 250), height=35, layer="E-RACK-PASSIVE")
        self.writer.add_text("Central NVR & Storage SAN", (riser_x + 60, riser_y + 180), height=35, layer="E-RACK-ACTIVE")
        self.writer.add_text("Dual Online UPS (10 kVA)", (riser_x + 60, riser_y + 110), height=35, layer="E-RACK-POWER")

        # Floor Telecom Room (IDF-01) Enclosure
        idf_y = riser_y + 800
        self.writer.add_rectangle(riser_x, idf_y, 600, 450, layer="E-RACK-ACTIVE")
        self.writer.add_text(f"FLOOR TELECOM ROOM (IDF) - {self.res.total_42u_racks_count}x 42U", (riser_x + 50, idf_y + 390), height=40, layer="E-RACK-TEXT")
        self.writer.add_text(f"1U Fiber LIU ({self.res.backbone_fiber_cores}-Core OM4)", (riser_x + 50, idf_y + 320), height=35, layer="E-RACK-PASSIVE")
        self.writer.add_text(f"{self.res.switches_48p_count}x 48-Port PoE+ Access Switches", (riser_x + 50, idf_y + 250), height=35, layer="E-RACK-ACTIVE")
        self.writer.add_text(f"{self.res.patch_panels_24p_count}x Cat6A Patch Panels ({self.res.grand_total_horizontal_ports} Ports)", (riser_x + 50, idf_y + 180), height=35, layer="E-RACK-PASSIVE")
        self.writer.add_text(f"Standby UPS ({self.res.recommended_ups_va} VA, 30m)", (riser_x + 50, idf_y + 110), height=35, layer="E-RACK-POWER")

        # Vertical Backbone Fiber Cable (Dual Redundant 12-Core OM4)
        self.writer.add_line((riser_x + 300, riser_y + 450), (riser_x + 300, idf_y), layer="E-RACK-PASSIVE")
        self.writer.add_text("2x 12-Core OM4 Multi-Mode Laser Optimized Fiber (Tight Buffer)", (riser_x + 320, riser_y + 620), height=35, layer="E-RACK-PASSIVE")
        self.writer.add_text("In 50mm High-Impact PVC / Rigid Galvanized Conduit", (riser_x + 320, riser_y + 560), height=30, layer="E-RACK-DIMS")

        # Horizontal Distribution Arrow
        self.writer.add_line((riser_x + 600, idf_y + 200), (riser_x + 950, idf_y + 200), layer="E-RACK-PASSIVE")
        self.writer.add_text(f"Horizontal Cat6A Cables ({self.res.grand_total_horizontal_ports} Runs <= 90m)", (riser_x + 620, idf_y + 230), height=35, layer="E-RACK-TEXT")
        self.writer.add_text("To Dual Workstations, WAPs, CCTV, & ACS Outlets", (riser_x + 620, idf_y + 160), height=30, layer="E-RACK-DIMS")

        # -------------------------------------------------------------
        # VIEW 3: Standard Specifications & Coordination Table
        # -------------------------------------------------------------
        tbl_x = 0.0
        tbl_y = -800.0
        self.writer.add_rectangle(tbl_x, tbl_y, 2400, 650, layer="E-RACK-TEXT")
        self.writer.add_text("STRUCTURED CABLING SPECIFICATIONS & INSTALLATION CRITERIA", (tbl_x + 50, tbl_y + 580), height=50, layer="E-RACK-TEXT")

        specs = [
            ("Category 6A Horizontal Cable", "Class EA 500MHz, 23 AWG, 4-pair F/UTP, LSZH sheath, max 90m permanent link"),
            ("Optical Fiber Backbone", "12-Core OM4 50/125um multimode, tight-buffered, 10G/40G/100G supported"),
            ("Work Area Outlets (WAO)", "Bevelled shuttered faceplates with dual Cat6A RJ45 keystone jacks and icon tags"),
            ("Network PoE+ Switches", "48x 10/100/1000Base-T PoE+ (802.3at) ports, minimum 740W power budget per switch"),
            ("Telecom Room Climate", "Continuous 24/7 cooling (20-24 deg C, 40-60% RH) with dedicated DX split unit"),
            ("Earthing & Telecom Bonding", "Rack bonded to Telecommunications Grounding Busbar (TGB) with 16mm2 green/yellow Cu"),
        ]

        for i, (param, val) in enumerate(specs):
            row_y = tbl_y + 480 - i * 80
            self.writer.add_text(f"• {param}:", (tbl_x + 60, row_y), height=35, layer="E-RACK-TEXT")
            self.writer.add_text(val, (tbl_x + 600, row_y), height=32, layer="E-RACK-DIMS")

        self.writer.save(filepath)
        return filepath
