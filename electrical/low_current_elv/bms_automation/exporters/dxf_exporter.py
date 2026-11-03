"""
AutoCAD DXF Exporter for Building Management System (BMS) Architecture and AHU DDC Control Hookups.
"""

from pathlib import Path
from core.exporters.dxf_writer import DXFWriter
from electrical.low_current_elv.bms_automation.scripts.design_engine import BMSDesignResult


class BMSDXFExporter:
    """Exports BMS system network architecture and AHU DDC hookup schematics to AutoCAD .dxf format."""

    def __init__(self, result: BMSDesignResult):
        self.res = result
        self.writer = DXFWriter("bms_network_architecture.dxf")
        self._setup_layers()

    def _setup_layers(self):
        layers = [
            ("E-BMS-SERVER", 1),    # Red: Management Level Servers & Workstations
            ("E-BMS-BACNET", 4),    # Cyan: BACnet/IP Ethernet Ring & Switches
            ("E-BMS-MSTP", 6),      # Magenta: BACnet MS/TP Field Bus
            ("E-BMS-DDC", 7),       # White: DDC Panels & Controllers
            ("E-BMS-FIELD", 3),     # Green: Field Sensors & Modulating Actuators
            ("E-BMS-DIMS", 2),      # Yellow: Dimensions and point tags
            ("E-BMS-TEXT", 7),      # White: Titles and text labels
        ]
        for name, color in layers:
            if name not in self.writer.doc.layers:
                lyr = self.writer.doc.layers.add(name)
                lyr.color = color

    def export(self, filepath: Path) -> Path:
        # Title Block
        self.writer.add_text(
            "BUILDING MANAGEMENT SYSTEM (BMS) - BACnet/IP ARCHITECTURE & AHU CONTROL HOOKUP",
            (0, 3100),
            height=120,
            layer="E-BMS-TEXT",
        )
        self.writer.add_text(
            f"Project: {self.res.project_name} | Code: {self.res.standard_used} | Total Hardwired I/O: {self.res.grand_total_active_points} Active + {self.res.grand_total_spare_points} Spare (20%)",
            (0, 2950),
            height=70,
            layer="E-BMS-TEXT",
        )

        # -------------------------------------------------------------
        # VIEW 1: BMS Three-Tier Network Architecture (BACnet Pyramid)
        # -------------------------------------------------------------
        arch_x = 0.0
        arch_y = 1200.0

        self.writer.add_text("THREE-TIER BMS SYSTEM ARCHITECTURE (MANAGEMENT / AUTOMATION / FIELD)", (arch_x, arch_y + 1600), height=60, layer="E-BMS-TEXT")

        # 1. Management Level (Top Box)
        mgmt_y = arch_y + 1200.0
        self.writer.add_rectangle(arch_x + 800, mgmt_y, 800, 300, layer="E-BMS-SERVER")
        self.writer.add_text("MANAGEMENT LEVEL: CENTRAL BMS SERVER", (arch_x + 850, mgmt_y + 230), height=30, layer="E-BMS-SERVER")
        self.writer.add_text("Dual 27\" Operator Workstations & Database SAN", (arch_x + 850, mgmt_y + 170), height=25, layer="E-BMS-TEXT")
        self.writer.add_text("BACnet/IP Gateway & Web Browser Client", (arch_x + 850, mgmt_y + 110), height=25, layer="E-BMS-DIMS")
        self.writer.add_text(f"Central UPS: {self.res.recommended_ups_va} VA (2.0h Backup)", (arch_x + 850, mgmt_y + 50), height=25, layer="E-BMS-DIMS")

        # Gigabit Ethernet Switch
        sw_y = mgmt_y - 250
        self.writer.add_rectangle(arch_x + 900, sw_y, 600, 150, layer="E-BMS-BACNET")
        self.writer.add_text("CORE BMS ETHERNET SWITCH (1 Gbps)", (arch_x + 950, sw_y + 80), height=28, layer="E-BMS-BACNET")
        self.writer.add_line((arch_x + 1200, mgmt_y), (arch_x + 1200, sw_y + 150), layer="E-BMS-BACNET")

        # 2. Automation Level: Distributed DDC Panels on BACnet/IP Backbone
        pnl_base_y = sw_y - 500
        for i, p in enumerate(self.res.ddc_panels):
            px = arch_x + 100 + i * 800
            self.writer.add_rectangle(px, pnl_base_y, 650, 380, layer="E-BMS-DDC")
            self.writer.add_text(f"DDC PANEL: [{p.panel_tag}]", (px + 40, pnl_base_y + 310), height=32, layer="E-BMS-DDC")
            self.writer.add_text(f"Loc: {p.panel_location}", (px + 40, pnl_base_y + 250), height=24, layer="E-BMS-TEXT")
            self.writer.add_text(f"Active I/O: {p.active_points} | Spare: {p.spare_points} (20%)", (px + 40, pnl_base_y + 190), height=22, layer="E-BMS-DIMS")
            self.writer.add_text(f"Hardware: {p.base_ddc_units_count}x DDC32 + {p.expansion_modules_count}x UI16", (px + 40, pnl_base_y + 130), height=22, layer="E-BMS-DIMS")
            self.writer.add_text(f"Native BACnet/IP RJ45 Port", (px + 40, pnl_base_y + 70), height=22, layer="E-BMS-BACNET")

            # Ethernet connection back to Switch
            self.writer.add_line((px + 325, pnl_base_y + 380), (arch_x + 1200, sw_y), layer="E-BMS-BACNET")

        # -------------------------------------------------------------
        # VIEW 2: Typical AHU DDC Control Hookup Schematic
        # -------------------------------------------------------------
        ahu_x = 0.0
        ahu_y = -300.0
        ahu_w = 2400.0
        ahu_h = 800.0

        self.writer.add_text("TYPICAL AIR HANDLING UNIT (AHU) DDC SENSOR & ACTUATOR CONTROL LOOP", (ahu_x, ahu_y + ahu_h + 100), height=60, layer="E-BMS-TEXT")

        # AHU Duct Outline
        self.writer.add_rectangle(ahu_x, ahu_y, ahu_w, ahu_h, layer="E-BMS-FIELD")
        self.writer.add_text("AHU DUCT CASING", (ahu_x + 100, ahu_y + ahu_h - 60), height=35, layer="E-BMS-FIELD")

        # 1. Fresh Air Damper
        self.writer.add_line((ahu_x + 200, ahu_y), (ahu_x + 200, ahu_y + ahu_h), layer="E-BMS-FIELD")
        self.writer.add_text("[DO] Damper Actuator (Spring Return)", (ahu_x + 50, ahu_y - 60), height=25, layer="E-BMS-DIMS")

        # 2. Air Filter with DPS
        self.writer.add_rectangle(ahu_x + 400, ahu_y + 50, 100, ahu_h - 100, layer="E-BMS-FIELD")
        self.writer.add_text("FILTER", (ahu_x + 410, ahu_y + 400), height=25, layer="E-BMS-FIELD")
        self.writer.add_text("[DI] Filter Dirty Alarm (DPS)", (ahu_x + 350, ahu_y + ahu_h + 40), height=25, layer="E-BMS-DIMS")

        # 3. Chilled Water Cooling Coil & Modulating Valve
        self.writer.add_rectangle(ahu_x + 800, ahu_y + 50, 150, ahu_h - 100, layer="E-BMS-FIELD")
        self.writer.add_text("CHW COIL", (ahu_x + 810, ahu_y + 400), height=25, layer="E-BMS-FIELD")
        # Valve Symbol on top
        self.writer.msp.add_circle((ahu_x + 875, ahu_y + ahu_h + 80), 30, dxfattribs={"layer": "E-BMS-FIELD"})
        self.writer.add_text("[AO] 2-Way Modulating Valve (0-100%)", (ahu_x + 750, ahu_y + ahu_h + 130), height=25, layer="E-BMS-DIMS")

        # 4. Supply Fan with DPS & VFD
        self.writer.msp.add_circle((ahu_x + 1400, ahu_y + 400), 200, dxfattribs={"layer": "E-BMS-FIELD"})
        self.writer.add_text("FAN", (ahu_x + 1350, ahu_y + 380), height=50, layer="E-BMS-FIELD")
        self.writer.add_text("[DI] Fan Run Status (Airflow DPS)", (ahu_x + 1250, ahu_y - 60), height=25, layer="E-BMS-DIMS")
        self.writer.add_text("[DO] Fan Start/Stop Command", (ahu_x + 1250, ahu_y - 110), height=25, layer="E-BMS-DIMS")
        self.writer.add_text("[AO] VFD Speed Modulation (0-10V)", (ahu_x + 1250, ahu_y - 160), height=25, layer="E-BMS-DIMS")

        # 5. Supply Air Duct Sensors (Temp & Static Pressure)
        self.writer.add_rectangle(ahu_x + 1900, ahu_y + 200, 100, 100, layer="E-BMS-FIELD")
        self.writer.add_text("[AI] Supply Air Temp Sensor (Pt1000)", (ahu_x + 1800, ahu_y + ahu_h + 40), height=25, layer="E-BMS-DIMS")
        self.writer.add_text("[AI] Duct Static Pressure (Pa)", (ahu_x + 1800, ahu_y + ahu_h + 90), height=25, layer="E-BMS-DIMS")

        # -------------------------------------------------------------
        # VIEW 3: Engineering Specifications Legend Table
        # -------------------------------------------------------------
        tbl_x = 0.0
        tbl_y = -900.0
        self.writer.add_rectangle(tbl_x, tbl_y, 2500, 500, layer="E-BMS-TEXT")
        self.writer.add_text("BMS AUTOMATION DESIGN CRITERIA & BACnet SPECIFICATIONS", (tbl_x + 50, tbl_y + 440), height=50, layer="E-BMS-TEXT")

        lines = [
            ("Network Protocols:", "Management/Automation: Native BACnet/IP over 10/100 Ethernet; Field bus: BACnet MS/TP RS-485"),
            ("Spare I/O Capacity:", f"Every DDC panel engineered with >= 20% spare points ({self.res.grand_total_spare_points} spare points project-wide)"),
            ("High-Level Gateways:", "Modbus RTU for VFD telemetry and MDB energy meters; native BACnet/IP for chiller packages"),
            ("Fail-Safe Operations:", "Fire Alarm Control Panel (FACP) hardwired interlock shuts down AHU supply fans immediately upon alarm"),
        ]

        for i, (hdr, val) in enumerate(lines):
            row_y = tbl_y + 350 - i * 90
            self.writer.add_text(f"• {hdr}", (tbl_x + 60, row_y), height=35, layer="E-BMS-TEXT")
            self.writer.add_text(val, (tbl_x + 550, row_y), height=32, layer="E-BMS-DIMS")

        self.writer.save(filepath)
        return filepath
