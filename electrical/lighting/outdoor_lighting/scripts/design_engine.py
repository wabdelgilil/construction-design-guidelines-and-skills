"""Outdoor Roadway and Area Lighting Design Engine.

Governing Standards:
- CIE 115:2010: Lighting of Roads for Motor and Pedestrian Traffic
- EN 13201 (Parts 2 & 3): Road Lighting - Performance Requirements & Calculation of Performance
- IESNA RP-8: Recommended Practice for Design and Maintenance of Roadway Lighting
- SBC 401: Saudi Building Code Electrical Installations
"""

import math
from typing import Dict, Any, List


class OutdoorLightingDesignEngine:
    """Calculates roadway lighting pole spacing, mounting height, illuminance,
    uniformity, circuit balancing, and long feeder voltage drop."""

    ROAD_CLASSES = {
        "M1": {"lavg": 2.0, "u0": 0.40, "ul": 0.70, "ti": 10.0},
        "M2": {"lavg": 1.5, "u0": 0.40, "ul": 0.70, "ti": 10.0},
        "M3": {"lavg": 1.0, "u0": 0.40, "ul": 0.60, "ti": 15.0},
        "M4": {"lavg": 0.75, "u0": 0.40, "ul": 0.60, "ti": 15.0},
        "M5": {"lavg": 0.50, "u0": 0.35, "ul": 0.40, "ti": 15.0},
    }

    def __init__(self, code_standard: str = "SBC"):
        self.code_standard = code_standard
        self.nominal_voltage_3ph = 400.0 if code_standard in ["SBC", "ECP"] else 480.0
        self.nominal_voltage_1ph = self.nominal_voltage_3ph / math.sqrt(3)
        self.maintenance_factor = 0.80  # Default LED MF
        self.q0_luminance_coefficient = 0.07  # Standard asphalt (CIE R3)

    def design_roadway_lighting(
        self,
        road_length_m: float,
        road_width_m: float,
        number_of_lanes: int = 2,
        road_class: str = "M3",
        pole_arrangement: str = "single_sided",  # "single_sided", "staggered", "opposite", "median_twin"
        luminaire_power_w: float = 150.0,
        luminaire_lumens: float = 21500.0,
        mounting_height_m: float = 10.0,
        feeder_cable_length_m: float = None,
        feeder_conductor_csa_mm2: float = 16.0
    ) -> Dict[str, Any]:
        """Calculates roadway lighting design, spacing, number of poles,
        illuminance/luminance levels, uniformity, and voltage drop."""
        if road_class not in self.ROAD_CLASSES:
            road_class = "M3"
        req = self.ROAD_CLASSES[road_class]

        # 1. Geometry & Pole Spacing (CIE 115 / EN 13201)
        # Empirical Spacing-to-Height ratio: Typically 3.0 to 3.6 for high uniformity
        target_s_h_ratio = 3.3
        calc_spacing = mounting_height_m * target_s_h_ratio

        # Determine number of poles based on road length and arrangement
        if pole_arrangement in ["single_sided", "staggered"]:
            num_spans = max(1, math.ceil(road_length_m / calc_spacing))
            actual_spacing = road_length_m / num_spans
            num_poles = num_spans + 1
            num_luminaires = num_poles
        elif pole_arrangement == "opposite":
            num_spans = max(1, math.ceil(road_length_m / calc_spacing))
            actual_spacing = road_length_m / num_spans
            num_poles_per_side = num_spans + 1
            num_poles = num_poles_per_side * 2
            num_luminaires = num_poles
        elif pole_arrangement == "median_twin":
            num_spans = max(1, math.ceil(road_length_m / calc_spacing))
            actual_spacing = road_length_m / num_spans
            num_poles = num_spans + 1
            num_luminaires = num_poles * 2  # Double arm bracket
        else:
            num_spans = max(1, math.ceil(road_length_m / calc_spacing))
            actual_spacing = road_length_m / num_spans
            num_poles = num_spans + 1
            num_luminaires = num_poles

        # 2. Photometric Calculation: Average Illuminance & Luminance
        # Average Illuminance: E_avg = (Total_Lumens * Utilisation_Factor * Maintenance_Factor) / (Length * Width)
        # Utilization Factor (UF) typical for LED roadway optics: ~0.45 - 0.52
        utilization_factor = 0.48
        total_lamp_lumens = num_luminaires * luminaire_lumens
        road_surface_area = road_length_m * road_width_m
        effective_maintained_lumens = total_lamp_lumens * utilization_factor * self.maintenance_factor
        e_avg_lux = effective_maintained_lumens / road_surface_area

        # Road Surface Luminance (L_avg in cd/m2)
        # L_avg approx = q0 * E_avg (where q0 ~ 0.07 for standard CIE R3 asphalt)
        l_avg_cd_m2 = self.q0_luminance_coefficient * e_avg_lux

        # Uniformity estimates based on S/H ratio and arrangement
        s_h_actual = actual_spacing / mounting_height_m
        if s_h_actual <= 3.5:
            est_u0 = 0.42
            est_ul = 0.68
        elif s_h_actual <= 4.0:
            est_u0 = 0.38
            est_ul = 0.60
        else:
            est_u0 = 0.32
            est_ul = 0.50

        # Check compliance
        lavg_compliant = l_avg_cd_m2 >= req["lavg"]
        u0_compliant = est_u0 >= req["u0"]

        # 3. Electrical Distribution & Circuit Balancing
        # Balanced across 3 phases (R-S-T)
        total_lighting_load_kw = (num_luminaires * luminaire_power_w * 1.10) / 1000.0  # 1.10 driver losses
        pf = 0.95
        total_lighting_load_kva = total_lighting_load_kw / pf
        flc_amps_3ph = (total_lighting_load_kva * 1000.0) / (math.sqrt(3) * self.nominal_voltage_3ph)

        # 4. Long Feeder Voltage Drop (Distributed Load Formulation)
        # For uniformly distributed loads along a feeder line, equivalent electrical length is L / 2
        feeder_length = feeder_cable_length_m if feeder_cable_length_m else road_length_m
        # Copper resistance at operating temp (70C): ~0.0225 ohm.mm2/m
        rho_cu = 0.0225
        r_cable_per_km = (rho_cu * 1000.0) / feeder_conductor_csa_mm2
        # Voltage drop for distributed 3-phase line:
        # V_drop = sqrt(3) * I_total * (R_per_km * (L / 2) / 1000) * cos(phi)
        v_drop_volts = math.sqrt(3) * flc_amps_3ph * (r_cable_per_km * (feeder_length / 2.0) / 1000.0) * pf
        v_drop_percent = (v_drop_volts / self.nominal_voltage_3ph) * 100.0
        v_drop_compliant = v_drop_percent <= 5.0

        return {
            "code_standard": self.code_standard,
            "road_class": road_class,
            "road_requirements": req,
            "road_geometry": {
                "road_length_m": road_length_m,
                "road_width_m": road_width_m,
                "number_of_lanes": number_of_lanes,
                "road_surface_area_m2": round(road_surface_area, 2),
                "pole_arrangement": pole_arrangement,
                "mounting_height_m": mounting_height_m,
                "actual_spacing_m": round(actual_spacing, 2),
                "spacing_to_height_ratio": round(s_h_actual, 2),
                "num_poles": num_poles,
                "num_luminaires": num_luminaires,
            },
            "photometrics": {
                "luminaire_power_w": luminaire_power_w,
                "luminaire_lumens": luminaire_lumens,
                "maintenance_factor": self.maintenance_factor,
                "utilization_factor": utilization_factor,
                "e_avg_lux": round(e_avg_lux, 2),
                "l_avg_cd_m2": round(l_avg_cd_m2, 2),
                "req_lavg_cd_m2": req["lavg"],
                "est_u0": round(est_u0, 2),
                "req_u0": req["u0"],
                "est_ul": round(est_ul, 2),
                "lavg_compliant": lavg_compliant,
                "u0_compliant": u0_compliant,
            },
            "electrical_feeder": {
                "total_lighting_load_kw": round(total_lighting_load_kw, 2),
                "total_lighting_load_kva": round(total_lighting_load_kva, 2),
                "power_factor": pf,
                "nominal_voltage_3ph": self.nominal_voltage_3ph,
                "flc_amps_3ph": round(flc_amps_3ph, 2),
                "feeder_length_m": feeder_length,
                "cable_csa_mm2": feeder_conductor_csa_mm2,
                "v_drop_volts": round(v_drop_volts, 2),
                "v_drop_percent": round(v_drop_percent, 2),
                "v_drop_compliant": v_drop_compliant,
            }
        }
