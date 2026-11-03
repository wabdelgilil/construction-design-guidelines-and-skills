"""
Deterministic Emergency & Exit Lighting (CBS & Self-Contained) Design Engine.
Computes escape route lux compliance (NFPA 101 / BS 5266 / SBC 801), EXIT sign placement,
Central Battery System (CBS) inverter & battery Ah sizing, and fire-resistant circuit allocation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class EmergencySpaceInput:
    space_name: str
    space_type: str  # escape_corridor, fire_staircase, open_hall, exit_door
    length_m: float
    width_m: float
    mounting_height_m: float = 3.0
    has_exit_door: bool = False


@dataclass
class SpaceEmergencyAllocation:
    space_name: str
    space_type: str
    area_m2: float
    emergency_luminaires_count: int
    exit_signs_count: int
    target_illuminance_lux: float
    total_watts: float


@dataclass
class EmergencyLightingDesignResult:
    project_name: str
    standard_used: str
    system_architecture: str  # Central Battery System (CBS) or Self-Contained
    autonomy_hours: float
    allocations: List[SpaceEmergencyAllocation]
    total_emergency_luminaires: int
    total_exit_signs: int
    grand_total_luminaires: int
    total_emergency_load_watts: float
    # CBS Sizing
    cbs_inverter_rated_va: int
    cbs_battery_dc_bus_v: float
    cbs_calculated_battery_ah: float
    cbs_selected_battery_ah: float
    cbs_battery_blocks_12v_count: int
    total_cbs_circuits_count: int
    coordination_notices: List[str] = field(default_factory=list)


class EmergencyLightingEngine:
    """Sizes emergency escape lighting, exit signs, and central battery systems."""

    LUMINAIRE_W = 5.0  # 5W high-efficiency LED emergency luminaire
    EXIT_SIGN_W = 3.0  # 3W illuminated LED exit sign
    MAX_CIRCUIT_LUMINAIRES = 20

    STANDARD_CBS_RATINGS_VA = [500, 1000, 1500, 2000, 3000, 5000, 7500, 10000]
    STANDARD_BATTERY_AH = [12.0, 18.0, 24.0, 38.0, 55.0, 65.0, 100.0]

    def __init__(self, standard: str = "NFPA 101 / BS 5266 / SBC 801"):
        self.standard = standard

    def design_emergency_lighting(
        self,
        project_name: str,
        spaces: List[EmergencySpaceInput],
        system_architecture: str = "Central Battery System (CBS)",
        autonomy_hours: float = 1.5,  # 90 minutes NFPA 101
        dc_bus_voltage_v: float = 220.0,
    ) -> EmergencyLightingDesignResult:
        allocations = []
        tot_emg = 0
        tot_exit = 0
        tot_watts = 0.0

        for sp in spaces:
            area = round(sp.length_m * sp.width_m, 2)

            # Sizing Luminaires
            if sp.space_type == "escape_corridor":
                # Spacing along corridor: S = 3.0 * H
                spacing = 3.0 * sp.mounting_height_m
                emg_cnt = max(math.ceil(sp.length_m / spacing), 1)
                lux_target = 1.0
            elif sp.space_type == "fire_staircase":
                # 1 per landing
                emg_cnt = max(math.ceil(sp.length_m / 4.0), 2)
                lux_target = 1.0
            elif sp.space_type == "open_hall":
                # Anti-panic: 1 per 40m2
                emg_cnt = max(math.ceil(area / 40.0), 1)
                lux_target = 0.5
            else:
                emg_cnt = 1
                lux_target = 1.0

            exit_cnt = 1 if sp.has_exit_door else 0

            space_w = (emg_cnt * self.LUMINAIRE_W) + (exit_cnt * self.EXIT_SIGN_W)

            tot_emg += emg_cnt
            tot_exit += exit_cnt
            tot_watts += space_w

            allocations.append(
                SpaceEmergencyAllocation(
                    space_name=sp.space_name,
                    space_type=sp.space_type.replace("_", " ").title(),
                    area_m2=area,
                    emergency_luminaires_count=emg_cnt,
                    exit_signs_count=exit_cnt,
                    target_illuminance_lux=lux_target,
                    total_watts=space_w,
                )
            )

        grand_total = tot_emg + tot_exit

        # CBS Inverter Sizing (With 25% future expansion margin)
        design_va = (tot_watts / 0.90) * 1.25
        selected_inverter = self.STANDARD_CBS_RATINGS_VA[-1]
        for inv in self.STANDARD_CBS_RATINGS_VA:
            if inv >= design_va:
                selected_inverter = inv
                break

        # Battery Sizing: C = (Watts * Hours) / (eta * V_dc) * 1.25
        # Inverter efficiency = 0.90, aging factor = 1.25
        c_raw = (tot_watts * autonomy_hours * 1.25) / (0.90 * dc_bus_voltage_v)

        selected_ah = self.STANDARD_BATTERY_AH[-1]
        for ah in self.STANDARD_BATTERY_AH:
            if ah >= c_raw:
                selected_ah = ah
                break

        # Number of 12V blocks in series for DC bus
        blocks_count = int(round(dc_bus_voltage_v / 12.0))

        # CBS Sub-circuits count (max 20 luminaires per circuit)
        cbs_circuits = max(math.ceil(grand_total / self.MAX_CIRCUIT_LUMINAIRES), 1)

        notices = [
            f"Life Safety / Egress Interface: Install self-illuminated EXIT signs with directional running man arrows over all {tot_exit} designated exit doors at +2200mm AFF.",
            f"Electrical Containment Interface: CBS emergency branch circuits must use 2x1.5mm² red fire-resistant cables (FP200 / PH120) with fire-rated clips every 300mm.",
            f"Central Battery System: Selected CBS Panel rating {selected_inverter} VA ({selected_ah} Ah @ {dc_bus_voltage_v}V DC) providing {autonomy_hours * 60:.0f} minutes continuous autonomy.",
            "Substation Phase-Loss Monitoring: Provide phase-failure relays on normal lighting panelboards to trigger emergency lighting automatically upon localized power blackout.",
        ]

        return EmergencyLightingDesignResult(
            project_name=project_name,
            standard_used=self.standard,
            system_architecture=system_architecture,
            autonomy_hours=autonomy_hours,
            allocations=allocations,
            total_emergency_luminaires=tot_emg,
            total_exit_signs=tot_exit,
            grand_total_luminaires=grand_total,
            total_emergency_load_watts=round(tot_watts, 1),
            cbs_inverter_rated_va=selected_inverter,
            cbs_battery_dc_bus_v=dc_bus_voltage_v,
            cbs_calculated_battery_ah=round(c_raw, 2),
            cbs_selected_battery_ah=selected_ah,
            cbs_battery_blocks_12v_count=blocks_count,
            total_cbs_circuits_count=cbs_circuits,
            coordination_notices=notices,
        )
