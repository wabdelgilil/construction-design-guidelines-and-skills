"""
Deterministic Design Engine for Reinforced Concrete Isolated Footings.
Supports SBC 304, ACI 318-19, and ECP 203.
Zero mental math, zero hallucination.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FootingInput:
    column_width_mm: float           # Column dimension along B (mm)
    column_length_mm: float          # Column dimension along L (mm)
    dead_load_kn: float              # Unfactored Dead Load (kN)
    live_load_kn: float              # Unfactored Live Load (kN)
    allowable_soil_capacity_kpa: float = 200.0  # q_all (kPa)
    fc_prime_mpa: float = 28.0       # Concrete cylinder strength (or fcu for ECP)
    fy_mpa: float = 420.0            # Steel rebar yield strength (MPa)
    concrete_cover_mm: float = 75.0  # Cover (mm)
    preferred_bar_dia_mm: int = 14   # Preferred bar diameter (mm)
    code: str = "SBC"                # SBC, ACI, or ECP


@dataclass
class FootingDesignResult:
    # Dimensions (mm & m)
    length_mm: float
    width_mm: float
    thickness_mm: float
    effective_depth_mm: float
    area_m2: float

    # Pressures (kPa)
    service_load_kn: float
    ultimate_load_kn: float
    actual_soil_pressure_service_kpa: float
    net_ultimate_soil_pressure_kpa: float

    # Cantilever Projections (mm)
    cantilever_l_mm: float
    cantilever_b_mm: float

    # Two-Way Punching Shear
    punching_perimeter_bo_mm: float
    punching_shear_force_vu_kn: float
    punching_shear_stress_mpa: float
    punching_capacity_mpa: float
    punching_safety_ratio: float
    punching_status: str

    # One-Way Beam Shear
    beam_shear_force_vu_kn: float
    beam_shear_stress_mpa: float
    beam_shear_capacity_mpa: float
    beam_shear_safety_ratio: float
    beam_shear_status: str

    # Flexure & Reinforcement (Long Direction - L)
    moment_ul_kn_m: float
    as_required_l_mm2: float
    as_min_l_mm2: float
    as_provided_l_mm2: float
    bars_l_count: int
    bar_dia_l_mm: int
    bar_spacing_l_mm: float
    bars_per_meter_l: str

    # Flexure & Reinforcement (Short Direction - B)
    moment_ub_kn_m: float
    as_required_b_mm2: float
    as_min_b_mm2: float
    as_provided_b_mm2: float
    bars_b_count: int
    bar_dia_b_mm: int
    bar_spacing_b_mm: float
    bars_per_meter_b: str

    code_used: str
    overall_status: str
    summary: Dict[str, Any] = field(default_factory=dict)


class IsolatedFootingEngine:
    """Computes exact, deterministic dimensions, shear, and reinforcement for isolated footings."""

    def __init__(self, data: FootingInput):
        self.inp = data
        self.code = data.code.upper()

    def design(self) -> FootingDesignResult:
        # Step 1: Loads
        p_d = self.inp.dead_load_kn
        p_l = self.inp.live_load_kn
        p_service = p_d + p_l
        
        # Self-weight allowance (8% estimated)
        self_weight_factor = 1.08
        p_service_total = p_service * self_weight_factor

        # Step 2: Ultimate Factored Load
        if self.code == "ECP":
            p_u = 1.4 * p_d + 1.6 * p_l
            phi_shear = 1.0  # ECP uses material gamma_c
            phi_flexure = 1.0
            gamma_c = 1.50
            gamma_s = 1.15
            min_rho = 0.0015
        else:  # SBC or ACI
            p_u = 1.2 * p_d + 1.6 * p_l
            phi_shear = 0.75
            phi_flexure = 0.90
            gamma_c = 1.0
            gamma_s = 1.0
            min_rho = 0.0018

        # Step 3: Required Area & Plan Dimensions (L, B)
        # To maintain equal projections: (L - col_l) = (B - col_w) => L = B + (col_l - col_w)
        a = max(self.inp.column_length_mm, self.inp.column_width_mm)
        b = min(self.inp.column_length_mm, self.inp.column_width_mm)
        col_diff = (a - b) / 1000.0  # meters

        q_all = self.inp.allowable_soil_capacity_kpa
        area_req = p_service_total / q_all  # m^2

        # B^2 + B*(col_diff) - area_req = 0
        b_calc = (-col_diff + math.sqrt(col_diff**2 + 4 * area_req)) / 2.0
        l_calc = b_calc + col_diff

        # Round up to nearest 50 mm (0.05 m)
        b_m = math.ceil(b_calc * 20.0) / 20.0
        l_m = math.ceil(l_calc * 20.0) / 20.0

        # Ensure L >= B
        if l_m < b_m:
            l_m, b_m = b_m, l_m

        length_mm = l_m * 1000.0
        width_mm = b_m * 1000.0
        actual_area = l_m * b_m

        # Service soil pressure check
        q_act_service = p_service_total / actual_area

        # Net ultimate soil pressure
        q_u = p_u / actual_area  # kPa = kN/m^2 = N/mm^2 * 1000 => 1 kPa = 0.001 MPa

        # Projections (cantilevers)
        col_l_mm = self.inp.column_length_mm
        col_w_mm = self.inp.column_width_mm
        cantilever_l = (length_mm - col_l_mm) / 2.0
        cantilever_b = (width_mm - col_w_mm) / 2.0

        # Step 4: Iterative Determination of Thickness (Punching & Beam Shear)
        # Initial depth estimation
        cover = self.inp.concrete_cover_mm
        t_mm = 400.0  # Start with 400 mm minimum
        fc = self.inp.fc_prime_mpa

        max_iterations = 20
        d_mm = t_mm - cover

        for _ in range(max_iterations):
            d_mm = t_mm - cover
            
            # --- Two-Way Punching Shear Check ---
            # Critical perimeter at d/2 from column face
            b1 = col_l_mm + d_mm
            b2 = col_w_mm + d_mm
            b_o = 2.0 * (b1 + b2)  # mm
            
            punching_area_m2 = (b1 * b2) / 1e6
            v_u_punch_kn = p_u - (q_u * punching_area_m2)
            v_u_punch_n = v_u_punch_kn * 1000.0
            
            punching_stress = v_u_punch_n / (b_o * d_mm)  # MPa

            if self.code == "ECP":
                # ECP Punching capacity: 0.316 * sqrt(fcu / gamma_c)
                v_c_punch = 0.316 * math.sqrt(fc / gamma_c)
                punch_cap = v_c_punch
            else:
                # SBC / ACI 318 Punching capacity
                beta = max(col_l_mm, col_w_mm) / min(col_l_mm, col_w_mm)
                alpha_s = 40.0  # Interior column
                v_c1 = 0.33 * math.sqrt(fc)
                v_c2 = 0.17 * (1.0 + 2.0 / beta) * math.sqrt(fc)
                v_c3 = 0.083 * (alpha_s * d_mm / b_o + 2.0) * math.sqrt(fc)
                v_c_nominal = min(v_c1, v_c2, v_c3)
                punch_cap = phi_shear * v_c_nominal

            # --- One-Way Beam Shear Check ---
            # Critical section at distance d from column face along longer cantilever
            crit_dist_l = cantilever_l - d_mm
            if crit_dist_l > 0:
                v_u_beam_kn = q_u * (width_mm / 1000.0) * (crit_dist_l / 1000.0)
            else:
                v_u_beam_kn = 0.0

            v_u_beam_n = v_u_beam_kn * 1000.0
            beam_shear_stress = v_u_beam_n / (width_mm * d_mm)  # MPa

            if self.code == "ECP":
                v_c_beam = 0.16 * math.sqrt(fc / gamma_c)
                beam_cap = v_c_beam
            else:
                v_c_nominal_beam = 0.17 * math.sqrt(fc)
                beam_cap = phi_shear * v_c_nominal_beam

            # Check if both shear checks are satisfied
            punching_safe = punching_stress <= punch_cap
            beam_safe = beam_shear_stress <= beam_cap

            if punching_safe and beam_safe:
                break
            else:
                t_mm += 50.0  # Increment thickness by 50 mm and recheck

        punch_ratio = punching_stress / punch_cap if punch_cap > 0 else 999.0
        beam_ratio = beam_shear_stress / beam_cap if beam_cap > 0 else 999.0

        # Step 5: Flexural Moments at Column Faces
        # Moment in Long Direction (L): cantilever is cantilever_l
        # M_uL = q_u * B * (C_L)^2 / 2
        m_ul_kn_m = q_u * (b_m) * ((cantilever_l / 1000.0) ** 2) / 2.0
        # Moment in Short Direction (B): cantilever is cantilever_b
        # M_uB = q_u * L * (C_B)^2 / 2
        m_ub_kn_m = q_u * (l_m) * ((cantilever_b / 1000.0) ** 2) / 2.0

        # Step 6: Reinforcement Calculation
        fy = self.inp.fy_mpa

        def calc_steel(mu_kn_m: float, width_for_flexure_mm: float) -> tuple[float, float]:
            mu_n_mm = mu_kn_m * 1e6
            if self.code == "ECP":
                # ECP Design of sections: d = C1 * sqrt(M / (fcu * b))
                # As = Mu / (fy/gamma_s * j * d), j approx 0.826
                j_factor = 0.826
                as_req = mu_n_mm / ((fy / gamma_s) * j_factor * d_mm)
            else:
                # SBC / ACI 318
                # a = d - sqrt(d^2 - 2*Mu / (0.85*fc*phi*b))
                term = d_mm**2 - (2.0 * mu_n_mm) / (0.85 * fc * phi_flexure * width_for_flexure_mm)
                if term > 0:
                    a_depth = d_mm - math.sqrt(term)
                    as_req = mu_n_mm / (phi_flexure * fy * (d_mm - a_depth / 2.0))
                else:
                    as_req = mu_n_mm / (phi_flexure * fy * 0.9 * d_mm)

            as_min = min_rho * width_for_flexure_mm * d_mm
            as_design = max(as_req, as_min)
            return as_design, as_min

        as_l_design, as_min_l = calc_steel(m_ul_kn_m, width_mm)
        as_b_design, as_min_b = calc_steel(m_ub_kn_m, length_mm)

        # Bar Detailing
        bar_dia = self.inp.preferred_bar_dia_mm
        bar_area = (math.pi / 4.0) * (bar_dia**2)

        # Long direction bars (distributed across width B)
        bars_l_count = max(math.ceil(as_l_design / bar_area), math.ceil(b_m * 5))  # Min 5 bars/meter
        as_l_provided = bars_l_count * bar_area
        spacing_l = (width_mm - 2 * cover) / max(bars_l_count - 1, 1)

        # Short direction bars (distributed across length L)
        bars_b_count = max(math.ceil(as_b_design / bar_area), math.ceil(l_m * 5))
        as_b_provided = bars_b_count * bar_area
        spacing_b = (length_mm - 2 * cover) / max(bars_b_count - 1, 1)

        overall_ok = (punch_ratio <= 1.0) and (beam_ratio <= 1.0)

        bars_per_m_l = f"{math.ceil(bars_l_count / b_m)} T{bar_dia} / m"
        bars_per_m_b = f"{math.ceil(bars_b_count / l_m)} T{bar_dia} / m"

        return FootingDesignResult(
            length_mm=length_mm,
            width_mm=width_mm,
            thickness_mm=t_mm,
            effective_depth_mm=d_mm,
            area_m2=actual_area,
            service_load_kn=p_service_total,
            ultimate_load_kn=p_u,
            actual_soil_pressure_service_kpa=round(q_act_service, 2),
            net_ultimate_soil_pressure_kpa=round(q_u, 2),
            cantilever_l_mm=cantilever_l,
            cantilever_b_mm=cantilever_b,
            punching_perimeter_bo_mm=round(b_o, 1),
            punching_shear_force_vu_kn=round(v_u_punch_kn, 2),
            punching_shear_stress_mpa=round(punching_stress, 3),
            punching_capacity_mpa=round(punch_cap, 3),
            punching_safety_ratio=round(punch_ratio, 3),
            punching_status="SAFE" if punching_safe else "UNSAFE",
            beam_shear_force_vu_kn=round(v_u_beam_kn, 2),
            beam_shear_stress_mpa=round(beam_shear_stress, 3),
            beam_shear_capacity_mpa=round(beam_cap, 3),
            beam_shear_safety_ratio=round(beam_ratio, 3),
            beam_shear_status="SAFE" if beam_safe else "UNSAFE",
            moment_ul_kn_m=round(m_ul_kn_m, 2),
            as_required_l_mm2=round(as_l_design, 1),
            as_min_l_mm2=round(as_min_l, 1),
            as_provided_l_mm2=round(as_l_provided, 1),
            bars_l_count=bars_l_count,
            bar_dia_l_mm=bar_dia,
            bar_spacing_l_mm=round(spacing_l, 1),
            bars_per_meter_l=bars_per_m_l,
            moment_ub_kn_m=round(m_ub_kn_m, 2),
            as_required_b_mm2=round(as_b_design, 1),
            as_min_b_mm2=round(as_min_b, 1),
            as_provided_b_mm2=round(as_b_provided, 1),
            bars_b_count=bars_b_count,
            bar_dia_b_mm=bar_dia,
            bar_spacing_b_mm=round(spacing_b, 1),
            bars_per_meter_b=bars_per_m_b,
            code_used=self.code,
            overall_status="SAFE" if overall_ok else "REVISE",
            summary={
                "footing_dimensions_m": f"{l_m:.2f} x {b_m:.2f} x {t_mm/1000.0:.2f} m",
                "reinforcement_l": f"{bars_l_count} T{bar_dia} (Bottom, Long Dir)",
                "reinforcement_b": f"{bars_b_count} T{bar_dia} (Bottom, Short Dir)"
            }
        )
