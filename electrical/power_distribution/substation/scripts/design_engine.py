"""
Deterministic Substation, Transformer, Diesel Generator & MDB Sizing Engine.
Computes diversified demand load, selects MV/LV distribution transformer, calculates
prospective short-circuit current (Isc), sizes MDB incomer ACB, sizes Standby Generator
with motor-starting inrush analysis, and specifies the 4-Pole ATS.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class BuildingLoadsInput:
    project_name: str
    lighting_kw: float
    sockets_kw: float
    hvac_kw: float
    elevators_kw: float
    pumps_kw: float
    life_safety_kw: float
    it_ups_kw: float
    largest_single_motor_kw: float = 30.0
    future_expansion_pct: float = 15.0


@dataclass
class SubstationDesignResult:
    project_name: str
    standard_used: str
    total_connected_kw: float
    total_connected_kva: float
    max_demand_kw: float
    max_demand_kva: float
    # Transformer Sizing
    selected_transformer_kva: int
    transformer_primary_kv: float
    transformer_secondary_v: float
    transformer_flc_amps: float
    transformer_loading_pct: float
    transformer_uk_pct: float
    prospective_short_circuit_ka: float
    # MDB Incomer
    mdb_incomer_breaker_type: str
    mdb_incomer_rating_amps: int
    mdb_incomer_icu_ka: int
    # Generator & ATS
    emergency_connected_kw: float
    emergency_demand_kva: float
    motor_starting_inrush_kva: float
    selected_generator_kva: int
    generator_standby_amps: float
    ats_rating_amps: int
    ats_poles: int
    coordination_notices: List[str] = field(default_factory=list)


class SubstationEngine:
    """Sizes distribution transformers, diesel generators, MDB incomers, and computes Isc."""

    STANDARD_TX_KVA = [500, 630, 800, 1000, 1250, 1500, 1600, 2000, 2500]
    STANDARD_GEN_KVA = [100, 150, 200, 250, 350, 500, 650, 800, 1000, 1250]
    STANDARD_BREAKERS = [400, 630, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000]

    def __init__(self, voltage_v: float = 400.0, standard: str = "IEC 60076 / SBC 401 / ISO 8528"):
        self.voltage_v = voltage_v
        self.standard = standard

    def design_substation(self, loads: BuildingLoadsInput) -> SubstationDesignResult:
        # 1. Connected Load calculation
        total_kw = (
            loads.lighting_kw
            + loads.sockets_kw
            + loads.hvac_kw
            + loads.elevators_kw
            + loads.pumps_kw
            + loads.life_safety_kw
            + loads.it_ups_kw
        )

        # Average assumed power factors
        pf_map = {
            "lighting": 0.90,
            "sockets": 0.85,
            "hvac": 0.85,
            "elevators": 0.80,
            "pumps": 0.82,
            "life_safety": 0.88,
            "it_ups": 0.95,
        }

        # 2. Demand Factor calculation
        df_map = {
            "lighting": 0.90,
            "sockets": 0.50,
            "hvac": 0.85,
            "elevators": 0.70,
            "pumps": 0.60,
            "life_safety": 1.00,
            "it_ups": 1.00,
        }

        demand_kw = (
            loads.lighting_kw * df_map["lighting"]
            + loads.sockets_kw * df_map["sockets"]
            + loads.hvac_kw * df_map["hvac"]
            + loads.elevators_kw * df_map["elevators"]
            + loads.pumps_kw * df_map["pumps"]
            + loads.life_safety_kw * df_map["life_safety"]
            + loads.it_ups_kw * df_map["it_ups"]
        )

        # Overall building diversity factor (0.90) + future expansion
        inter_diversity = 0.90
        growth_multiplier = 1.0 + (loads.future_expansion_pct / 100.0)
        final_demand_kw = round(demand_kw * inter_diversity * growth_multiplier, 1)
        final_demand_kva = round(final_demand_kw / 0.85, 1)

        total_connected_kva = round(total_kw / 0.85, 1)

        # 3. Distribution Transformer Sizing
        # Target loading <= 80%
        target_tx_kva = final_demand_kva / 0.80
        selected_tx = self.STANDARD_TX_KVA[-1]
        for tx in self.STANDARD_TX_KVA:
            if tx >= target_tx_kva:
                selected_tx = tx
                break

        tx_flc = round((selected_tx * 1000.0) / (math.sqrt(3.0) * self.voltage_v), 1)
        loading_pct = round((final_demand_kva / selected_tx) * 100.0, 1)

        # Transformer Impedance (uk%)
        if selected_tx <= 630:
            uk = 4.5
        elif selected_tx <= 1250:
            uk = 5.0
        else:
            uk = 6.0

        # Prospective Short Circuit Current: Isc = I_flc / (uk / 100)
        isc_ka = round(tx_flc / (uk / 100.0) / 1000.0, 1)

        # 4. MDB Incomer Breaker Sizing
        # Next standard breaker >= tx_flc
        mdb_incomer = self.STANDARD_BREAKERS[-1]
        for b in self.STANDARD_BREAKERS:
            if b >= tx_flc:
                mdb_incomer = b
                break

        breaker_type = "4-Pole Drawout ACB" if mdb_incomer >= 800 else "4-Pole Fixed MCCB"

        # Breaking capacity Icu: standard ratings 36kA, 50kA, 65kA, 85kA, 100kA
        icu_options = [36, 50, 65, 85, 100]
        selected_icu = icu_options[-1]
        for icu in icu_options:
            if icu >= isc_ka * 1.25:
                selected_icu = icu
                break

        # 5. Standby Diesel Generator Sizing (Essential loads + motor starting inrush)
        # Essential loads: Life safety (100%), Pumps (60%), Elevators (1 car per bank ~ 50%), IT/UPS (100%), 20% lighting
        emg_kw = (
            loads.life_safety_kw
            + loads.it_ups_kw
            + (loads.pumps_kw * 0.60)
            + (loads.elevators_kw * 0.50)
            + (loads.lighting_kw * 0.20)
        )
        emg_kva = emg_kw / 0.80

        # Motor starting inrush: largest motor starting DOL / Star-Delta
        # Starting inrush kVA ~ 6x running kVA
        motor_running_kva = loads.largest_single_motor_kw / 0.82
        starting_inrush_kva = round(motor_running_kva * 6.0, 1)

        # Sizing generator: running load / 0.80 and check transient inrush
        gen_req_kva = max(emg_kva / 0.80, starting_inrush_kva * 0.55)
        selected_gen = self.STANDARD_GEN_KVA[-1]
        for gen in self.STANDARD_GEN_KVA:
            if gen >= gen_req_kva:
                selected_gen = gen
                break

        gen_amps = round((selected_gen * 1000.0) / (math.sqrt(3.0) * self.voltage_v), 1)

        # ATS Sizing: Matches generator capacity or emergency bus rating
        ats_rating = self.STANDARD_BREAKERS[-1]
        for b in self.STANDARD_BREAKERS:
            if b >= gen_amps:
                ats_rating = b
                break

        notices = [
            f"Civil / Structural: Provide reinforced concrete foundation plinth for {selected_tx} kVA transformer with integral oil catchment pit and gravel bed.",
            f"Mechanical / HVAC: Generator room requires acoustic attenuated air intake louvers and radiator exhaust duct sized for minimum {selected_gen * 4.5:.0f} CFM.",
            f"Electrical Protection: MDB incomer {breaker_type} must have minimum short-circuit breaking capacity Icu = {selected_icu} kA (Isc calculated = {isc_ka} kA).",
            f"Automatic Transfer Switch: 4-Pole ATS ({ats_rating}A) with electrical and mechanical interlocks to prevent parallel utility/generator coupling.",
            "Fire Life Safety: Dedicated clean agent total flooding fire suppression system (FM-200 / Novec 1230) required in MV/LV transformer room.",
        ]

        return SubstationDesignResult(
            project_name=loads.project_name,
            standard_used=self.standard,
            total_connected_kw=round(total_kw, 1),
            total_connected_kva=total_connected_kva,
            max_demand_kw=final_demand_kw,
            max_demand_kva=final_demand_kva,
            selected_transformer_kva=selected_tx,
            transformer_primary_kv=13.8,
            transformer_secondary_v=self.voltage_v,
            transformer_flc_amps=tx_flc,
            transformer_loading_pct=loading_pct,
            transformer_uk_pct=uk,
            prospective_short_circuit_ka=isc_ka,
            mdb_incomer_breaker_type=breaker_type,
            mdb_incomer_rating_amps=mdb_incomer,
            mdb_incomer_icu_ka=selected_icu,
            emergency_connected_kw=round(emg_kw, 1),
            emergency_demand_kva=round(emg_kva, 1),
            motor_starting_inrush_kva=starting_inrush_kva,
            selected_generator_kva=selected_gen,
            generator_standby_amps=gen_amps,
            ats_rating_amps=ats_rating,
            ats_poles=4,
            coordination_notices=notices,
        )
