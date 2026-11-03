"""
AutoCAD DXF Exporter for Access Control Door Elevations, Device Placement, and Interlock Schematics.
"""

from pathlib import Path
from core.exporters.dxf_writer import DXFWriter
from electrical.low_current_elv.access_control.scripts.design_engine import AccessControlDesignResult


class AccessControlDXFExporter:
    """Exports Access Control CAD drawings including door elevations and wiring schematics."""

    def __init__(self, result: AccessControlDesignResult):
        self.res = result
        self.writer = DXFWriter("access_control_schematic.dxf")
        self._setup_layers()

    def _setup_layers(self):
        layers = [
            ("E-ACS-DOOR", 8),       # Dark Grey: Architectural Door Outline
            ("E-ACS-DEVICES", 4),    # Cyan: Readers, Maglocks, REX, BGU
            ("E-ACS-PANEL", 6),      # Magenta: Controllers and PSU Enclosures
            ("E-ACS-WIRING", 3),     # Green: Signal & DC Power Conduits
            ("E-ACS-DIMS", 2),       # Yellow: Dimensions and Level Marks
            ("E-ACS-TEXT", 7),       # White: Annotations and Title
        ]
        for name, color in layers:
            if name not in self.writer.doc.layers:
                lyr = self.writer.doc.layers.add(name)
                lyr.color = color

    def export(self, filepath: Path) -> Path:
        # Title Block
        self.writer.add_text(
            "ACCESS CONTROL SYSTEM (ACS) - DOOR ELEVATION & LIFE SAFETY INTERLOCK SCHEMATIC",
            (0, 3200),
            height=120,
            layer="E-ACS-TEXT",
        )
        self.writer.add_text(
            f"Project: {self.res.project_name} | Code: {self.res.standard_used} | Total Doors: {self.res.total_doors_count} | 4-Hour Battery Autonomy",
            (0, 3050),
            height=70,
            layer="E-ACS-TEXT",
        )

        # -------------------------------------------------------------
        # VIEW 1: Standard Controlled Door Elevation (Secured & Egress View)
        # -------------------------------------------------------------
        base_x = 0.0
        base_y = 0.0

        # Finished Floor Line (AFF = 0)
        self.writer.add_line((-600, 0), (2200, 0), layer="E-ACS-DOOR")
        self.writer.add_text("FINISHED FLOOR LEVEL (0.00 AFF)", (-550, -60), height=50, layer="E-ACS-DIMS")

        # Door Frame (1000mm width x 2150mm height, opening 900x2100mm)
        door_w = 900.0
        door_h = 2100.0
        frame_th = 50.0

        # Outer Frame
        self.writer.add_rectangle(base_x - frame_th, base_y, door_w + 2 * frame_th, door_h + frame_th, layer="E-ACS-DOOR")
        # Door Leaf
        self.writer.add_rectangle(base_x, base_y, door_w, door_h, layer="E-ACS-DOOR")
        # Door handle
        self.writer.add_rectangle(base_x + door_w - 90, base_y + 1000, 30, 100, layer="E-ACS-DOOR")

        # 1. Electromagnetic Lock (Mounted at door header, inside frame)
        self.writer.add_rectangle(base_x + door_w - 300, base_y + door_h - 40, 250, 40, layer="E-ACS-DEVICES")
        self.writer.add_text("MAGLOCK (600/1200 lbs)", (base_x + door_w - 320, base_y + door_h + 80), height=45, layer="E-ACS-TEXT")

        # 2. Door Position Sensor (DPS / Reed Switch) centered on header
        self.writer.msp.add_circle((base_x + door_w / 2, base_y + door_h), 25, dxfattribs={"layer": "E-ACS-DEVICES"})
        self.writer.add_text("[DPS]", (base_x + door_w / 2 - 40, base_y + door_h + 60), height=40, layer="E-ACS-TEXT")

        # 3. Request-to-Exit (REX) PIR Motion Sensor (Mounted at +2300mm AFF centered)
        self.writer.add_rectangle(base_x + door_w / 2 - 60, base_y + 2250, 120, 50, layer="E-ACS-DEVICES")
        self.writer.add_text("[REX PIR] (+2300mm AFF)", (base_x + door_w / 2 - 130, base_y + 2330), height=40, layer="E-ACS-TEXT")

        # 4. Emergency Break Glass Unit (BGU - Green) at +1200mm AFF on latch side
        bgu_x = base_x + door_w + 150
        bgu_y = base_y + 1200
        self.writer.add_rectangle(bgu_x, bgu_y, 80, 80, layer="E-ACS-DEVICES")
        self.writer.add_text("GREEN BGU", (bgu_x - 10, bgu_y + 100), height=40, layer="E-ACS-TEXT")
        self.writer.add_text("(EMERGENCY EXIT)", (bgu_x - 30, bgu_y - 40), height=35, layer="E-ACS-TEXT")

        # 5. Push-to-Exit Button / REX Button at +1200mm AFF (adjacent to BGU)
        rex_btn_x = bgu_x + 120
        self.writer.add_rectangle(rex_btn_x, bgu_y, 80, 80, layer="E-ACS-DEVICES")
        self.writer.add_text("[REX BTN]", (rex_btn_x - 10, bgu_y + 100), height=40, layer="E-ACS-TEXT")

        # 6. Card / Biometric Reader (Exterior side shown with phantom leader)
        rdr_x = base_x - 220
        rdr_y = base_y + 1200
        self.writer.add_rectangle(rdr_x, rdr_y, 80, 130, layer="E-ACS-DEVICES")
        self.writer.add_text("CARD/BIO", (rdr_x - 10, rdr_y + 150), height=40, layer="E-ACS-TEXT")
        self.writer.add_text("READER (+1200)", (rdr_x - 30, rdr_y - 40), height=35, layer="E-ACS-TEXT")

        # Dimension Leaders
        self.writer.add_line((rdr_x + 40, rdr_y), (rdr_x + 40, 0), layer="E-ACS-DIMS")
        self.writer.add_text("+1200 mm AFF", (rdr_x - 140, 600), height=40, layer="E-ACS-DIMS")

        self.writer.add_line((bgu_x + 40, bgu_y), (bgu_x + 40, 0), layer="E-ACS-DIMS")
        self.writer.add_text("+1200 mm AFF", (bgu_x + 230, 600), height=40, layer="E-ACS-DIMS")

        # -------------------------------------------------------------
        # VIEW 2: Life Safety Interlock & Controller Schematic
        # -------------------------------------------------------------
        sch_x = 2800.0
        sch_y = 1200.0

        self.writer.add_text("FAIL-SAFE LIFE SAFETY WIRING & FACP INTERLOCK (NFPA 101 / SBC 801)", (sch_x, sch_y + 1400), height=80, layer="E-ACS-TEXT")

        # 4-Door Controller Block
        self.writer.add_rectangle(sch_x, sch_y + 400, 500, 700, layer="E-ACS-PANEL")
        self.writer.add_text("4-DOOR INTELLIGENT", (sch_x + 40, sch_y + 1000), height=45, layer="E-ACS-PANEL")
        self.writer.add_text("ACS CONTROLLER", (sch_x + 70, sch_y + 920), height=45, layer="E-ACS-PANEL")
        self.writer.add_text("TCP/IP RJ45 -> LAN", (sch_x + 60, sch_y + 840), height=40, layer="E-ACS-TEXT")
        self.writer.add_text("OSDP / Wiegand Bus", (sch_x + 60, sch_y + 760), height=40, layer="E-ACS-TEXT")

        # Regulated PSU Block
        psu_x = sch_x + 800
        self.writer.add_rectangle(psu_x, sch_y + 400, 500, 700, layer="E-ACS-PANEL")
        self.writer.add_text("REGULATED 12V DC PSU", (psu_x + 50, sch_y + 1000), height=45, layer="E-ACS-PANEL")
        self.writer.add_text(f"Rating: {self.res.recommended_psu_current_a}A ({self.res.recommended_psu_rating_w}W)", (psu_x + 50, sch_y + 920), height=40, layer="E-ACS-TEXT")
        self.writer.add_text(f"Battery: {self.res.selected_battery_ah}Ah SLA (4h)", (psu_x + 50, sch_y + 840), height=40, layer="E-ACS-TEXT")
        self.writer.add_text("Input: 230V AC Fused Spur", (psu_x + 50, sch_y + 760), height=40, layer="E-ACS-TEXT")

        # FACP Relay Contact Block (Normally Closed / Drops on Fire Alarm)
        facp_x = psu_x + 800
        facp_y = sch_y + 700
        self.writer.add_rectangle(facp_x, facp_y, 400, 300, layer="E-ACS-DEVICES")
        self.writer.add_text("FACP FIRE RELAY", (facp_x + 40, facp_y + 220), height=40, layer="E-ACS-TEXT")
        self.writer.add_text("[ NC CONTACT ]", (facp_x + 60, facp_y + 150), height=40, layer="E-ACS-DEVICES")
        self.writer.add_text("Drops on Fire Alarm", (facp_x + 40, facp_y + 80), height=35, layer="E-ACS-TEXT")

        # Series Emergency BGU Block
        bgu_sch_x = facp_x + 600
        self.writer.add_rectangle(bgu_sch_x, facp_y, 400, 300, layer="E-ACS-DEVICES")
        self.writer.add_text("EMERGENCY BGU", (bgu_sch_x + 40, facp_y + 220), height=40, layer="E-ACS-TEXT")
        self.writer.add_text("[ NC CONTACT ]", (bgu_sch_x + 60, facp_y + 150), height=40, layer="E-ACS-DEVICES")
        self.writer.add_text("Manual Glass Break", (bgu_sch_x + 40, facp_y + 80), height=35, layer="E-ACS-TEXT")

        # Maglock Load Symbol
        ml_sch_x = bgu_sch_x + 600
        self.writer.add_rectangle(ml_sch_x, facp_y + 50, 300, 200, layer="E-ACS-DEVICES")
        self.writer.add_text("MAGLOCK", (ml_sch_x + 50, facp_y + 160), height=40, layer="E-ACS-TEXT")
        self.writer.add_text("12V FAIL-SAFE", (ml_sch_x + 40, facp_y + 100), height=35, layer="E-ACS-TEXT")

        # Interconnecting Wiring
        # PSU +12V -> FACP NC Relay -> BGU NC Contact -> Maglock (+)
        self.writer.add_line((psu_x + 500, sch_y + 850), (facp_x, facp_y + 150), layer="E-ACS-WIRING")
        self.writer.add_text("+12V DC Supply", (psu_x + 540, sch_y + 870), height=35, layer="E-ACS-WIRING")

        self.writer.add_line((facp_x + 400, facp_y + 150), (bgu_sch_x, facp_y + 150), layer="E-ACS-WIRING")
        self.writer.add_text("Supervised Loop", (facp_x + 420, facp_y + 170), height=35, layer="E-ACS-WIRING")

        self.writer.add_line((bgu_sch_x + 400, facp_y + 150), (ml_sch_x, facp_y + 150), layer="E-ACS-WIRING")
        self.writer.add_text("Direct Series Cut", (bgu_sch_x + 420, facp_y + 170), height=35, layer="E-ACS-WIRING")

        # Negative Return: Maglock (-) -> PSU GND
        self.writer.add_line((ml_sch_x + 150, facp_y + 50), (ml_sch_x + 150, sch_y + 300), layer="E-ACS-WIRING")
        self.writer.add_line((ml_sch_x + 150, sch_y + 300), (psu_x + 250, sch_y + 300), layer="E-ACS-WIRING")
        self.writer.add_line((psu_x + 250, sch_y + 300), (psu_x + 250, sch_y + 400), layer="E-ACS-WIRING")
        self.writer.add_text("0V (GND) Common Return", (psu_x + 600, sch_y + 330), height=35, layer="E-ACS-WIRING")

        # -------------------------------------------------------------
        # VIEW 3: Standard Symbol Legend
        # -------------------------------------------------------------
        leg_x = 0.0
        leg_y = -1200.0
        self.writer.add_rectangle(leg_x, leg_y, 4200, 900, layer="E-ACS-TEXT")
        self.writer.add_text("ACCESS CONTROL SYMBOL LEGEND & INSTALLATION SPECIFICATIONS", (leg_x + 100, leg_y + 800), height=60, layer="E-ACS-TEXT")

        legend_items = [
            ("[CR]", "Proximity Card / Smart Reader (+1200mm AFF, exterior)", "4-Pair Cat6A shielded or 6-Core 0.8mm"),
            ("[BIO]", "Biometric Fingerprint / Facial Reader (+1200mm AFF)", "Cat6A PoE or 12V DC auxiliary + RS485"),
            ("[ML]", "Electromagnetic Lock (600/1200 lbs fail-safe)", "2x 1.5mm2 Fire Rated (FP200) from PSU"),
            ("[REX]", "Request-to-Exit PIR / Push Button (+1200 / +2300mm)", "4-Core 0.8mm twisted shielded"),
            ("[BGU]", "Emergency Break Glass Unit (Green, +1200mm AFF)", "2x 1.5mm2 in direct series with lock power"),
            ("[DPS]", "Concealed Magnetic Door Contact (Door Status)", "2-Core 0.8mm alarm cable"),
            ("[FACP]", "Fire Alarm Control Panel Supervised Interlock", "Interface relay drops lock power on alarm"),
        ]

        for i, (sym, desc, cable) in enumerate(legend_items):
            col = leg_x + 100 + (i % 2) * 2000
            row = leg_y + 680 - (i // 2) * 160
            self.writer.add_text(f"{sym}  {desc}", (col, row), height=45, layer="E-ACS-TEXT")
            self.writer.add_text(f"        Wiring: {cable}", (col, row - 60), height=35, layer="E-ACS-DIMS")

        self.writer.save(filepath)
        return filepath
