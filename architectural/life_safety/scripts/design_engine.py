"""
Deterministic Life Safety & Means of Egress Engine.
Computes occupant loads, number of required exits, egress widths, travel distance limits,
and MEP fire protection & emergency lighting interfaces per SBC 801 / NFPA 101.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class EgressZoneInput:
    zone_name: str
    area_m2: float
    occupancy_type: str  # e.g., business_office, assembly_unconcentrated, educational_classroom
    longest_travel_distance_m: float
    common_path_distance_m: float = 12.0


@dataclass
class EgressZoneResult:
    zone_name: str
    area_m2: float
    occupancy_type: str
    occupant_load_factor_m2: float
    calculated_occupants: int
    min_exits_required: int
    longest_travel_distance_m: float
    max_travel_distance_allowed_m: float
    travel_pass: bool
    door_capacity_width_required_mm: float
    door_clear_width_provided_mm: float
    door_pass: bool
    stair_width_required_mm: float
    stair_width_provided_mm: float
    stair_pass: bool
    overall_status: str


@dataclass
class LifeSafetyProjectResult:
    building_name: str
    code_used: str
    is_sprinklered: bool
    building_length_m: float
    building_width_m: float
    building_diagonal_m: float
    min_exit_separation_required_m: float
    actual_exit_separation_m: float
    separation_pass: bool
    total_building_occupants: int
    zones: List[EgressZoneResult]
    overall_status: str
    mep_fire_safety_notices: List[str] = field(default_factory=list)


class LifeSafetyEngine:
    """Calculates life safety and egress requirements."""

    def __init__(self, is_sprinklered: bool = True, code: str = "SBC"):
        self.is_sprinklered = is_sprinklered
        self.code = code

    def compute_life_safety(
        self,
        building_name: str,
        building_length_m: float,
        building_width_m: float,
        actual_exit_separation_m: float,
        zones_data: List[EgressZoneInput],
        load_factors: Dict[str, float],
    ) -> LifeSafetyProjectResult:
        diag = round(math.sqrt(building_length_m**2 + building_width_m**2), 2)
        # Remoteness: 1/3 diagonal if sprinklered, 1/2 if unsprinklered
        req_separation = round(diag / 3.0 if self.is_sprinklered else diag / 2.0, 2)
        sep_pass = actual_exit_separation_m >= req_separation

        zone_results = []
        total_occupants = 0
        overall_pass = sep_pass

        # Width capacity factors (mm per person)
        f_level = 3.8 if self.is_sprinklered else 5.1
        f_stair = 5.1 if self.is_sprinklered else 7.6

        # Travel distance limit
        max_travel = 76.0 if self.is_sprinklered else 61.0

        for z in zones_data:
            factor = load_factors.get(z.occupancy_type, 9.3)
            occupants = max(math.ceil(z.area_m2 / factor), 1)
            total_occupants += occupants

            # Required exits
            if occupants <= 49:
                min_exits = 1
            elif occupants <= 500:
                min_exits = 2
            elif occupants <= 1000:
                min_exits = 3
            else:
                min_exits = 4

            # Widths
            req_door_w = max(occupants * f_level, 900.0)
            prov_door_w = 1000.0 if min_exits == 1 else min_exits * 900.0
            door_ok = prov_door_w >= req_door_w

            req_stair_w = max(occupants * f_stair, 1120.0)
            prov_stair_w = 1200.0 if min_exits == 1 else min_exits * 1120.0
            stair_ok = prov_stair_w >= req_stair_w

            travel_ok = z.longest_travel_distance_m <= max_travel

            zone_ok = door_ok and stair_ok and travel_ok
            if not zone_ok:
                overall_pass = False

            zone_results.append(
                EgressZoneResult(
                    zone_name=z.zone_name,
                    area_m2=z.area_m2,
                    occupancy_type=z.occupancy_type,
                    occupant_load_factor_m2=factor,
                    calculated_occupants=occupants,
                    min_exits_required=min_exits,
                    longest_travel_distance_m=z.longest_travel_distance_m,
                    max_travel_distance_allowed_m=max_travel,
                    travel_pass=travel_ok,
                    door_capacity_width_required_mm=round(req_door_w, 1),
                    door_clear_width_provided_mm=prov_door_w,
                    door_pass=door_ok,
                    stair_width_required_mm=round(req_stair_w, 1),
                    stair_width_provided_mm=prov_stair_w,
                    stair_pass=stair_ok,
                    overall_status="PASS" if zone_ok else "VIOLATION",
                )
            )

        mep_notices = [
            "Electrical / Fire Alarm: Install illuminated EXIT signs with minimum 90-minute internal battery backup above all designated egress doors.",
            "Electrical / Fire Alarm: Manual Pull Stations (MCP) must be placed within 1.5m of every required exit door at +1200mm to +1400mm AFF.",
            "Mechanical / Fire Protection: Automatic wet sprinkler system provides building-wide 0.10 gpm/sq.ft design density, allowing extended 76m travel distance.",
            "Mechanical / Smoke Control: Corridors serving more than 30 persons require dedicated smoke extraction or staircase pressurization fans.",
        ]

        return LifeSafetyProjectResult(
            building_name=building_name,
            code_used=self.code,
            is_sprinklered=self.is_sprinklered,
            building_length_m=building_length_m,
            building_width_m=building_width_m,
            building_diagonal_m=diag,
            min_exit_separation_required_m=req_separation,
            actual_exit_separation_m=actual_exit_separation_m,
            separation_pass=sep_pass,
            total_building_occupants=total_occupants,
            zones=zone_results,
            overall_status="FULLY COMPLIANT" if overall_pass else "LIFE SAFETY VIOLATIONS",
            mep_fire_safety_notices=mep_notices,
        )
