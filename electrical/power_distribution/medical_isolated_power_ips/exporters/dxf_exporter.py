"""
AutoCAD DXF Exporter for Medical Isolated Power System (IPS) Single-Line Diagram (SLD).
Generates standard electrical schematic representation of Isolation Transformer, IMD,
and 2-Pole branch circuits.
"""

from pathlib import Path
from ezdxf.enums import TextEntityAlignment
from core.exporters.dxf_writer import DXFWriter
from electrical.power_distribution.medical_isolated_power_ips.scripts.design_engine import IPSDesignResult


class MedicalIPSDXFExporter:
    """Exports Medical IPS SLD to AutoCAD .dxf format."""

    def __init__(self, result: IPSDesignResult):
        self.res = result
        self.writer = DXFWriter("medical_ips_sld.dxf")

    def export(self, filepath: Path) -> Path:
        # Drawing Border
        self.writer.add_rectangle(0, 0, 1400, 900, layer="S-TITLEBLOCK")

        # Title Block
        self.writer.add_text("GROUP 2 MEDICAL LOCATION ISOLATED POWER SYSTEM (IPS) - SLD", (40, 850), height=22, layer="E-TEXT")
        self.writer.add_text(f"Room: {self.res.room_name} | Standards: {self.res.standard_used}", (40, 820), height=14, layer="E-TEXT")
        self.writer.add_text(f"Isolation Transformer: {self.res.selected_transformer_kva} kVA (230V/230V 1-Phase IT System)", (40, 795), height=14, layer="E-TEXT")

        # 1. Primary Supply Feed (Normal / Generator Essential ATS supply)
        pri_x, pri_y = 150, 720
        self.writer.add_text("ESSENTIAL POWER SUPPLY (UPS / ATS 230V)", (pri_x - 100, pri_y + 30), height=12, layer="E-TEXT")
        self.writer.add_line((pri_x, pri_y + 20), (pri_x, pri_y - 20), layer="E-POWR-PANL")

        # Primary MCB Curve D
        self.writer.add_rectangle(pri_x - 15, pri_y - 50, 30, 30, layer="E-POWR-PANL")
        self.writer.add_text(f"{self.res.primary_mcb_rating_amps}A [D]", (pri_x + 25, pri_y - 35), height=10, layer="E-TEXT")
        self.writer.add_line((pri_x, pri_y - 50), (pri_x, pri_y - 90), layer="E-POWR-PANL")

        # 2. Medical Isolation Transformer (Overlapping circles symbol)
        tx_y = pri_y - 140
        self.writer.msp.add_circle((pri_x, tx_y + 25), radius=25, dxfattribs={"layer": "E-POWR-PANL"})
        self.writer.msp.add_circle((pri_x, tx_y - 15), radius=25, dxfattribs={"layer": "E-POWR-PANL"})
        self.writer.add_text(f"TX {self.res.selected_transformer_kva} kVA", (pri_x + 35, tx_y + 5), height=11, layer="E-TEXT")
        self.writer.add_text("Electrostatic Shielded", (pri_x + 35, tx_y - 15), height=9, layer="E-TEXT")

        # Transformer Shield Earth connection
        self.writer.add_line((pri_x - 25, tx_y + 5), (pri_x - 60, tx_y + 5), layer="E-POWR-CIRC")
        self.writer.add_text("PE Shield", (pri_x - 110, tx_y + 2), height=8, layer="E-TEXT")

        # 3. Secondary Isolated Busbars (L1, L2 - No Earth Connection)
        bus_y = tx_y - 80
        self.writer.add_line((pri_x, tx_y - 40), (pri_x, bus_y), layer="E-POWR-PANL")
        self.writer.add_line((pri_x - 40, bus_y), (pri_x + 600, bus_y), layer="E-POWR-PANL")
        self.writer.add_text("ISOLATED SECONDARY BUSBAR 230V IT", (pri_x + 20, bus_y + 12), height=12, layer="E-TEXT")

        # 4. Insulation Monitoring Device (IMD) connected across bus
        imd_x = pri_x + 100
        self.writer.add_line((imd_x, bus_y), (imd_x, bus_y - 50), layer="E-POWR-CIRC")
        self.writer.add_rectangle(imd_x - 30, bus_y - 110, 60, 60, layer="E-POWR-PANL")
        self.writer.add_text("IMD", (imd_x, bus_y - 75), height=12, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
        self.writer.add_text("50 kOhm", (imd_x, bus_y - 95), height=9, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)

        # IMD PE reference connection
        self.writer.add_line((imd_x, bus_y - 110), (imd_x, bus_y - 140), layer="E-POWR-CIRC")
        self.writer.add_text("REF PE", (imd_x + 5, bus_y - 130), height=8, layer="E-TEXT")

        # 5. Remote Alarm Annunciator Unit
        ann_x, ann_y = imd_x + 130, bus_y - 80
        self.writer.add_rectangle(ann_x - 35, ann_y - 25, 70, 50, layer="S-TITLEBLOCK")
        self.writer.add_text("OR REMOTE", (ann_x, ann_y + 8), height=9, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
        self.writer.add_text("ANNUNCIATOR", (ann_x, ann_y - 8), height=9, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
        self.writer.add_line((imd_x + 30, bus_y - 80), (ann_x - 35, ann_y), layer="E-POWR-CIRC")
        self.writer.add_text("RS485 Bus", (imd_x + 40, bus_y - 70), height=8, layer="E-TEXT")

        # 6. Branch Circuits (2-Pole MCBs)
        spacing_x = 70
        start_ckt_x = pri_x + 260
        for i, ckt in enumerate(self.res.secondary_circuits[:6]):
            cx = start_ckt_x + (i * spacing_x)
            self.writer.add_line((cx, bus_y), (cx, bus_y - 40), layer="E-POWR-CIRC")
            # 2-pole breaker
            self.writer.add_rectangle(cx - 12, bus_y - 70, 24, 30, layer="E-POWR-PANL")
            self.writer.add_text("2P", (cx, bus_y - 55), height=8, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
            self.writer.add_line((cx, bus_y - 70), (cx, bus_y - 120), layer="E-POWR-CIRC")
            # Socket outlet symbol
            self.writer.msp.add_circle((cx, bus_y - 128), radius=8, dxfattribs={"layer": "E-POWR-SCKT"})
            self.writer.add_text(ckt.circuit_tag, (cx, bus_y - 150), height=8, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)

        # 7. Equipotential Grounding Busbar (POAG / EPG)
        poag_y = 180
        self.writer.add_rectangle(pri_x - 40, poag_y - 10, 600, 20, layer="S-REBAR-BOT")
        self.writer.add_text("EQUIPOTENTIAL BONDING BUSBAR (POAG / EPG) [R <= 0.1 OHM]", (pri_x + 20, poag_y - 3), height=11, layer="E-TEXT")

        # 8. Notes & Safety Summary Box
        notes_x, notes_y = 850, 720
        self.writer.add_rectangle(notes_x, notes_y - 450, 500, 450, layer="S-TITLEBLOCK")
        self.writer.add_text("MEDICAL IT SYSTEM SAFETY CRITERIA", (notes_x + 25, notes_y - 35), height=14, layer="E-TEXT")

        criteria = [
            "1. Secondary circuit conductors MUST be fully isolated from Earth.",
            "2. First insulation fault: SYSTEM DOES NOT TRIP, IMD ALARMS.",
            "3. All branch breakers must be 2-Pole (Double Pole) simultaneous trip.",
            "4. Branch cables must be low-capacitance shielded (leakage < 0.5mA).",
            "5. Maximum cable run length from IPS to sockets: 25 meters.",
            "6. All metallic fixtures & gas pendants bonded to POAG busbar.",
            "7. Visual & Audible alarm annunciator tested per NFPA 99 / IEC 60364.",
        ]
        for c_idx, crit in enumerate(criteria):
            self.writer.add_text(crit, (notes_x + 25, notes_y - 80 - (c_idx * 40)), height=10, layer="E-TEXT")

        return self.writer.save(filepath)
