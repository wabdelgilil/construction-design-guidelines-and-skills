"""
Cable Sizing & Voltage Drop Engine.
Computes design current (Ib), breaker rating (In), cable cross-section (Iz),
and iterates cable size until voltage drop limits (< 3% / < 5%) are satisfied.
Zero mental math, zero hallucination.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# Standard Copper XLPE/PVC conductors current carrying capacity (Amperes)
# In conduit/trunking at ambient 40°C
STANDARD_COPPER_CABLES = [
    # (size_sqmm, ampacity_iz, resistance_ohm_per_km, reactance_ohm_per_km)
    (1.5, 16.0, 14.8, 0.105),
    (2.5, 22.0, 8.87, 0.099),
    (4.0, 30.0, 5.52, 0.094),
    (6.0, 38.0, 3.69, 0.090),
    (10.0, 52.0, 2.19, 0.086),
    (16.0, 69.0, 1.38, 0.083),
    (25.0, 90.0, 0.87, 0.082),
    (35.0, 111.0, 0.627, 0.081),
    (50.0, 134.0, 0.493, 0.080),
    (70.0, 171.0, 0.342, 0.079),
    (95.0, 207.0, 0.247, 0.078),
    (120.0, 239.0, 0.196, 0.077),
    (150.0, 272.0, 0.159, 0.076),
    (185.0, 310.0, 0.128, 0.076),
    (240.0, 364.0, 0.098, 0.075),
    (300.0, 419.0, 0.079, 0.075),
    (400.0, 480.0, 0.063, 0.074),
]

STANDARD_BREAKERS = [6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 400, 630]


@dataclass
class FeederRequest:
    tag: str
    description: str
    load_kw: float
    length_m: float
    phases: int = 3
    power_factor: float = 0.85
    is_branch_circuit: bool = False


@dataclass
class CableTraySizingResult:
    tray_tag: str
    cables_count: int
    total_cables_cross_section_mm2: float
    max_fill_ratio_allowed_pct: float
    min_required_tray_area_mm2: float
    selected_tray_width_mm: int
    selected_tray_depth_mm: int
    actual_tray_area_mm2: float
    achieved_fill_ratio_pct: float
    status: str


@dataclass
class CableSizingResult:
    load_kw: float
    power_factor: float
    phases: int
    system_voltage_v: float
    circuit_length_m: float
    design_current_ib: float
    breaker_rating_in: int
    cable_size_sqmm: float
    cable_ampacity_iz: float
    voltage_drop_v: float
    voltage_drop_pct: float
    max_allowed_drop_pct: float
    compliance_status: str
    short_circuit_withstand_ka: float = 0.0
    approx_outer_diameter_mm: float = 0.0
    summary: Dict[str, Any] = field(default_factory=dict)


class CableEngine:
    """Calculates design current, breaker size, cable gauge, and voltage drop."""

    @classmethod
    def size_cable(
        cls,
        load_kw: float,
        phases: int = 1,
        system_voltage_v: float = 230.0,
        circuit_length_m: float = 30.0,
        power_factor: float = 0.85,
        temp_derating_factor: float = 0.91,  # 45C ambient
        grouping_derating_factor: float = 0.80,
        is_branch_circuit: bool = True,
    ) -> CableSizingResult:
        # Step 1: Design Current (Ib)
        p_watts = load_kw * 1000.0
        if phases == 3:
            # 3-phase line voltage
            v_line = system_voltage_v if system_voltage_v > 300.0 else system_voltage_v * math.sqrt(3.0)
            ib = p_watts / (math.sqrt(3.0) * v_line * power_factor)
        else:
            # 1-phase phase-to-neutral voltage
            v_phase = system_voltage_v if system_voltage_v <= 250.0 else system_voltage_v / math.sqrt(3.0)
            ib = p_watts / (v_phase * power_factor)

        # Step 2: Sizing Protective Breaker (In >= Ib)
        breaker_in = next((b for b in STANDARD_BREAKERS if b >= ib), STANDARD_BREAKERS[-1])

        # Step 3: Required Cable Ampacity (Iz >= In / (Ct * Cg))
        total_derating = temp_derating_factor * grouping_derating_factor
        required_iz = breaker_in / max(total_derating, 0.1)

        # Allowable voltage drop threshold
        max_allowed_pct = 3.0 if is_branch_circuit else 5.0

        # Step 4: Find matching cable and verify voltage drop (auto-upsize if drop exceeds limit)
        sin_phi = math.sqrt(max(1.0 - power_factor**2, 0.0))

        selected_cable = None
        vd_v = 0.0
        vd_pct = 0.0

        # Start from the cable meeting required ampacity
        start_idx = 0
        for i, c in enumerate(STANDARD_COPPER_CABLES):
            if c[1] >= required_iz:
                start_idx = i
                break

        # Iterate upsize if voltage drop exceeds threshold
        for idx in range(start_idx, len(STANDARD_COPPER_CABLES)):
            cable = STANDARD_COPPER_CABLES[idx]
            size_mm2, iz, r_per_km, x_per_km = cable

            # Resistance and reactance
            r_total = (r_per_km * circuit_length_m) / 1000.0
            x_total = (x_per_km * circuit_length_m) / 1000.0

            # Impedance drop
            if phases == 3:
                vd_v = math.sqrt(3.0) * ib * (r_total * power_factor + x_total * sin_phi)
                v_ref = v_line
            else:
                vd_v = 2.0 * ib * (r_total * power_factor + x_total * sin_phi)
                v_ref = v_phase

            vd_pct = (vd_v / v_ref) * 100.0

            if vd_pct <= max_allowed_pct or idx == len(STANDARD_COPPER_CABLES) - 1:
                selected_cable = cable
                break

        size_sqmm, ampacity_iz, _, _ = selected_cable

        # Adiabatic Short Circuit Thermal Withstand (kA for t = 0.1s, k = 143 for Cu/XLPE)
        # Isc = (k * S) / sqrt(t) -> in kA
        sc_withstand_ka = round((143.0 * size_sqmm) / (math.sqrt(0.1) * 1000.0), 1)

        # Approximate 4-Core XLPE outer diameter (mm)
        # Empirical standard: OD ~ 3.5 * sqrt(size) + 8
        approx_od = round(3.5 * math.sqrt(size_sqmm) + 8.0, 1)

        is_safe = vd_pct <= max_allowed_pct and ampacity_iz >= ib

        return CableSizingResult(
            load_kw=round(load_kw, 2),
            power_factor=power_factor,
            phases=phases,
            system_voltage_v=system_voltage_v,
            circuit_length_m=circuit_length_m,
            design_current_ib=round(ib, 2),
            breaker_rating_in=breaker_in,
            cable_size_sqmm=size_sqmm,
            cable_ampacity_iz=ampacity_iz,
            voltage_drop_v=round(vd_v, 2),
            voltage_drop_pct=round(vd_pct, 2),
            max_allowed_drop_pct=max_allowed_pct,
            compliance_status="SAFE" if is_safe else "EXCEEDS_DROP",
            short_circuit_withstand_ka=sc_withstand_ka,
            approx_outer_diameter_mm=approx_od,
            summary={
                "breaker": f"{breaker_in} A",
                "cable_size": f"{size_sqmm} mm2 Cu/XLPE",
                "voltage_drop": f"{vd_pct:.2f}% (Limit: {max_allowed_pct}%)",
                "status": "SAFE" if is_safe else "EXCEEDED",
            },
        )

    @classmethod
    def size_cable_tray(
        cls,
        tray_tag: str,
        cable_diameters_mm: List[float],
        standard_depth_mm: int = 50,
        max_fill_ratio_pct: float = 40.0,
    ) -> CableTraySizingResult:
        """Sizes standard perforated cable tray based on cable cross-sections and 40% fill limit."""
        # Sum of cross-sectional areas of all cables
        total_cable_area = sum(math.pi * ((d / 2.0) ** 2) for d in cable_diameters_mm)

        # Min tray cross-section: A_tray >= A_cables / fill_ratio
        req_tray_area = total_cable_area / (max_fill_ratio_pct / 100.0)

        # Standard tray widths (mm)
        standard_widths = [100, 150, 200, 300, 450, 600, 750, 900]
        selected_width = standard_widths[-1]
        for w in standard_widths:
            if (w * standard_depth_mm) >= req_tray_area:
                selected_width = w
                break

        actual_tray_area = selected_width * standard_depth_mm
        achieved_fill = round((total_cable_area / actual_tray_area) * 100.0, 1)

        return CableTraySizingResult(
            tray_tag=tray_tag,
            cables_count=len(cable_diameters_mm),
            total_cables_cross_section_mm2=round(total_cable_area, 1),
            max_fill_ratio_allowed_pct=max_fill_ratio_pct,
            min_required_tray_area_mm2=round(req_tray_area, 1),
            selected_tray_width_mm=selected_width,
            selected_tray_depth_mm=standard_depth_mm,
            actual_tray_area_mm2=round(actual_tray_area, 1),
            achieved_fill_ratio_pct=achieved_fill,
            status="COMPLIANT" if achieved_fill <= max_fill_ratio_pct else "OVERFILLED",
        )
