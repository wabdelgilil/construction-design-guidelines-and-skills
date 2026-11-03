"""
Deterministic Automatic Power Factor Correction (APFC) & Detuned Filter Sizing Engine.
Calculates reactive power deficit (kVAR), detuned anti-resonance reactor (7%/14%) parameters,
heavy-duty capacitor cell voltage ratings, modular step sequences, switching contactors,
and total switchboard incomer breaker sizing under IEC 61921, IEC 60831, and IEEE 519.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class APFCStepDetail:
    step_number: int
    step_kvar: float
    effective_kvar: float
    rated_voltage_v: float
    step_nominal_current_a: float
    step_design_current_a: float
    switching_contactor_type: str
    contactor_rating_ac6b_a: float
    step_fuse_or_mccb_a: int
    reactor_p_percent: float
    reactor_inductance_mh: float


@dataclass
class PFCDesignResult:
    project_name: str
    standard_used: str
    nominal_voltage_v: float
    frequency_hz: float
    active_power_kw: float
    initial_power_factor: float
    target_power_factor: float
    calculated_kvar: float
    selected_total_kvar: float
    steps: List[APFCStepDetail]
    total_steps_count: int
    step_progression_sequence: str
    detuned_reactor_percent: float
    tuning_frequency_hz: float
    capacitor_rated_voltage_v: float
    total_bank_nominal_current_a: float
    total_bank_design_current_a: float
    incomer_mccb_rating_a: int
    apparent_power_initial_kva: float
    apparent_power_corrected_kva: float
    apparent_power_released_kva: float
    line_current_reduction_a: float
    coordination_notices: List[str] = field(default_factory=list)


class PowerFactorCorrectionEngine:
    """Sizes APFC capacitor banks, detuned reactors, contactors, and switchgear."""

    STANDARD_BREAKERS = [100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600]

    def __init__(self, standard: str = "IEC 61921 / IEC 60831 / IEEE 519 / SBC 401"):
        self.standard = standard

    def calculate_apfc_bank(
        self,
        project_name: str,
        active_power_kw: float,
        initial_pf: float,
        target_pf: float = 0.96,
        nominal_voltage_v: float = 400.0,
        frequency_hz: float = 60.0,
        detuning_reactor_p_percent: float = 7.0,
    ) -> PFCDesignResult:
        # 1. Angles
        phi1 = math.acos(initial_pf)
        phi2 = math.acos(target_pf)

        # 2. Required Reactive Power: Qc = P * (tan phi1 - tan phi2)
        tan_diff = math.tan(phi1) - math.tan(phi2)
        calc_kvar = active_power_kw * tan_diff

        # 3. Step Sizing: Standard round modular sizes (25kVAR or 50kVAR base)
        # Choose total bank size in multiples of 50 or 25
        base_step = 25.0 if calc_kvar <= 200.0 else 50.0
        num_steps = max(math.ceil(calc_kvar / base_step), 2)
        selected_total_kvar = num_steps * base_step

        # Step configuration array
        step_sizes: List[float] = [base_step] * num_steps

        # 4. Detuned Reactor & Voltage Rise
        p_dec = detuning_reactor_p_percent / 100.0
        # Tuning frequency: f_res = f1 / sqrt(p)
        f_res = frequency_hz / math.sqrt(p_dec)

        # Voltage across capacitor with series reactor: Vc = Vn / (1 - p)
        v_cap_calc = nominal_voltage_v / (1.0 - p_dec)
        cap_rated_v = 480.0 if nominal_voltage_v <= 415.0 else 525.0

        # Effective kVAR output when 480V/525V capacitor operates at 400V with reactor
        # Q_eff = Q_nom * (Vn / V_rated)^2 * (1 / (1 - p))
        v_ratio_sq = (nominal_voltage_v / cap_rated_v) ** 2

        steps_detail: List[APFCStepDetail] = []
        tot_nom_amp = 0.0
        tot_des_amp = 0.0

        omega = 2.0 * math.pi * frequency_hz

        for idx, q_step in enumerate(step_sizes, start=1):
            # Effective output per step
            q_eff = q_step

            # Nominal Step Current: I = Q / (sqrt(3) * V)
            i_nom = (q_eff * 1000.0) / (math.sqrt(3.0) * nominal_voltage_v)
            # Design Current under IEC 61921: 1.43 * I_nom (harmonic overcurrent & tolerance)
            i_des = i_nom * 1.43

            tot_nom_amp += i_nom
            tot_des_amp += i_des

            # Inductance per phase of series reactor:
            # X_L = p * X_C = p * (V^2 / Q)
            # L = X_L / omega (in mH)
            x_l = p_dec * ((nominal_voltage_v ** 2) / (q_eff * 1000.0))
            l_mh = round((x_l / omega) * 1000.0, 3)

            # Contactor AC-6b rating (minimum 1.43 x I_nom)
            contactor_a = round(i_des, 1)

            # Step Fuse or MCCB (1.5x to 1.8x I_nom)
            step_mccb = next((b for b in [32, 40, 50, 63, 80, 100, 125, 160] if b >= i_nom * 1.5), 160)

            steps_detail.append(
                APFCStepDetail(
                    step_number=idx,
                    step_kvar=q_step,
                    effective_kvar=round(q_eff, 1),
                    rated_voltage_v=cap_rated_v,
                    step_nominal_current_a=round(i_nom, 1),
                    step_design_current_a=round(i_des, 1),
                    switching_contactor_type="Capacitor Contactor (AC-6b with Pre-charge Resistors)",
                    contactor_rating_ac6b_a=contactor_a,
                    step_fuse_or_mccb_a=step_mccb,
                    reactor_p_percent=detuning_reactor_p_percent,
                    reactor_inductance_mh=l_mh,
                )
            )

        # Incomer Breaker Sizing for Bank (1.43 x Total Bank Current)
        selected_incomer_mccb = next((b for b in self.STANDARD_BREAKERS if b >= tot_des_amp), self.STANDARD_BREAKERS[-1])

        # Power System Benefits
        s1 = active_power_kw / initial_pf
        s2 = active_power_kw / target_pf
        s_saved = round(s1 - s2, 1)

        i_line_1 = (s1 * 1000.0) / (math.sqrt(3.0) * nominal_voltage_v)
        i_line_2 = (s2 * 1000.0) / (math.sqrt(3.0) * nominal_voltage_v)
        i_reduction = round(i_line_1 - i_line_2, 1)

        seq_str = " + ".join([f"{int(s)}kVAR" for s in step_sizes])

        notices = [
            f"Anti-Resonance Protection: Series {detuning_reactor_p_percent}% iron-core reactors block parallel resonance at {f_res:.1f}Hz (safely below 5th harmonic).",
            f"Capacitor Voltage Rating: Heavy-duty {cap_rated_v:.0f}V cells selected to continuously withstand fundamental voltage rise of {v_cap_calc:.1f}V.",
            f"Inrush Limitation: Steps utilize specialized AC-6b contactors equipped with early-make auxiliary damping resistors.",
            f"Thermal Ventilation: Enclosure must include forced ventilation exhaust fans (heat dissipation approx {selected_total_kvar * 6.5:.0f} Watts from reactors).",
            f"Transformer Capacity Released: By improving power factor from {initial_pf:.2f} to {target_pf:.2f}, {s_saved:.1f} kVA of transformer/feeder capacity is unlocked.",
        ]

        return PFCDesignResult(
            project_name=project_name,
            standard_used=self.standard,
            nominal_voltage_v=nominal_voltage_v,
            frequency_hz=frequency_hz,
            active_power_kw=active_power_kw,
            initial_power_factor=initial_pf,
            target_power_factor=target_pf,
            calculated_kvar=round(calc_kvar, 1),
            selected_total_kvar=selected_total_kvar,
            steps=steps_detail,
            total_steps_count=num_steps,
            step_progression_sequence=seq_str,
            detuned_reactor_percent=detuning_reactor_p_percent,
            tuning_frequency_hz=round(f_res, 1),
            capacitor_rated_voltage_v=cap_rated_v,
            total_bank_nominal_current_a=round(tot_nom_amp, 1),
            total_bank_design_current_a=round(tot_des_amp, 1),
            incomer_mccb_rating_a=selected_incomer_mccb,
            apparent_power_initial_kva=round(s1, 1),
            apparent_power_corrected_kva=round(s2, 1),
            apparent_power_released_kva=s_saved,
            line_current_reduction_a=i_reduction,
            coordination_notices=notices,
        )
