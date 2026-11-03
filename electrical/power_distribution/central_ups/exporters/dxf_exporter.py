"""AutoCAD DXF Exporter for Central UPS and DC Battery Room Systems."""

import math
from typing import Dict, Any
from core.exporters.dxf_writer import DXFWriter


class CentralUPSDXFExporter:
    """Exports 2D Single Line Diagram (SLD) and Battery Room Equipment Layout to DXF."""

    def __init__(self):
        self.writer = None

    def export(self, design_data: Dict[str, Any], file_path: str):
        self.writer = DXFWriter()
        self._setup_layers()

        # Sheet 1: Single Line Diagram of Online UPS System with Dual-Feed & Bypass
        self._draw_single_line_diagram(design_data)

        # Sheet 2 / Section: Battery Room Layout
        self._draw_battery_room_layout(design_data)

        # Drawing Title Block & Notes
        self._draw_title_block_and_notes(design_data)

        self.writer.save(file_path)

    def _setup_layers(self):
        doc = self.writer.doc
        layers = [
            ("E-POWR-UPS", 4),      # Cyan (UPS Module & Primary AC)
            ("E-POWR-DC", 1),       # Red (DC Battery & Inverter Link)
            ("E-POWR-BYPASS", 2),   # Yellow (Static & Maintenance Bypass)
            ("E-SWG-BRKR", 3),      # Green (Circuit Breakers)
            ("E-BATT-ROOM", 7),     # White (Architectural Walls & Door)
            ("E-BATT-RACK", 6),     # Magenta (Battery Racks & Monoblocs)
            ("M-HVAC-EXH", 5),      # Blue (Hydrogen Exhaust Fan)
            ("E-TEXT-LABEL", 7),    # White (Annotations)
            ("E-DIM-LINE", 8),      # Gray (Dimensions)
        ]
        for name, color in layers:
            if name not in doc.layers:
                doc.layers.add(name, color=color)

    def _draw_single_line_diagram(self, data: Dict[str, Any]):
        msp = self.writer.msp
        ups = data["ups_module"]
        batt = data["battery_plant"]
        brk = data["breakers"]

        # Base origin for SLD
        x_base = 50.0
        y_base = 180.0

        # Title
        msp.add_text(
            f"TRUE ONLINE DOUBLE-CONVERSION UPS SYSTEM ({data.get('redundancy_type', 'N+1')} ARCHITECTURE)",
            dxfattribs={"layer": "E-TEXT-LABEL", "height": 3.5}
        ).set_placement((x_base, y_base + 35.0))

        # 1. Dual Supply Feeds from Essential MDB / EM-Switchboard
        # Feed 1: Normal / Rectifier Mains
        msp.add_line((x_base, y_base + 20), (x_base + 25, y_base + 20), dxfattribs={"layer": "E-POWR-UPS"})
        msp.add_text("400V MDB RECTIFIER FEED", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.8}).set_placement((x_base, y_base + 22))

        # Feed 2: Bypass Mains
        msp.add_line((x_base, y_base - 10), (x_base + 25, y_base - 10), dxfattribs={"layer": "E-POWR-BYPASS"})
        msp.add_text("400V BYPASS MAINS FEED", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.8}).set_placement((x_base, y_base - 8))

        # Input Breakers
        self._draw_breaker(msp, x_base + 25, y_base + 20, f"Q1: {brk['rectifier_input_breaker_a']}A", "E-SWG-BRKR")
        self._draw_breaker(msp, x_base + 25, y_base - 10, f"Q2: {brk['static_bypass_breaker_a']}A", "E-SWG-BRKR")

        # 2. UPS Converter Cabinet Box
        ups_box_x = x_base + 45
        ups_box_y = y_base - 20
        msp.add_lwpolyline(
            [(ups_box_x, ups_box_y), (ups_box_x + 95, ups_box_y), (ups_box_x + 95, ups_box_y + 50),
             (ups_box_x, ups_box_y + 50), (ups_box_x, ups_box_y)],
            dxfattribs={"layer": "E-POWR-UPS"}
        )
        msp.add_text(
            f"UPS MODULE ({ups['selected_module_kva']} kVA / {int(ups['selected_module_kva']*0.9)} kW)",
            dxfattribs={"layer": "E-TEXT-LABEL", "height": 2.2}
        ).set_placement((ups_box_x + 10, ups_box_y + 45))

        # Internal Rectifier (AC -> DC)
        rect_x = ups_box_x + 15
        rect_y = y_base + 20
        self._draw_converter_block(msp, rect_x, rect_y, "RECTIFIER\n(IGBT AC/DC)")

        # Internal Inverter (DC -> AC)
        inv_x = ups_box_x + 55
        inv_y = y_base + 20
        self._draw_converter_block(msp, inv_x, inv_y, "INVERTER\n(PWM DC/AC)")

        # DC Bus connecting Rectifier, Battery, and Inverter
        msp.add_line((rect_x + 10, rect_y), (inv_x - 10, rect_y), dxfattribs={"layer": "E-POWR-DC"})
        dc_mid_x = (rect_x + 10 + inv_x - 10) / 2.0

        # Connection down to Battery DC breaker
        msp.add_line((dc_mid_x, rect_y), (dc_mid_x, rect_y - 25), dxfattribs={"layer": "E-POWR-DC"})
        self._draw_breaker(msp, dc_mid_x, rect_y - 25, f"Q_DC: {brk['battery_dc_breaker_a']}A", "E-SWG-BRKR")

        # Battery Bank Symbol
        batt_y = rect_y - 45
        self._draw_battery_bank_symbol(msp, dc_mid_x, batt_y, f"{batt['blocks_per_string']} x 12V VRLA ({batt['actual_installed_ah']} Ah)")

        # Static Switch (Bypass path)
        bypass_sw_x = ups_box_x + 40
        bypass_sw_y = y_base - 10
        self._draw_converter_block(msp, bypass_sw_x, bypass_sw_y, "STATIC BYPASS\n(< 4ms SCR)")

        # Feed lines inside UPS
        msp.add_line((x_base + 32, y_base + 20), (rect_x - 10, rect_y), dxfattribs={"layer": "E-POWR-UPS"})
        msp.add_line((x_base + 32, y_base - 10), (bypass_sw_x - 10, bypass_sw_y), dxfattribs={"layer": "E-POWR-BYPASS"})

        # Junction to output
        out_junc_x = ups_box_x + 85
        msp.add_line((inv_x + 10, inv_y), (out_junc_x, inv_y), dxfattribs={"layer": "E-POWR-UPS"})
        msp.add_line((bypass_sw_x + 10, bypass_sw_y), (out_junc_x, bypass_sw_y), dxfattribs={"layer": "E-POWR-BYPASS"})
        msp.add_line((out_junc_x, bypass_sw_y), (out_junc_x, inv_y), dxfattribs={"layer": "E-POWR-UPS"})

        # Output Breaker & Critical Output Bus
        self._draw_breaker(msp, ups_box_x + 105, (inv_y + bypass_sw_y) / 2.0, f"Q3: {brk['inverter_output_breaker_a']}A", "E-SWG-BRKR")
        crit_bus_x = ups_box_x + 125
        msp.add_line((ups_box_x + 112, (inv_y + bypass_sw_y) / 2.0), (crit_bus_x + 30, (inv_y + bypass_sw_y) / 2.0), dxfattribs={"layer": "E-POWR-UPS"})
        msp.add_text("TO CRITICAL POWER DISTRIBUTION BOARD (PDU / MDB-UPS)", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.8}).set_placement((crit_bus_x - 5, (inv_y + bypass_sw_y) / 2.0 + 3.0))

        # External Maintenance Bypass Line (Over the top)
        mbp_y = y_base + 40
        msp.add_line((x_base + 20, y_base + 20), (x_base + 20, mbp_y), dxfattribs={"layer": "E-POWR-BYPASS"})
        msp.add_line((x_base + 20, mbp_y), (crit_bus_x + 10, mbp_y), dxfattribs={"layer": "E-POWR-BYPASS"})
        msp.add_line((crit_bus_x + 10, mbp_y), (crit_bus_x + 10, (inv_y + bypass_sw_y) / 2.0), dxfattribs={"layer": "E-POWR-BYPASS"})
        self._draw_breaker(msp, (x_base + 20 + crit_bus_x + 10) / 2.0, mbp_y, "MANUAL MAINTENANCE BYPASS (MBP - INTERLOCKED)", "E-SWG-BRKR")

    def _draw_battery_room_layout(self, data: Dict[str, Any]):
        msp = self.writer.msp
        batt = data["battery_plant"]
        vent = data["ventilation"]

        # Battery Room Architectural Layout
        rx = 50.0
        ry = 40.0
        rw = 110.0
        rh = 70.0

        # Room Outline
        msp.add_lwpolyline(
            [(rx, ry), (rx + rw, ry), (rx + rw, ry + rh), (rx, ry + rh), (rx, ry)],
            dxfattribs={"layer": "E-BATT-ROOM"}
        )
        msp.add_text("DEDICATED BATTERY ROOM EQUIPMENT LAYOUT (PLAN VIEW)", dxfattribs={"layer": "E-TEXT-LABEL", "height": 3.0}).set_placement((rx, ry + rh + 4))

        # Double Entrance Door with Panic Hardware
        door_x = rx + 15
        msp.add_line((door_x, ry), (door_x + 16, ry + 16), dxfattribs={"layer": "E-BATT-ROOM"})
        msp.add_text("FIRE-RATED DOOR (2-HR)", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.4}).set_placement((door_x, ry - 3))

        # Battery Racks (2-Tier Steel Acid-Resistant Racks)
        rack_w = 40.0
        rack_d = 12.0

        for idx in range(batt["num_parallel_strings"]):
            rack_x = rx + 15 + (idx * 48.0)
            rack_y = ry + 25.0

            msp.add_lwpolyline(
                [(rack_x, rack_y), (rack_x + rack_w, rack_y), (rack_x + rack_w, rack_y + rack_d),
                 (rack_x, rack_y + rack_d), (rack_x, rack_y)],
                dxfattribs={"layer": "E-BATT-RACK"}
            )
            msp.add_text(f"BATTERY RACK STRING #{idx+1}", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.8}).set_placement((rack_x + 2, rack_y + rack_d + 2))
            msp.add_text(f"({batt['blocks_per_string']} Blocks 12V {batt['selected_block_ah']}Ah VRLA)", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.4}).set_placement((rack_x + 2, rack_y + 4))

            # Monobloc visual grids
            n_blocks = min(batt['blocks_per_string'], 16)
            block_w = (rack_w - 4) / n_blocks
            for b in range(n_blocks):
                bx = rack_x + 2 + b * block_w
                msp.add_lwpolyline(
                    [(bx, rack_y + 2), (bx + block_w - 0.4, rack_y + 2),
                     (bx + block_w - 0.4, rack_y + rack_d - 2), (bx, rack_y + rack_d - 2), (bx, rack_y + 2)],
                    dxfattribs={"layer": "E-BATT-RACK"}
                )

        # DC Battery Disconnect Switchboard (Wall-mounted)
        msp.add_lwpolyline(
            [(rx + 5, ry + 40), (rx + 11, ry + 40), (rx + 11, ry + 52), (rx + 5, ry + 52), (rx + 5, ry + 40)],
            dxfattribs={"layer": "E-SWG-BRKR"}
        )
        msp.add_text("DC BATT PANEL\n(2P MCCB + SHUNT)", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.3}).set_placement((rx + 2, ry + 54))

        # Emergency Eye-Wash & Drench Shower (Safety Code)
        msp.add_circle((rx + rw - 12, ry + 12), radius=3.5, dxfattribs={"layer": "E-TEXT-LABEL"})
        msp.add_text("EYE-WASH &\nSAFETY SHOWER", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.3}).set_placement((rx + rw - 24, ry + 12))

        # Spark-Proof Hydrogen Exhaust Fan & Sensor (Top wall near ceiling)
        fan_x = rx + rw - 25
        fan_y = ry + rh - 6
        msp.add_circle((fan_x, fan_y), radius=4.0, dxfattribs={"layer": "M-HVAC-EXH"})
        msp.add_line((fan_x - 3, fan_y - 3), (fan_x + 3, fan_y + 3), dxfattribs={"layer": "M-HVAC-EXH"})
        msp.add_line((fan_x - 3, fan_y + 3), (fan_x + 3, fan_y - 3), dxfattribs={"layer": "M-HVAC-EXH"})
        msp.add_text(f"ATEX SPARK-PROOF EXHAUST FAN\n{vent['design_exhaust_airflow_m3_per_hr']} m3/h ({vent['design_exhaust_airflow_cfm']} CFM)", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.4}).set_placement((fan_x - 15, fan_y - 8))

        # Hydrogen H2 Gas Detector
        msp.add_circle((fan_x - 15, fan_y + 2), radius=1.5, dxfattribs={"layer": "E-TEXT-LABEL"})
        msp.add_text("H2 DETECTOR (1.0% ALARM)", dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.2}).set_placement((fan_x - 35, fan_y + 2))

    def _draw_breaker(self, msp, x: float, y: float, label: str, layer: str):
        # Draw IEC standard circuit breaker symbol (cross within square or circle)
        sz = 3.0
        msp.add_lwpolyline(
            [(x - sz, y - sz), (x + sz, y - sz), (x + sz, y + sz), (x - sz, y + sz), (x - sz, y - sz)],
            dxfattribs={"layer": layer}
        )
        msp.add_line((x - sz, y - sz), (x + sz, y + sz), dxfattribs={"layer": layer})
        msp.add_text(label, dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.4}).set_placement((x - sz, y + sz + 1.2))

    def _draw_converter_block(self, msp, cx: float, cy: float, label: str):
        w = 14.0
        h = 10.0
        msp.add_lwpolyline(
            [(cx - w/2, cy - h/2), (cx + w/2, cy - h/2), (cx + w/2, cy + h/2), (cx - w/2, cy + h/2), (cx - w/2, cy - h/2)],
            dxfattribs={"layer": "E-POWR-UPS"}
        )
        # Diagonal divider
        msp.add_line((cx - w/2, cy + h/2), (cx + w/2, cy - h/2), dxfattribs={"layer": "E-POWR-UPS"})
        lines = label.split("\n")
        if len(lines) >= 2:
            msp.add_text(lines[0], dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.3}).set_placement((cx - w/2 + 1, cy + 1))
            msp.add_text(lines[1], dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.1}).set_placement((cx - w/2 + 1, cy - 3.5))
        else:
            msp.add_text(label, dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.3}).set_placement((cx - w/2 + 1, cy - 1))

    def _draw_battery_bank_symbol(self, msp, cx: float, cy: float, label: str):
        # Draw series battery plates
        w = 8.0
        h_long = 6.0
        h_short = 3.5
        gap = 2.0

        for offset in [-gap, 0, gap]:
            x = cx + offset
            # Long line (positive)
            msp.add_line((x - 0.5, cy - h_long/2), (x - 0.5, cy + h_long/2), dxfattribs={"layer": "E-POWR-DC"})
            # Short thick line (negative)
            msp.add_line((x + 0.5, cy - h_short/2), (x + 0.5, cy + h_short/2), dxfattribs={"layer": "E-POWR-DC"})

        msp.add_text(label, dxfattribs={"layer": "E-TEXT-LABEL", "height": 1.4}).set_placement((cx - 20, cy - h_long/2 - 3.0))

    def _draw_title_block_and_notes(self, data: Dict[str, Any]):
        msp = self.writer.msp

        # Notes block
        nx = 190.0
        ny = 40.0
        notes = [
            "GENERAL ENGINEERING NOTES:",
            "1. UPS SYSTEM SHALL BE TRUE ONLINE DOUBLE CONVERSION CLASSIFIED VFI-SS-111 AS PER IEC 62040-3.",
            "2. BATTERY PLANT SIZED UNDER CONSTANT POWER DISCHARGE METHOD COMPLYING WITH IEEE 485 AND IEEE 1184.",
            "3. STATIC BYPASS SWITCH SHALL COMPLETE TRANSFER TO BYPASS IN LESS THAN 4 MILLISECONDS UPON OVERLOAD/FAULT.",
            "4. MAINTENANCE BYPASS SWITCH IS ROTARY MAKE-BEFORE-BREAK WITH MECHANICAL KIRK-KEY INTERLOCKING.",
            "5. BATTERY ROOM SHALL BE EQUIPPED WITH SPARK-PROOF CONTINUOUS EXHAUST VENTILATION (NFPA 1 / SBC 401).",
            "6. EYE-WASH AND EMERGENCY SHOWER STATION SHALL BE OPERATIONAL ACCORDING TO OSHA 1910.151(C).",
            f"7. CODE STANDARD APPLIED: {data.get('code_standard', 'SBC')}."
        ]

        for idx, line in enumerate(notes):
            h = 1.6 if idx == 0 else 1.3
            msp.add_text(line, dxfattribs={"layer": "E-TEXT-LABEL", "height": h}).set_placement((nx, ny + (len(notes) - idx) * 4.0))
