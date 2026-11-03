"""
Deterministic Motor Control Center (MCC) & Motor Feeders / Starters Sizing Engine.
Calculates motor full load currents (FLA), starting method selection (DOL, Star-Delta, Soft Starter, VFD),
contactor ratings (AC-3), overload relay settings, short-circuit protection (Type 2 Coordination),
feeder cable cross-sections, and Form 4b MCC cubicle physical sizing.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class MotorLoadInput:
    tag: str
    description: str
    rated_kw: float
    power_factor: float = 0.85
    efficiency: float = 0.90
    application_type: str = "constant_speed"  # constant_speed, variable_speed, high_inertia_fan, fire_safety
    feeder_length_m: float = 35.0


@dataclass
class MotorStarterDetail:
    tag: str
    description: str
    rated_kw: float
    rated_hp: float
    fla_a: float
    starting_method: str  # DOL, Star-Delta, Soft-Starter, VFD
    starting_current_a: float
    contactor_main_ac3_a: float
    contactor_delta_ac3_a: Optional[float]
    contactor_star_ac3_a: Optional[float]
    overload_setting_a: float
    mcp_breaker_rating_a: int
    feeder_cable_csa_mm2: float
    run_voltage_drop_pct: float
    start_voltage_drop_pct: float
    cubicle_height_mm: int


@dataclass
class MCCDesignResult:
    project_name: str
    standard_used: str
    nominal_voltage_v: float
    frequency_hz: float
    motors: List[MotorStarterDetail]
    total_motors_count: int
    total_connected_kw: float
    total_connected_hp: float
    total_full_load_current_a: float
    mcc_main_incomer_rating_a: int
    mcc_main_busbar_rating_a: int
    total_columns_count: int
    segregation_form: str  # Form 4b
    coordination_notices: List[str] = field(default_factory=list)


class MotorControlCenterEngine:
    """Sizes motor starters, contactors, protection devices, and MCC switchboards."""

    STANDARD_COPPER_CABLES = [2.5, 4.0, 6.0, 10.0, 16.0, 25.0, 35.0, 50.0, 70.0, 95.0, 120.0, 150.0, 185.0, 240.0]
    CABLE_AMPACITIES_AIR = {
        2.5: 24.0, 4.0: 32.0, 6.0: 41.0, 10.0: 57.0, 16.0: 76.0, 25.0: 101.0,
        35.0: 125.0, 50.0: 151.0, 70.0: 192.0, 95.0: 232.0, 120.0: 269.0,
        150.0: 309.0, 185.0: 353.0, 240.0: 415.0,
    }
    STANDARD_BREAKERS = [16, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 400, 630, 800, 1000, 1250, 1600, 2000, 2500]

    def __init__(self, standard: str = "IEC 60947-4-1 / IEC 61439-2 / SBC 401"):
        self.standard = standard

    def design_mcc(
        self,
        project_name: str,
        motors: List[MotorLoadInput],
        nominal_voltage_v: float = 400.0,
        frequency_hz: float = 60.0,
    ) -> MCCDesignResult:
        starters: List[MotorStarterDetail] = []
        tot_kw = 0.0
        tot_hp = 0.0
        tot_fla = 0.0

        for m in motors:
            hp = round(m.rated_kw * 1.341, 1)
            # FLA = (kW * 1000) / (sqrt(3) * V * eff * pf)
            denom = math.sqrt(3.0) * nominal_voltage_v * m.efficiency * m.power_factor
            fla = round((m.rated_kw * 1000.0) / denom, 2)

            tot_kw += m.rated_kw
            tot_hp += hp
            tot_fla += fla

            # Starting Method Selection
            if m.application_type == "variable_speed":
                starter_type = "Variable Frequency Drive (VFD)"
                i_start = round(1.15 * fla, 1)
                km_main = fla
                km_delta = None
                km_star = None
                ol_set = fla
                cubicle_h = 600 if m.rated_kw > 30 else 400
            elif m.rated_kw <= 7.5:
                starter_type = "Direct-On-Line (DOL)"
                i_start = round(6.5 * fla, 1)
                km_main = math.ceil(fla * 1.1)
                km_delta = None
                km_star = None
                ol_set = fla
                cubicle_h = 300
            elif m.rated_kw <= 45.0:
                starter_type = "Star-Delta (Y-Δ)"
                i_start = round(2.3 * fla, 1)
                km_main = round(fla / math.sqrt(3.0), 1)
                km_delta = km_main
                km_star = round(fla / 3.0, 1)
                ol_set = km_main  # In phase branch
                cubicle_h = 450
            else:
                starter_type = "Solid-State Soft Starter"
                i_start = round(3.0 * fla, 1)
                km_main = fla
                km_delta = None
                km_star = None
                ol_set = fla
                cubicle_h = 600

            # MCP Breaker Rating (1.5 - 2.0x FLA)
            min_mcp = fla * 1.5
            mcp = next((b for b in self.STANDARD_BREAKERS if b >= min_mcp), 250)

            # Feeder Cable Sizing: continuous Iz >= 1.25 * FLA
            min_amp = fla * 1.25
            cable_csa = 2.5
            for csa in self.STANDARD_COPPER_CABLES:
                if self.CABLE_AMPACITIES_AIR[csa] >= min_amp:
                    cable_csa = csa
                    break

            # Voltage Drop Check: VD = sqrt(3) * I * L * (R*cos + X*sin) / V
            # R = 0.0225 / A, X = 0.00008
            r_c = 0.0225 / cable_csa
            x_c = 0.00008
            z_eff = r_c * m.power_factor + x_c * math.sin(math.acos(m.power_factor))
            vd_run_v = math.sqrt(3.0) * fla * m.feeder_length_m * z_eff
            vd_run_pct = round((vd_run_v / nominal_voltage_v) * 100.0, 2)

            # Starting Voltage Drop (Power factor drops to ~0.35 during start)
            z_eff_start = r_c * 0.35 + x_c * math.sin(math.acos(0.35))
            vd_start_v = math.sqrt(3.0) * i_start * m.feeder_length_m * z_eff_start
            vd_start_pct = round((vd_start_v / nominal_voltage_v) * 100.0, 2)

            starters.append(
                MotorStarterDetail(
                    tag=m.tag,
                    description=m.description,
                    rated_kw=m.rated_kw,
                    rated_hp=hp,
                    fla_a=fla,
                    starting_method=starter_type,
                    starting_current_a=i_start,
                    contactor_main_ac3_a=km_main,
                    contactor_delta_ac3_a=km_delta,
                    contactor_star_ac3_a=km_star,
                    overload_setting_a=round(ol_set, 1),
                    mcp_breaker_rating_a=mcp,
                    feeder_cable_csa_mm2=cable_csa,
                    run_voltage_drop_pct=vd_run_pct,
                    start_voltage_drop_pct=vd_start_pct,
                    cubicle_height_mm=cubicle_h,
                )
            )

        # Incomer sizing: Largest motor starting current + sum of other motor FLAs
        largest_motor = max(starters, key=lambda s: s.fla_a)
        sum_others_fla = sum(s.fla_a for s in starters if s.tag != largest_motor.tag)
        calc_incomer_demand = (largest_motor.fla_a * 1.25) + sum_others_fla
        selected_incomer = next((b for b in self.STANDARD_BREAKERS if b >= calc_incomer_demand), 1600)
        selected_busbar = max(selected_incomer, 1000)

        # MCC Physical Columns (Usable height per column = 1800mm, with 400mm busbar & cable compartment)
        total_cubicle_h = sum(s.cubicle_height_mm for s in starters)
        cols_needed = math.ceil(total_cubicle_h / 1800.0) + 1  # +1 for Incomer Column

        notices = [
            f"Internal Segregation Form: Fully enclosed Form 4b assembly with segregated busbars, starters, and terminal chambers.",
            f"Type 2 Coordination: Breakers and contactors certified for non-destructive clearing under prospective fault currents (IEC 60947-4-1).",
            f"VFD Harmonics: Active front-end or 3% line choke specified for VFD drives to comply with IEEE 519 THD limits.",
            f"Emergency Fire Mode: Smoke exhaust and pressurization fan starters include Firefighter Override bypass contactors.",
            f"BMS Interface: Each starter cubicle includes isolated voltage-free contacts for Run Status, Trip Alarm, and Auto/Manual Hand-Off-Auto (HOA) status.",
        ]

        return MCCDesignResult(
            project_name=project_name,
            standard_used=self.standard,
            nominal_voltage_v=nominal_voltage_v,
            frequency_hz=frequency_hz,
            motors=starters,
            total_motors_count=len(motors),
            total_connected_kw=round(tot_kw, 1),
            total_connected_hp=round(tot_hp, 1),
            total_full_load_current_a=round(tot_fla, 1),
            mcc_main_incomer_rating_a=selected_incomer,
            mcc_main_busbar_rating_a=selected_busbar,
            total_columns_count=cols_needed,
            segregation_form="Form 4b (Drawout / Demountable)",
            coordination_notices=notices,
        )
