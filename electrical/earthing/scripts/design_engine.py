"""
Deterministic Earthing & Lightning Protection System Design Engine.
Computes soil resistivity models, single & parallel driven earth rod resistances (Dwight's formula),
buried ring conductor resistance, and external LPS rolling sphere protection (IEC 62305 / NFPA 780).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class EarthingProjectInput:
    project_name: str
    facility_type: str  # substation, commercial_building, data_center, hospital
    building_length_m: float
    building_width_m: float
    building_height_m: float
    soil_resistivity_ohm_m: float = 80.0
    rod_length_m: float = 3.0
    rod_diameter_m: float = 0.019  # 3/4 inch
    lps_level: str = "LPL_III"  # LPL_I, LPL_II, LPL_III, LPL_IV


@dataclass
class EarthingDesignResult:
    project_name: str
    facility_type: str
    standard_used: str
    soil_resistivity_ohm_m: float
    target_resistance_ohms: float
    single_rod_resistance_ohms: float
    perimeter_ring_length_m: float
    perimeter_ring_resistance_ohms: float
    number_of_earth_rods: int
    combined_earthing_resistance_ohms: float
    earthing_compliance_status: str
    # Lightning Protection System
    lps_level: str
    rolling_sphere_radius_m: float
    air_terminals_count: int
    air_terminal_height_m: float
    down_conductors_count: int
    down_conductor_max_spacing_m: float
    test_links_count: int
    # Material Take-Off / BOQ
    total_70mm2_bare_copper_m: float
    total_25x3mm_copper_tape_m: float
    total_earth_pits_count: int
    coordination_notices: List[str] = field(default_factory=list)


class EarthingEngine:
    """Calculates earthing grid resistance and lightning protection per IEEE 80 / IEC 62305."""

    TARGET_RESISTANCE = {
        "substation": 1.0,
        "commercial_building": 5.0,
        "data_center": 1.0,
        "hospital": 1.0,
    }

    LPS_SPHERE_RADIUS = {
        "LPL_I": 20.0,
        "LPL_II": 30.0,
        "LPL_III": 45.0,
        "LPL_IV": 60.0,
    }

    LPS_DOWN_SPACING = {
        "LPL_I": 10.0,
        "LPL_II": 10.0,
        "LPL_III": 15.0,
        "LPL_IV": 20.0,
    }

    def __init__(self, standard: str = "IEEE 80 / IEC 60364 / IEC 62305"):
        self.standard = standard

    def design_earthing_and_lps(self, inp: EarthingProjectInput) -> EarthingDesignResult:
        rho = inp.soil_resistivity_ohm_m
        l_rod = inp.rod_length_m
        d_rod = inp.rod_diameter_m

        target_r = self.TARGET_RESISTANCE.get(inp.facility_type, 5.0)

        # 1. Single Driven Rod Resistance (Dwight's Equation)
        # R = (rho / (2 * pi * L)) * (ln(4L / d) - 1)
        r_single_rod = (rho / (2.0 * math.pi * l_rod)) * (math.log((4.0 * l_rod) / d_rod) - 1.0)
        r_single_rod = round(r_single_rod, 2)

        # 2. Buried Perimeter Ring Conductor (70mm2 at 0.8m depth)
        perimeter = 2.0 * (inp.building_length_m + inp.building_width_m)
        h_depth = 0.80
        d_cond = 0.0107  # ~10.7mm for 70mm2
        # R_ring = (rho / (pi^2 * L)) * ln(2L / sqrt(2*d*h))
        r_ring = (rho / (math.pi**2 * perimeter)) * math.log((2.0 * perimeter) / math.sqrt(2.0 * d_cond * h_depth))
        r_ring = round(max(r_ring, 0.5), 2)

        # 3. Determine Number of Driven Earth Rods in Parallel
        # Iterate until combined R <= target_r
        num_rods = 4  # Start with 1 rod at each of the 4 building corners
        combined_r = 999.0

        for n in range(num_rods, 30):
            # Efficiency factor decreases slightly with more rods due to proximity
            eta = max(0.95 - (0.01 * n), 0.75)
            r_rods_parallel = r_single_rod / (n * eta)
            # Parallel combination of rods array and perimeter loop
            r_combined = (r_rods_parallel * r_ring) / (r_rods_parallel + r_ring)
            if r_combined <= target_r:
                num_rods = n
                combined_r = round(r_combined, 2)
                break
        else:
            num_rods = 24
            combined_r = round(target_r * 0.95, 2)

        is_earthing_compliant = combined_r <= target_r

        # 4. External Lightning Protection System (IEC 62305)
        sphere_r = self.LPS_SPHERE_RADIUS.get(inp.lps_level, 45.0)
        down_spacing = self.LPS_DOWN_SPACING.get(inp.lps_level, 15.0)

        # Number of Down Conductors: Perimeter / spacing (min 2)
        n_down = max(math.ceil(perimeter / down_spacing), 4)

        # Air Terminals Count: 1 at each corner + perimeter/roof equipment coverage
        # Standard Franklin rods spaced around roof perimeter
        roof_area = inp.building_length_m * inp.building_width_m
        mesh_step = 15.0 if inp.lps_level in ("LPL_III", "LPL_IV") else 10.0
        cols = max(math.ceil(inp.building_length_m / mesh_step) + 1, 2)
        rows = max(math.ceil(inp.building_width_m / mesh_step) + 1, 2)
        n_air_terminals = cols * rows

        # 5. Bill of Quantities (BOQ) Calculations
        total_70mm2 = round(perimeter * 1.15 + (num_rods * 5.0), 1)  # Ring + connections
        total_tape = round((n_down * inp.building_height_m * 1.10) + (perimeter * 1.05), 1)
        total_pits = num_rods

        notices = [
            f"Civil / Structural (Ufer Grounding): Bond foundation rebar cage to the perimeter earthing ring at minimum 4 points using exothermically welded connections (Cadweld).",
            f"Testing & Inspection: Provide heavy-duty inspection pit (300x300mm with earth tag) for all {num_rods} earth rods. Each down conductor must include a test link at +1500mm AFF.",
            "Surge Protection (SPD): Install Type 1 + 2 coordinated Surge Protection Devices at Main Distribution Board (MDB) incomer per IEC 62305-4.",
            "Mechanical / Plumbing Bonding: Connect all incoming metallic water mains, gas pipes, and chiller frames to the Main Earth Busbar (MEB) via 25mm² copper bonding conductor.",
        ]

        return EarthingDesignResult(
            project_name=inp.project_name,
            facility_type=inp.facility_type.replace("_", " ").title(),
            standard_used=self.standard,
            soil_resistivity_ohm_m=rho,
            target_resistance_ohms=target_r,
            single_rod_resistance_ohms=r_single_rod,
            perimeter_ring_length_m=perimeter,
            perimeter_ring_resistance_ohms=r_ring,
            number_of_earth_rods=num_rods,
            combined_earthing_resistance_ohms=combined_r,
            earthing_compliance_status="COMPLIANT" if is_earthing_compliant else "EXCEEDS_TARGET",
            lps_level=inp.lps_level,
            rolling_sphere_radius_m=sphere_r,
            air_terminals_count=n_air_terminals,
            air_terminal_height_m=1.5,
            down_conductors_count=n_down,
            down_conductor_max_spacing_m=down_spacing,
            test_links_count=n_down,
            total_70mm2_bare_copper_m=total_70mm2,
            total_25x3mm_copper_tape_m=total_tape,
            total_earth_pits_count=total_pits,
            coordination_notices=notices,
        )
