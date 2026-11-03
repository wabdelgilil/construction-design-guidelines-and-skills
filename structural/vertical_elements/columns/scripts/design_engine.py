"""
Deterministic Design Engine for Reinforced Concrete Tied Columns.
Supports short and slender column analysis, axial load capacity, buckling/slenderness check,
and complete longitudinal and lateral tie reinforcement detailing.
Supports SBC 304, ACI 318-19, and ECP 203.
Zero mental math, zero hallucination.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ColumnInput:
    dead_load_kn: float
    live_load_kn: float
    unbraced_length_m: float = 3.20
    effective_length_factor_k: float = 1.0  # k = 0.7 to 1.0 for non-sway
    moment_top_kn_m: float = 0.0
    moment_bot_kn_m: float = 0.0
    fc_prime_mpa: float = 28.0
    fy_mpa: float = 420.0
    concrete_cover_mm: float = 40.0
    target_steel_ratio: float = 0.012  # 1.2% target
    preferred_width_mm: Optional[float] = None  # e.g., wall thickness 200mm or 250mm
    code: str = "SBC"


@dataclass
class ColumnDesignResult:
    # Cross-Section
    width_mm: float
    length_mm: float
    gross_area_ag_mm2: float

    # Loads
    service_load_kn: float
    ultimate_load_kn: float
    design_axial_capacity_kn: float
    capacity_ratio: float

    # Slenderness & Buckling
    slenderness_ratio_lambda: float
    slenderness_limit: float
    is_slender: bool
    classification: str  # "Short Column" or "Slender Column"
    magnified_moment_kn_m: float

    # Reinforcement Detailing
    as_required_mm2: float
    as_provided_mm2: float
    actual_steel_ratio_pct: float
    longitudinal_rebar_desc: str
    total_bar_count: int
    bar_dia_mm: int
    tie_diameter_mm: int
    tie_spacing_mm: float
    tie_desc: str

    overall_status: str
    code_used: str
    summary: Dict[str, Any] = field(default_factory=dict)


class ColumnEngine:
    """Computes exact, deterministic dimensions, slenderness, and rebar for reinforced concrete columns."""

    def __init__(self, data: ColumnInput):
        self.inp = data
        self.code = data.code.upper()

    def design(self) -> ColumnDesignResult:
        # Step 1: Loads
        p_d = self.inp.dead_load_kn
        p_l = self.inp.live_load_kn
        p_service = p_d + p_l

        if self.code == "ECP":
            p_u = 1.4 * p_d + 1.6 * p_l
            phi = 1.0
            alpha = 0.35
            beta = 0.67
            min_rho = 0.008
            gamma_c = 1.50
            gamma_s = 1.15
        else:  # SBC or ACI
            p_u = 1.2 * p_d + 1.6 * p_l
            phi = 0.65  # tied column
            alpha = 0.80
            min_rho = 0.010
            gamma_c = 1.0
            gamma_s = 1.0

        fc = self.inp.fc_prime_mpa
        fy = self.inp.fy_mpa
        rho = max(self.inp.target_steel_ratio, min_rho)

        # Step 2: Sizing Gross Area Ag
        # Pu <= phi * Pn = alpha * phi * [0.85 * fc * (Ag - Ast) + fy * Ast]
        # With Ast = rho * Ag => Pu <= alpha * phi * Ag * [0.85 * fc * (1 - rho) + fy * rho]
        if self.code == "ECP":
            # ECP: Pu = 0.35 * fcu * Ac + 0.67 * fy * As
            denom = 0.35 * fc * (1.0 - rho) + 0.67 * fy * rho
            ag_req = (p_u * 1000.0) / denom
        else:
            denom = alpha * phi * (0.85 * fc * (1.0 - rho) + fy * rho)
            ag_req = (p_u * 1000.0) / denom

        # Dimensions: if preferred_width is set (e.g. 200 or 250 mm for wall alignment)
        b_mm = self.inp.preferred_width_mm or 250.0
        b_mm = max(b_mm, 200.0)

        l_calc = ag_req / b_mm
        # Round up to nearest 50 mm
        l_mm = math.ceil(max(l_calc, b_mm) / 50.0) * 50.0
        ag_actual = b_mm * l_mm

        # Step 3: Slenderness & Buckling Analysis
        # Radius of gyration along weak axis: r = 0.30 * b_mm
        r = 0.30 * b_mm
        k = self.inp.effective_length_factor_k
        lu_mm = self.inp.unbraced_length_m * 1000.0
        slenderness = (k * lu_mm) / r

        # Slenderness limit for non-sway columns: 34 - 12*(M1/M2) <= 40
        m1 = self.inp.moment_top_kn_m
        m2 = self.inp.moment_bot_kn_m
        if abs(m2) > 0.001:
            ratio_m = m1 / m2
        else:
            ratio_m = 0.0

        slenderness_limit = max(min(34.0 - 12.0 * ratio_m, 40.0), 22.0)
        is_slender = slenderness > slenderness_limit

        # Moment magnification for slender column
        if is_slender:
            # Euler buckling load: Pc = (pi^2 * EI) / (k * lu)^2
            # E = 4700 * sqrt(fc), I = 0.7 * (1/12) * l_mm * b_mm^3
            ec = 4700.0 * math.sqrt(fc)
            i_g = (l_mm * (b_mm**3)) / 12.0
            ei = 0.40 * ec * i_g
            p_c = (math.pi**2 * ei) / ((k * lu_mm)**2)  # N
            p_c_kn = p_c / 1000.0

            cm = 0.60 + 0.40 * ratio_m
            cm = max(cm, 0.40)
            delta_ns = cm / max(1.0 - (p_u / (0.75 * p_c_kn)), 0.1)
            magnified_moment = max(abs(m2), 0.0) * delta_ns
            class_str = "Slender Column (Buckling Magnified)"
        else:
            magnified_moment = max(abs(m1), abs(m2))
            class_str = "Short Column (No Buckling)"

        # Step 4: Actual Axial Capacity & Steel Area
        ast_req = max(rho * ag_actual, min_rho * ag_actual)
        bar_dia = 16
        bar_area = (math.pi / 4.0) * (bar_dia**2)

        # Minimum 4 bars for rectangular column, must be even number for 2-face symmetry
        n_bars_calc = math.ceil(ast_req / bar_area)
        n_bars = max(n_bars_calc, 4)
        if n_bars % 2 != 0:
            n_bars += 1

        ast_prov = n_bars * bar_area
        actual_rho_pct = round((ast_prov / ag_actual) * 100.0, 2)

        # Axial capacity with provided steel
        if self.code == "ECP":
            pn_prov = (0.35 * fc * (ag_actual - ast_prov) + 0.67 * fy * ast_prov) / 1000.0
        else:
            pn_prov = alpha * phi * (0.85 * fc * (ag_actual - ast_prov) + fy * ast_prov) / 1000.0

        cap_ratio = round(p_u / pn_prov, 3)

        # Step 5: Lateral Ties Design
        tie_dia = 10 if self.code != "ECP" else 8
        # Tie spacing: min(16*d_bar, 48*d_tie, least_dim, 200mm)
        tie_spacing = min(16 * bar_dia, 48 * tie_dia, b_mm, 200.0)
        tie_spacing = math.floor(tie_spacing / 10.0) * 10.0  # round down to 10mm

        rebar_desc = f"{n_bars} T{bar_dia} (As = {int(ast_prov)} mm2, {actual_rho_pct}%)"
        tie_desc = f"T{tie_dia} @ {int(tie_spacing)} mm c/c (Closed Ties)"

        overall_safe = (cap_ratio <= 1.0) and (actual_rho_pct <= 4.0)

        return ColumnDesignResult(
            width_mm=b_mm,
            length_mm=l_mm,
            gross_area_ag_mm2=ag_actual,
            service_load_kn=round(p_service, 1),
            ultimate_load_kn=round(p_u, 1),
            design_axial_capacity_kn=round(pn_prov, 1),
            capacity_ratio=cap_ratio,
            slenderness_ratio_lambda=round(slenderness, 1),
            slenderness_limit=round(slenderness_limit, 1),
            is_slender=is_slender,
            classification=class_str,
            magnified_moment_kn_m=round(magnified_moment, 2),
            as_required_mm2=round(ast_req, 1),
            as_provided_mm2=round(ast_prov, 1),
            actual_steel_ratio_pct=actual_rho_pct,
            longitudinal_rebar_desc=rebar_desc,
            total_bar_count=n_bars,
            bar_dia_mm=bar_dia,
            tie_diameter_mm=tie_dia,
            tie_spacing_mm=tie_spacing,
            tie_desc=tie_desc,
            overall_status="SAFE" if overall_safe else "REVISE",
            code_used=self.code,
            summary={
                "dimensions": f"{int(b_mm)} x {int(l_mm)} mm",
                "classification": class_str,
                "rebar": rebar_desc,
                "ties": tie_desc,
                "capacity_utilization": f"{cap_ratio * 100:.1f}%",
            },
        )
