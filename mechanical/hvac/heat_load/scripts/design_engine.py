"""
Deterministic HVAC Cooling Load & Airflow Sizing Engine.
Computes room heat gains, sensible/latent balance, CFM, equipment tonnage (TR),
diffuser layout, and cross-discipline electrical/structural coordination requirements.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class HVACSpaceInput:
    space_name: str
    length_m: float
    width_m: float
    height_m: float = 3.0
    space_type: str = "office"
    occupant_count: int = 4
    lighting_power_watts: float = 240.0
    equipment_power_watts: float = 600.0
    external_wall_area_m2: float = 18.0
    glass_window_area_m2: float = 4.0
    roof_exposed: bool = False
    outdoor_summer_db_c: float = 46.0
    indoor_comfort_temp_c: float = 23.5


@dataclass
class HVACDesignResult:
    space_name: str
    code_used: str
    area_m2: float
    volume_m3: float
    envelope_heat_gain_w: float
    glass_solar_gain_w: float
    occupant_sensible_gain_w: float
    occupant_latent_gain_w: float
    lighting_gain_w: float
    equipment_gain_w: float
    ventilation_sensible_w: float
    ventilation_latent_w: float
    total_sensible_heat_w: float
    total_latent_heat_w: float
    grand_total_heat_w: float
    grand_total_cooling_btu_hr: float
    sensible_heat_ratio_shr: float
    required_cooling_tons_tr: float
    selected_unit_tons_tr: float
    selected_unit_model: str
    supply_airflow_cfm: float
    supply_diffusers_count: int
    cfm_per_diffuser: float
    return_grilles_count: int
    # Electrical Interface
    equipment_electrical_kw: float
    electrical_mca_amps: float
    electrical_mop_amps: int
    electrical_voltage_v: float
    thermostat_height_aff_m: float
    isolator_height_aff_m: float
    coordination_notices: List[str] = field(default_factory=list)


class CoolingLoadEngine:
    """Calculates cooling load, sizing equipment and producing MEP coordination interfaces."""

    STANDARD_TR_SIZES = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 7.5, 10.0]

    def __init__(self, code: str = "SBC"):
        self.code = code

    def compute_cooling_load(self, inp: HVACSpaceInput) -> HVACDesignResult:
        area_m2 = round(inp.length_m * inp.width_m, 2)
        vol_m3 = round(area_m2 * inp.height_m, 2)

        delta_t_c = inp.outdoor_summer_db_c - inp.indoor_comfort_temp_c
        delta_t_f = delta_t_c * 1.8

        # 1. Envelope heat gains
        u_wall = 0.35 if self.code == "SBC" else 0.45
        q_wall = inp.external_wall_area_m2 * u_wall * delta_t_c

        u_roof = 0.25 if self.code == "SBC" else 0.30
        q_roof = (area_m2 * u_roof * delta_t_c) if inp.roof_exposed else 0.0

        q_envelope = round(q_wall + q_roof, 1)

        # 2. Window Solar & Conduction
        # Average summer solar heat gain ~ 180 W/m2 for double-glazed low-e glass
        q_glass = round(inp.glass_window_area_m2 * 180.0 + (inp.glass_window_area_m2 * 2.2 * delta_t_c), 1)

        # 3. Internal Gains
        occ_sensible_w = 75.0
        occ_latent_w = 55.0
        q_occ_sensible = round(inp.occupant_count * occ_sensible_w, 1)
        q_occ_latent = round(inp.occupant_count * occ_latent_w, 1)

        q_lights = round(inp.lighting_power_watts, 1)
        q_equipment = round(inp.equipment_power_watts, 1)

        # 4. Fresh Air Ventilation (ASHRAE 62.1 / SBC 501: ~ 17 CFM per person for office)
        oa_cfm = inp.occupant_count * 17.0
        q_vent_sensible = round(1.08 * oa_cfm * delta_t_f / 3.412, 1)  # W
        q_vent_latent = round(4840 * oa_cfm * 0.008 / 3.412, 1)        # W

        # Totals
        total_sensible_w = round(q_envelope + q_glass + q_occ_sensible + q_lights + q_equipment + q_vent_sensible, 1)
        total_latent_w = round(q_occ_latent + q_vent_latent, 1)
        grand_total_w = round(total_sensible_w + total_latent_w, 1)
        grand_total_btu = round(grand_total_w * 3.412, 1)

        shr = round(total_sensible_w / max(grand_total_w, 1.0), 2)
        raw_tr = grand_total_btu / 12000.0

        # Select Standard Equipment Tonnage
        selected_tr = self.STANDARD_TR_SIZES[-1]
        for tr in self.STANDARD_TR_SIZES:
            if tr >= raw_tr:
                selected_tr = tr
                break

        # Sizing Airflow CFM: CFM = Sensible BTU/hr / (1.08 * 20 deg F)
        sensible_btu = total_sensible_w * 3.412
        supply_cfm = round(sensible_btu / (1.08 * 20.0), 0)

        # Diffusers count (standard 4-way square diffuser delivers ~ 150 - 250 CFM at NC < 30)
        target_cfm_per_diffuser = 180.0
        diffusers_count = max(math.ceil(supply_cfm / target_cfm_per_diffuser), 1)
        cfm_per_diffuser = round(supply_cfm / diffusers_count, 1)
        return_grilles_count = max(math.ceil(diffusers_count / 2), 1)

        # Electrical Interface Calculations
        # Modern Inverter VRF / Split AC consumes ~ 1.15 kW per TR
        elec_kw = round(selected_tr * 1.15, 2)
        voltage_v = 230.0  # 1-phase for up to 3.0 TR, 400V 3-phase for >= 4.0 TR
        if selected_tr >= 4.0:
            elec_i = round((elec_kw * 1000.0) / (math.sqrt(3) * 400.0 * 0.88), 1)
            elec_voltage = 400.0
        else:
            elec_i = round((elec_kw * 1000.0) / (230.0 * 0.88), 1)
            elec_voltage = 230.0

        # MCA = 1.25 * I
        mca = round(elec_i * 1.25, 1)
        # MOP standard breaker rating
        std_breakers = [16, 20, 25, 32, 40, 50, 63]
        mop_raw = elec_i * 1.75
        mop = std_breakers[-1]
        for b in std_breakers:
            if b >= mop_raw:
                mop = b
                break

        notices = [
            f"Electrical Power Interface: Provide dedicated feeder from DB to Outdoor Unit: {elec_voltage}V, MCA = {mca}A, MOP Breaker = {mop}A.",
            "Controls Interface: Provide flush wall box and 20mm conduit for Digital Room Thermostat at +1500mm AFF, away from direct diffuser throw and solar radiation.",
            "Mechanical Maintenance: Provide local IP65 weatherproof rotary isolator switch within 1.0m line-of-sight of outdoor condensing unit at +2200mm AFF.",
            f"Civil/Structural Interface: Verify rooftop concrete plinth / anti-vibration rubber pads for operating weight approx {int(selected_tr * 55)} kg.",
            "Plumbing Interface: Provide 1-inch (25mm) insulated UPVC condensate drain pipe with deep trap connecting to nearest drainage stack.",
        ]

        return HVACDesignResult(
            space_name=inp.space_name,
            code_used=self.code,
            area_m2=area_m2,
            volume_m3=vol_m3,
            envelope_heat_gain_w=q_envelope,
            glass_solar_gain_w=q_glass,
            occupant_sensible_gain_w=q_occ_sensible,
            occupant_latent_gain_w=q_occ_latent,
            lighting_gain_w=q_lights,
            equipment_gain_w=q_equipment,
            ventilation_sensible_w=q_vent_sensible,
            ventilation_latent_w=q_vent_latent,
            total_sensible_heat_w=total_sensible_w,
            total_latent_heat_w=total_latent_w,
            grand_total_heat_w=grand_total_w,
            grand_total_cooling_btu_hr=grand_total_btu,
            sensible_heat_ratio_shr=shr,
            required_cooling_tons_tr=round(raw_tr, 2),
            selected_unit_tons_tr=selected_tr,
            selected_unit_model=f"High-Efficiency Inverter Split / VRF FCU ({selected_tr:.1f} TR)",
            supply_airflow_cfm=supply_cfm,
            supply_diffusers_count=diffusers_count,
            cfm_per_diffuser=cfm_per_diffuser,
            return_grilles_count=return_grilles_count,
            equipment_electrical_kw=elec_kw,
            electrical_mca_amps=mca,
            electrical_mop_amps=mop,
            electrical_voltage_v=elec_voltage,
            thermostat_height_aff_m=1.50,
            isolator_height_aff_m=2.20,
            coordination_notices=notices,
        )
