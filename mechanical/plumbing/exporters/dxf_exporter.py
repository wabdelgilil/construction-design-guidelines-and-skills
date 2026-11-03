"""
AutoCAD DXF Exporter for Plumbing Riser Diagram and Sleeve Details.
Generates schematic drainage stack, water booster pump, and civil foundation sleeve callouts.
"""

from pathlib import Path
from ezdxf.enums import TextEntityAlignment
from core.exporters.dxf_writer import DXFWriter
from mechanical.plumbing.scripts.design_engine import PlumbingDesignResult


class PlumbingDXFExporter:
    """Exports plumbing riser and sleeve details to AutoCAD .dxf format."""

    def __init__(self, result: PlumbingDesignResult):
        self.res = result
        self.writer = DXFWriter("plumbing_riser.dxf")

    def export(self, filepath: Path) -> Path:
        # Drawing Border
        self.writer.add_rectangle(0, 0, 1400, 950, layer="S-TITLEBLOCK")

        # Title Block
        self.writer.add_text("PLUMBING DRAINAGE RISER & WATER BOOSTER SCHEMATIC", (40, 900), height=22, layer="M-TEXT")
        self.writer.add_text(f"Building: {self.res.building_tag} | Standards: {self.res.code_used} / IPC", (40, 870), height=14, layer="M-TEXT")
        self.writer.add_text(f"Drainage: {self.res.selected_soil_stack_diameter_in}\" Soil Stack | Water: {self.res.pump_motor_power_kw} kW Booster Set ({self.res.total_pump_head_bar} bar)", (40, 845), height=14, layer="M-TEXT")

        # 1. Drainage Riser Stack (Left side)
        stack_x = 250
        ground_y = 300
        roof_y = 800

        # Draw vertical soil stack pipe
        self.writer.add_line((stack_x, ground_y), (stack_x, roof_y), layer="M-PLMB-PIPE")
        self.writer.add_line((stack_x + 10, ground_y), (stack_x + 10, roof_y), layer="M-PLMB-PIPE")
        self.writer.add_text(f"{self.res.selected_soil_stack_diameter_in}\" SOIL & WASTE STACK (UPVC)", (stack_x - 180, 550), height=12, layer="M-TEXT")

        # Vent Through Roof (VTR)
        self.writer.add_line((stack_x + 5, roof_y), (stack_x + 5, roof_y + 40), layer="M-PLMB-PIPE")
        self.writer.add_text("VENT COWL (VTR)", (stack_x - 40, roof_y + 50), height=10, layer="M-TEXT")

        # Floor branch connections
        floors = [("ROOF LEVEL", 750), ("SECOND FLOOR", 600), ("FIRST FLOOR", 450), ("GROUND FLOOR", ground_y)]
        for fl_name, fl_y in floors:
            self.writer.add_line((stack_x - 150, fl_y), (stack_x + 250, fl_y), layer="S-CONC-BLINDING")
            self.writer.add_text(fl_name, (stack_x + 260, fl_y), height=9, layer="S-TEXT")
            # Branch pipe into stack
            self.writer.add_line((stack_x + 50, fl_y + 20), (stack_x, fl_y), layer="M-PLMB-PIPE")
            self.writer.add_text("Branch Drain", (stack_x + 60, fl_y + 15), height=8, layer="M-TEXT")

        # 2. Main Building Drain & Structural Grade Beam Sleeve Penetration
        self.writer.add_line((stack_x, ground_y), (stack_x, ground_y - 80), layer="M-PLMB-PIPE")
        self.writer.add_line((stack_x, ground_y - 80), (stack_x + 400, ground_y - 120), layer="M-PLMB-PIPE")
        self.writer.add_text(
            f"MAIN BUILDING DRAIN {self.res.selected_building_drain_diameter_in}\" @ {self.res.minimum_drain_slope_pct}% SLOPE",
            (stack_x + 50, ground_y - 130),
            height=10,
            layer="M-TEXT",
        )

        # Grade Beam Sleeve Callout Box
        sleeve_x, sleeve_y = stack_x + 220, ground_y - 100
        self.writer.add_rectangle(sleeve_x - 20, sleeve_y - 30, 40, 60, layer="S-COLUMN")
        self.writer.add_text("GRADE BEAM GB-01", (sleeve_x - 45, sleeve_y + 40), height=9, layer="S-TEXT")
        self.writer.add_text(f"PIPE SLEEVE {self.res.selected_building_drain_diameter_in + 2}\"", (sleeve_x - 45, sleeve_y - 45), height=9, layer="S-REBAR-BOT")

        # 3. Domestic Water Break Tank & Booster Set (Right side)
        tank_x, tank_y = 800, 300
        tank_w, tank_h = 160, 120
        self.writer.add_rectangle(tank_x, tank_y, tank_w, tank_h, layer="M-HVAC-EQUP")
        self.writer.add_text("POTABLE BREAK TANK", (tank_x + tank_w / 2, tank_y + tank_h / 2), height=10, layer="M-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)

        # Float switch inside tank
        self.writer.msp.add_circle((tank_x + 30, tank_y + 40), radius=8, dxfattribs={"layer": "E-POWR-SCKT"})
        self.writer.add_text("Low-Water Float Switch", (tank_x + 45, tank_y + 35), height=8, layer="E-TEXT")

        # Twin Booster Pumps
        pump1_x, pump1_y = tank_x + 220, tank_y + 20
        self.writer.msp.add_circle((pump1_x, pump1_y), radius=16, dxfattribs={"layer": "M-HVAC-EQUP"})
        self.writer.add_text("P-1 (Duty)", (pump1_x, pump1_y - 5), height=8, layer="M-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)

        pump2_x, pump2_y = tank_x + 220, tank_y + 70
        self.writer.msp.add_circle((pump2_x, pump2_y), radius=16, dxfattribs={"layer": "M-HVAC-EQUP"})
        self.writer.add_text("P-2 (Stby)", (pump2_x, pump2_y - 5), height=8, layer="M-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)

        # Suction and Discharge Headers
        self.writer.add_line((tank_x + tank_w, tank_y + 45), (pump1_x - 16, pump1_y), layer="M-PLMB-PIPE")
        self.writer.add_line((tank_x + tank_w, tank_y + 45), (pump2_x - 16, pump2_y), layer="M-PLMB-PIPE")
        self.writer.add_line((pump1_x + 16, pump1_y), (pump1_x + 60, tank_y + 45), layer="M-PLMB-PIPE")
        self.writer.add_line((pump2_x + 16, pump2_y), (pump2_x + 60, tank_y + 45), layer="M-PLMB-PIPE")

        # Discharge Riser to Building
        self.writer.add_line((pump1_x + 60, tank_y + 45), (pump1_x + 60, roof_y), layer="M-PLMB-PIPE")
        self.writer.add_text("DOMESTIC WATER RISER TO FIXTURES", (pump1_x + 70, 600), height=10, layer="M-TEXT")

        # Electrical Control Panel Box
        cp_x, cp_y = tank_x + 150, tank_y + 160
        self.writer.add_rectangle(cp_x, cp_y, 80, 50, layer="E-POWR-PANL")
        self.writer.add_text("PUMP PANEL", (cp_x + 40, cp_y + 30), height=8, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
        self.writer.add_text(f"{self.res.pump_voltage_v}V / {self.res.pump_mcb_rating_amps}A", (cp_x + 40, cp_y + 15), height=7, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)

        # 4. Legend & Summary Box
        leg_x = 800
        leg_y = 800
        self.writer.add_rectangle(leg_x, leg_y - 200, 550, 200, layer="S-TITLEBLOCK")
        self.writer.add_text("PLUMBING & MEP INTERFACE SUMMARY", (leg_x + 20, leg_y - 25), height=12, layer="M-TEXT")

        items = [
            f"1. Soil Stack: {self.res.selected_soil_stack_diameter_in}\" UPVC (Total DFU = {self.res.total_dfu})",
            f"2. Building Drain: {self.res.selected_building_drain_diameter_in}\" UPVC @ {self.res.minimum_drain_slope_pct}% minimum fall",
            f"3. Booster Pump Set: {self.res.pump_configuration}",
            f"4. Pump Duty: {self.res.pump_motor_power_kw} kW ea, Head = {self.res.total_pump_head_m}m ({self.res.total_pump_head_bar} bar)",
            f"5. Structural Sleeve: {self.res.selected_building_drain_diameter_in + 2}\" through GB-01 (Mid-depth, >200mm from C1)",
        ]
        for idx, text in enumerate(items):
            self.writer.add_text(text, (leg_x + 20, leg_y - 55 - (idx * 28)), height=9, layer="M-TEXT")

        return self.writer.save(filepath)
