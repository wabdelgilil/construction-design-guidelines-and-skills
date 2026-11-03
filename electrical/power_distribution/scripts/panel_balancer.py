"""
3-Phase Panel Board Load Balancer & Optimization Engine.
Distributes single-phase branch circuits across three phases (R, Y, B / L1, L2, L3)
to achieve minimum unbalance factor (< 5%) and minimize neutral current.
Zero mental math, zero hallucination.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class BranchCircuit:
    circuit_id: str
    description: str
    load_watts: float
    load_type: str = "sockets"  # 'lighting', 'sockets', 'ac', 'water_heater', 'kitchen'
    phases: int = 1             # 1 or 3
    power_factor: float = 0.85
    breaker_rating_a: int = 16
    cable_size_sqmm: float = 2.5
    assigned_phase: Optional[str] = None  # 'R', 'Y', 'B' (or 'RYB' for 3-phase)

    @property
    def load_va(self) -> float:
        return round(self.load_watts / max(0.5, self.power_factor), 1)


@dataclass
class PanelScheduleResult:
    panel_name: str
    system_voltage_v: float
    circuits: List[BranchCircuit]
    phase_loads_va: Dict[str, float]
    phase_currents_a: Dict[str, float]
    total_connected_load_va: float
    total_connected_load_kw: float
    unbalance_pct: float
    neutral_current_a: float
    main_breaker_rating_a: int
    is_balanced: bool
    summary: Dict[str, Any] = field(default_factory=dict)


class PanelBalancer:
    """Balances electrical panelboards across 3 phases."""

    STANDARD_MAIN_BREAKERS = [32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 400, 630]

    @classmethod
    def balance_panel(
        cls,
        panel_name: str,
        circuits: List[BranchCircuit],
        system_voltage_v: float = 400.0,
    ) -> PanelScheduleResult:
        # Phase-to-neutral voltage
        v_phase = system_voltage_v / math.sqrt(3.0)

        # 1. Distribute 3-phase loads equally across all 3 phases
        three_phase = [c for c in circuits if c.phases == 3]
        single_phase = [c for c in circuits if c.phases == 1]

        phase_va = {"R": 0.0, "Y": 0.0, "B": 0.0}

        for c in three_phase:
            c.assigned_phase = "RYB"
            share = c.load_va / 3.0
            phase_va["R"] += share
            phase_va["Y"] += share
            phase_va["B"] += share

        # 2. Greedy assignment of single-phase loads (Largest first)
        sorted_circuits = sorted(single_phase, key=lambda c: c.load_va, reverse=True)

        for c in sorted_circuits:
            min_phase = min(phase_va, key=phase_va.get)
            c.assigned_phase = min_phase
            phase_va[min_phase] += c.load_va

        # 3. Local search pairwise swap refinement
        phases = ["R", "Y", "B"]
        improved = True
        iterations = 0

        while improved and iterations < 50:
            improved = False
            iterations += 1
            max_phase = max(phase_va, key=phase_va.get)
            min_phase = min(phase_va, key=phase_va.get)
            current_diff = phase_va[max_phase] - phase_va[min_phase]

            if current_diff < 50.0:
                break

            # Find best swap between max_phase and min_phase
            best_swap = None
            best_diff = current_diff

            max_circuits = [c for c in single_phase if c.assigned_phase == max_phase]
            min_circuits = [c for c in single_phase if c.assigned_phase == min_phase]

            for c_max in max_circuits:
                for c_min in min_circuits:
                    delta = c_max.load_va - c_min.load_va
                    if 0 < delta < current_diff:
                        new_diff = abs((phase_va[max_phase] - delta) - (phase_va[min_phase] + delta))
                        if new_diff < best_diff:
                            best_diff = new_diff
                            best_swap = (c_max, c_min)

            if best_swap and best_diff < current_diff - 10.0:
                c1, c2 = best_swap
                c1.assigned_phase = min_phase
                c2.assigned_phase = max_phase
                phase_va[max_phase] -= (c1.load_va - c2.load_va)
                phase_va[min_phase] += (c1.load_va - c2.load_va)
                improved = True

        # 4. Compute currents and unbalance metrics
        phase_currents = {
            ph: round(phase_va[ph] / v_phase, 2) for ph in phases
        }
        avg_current = sum(phase_currents.values()) / 3.0
        max_dev = max(abs(i - avg_current) for i in phase_currents.values())
        unbalance_pct = round((max_dev / max(avg_current, 0.001)) * 100.0, 2)

        # Neutral current formula
        i_r, i_y, i_b = phase_currents["R"], phase_currents["Y"], phase_currents["B"]
        i_neut_sq = (
            i_r**2 + i_y**2 + i_b**2 - (i_r * i_y + i_y * i_b + i_b * i_r)
        )
        neutral_current = round(math.sqrt(max(i_neut_sq, 0.0)), 2)

        total_connected_va = sum(phase_va.values())
        total_connected_kw = sum(c.load_watts for c in circuits) / 1000.0

        # Sizing main incoming breaker (1.25 continuous design current)
        max_phase_current = max(phase_currents.values())
        design_incomer_current = max_phase_current * 1.25
        main_breaker = next(
            (b for b in cls.STANDARD_MAIN_BREAKERS if b >= design_incomer_current),
            cls.STANDARD_MAIN_BREAKERS[-1],
        )

        return PanelScheduleResult(
            panel_name=panel_name,
            system_voltage_v=system_voltage_v,
            circuits=circuits,
            phase_loads_va={k: round(v, 1) for k, v in phase_va.items()},
            phase_currents_a=phase_currents,
            total_connected_load_va=round(total_connected_va, 1),
            total_connected_load_kw=round(total_connected_kw, 2),
            unbalance_pct=unbalance_pct,
            neutral_current_a=neutral_current,
            main_breaker_rating_a=main_breaker,
            is_balanced=(unbalance_pct <= 5.0),
            summary={
                "R_phase_load_va": round(phase_va["R"], 1),
                "Y_phase_load_va": round(phase_va["Y"], 1),
                "B_phase_load_va": round(phase_va["B"], 1),
                "unbalance_percentage": f"{unbalance_pct}%",
                "neutral_current_amps": f"{neutral_current} A",
                "recommended_main_breaker": f"{main_breaker} A 3P",
            },
        )
