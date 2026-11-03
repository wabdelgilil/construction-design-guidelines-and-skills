"""
AutoCAD DXF Exporter for Substation Single Line Diagram (SLD).
Generates Transformer, Generator, ATS, MDB Busbars, and Outgoing Feeders.
"""

from pathlib import Path
from ezdxf.enums import TextEntityAlignment
from core.exporters.dxf_writer import DXFWriter
from electrical.power_distribution.substation.scripts.design_engine import SubstationDesignResult


class SubstationDXFExporter:
    """Exports Power Single Line Diagram (SLD) to AutoCAD .dxf format."""

    def __init__(self, result: SubstationDesignResult):
        self.res = result
        self.writer = DXFWriter("power_single_line_diagram.dxf")

    def export(self, filepath: Path) -> Path:
        # Sheet Border
        self.writer.add_rectangle(0, 0, 1600, 1000, layer="S-TITLEBLOCK")

        # Title Block
        self.writer.add_text("POWER DISTRIBUTION SINGLE LINE DIAGRAM (SLD)", (40, 940), height=24, layer="E-TEXT")
        self.writer.add_text(f"Project: {self.res.project_name} | Standards: {self.res.standard_used}", (40, 910), height=14, layer="E-TEXT")
        self.writer.add_text(
            f"Transformer: {self.res.selected_transformer_kva} kVA ({self.res.transformer_primary_kv}kV/{self.res.transformer_secondary_v}V) | Standby Generator: {self.res.selected_generator_kva} kVA | MDB Icu: {self.res.mdb_incomer_icu_ka} kA",
            (40, 885),
            height=14,
            layer="E-TEXT",
        )

        # 1. Utility Feed & Transformer (Left Top: x=250, y=800)
        tx_x, tx_y = 250.0, 750.0
        self.writer.add_text(f"UTILITY GRID MV INFEED ({self.res.transformer_primary_kv} kV)", (tx_x - 120, tx_y + 60), height=12, layer="E-TEXT")
        self.writer.add_line((tx_x, tx_y + 50), (tx_x, tx_y + 20), layer="E-POWR-PANL")

        # Transformer Overlapping Circles
        self.writer.msp.add_circle((tx_x, tx_y + 10), radius=20, dxfattribs={"layer": "E-POWR-PANL"})
        self.writer.msp.add_circle((tx_x, tx_y - 20), radius=20, dxfattribs={"layer": "E-POWR-PANL"})
        self.writer.add_text(f"TX-01: {self.res.selected_transformer_kva} kVA", (tx_x + 35, tx_y), height=11, layer="E-TEXT")
        self.writer.add_text(f"Dyn11, uk = {self.res.transformer_uk_pct}%", (tx_x + 35, tx_y - 15), height=9, layer="E-TEXT")
        self.writer.add_text(f"Isc = {self.res.prospective_short_circuit_ka} kA", (tx_x + 35, tx_y - 30), height=9, layer="E-POWR-PANL")

        # Transformer Secondary Feed Line down to Normal Incomer ACB
        self.writer.add_line((tx_x, tx_y - 40), (tx_x, tx_y - 120), layer="E-POWR-PANL")

        # Normal Incomer ACB
        self.writer.add_rectangle(tx_x - 20, tx_y - 160, 40, 40, layer="E-POWR-PANL")
        self.writer.add_text(f"{self.res.mdb_incomer_rating_amps}A", (tx_x, tx_y - 145), height=10, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
        self.writer.add_text(f"ACB ({self.res.mdb_incomer_icu_ka}kA)", (tx_x + 30, tx_y - 145), height=9, layer="E-TEXT")
        self.writer.add_line((tx_x, tx_y - 160), (tx_x, 500.0), layer="E-POWR-PANL")

        # 2. Standby Generator & ATS (Right Top: x=750, y=750)
        gen_x, gen_y = 750.0, 750.0
        self.writer.msp.add_circle((gen_x, gen_y), radius=25, dxfattribs={"layer": "E-POWR-PANL"})
        self.writer.add_text("G", (gen_x, gen_y), height=16, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
        self.writer.add_text(f"GEN-01: {self.res.selected_generator_kva} kVA", (gen_x + 35, gen_y + 10), height=11, layer="E-TEXT")
        self.writer.add_text("Standby Diesel Set", (gen_x + 35, gen_y - 10), height=9, layer="E-TEXT")

        # Generator Feed Line down to Generator Incomer ACB
        self.writer.add_line((gen_x, gen_y - 25), (gen_x, tx_y - 120), layer="E-POWR-PANL")
        self.writer.add_rectangle(gen_x - 20, tx_y - 160, 40, 40, layer="E-POWR-PANL")
        self.writer.add_text(f"{self.res.ats_rating_amps}A", (gen_x, tx_y - 145), height=10, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
        self.writer.add_text("GEN ACB", (gen_x + 30, tx_y - 145), height=9, layer="E-TEXT")
        self.writer.add_line((gen_x, tx_y - 160), (gen_x, 500.0), layer="E-POWR-PANL")

        # 3. Automatic Transfer Switch (ATS) Interlocking
        self.writer.add_line((tx_x + 20, tx_y - 140), (gen_x - 20, tx_y - 140), layer="S-REBAR-BOT")
        self.writer.add_text("MECHANICAL & ELECTRICAL INTERLOCK (ATS)", ((tx_x + gen_x) / 2, tx_y - 130), height=9, layer="S-REBAR-BOT", align=TextEntityAlignment.MIDDLE_CENTER)

        # 4. Main Distribution Board (MDB) Busbars (y=500.0)
        # Normal Busbar
        self.writer.add_line((150.0, 500.0), (450.0, 500.0), layer="E-POWR-PANL")
        self.writer.add_text(f"MDB NORMAL BUSBAR (400V 3PH) [{self.res.mdb_incomer_icu_ka} kA]", (150.0, 515.0), height=11, layer="E-TEXT")

        # Essential / Emergency Busbar
        self.writer.add_line((650.0, 500.0), (1050.0, 500.0), layer="E-POWR-PANL")
        self.writer.add_text(f"MDB ESSENTIAL BUSBAR (ATS FED) [{self.res.mdb_incomer_icu_ka} kA]", (650.0, 515.0), height=11, layer="E-TEXT")

        # Bus Coupler (Between Normal and Essential)
        self.writer.add_line((450.0, 500.0), (520.0, 500.0), layer="E-POWR-PANL")
        self.writer.add_rectangle(520.0, 485.0, 30, 30, layer="E-POWR-PANL")
        self.writer.add_text("BC", (535.0, 500.0), height=9, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
        self.writer.add_line((550.0, 500.0), (650.0, 500.0), layer="E-POWR-PANL")

        # 5. Outgoing Feeders branching down from busbars
        # Normal Feeders
        normal_feeders = [
            ("F1", "Chiller Plant 01", "250A"),
            ("F2", "Chiller Plant 02", "250A"),
            ("F3", "Sub-Panel SMDB-01", "160A"),
        ]
        for n_idx, (tag, desc, rating) in enumerate(normal_feeders):
            fx = 200.0 + (n_idx * 100.0)
            self.writer.add_line((fx, 500.0), (fx, 450.0), layer="E-POWR-CIRC")
            self.writer.add_rectangle(fx - 12, 420.0, 24, 30, layer="E-POWR-PANL")
            self.writer.add_text(rating, (fx, 435.0), height=7, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
            self.writer.add_line((fx, 420.0), (fx, 360.0), layer="E-POWR-CIRC")
            self.writer.add_text(f"{tag}: {desc}", (fx, 340.0), height=8, layer="E-TEXT", align=TextEntityAlignment.TOP_CENTER)

        # Essential Feeders
        essential_feeders = [
            ("E1", "Fire Pump Panel", "160A"),
            ("E2", "Elevators & Escalators", "125A"),
            ("E3", "Emergency Lighting UPS", "100A"),
            ("E4", "Domestic Water Booster", "63A"),
        ]
        for e_idx, (tag, desc, rating) in enumerate(essential_feeders):
            fx = 700.0 + (e_idx * 90.0)
            self.writer.add_line((fx, 500.0), (fx, 450.0), layer="E-POWR-CIRC")
            self.writer.add_rectangle(fx - 12, 420.0, 24, 30, layer="E-POWR-PANL")
            self.writer.add_text(rating, (fx, 435.0), height=7, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)
            self.writer.add_line((fx, 420.0), (fx, 360.0), layer="E-POWR-CIRC")
            self.writer.add_text(f"{tag}: {desc}", (fx, 340.0), height=8, layer="E-TEXT", align=TextEntityAlignment.TOP_CENTER)

        # 6. Substation Engineering Notes & Summary Box
        notes_x = 1120.0
        notes_y = 850.0
        self.writer.add_rectangle(notes_x, notes_y - 600, 440, 600, layer="S-TITLEBLOCK")
        self.writer.add_text("SUBSTATION DESIGN CRITERIA", (notes_x + 20, notes_y - 35), height=14, layer="E-TEXT")

        criteria = [
            f"1. Connected Load: {self.res.total_connected_kw:.0f} kW ({self.res.total_connected_kva:.0f} kVA)",
            f"2. Diversified Demand: {self.res.max_demand_kw:.0f} kW ({self.res.max_demand_kva:.0f} kVA)",
            f"3. Transformer: {self.res.selected_transformer_kva} kVA (Loading: {self.res.transformer_loading_pct}%)",
            f"4. Symmetrical Fault (Isc): {self.res.prospective_short_circuit_ka} kA @ 400V",
            f"5. MDB Incomer ACB: {self.res.mdb_incomer_rating_amps}A (Icu = {self.res.mdb_incomer_icu_ka} kA)",
            f"6. Generator Standby: {self.res.selected_generator_kva} kVA (Essential Load)",
            f"7. ATS Changeover: {self.res.ats_rating_amps}A (4-Pole Interlocked)",
            "8. Earth System: TN-S System with solid neutral",
            "9. Fire Suppression: Clean Agent FM-200 in Tx Room",
        ]
        for c_idx, crit in enumerate(criteria):
            self.writer.add_text(crit, (notes_x + 20, notes_y - 80 - (c_idx * 45)), height=9, layer="E-TEXT")

        return self.writer.save(filepath)
