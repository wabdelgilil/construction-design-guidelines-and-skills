"""
AutoCAD DXF Exporter for HVAC Air Distribution and Equipment Layout.
Generates scaled duct runs, supply diffusers, return grilles, and MEP coordination tags.
"""

from pathlib import Path
from ezdxf.enums import TextEntityAlignment
from core.exporters.dxf_writer import DXFWriter
from mechanical.hvac.heat_load.scripts.design_engine import HVACDesignResult


class HVACDXFExporter:
    """Exports HVAC room air distribution layout to AutoCAD .dxf format."""

    def __init__(self, result: HVACDesignResult, room_length_m: float = 8.0, room_width_m: float = 6.0):
        self.res = result
        self.l_m = room_length_m
        self.w_m = room_width_m
        self.writer = DXFWriter("hvac_layout.dxf")

    def export(self, filepath: Path) -> Path:
        scale = 1000.0  # 1m = 1000mm
        l_mm = self.l_m * scale
        w_mm = self.w_m * scale
        margin = 600.0

        # 1. Sheet Border & Header
        self.writer.add_rectangle(-margin, -margin, l_mm + 2 * margin + 900, w_mm + 2 * margin, layer="S-TITLEBLOCK")
        self.writer.add_text(
            f"HVAC DUCTING & AIR DISTRIBUTION PLAN - {self.res.space_name.upper()}",
            (0, w_mm + 400),
            height=60,
            layer="M-TEXT",
        )
        self.writer.add_text(
            f"Equipment: {self.res.selected_unit_model} | Total Airflow: {self.res.supply_airflow_cfm} CFM",
            (0, w_mm + 250),
            height=35,
            layer="M-TEXT",
        )
        self.writer.add_text(
            f"Electrical Feed: {self.res.electrical_voltage_v}V, MCA: {self.res.electrical_mca_amps}A, MOP: {self.res.electrical_mop_amps}A",
            (0, w_mm + 120),
            height=30,
            layer="M-TEXT",
        )

        # 2. Room Perimeter
        self.writer.add_rectangle(0, 0, l_mm, w_mm, layer="S-COLUMN")

        # 3. Draw Indoor Unit (FCU)
        fcu_w, fcu_h = 1000.0, 600.0
        fcu_x = 200.0
        fcu_y = w_mm - fcu_h - 200.0
        self.writer.add_rectangle(fcu_x, fcu_y, fcu_w, fcu_h, layer="M-HVAC-EQUP")
        self.writer.add_text(
            f"FCU-01 ({self.res.selected_unit_tons_tr} TR)",
            (fcu_x + fcu_w / 2, fcu_y + fcu_h / 2),
            height=30,
            layer="M-TEXT",
            align=TextEntityAlignment.MIDDLE_CENTER,
        )

        # 4. Supply Main Duct Run
        duct_w = 300.0
        duct_y = fcu_y + fcu_h / 2
        self.writer.add_line((fcu_x + fcu_w, duct_y - duct_w / 2), (l_mm - 500, duct_y - duct_w / 2), layer="M-HVAC-DUCT")
        self.writer.add_line((fcu_x + fcu_w, duct_y + duct_w / 2), (l_mm - 500, duct_y + duct_w / 2), layer="M-HVAC-DUCT")
        self.writer.add_text(f"SUPPLY DUCT {int(duct_w)}x250", (fcu_x + fcu_w + 200, duct_y + duct_w / 2 + 30), height=20, layer="M-TEXT")

        # 5. Supply Diffusers (Square 600x600 with diagonal crosses)
        diff_count = self.res.supply_diffusers_count
        spacing_x = (l_mm - 1200) / max(diff_count, 1)
        for i in range(diff_count):
            dx = 800 + (i * spacing_x)
            dy = w_mm / 2.0
            diff_size = 600.0
            half_d = diff_size / 2.0

            # Branch duct to diffuser
            self.writer.add_line((dx, duct_y - duct_w / 2), (dx, dy + half_d), layer="M-HVAC-DUCT")

            # Diffuser box
            self.writer.add_rectangle(dx - half_d, dy - half_d, diff_size, diff_size, layer="M-HVAC-EQUP")
            # 4-way arrows
            self.writer.add_line((dx - half_d, dy - half_d), (dx + half_d, dy + half_d), layer="M-HVAC-EQUP")
            self.writer.add_line((dx - half_d, dy + half_d), (dx + half_d, dy - half_d), layer="M-HVAC-EQUP")
            self.writer.add_text(
                f"SAD ({self.res.cfm_per_diffuser:.0f} CFM)",
                (dx, dy - half_d - 40),
                height=20,
                layer="M-TEXT",
                align=TextEntityAlignment.TOP_CENTER,
            )

        # 6. Return Air Grille
        rg_x = 200.0
        rg_y = 200.0
        self.writer.add_rectangle(rg_x, rg_y, 600.0, 600.0, layer="M-HVAC-EQUP")
        # Hatch-like diagonal lines for return grille
        self.writer.add_line((rg_x, rg_y), (rg_x + 600, rg_y + 600), layer="M-HVAC-EQUP")
        self.writer.add_text("RAD (RETURN)", (rg_x + 300, rg_y - 30), height=20, layer="M-TEXT", align=TextEntityAlignment.TOP_CENTER)

        # 7. Coordination Symbols: Wall Thermostat [T] and Isolator [ISO]
        # Thermostat on internal wall
        stat_x, stat_y = 0.0, w_mm / 3.0
        self.writer.msp.add_circle((stat_x + 30, stat_y), radius=20, dxfattribs={"layer": "E-POWR-SCKT"})
        self.writer.add_text("T", (stat_x + 30, stat_y), height=18, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
        self.writer.add_text("Thermostat (+1500mm AFF)", (stat_x + 70, stat_y - 10), height=18, layer="E-TEXT")

        # Isolator on outer boundary near condensing unit
        iso_x, iso_y = l_mm, w_mm - 400
        self.writer.add_rectangle(iso_x - 50, iso_y - 25, 50, 50, layer="E-POWR-SCKT")
        self.writer.add_text("ISO", (iso_x - 25, iso_y), height=14, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
        self.writer.add_text("AC Isolator (+2200mm AFF)", (iso_x - 260, iso_y - 40), height=16, layer="E-TEXT")

        # 8. Legend & MEP Interface Box
        leg_x = l_mm + 150
        leg_y = w_mm
        self.writer.add_rectangle(leg_x, leg_y - 500, 650, 500, layer="S-TITLEBLOCK")
        self.writer.add_text("HVAC & MEP COORDINATION SCHEDULE", (leg_x + 30, leg_y - 50), height=28, layer="M-TEXT")

        leg_rows = [
            f"Indoor Unit: {self.res.selected_unit_model}",
            f"Sensible Capacity: {self.res.total_sensible_heat_w/1000.0:.2f} kW | SHR: {self.res.sensible_heat_ratio_shr}",
            f"Total Supply Airflow: {self.res.supply_airflow_cfm} CFM",
            f"Diffusers: {self.res.supply_diffusers_count}x 4-Way Square ({self.res.cfm_per_diffuser} CFM ea)",
            f"Elec Feeder: {self.res.electrical_voltage_v}V, MCA {self.res.electrical_mca_amps}A, MOP {self.res.electrical_mop_amps}A MCB",
            f"Thermostat: 20mm conduit at +1500mm AFF",
            f"Plumbing: 25mm UPVC insulated condensate with P-Trap",
        ]
        for idx, text in enumerate(leg_rows):
            self.writer.add_text(text, (leg_x + 30, leg_y - 110 - (idx * 50)), height=20, layer="M-TEXT")

        return self.writer.save(filepath)
