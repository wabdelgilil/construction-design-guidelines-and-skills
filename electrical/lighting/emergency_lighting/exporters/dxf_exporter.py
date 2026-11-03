"""
AutoCAD DXF Exporter for Emergency Lighting and Exit Signs Layout.
Generates escape route luminaires, illuminated exit signs, CBS panel, and circuit paths.
"""

from pathlib import Path
from ezdxf.enums import TextEntityAlignment
from core.exporters.dxf_writer import DXFWriter
from electrical.lighting.emergency_lighting.scripts.design_engine import EmergencyLightingDesignResult


class EmergencyLightingDXFExporter:
    """Exports emergency lighting plan and exit sign layout to AutoCAD .dxf format."""

    def __init__(self, result: EmergencyLightingDesignResult):
        self.res = result
        self.writer = DXFWriter("emergency_lighting_layout.dxf")

    def export(self, filepath: Path) -> Path:
        plan_w = 14000.0
        plan_h = 10000.0
        margin = 1000.0

        # Sheet Border
        self.writer.add_rectangle(-margin, -margin, plan_w + 2 * margin + 2500, plan_h + 2 * margin, layer="S-TITLEBLOCK")

        # Title Block
        self.writer.add_text("EMERGENCY EVACUATION LIGHTING & EXIT SIGNS PLAN", (0, plan_h + 650), height=180, layer="E-TEXT")
        self.writer.add_text(
            f"Standards: {self.res.standard_used} | System: {self.res.system_architecture} | Autonomy: {self.res.autonomy_hours * 60:.0f} Minutes | CBS Inverter: {self.res.cbs_inverter_rated_va} VA",
            (0, plan_h + 350),
            height=110,
            layer="E-TEXT",
        )

        # 1. Building Outer Boundary
        self.writer.add_rectangle(0, 0, plan_w, plan_h, layer="S-COLUMN")

        # 2. Main Corridor (Escape Route across center: y=4500 to y=5500)
        corr_y = 4500.0
        corr_h = 1000.0
        self.writer.add_rectangle(0, corr_y, plan_w, corr_h, layer="S-CONC-BLINDING")
        self.writer.add_text("PRIMARY ESCAPE CORRIDOR (MIN 1.0 LUX)", (plan_w / 2, corr_y + corr_h / 2), height=90, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)

        # 3. CBS Panel in Electrical Room (Bottom-Left)
        cbs_x, cbs_y = 400.0, 500.0
        self.writer.add_rectangle(cbs_x, cbs_y, 400.0, 500.0, layer="E-POWR-PANL")
        self.writer.add_text("CBS", (cbs_x + 200, cbs_y + 300), height=70, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
        self.writer.add_text(f"{self.res.cbs_inverter_rated_va}VA", (cbs_x + 200, cbs_y + 150), height=55, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)

        # 4. Emergency Luminaires spaced along corridor
        n_lights = max(self.res.total_emergency_luminaires, 4)
        spacing_x = (plan_w - 2000.0) / max(n_lights - 1, 1)

        cbs_points = [(cbs_x + 200, cbs_y + 500)]

        for i in range(n_lights):
            lx = 1000.0 + (i * spacing_x)
            ly = corr_y + corr_h / 2.0
            cbs_points.append((lx, ly))

            # Emergency Light symbol: Circle with [E] inside
            self.writer.msp.add_circle((lx, ly), radius=80, dxfattribs={"layer": "E-LITE-FIXT"})
            self.writer.add_text("E", (lx, ly), height=70, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
            self.writer.add_text("1.0 Lux", (lx, ly - 140), height=45, layer="E-TEXT", align=TextEntityAlignment.TOP_CENTER)

        # 5. Illuminated EXIT Signs over exit doors (Left and Right ends)
        # Exit 1 (Left End of Corridor)
        self.writer.add_rectangle(50.0, corr_y + 100, 150.0, 800.0, layer="S-REBAR-BOT")
        self.writer.add_text("[<-- EXIT 1]", (400.0, corr_y + corr_h + 100), height=70, layer="S-DIMS")

        # Exit 2 (Right End of Corridor)
        self.writer.add_rectangle(plan_w - 200.0, corr_y + 100, 150.0, 800.0, layer="S-REBAR-BOT")
        self.writer.add_text("[EXIT 2 -->]", (plan_w - 700.0, corr_y + corr_h + 100), height=70, layer="S-DIMS")

        # 6. CBS Circuit Homerun line
        if len(cbs_points) > 1:
            for p_idx in range(len(cbs_points) - 1):
                self.writer.add_line(cbs_points[p_idx], cbs_points[p_idx + 1], layer="E-LITE-CIRC")

        # 7. Legend & Compliance Box
        leg_x = plan_w + 300
        leg_y = plan_h
        self.writer.add_rectangle(leg_x, leg_y - 4500, 2000, 4500, layer="S-TITLEBLOCK")
        self.writer.add_text("EMERGENCY LIGHTING LEGEND", (leg_x + 100, leg_y - 250), height=100, layer="E-TEXT")

        legend_items = [
            ("[E] Emergency LED Luminaire", "Min 1.0 Lux on Escape Path"),
            ("[EXIT] Illuminated Directional Sign", "Mounted @ +2200mm Over Doors"),
            ("[CBS] Central Battery System Inverter", f"{self.res.cbs_inverter_rated_va} VA ({self.res.cbs_battery_dc_bus_v}V DC)"),
            (f"Total Emergency Load: {self.res.total_emergency_load_watts} W", "High-Efficiency LED Fixtures"),
            (f"Autonomy Duration: {self.res.autonomy_hours * 60:.0f} Minutes", "NFPA 101 / SBC 801 Mandate"),
            ("Cable Type: 2x1.5mm2 Fire-Resistant", "FP200 / PH120 Red Shielded"),
            ("Phase Monitor Relay: Included", "Auto-Transfer on Blackout"),
        ]

        for idx, (sym, desc) in enumerate(legend_items):
            self.writer.add_text(f"{sym}", (leg_x + 100, leg_y - 650 - (idx * 300)), height=70, layer="E-TEXT")
            self.writer.add_text(f"  - {desc}", (leg_x + 100, leg_y - 750 - (idx * 300)), height=55, layer="S-TEXT")

        return self.writer.save(filepath)
