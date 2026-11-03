"""
AutoCAD DXF Exporter for Addressable Fire Alarm Layout.
Generates scaled detector symbols, sounder/strobes, manual call points, and addressable loop path.
"""

from pathlib import Path
from ezdxf.enums import TextEntityAlignment
from core.exporters.dxf_writer import DXFWriter
from electrical.low_current_elv.fire_alarm.scripts.design_engine import FireAlarmDesignResult


class FireAlarmDXFExporter:
    """Exports fire alarm ceiling plan and loop wiring to AutoCAD .dxf format."""

    def __init__(self, result: FireAlarmDesignResult):
        self.res = result
        self.writer = DXFWriter("fire_alarm_layout.dxf")

    def export(self, filepath: Path) -> Path:
        scale = 1000.0  # mm
        # Base dimensions for floor plan presentation
        plan_w = 14000.0
        plan_h = 10000.0
        margin = 1000.0

        # 1. Title Block Border
        self.writer.add_rectangle(-margin, -margin, plan_w + 2 * margin + 2500, plan_h + 2 * margin, layer="S-TITLEBLOCK")
        self.writer.add_text(
            f"ADDRESSABLE FIRE ALARM SYSTEM PLAN - {self.res.project_name.upper()}",
            (0, plan_h + 650),
            height=180,
            layer="E-TEXT",
        )
        self.writer.add_text(
            f"Standards: {self.res.standard_used} | Total Devices: {self.res.grand_total_addressable_devices} | Loops: {self.res.total_loops_required} | Battery: {self.res.selected_battery_rating_ah} Ah",
            (0, plan_h + 350),
            height=110,
            layer="E-TEXT",
        )

        # 2. Outer Building Perimeter Wall
        self.writer.add_rectangle(0, 0, plan_w, plan_h, layer="S-COLUMN")

        # 3. Fire Alarm Control Panel (FACP)
        facp_x, facp_y = 400.0, 500.0
        self.writer.add_rectangle(facp_x, facp_y, 400.0, 600.0, layer="E-POWR-PANL")
        self.writer.add_text("FACP", (facp_x + 200, facp_y + 300), height=70, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)

        # 4. Draw Spaces and Allocate Devices
        grid_cols = 3
        cell_w = plan_w / grid_cols
        cell_h = plan_h / 2.0

        loop_points = [(facp_x + 200, facp_y + 600)]

        for idx, alloc in enumerate(self.res.allocations[:6]):
            col = idx % grid_cols
            row = idx // grid_cols

            rx = col * cell_w
            ry = plan_h - ((row + 1) * cell_h)

            # Room wall boundary
            self.writer.add_rectangle(rx + 50, ry + 50, cell_w - 100, cell_h - 100, layer="S-CONC-BLINDING")
            self.writer.add_text(
                f"{alloc.space_name} ({alloc.area_m2:.0f}m2)",
                (rx + cell_w / 2, ry + cell_h - 200),
                height=80,
                layer="E-TEXT",
                align=TextEntityAlignment.TOP_CENTER,
            )

            # Detector at room center
            cx = rx + cell_w / 2.0
            cy = ry + cell_h / 2.0
            loop_points.append((cx, cy))

            if "Heat" in alloc.detector_type:
                # Heat detector: circle with H
                self.writer.msp.add_circle((cx, cy), radius=80, dxfattribs={"layer": "E-POWR-SCKT"})
                self.writer.add_text("H", (cx, cy), height=70, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
            else:
                # Smoke detector: circle with S
                self.writer.msp.add_circle((cx, cy), radius=80, dxfattribs={"layer": "E-POWR-SCKT"})
                self.writer.add_text("S", (cx, cy), height=70, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)

            # Sounder / Strobe in room
            if alloc.sounder_strobe_count > 0:
                ss_x, ss_y = cx + 500, cy
                self.writer.add_rectangle(ss_x - 60, ss_y - 60, 120, 120, layer="E-POWR-CIRC")
                self.writer.add_text(f"SS({alloc.strobe_candela_cd}cd)", (ss_x, ss_y - 120), height=50, layer="E-TEXT", align=TextEntityAlignment.TOP_CENTER)

            # Manual Call Point (if exit space)
            if alloc.mcp_count > 0:
                mcp_x, mcp_y = rx + 150, ry + 150
                self.writer.add_rectangle(mcp_x - 50, mcp_y - 50, 100, 100, layer="S-REBAR-BOT")
                self.writer.add_text("MCP", (mcp_x, mcp_y), height=45, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)

        # 5. Draw Addressable Class A / Class B Loop Cable Run
        if len(loop_points) > 1:
            for p_idx in range(len(loop_points) - 1):
                self.writer.add_line(loop_points[p_idx], loop_points[p_idx + 1], layer="S-REBAR-BOT")
            # Loop Return to FACP (Class A Loop)
            self.writer.add_line(loop_points[-1], (facp_x + 200, facp_y), layer="S-REBAR-BOT")

        # 6. Fire Alarm Legend Box
        leg_x = plan_w + 300
        leg_y = plan_h
        self.writer.add_rectangle(leg_x, leg_y - 4500, 2000, 4500, layer="S-TITLEBLOCK")
        self.writer.add_text("FIRE ALARM DEVICE LEGEND", (leg_x + 100, leg_y - 250), height=100, layer="E-TEXT")

        legend_items = [
            ("[S] Optical Smoke Detector (Max 81m2)", "Ceiling Mounted"),
            ("[H] Rate-of-Rise Heat Detector (Max 49m2)", "Ceiling Mounted"),
            ("[MCP] Manual Call Point (Break Glass)", "+1200mm AFF @ Exits"),
            ("[SS] Sounder / Flashing Strobe", "Wall Mounted (+2200mm AFF)"),
            ("[FACP] Fire Alarm Control Panel", "Main Security Room"),
            ("Loop Cable: 2x1.5mm2 Fire-Resistant", "FP200 / PH120 Shielded"),
            (f"Total Addressable Points: {self.res.grand_total_addressable_devices}", "Across System"),
            (f"Standby Battery: {self.res.selected_battery_rating_ah} Ah (24V)", "24h Standby + 15m Alarm"),
        ]

        for idx, (sym, desc) in enumerate(legend_items):
            self.writer.add_text(f"{sym}", (leg_x + 100, leg_y - 650 - (idx * 300)), height=70, layer="E-TEXT")
            self.writer.add_text(f"  - {desc}", (leg_x + 100, leg_y - 750 - (idx * 300)), height=55, layer="S-TEXT")

        return self.writer.save(filepath)
