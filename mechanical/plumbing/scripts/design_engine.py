"""
Deterministic Plumbing Design Engine.
Computes DFU drainage load, stack sizing, WSFU water demand, Hunter's Curve flow rate,
booster pump head & motor sizing, and cross-discipline structural sleeves & electrical feeds.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class PlumbingFixturesSchedule:
    water_closet_tank: int = 4
    lavatory: int = 4
    shower: int = 2
    kitchen_sink: int = 2
    washing_machine: int = 1
    floor_drain: int = 3


@dataclass
class PlumbingDesignResult:
    building_tag: str
    code_used: str
    total_dfu: float
    selected_soil_stack_diameter_in: int
    selected_building_drain_diameter_in: int
    minimum_drain_slope_pct: float
    total_wsfu: float
    design_flow_gpm: float
    design_flow_l_per_s: float
    static_head_m: float
    friction_head_m: float
    residual_pressure_m: float
    total_pump_head_m: float
    total_pump_head_bar: float
    pump_motor_power_kw: float
    pump_configuration: str  # e.g. 1 Duty + 1 Standby
    # Electrical Interface
    pump_voltage_v: float
    pump_current_amps: float
    pump_mcb_rating_amps: int
    # Structural Interface
    sleeves_required: List[Dict[str, str]]
    coordination_notices: List[str] = field(default_factory=list)


class PlumbingEngine:
    """Sizes sanitary drainage and domestic water boosting systems per SBC 701 / IPC."""

    DFU_VALUES = {
        "wc": 3.0,
        "lav": 1.0,
        "shower": 2.0,
        "sink": 2.0,
        "wm": 3.0,
        "fd": 2.0,
    }

    WSFU_VALUES = {
        "wc": 2.5,
        "lav": 1.5,
        "shower": 2.0,
        "sink": 2.0,
        "wm": 2.0,
    }

    def __init__(self, code: str = "SBC"):
        self.code = code

    def design_plumbing(
        self,
        building_tag: str,
        fixtures: PlumbingFixturesSchedule,
        building_height_m: float = 12.0,
        equivalent_pipe_length_m: float = 40.0,
    ) -> PlumbingDesignResult:
        # 1. Drainage Fixture Units (DFU)
        total_dfu = (
            fixtures.water_closet_tank * self.DFU_VALUES["wc"]
            + fixtures.lavatory * self.DFU_VALUES["lav"]
            + fixtures.shower * self.DFU_VALUES["shower"]
            + fixtures.kitchen_sink * self.DFU_VALUES["sink"]
            + fixtures.washing_machine * self.DFU_VALUES["wm"]
            + fixtures.floor_drain * self.DFU_VALUES["fd"]
        )

        # Sizing Soil Stack
        if total_dfu <= 72:
            soil_stack_in = 3
        elif total_dfu <= 500:
            soil_stack_in = 4
        else:
            soil_stack_in = 6

        # Sizing Horizontal Building Drain (at 1% slope)
        if total_dfu <= 36:
            drain_in = 3
            slope_pct = 2.0  # 3-inch needs 2% slope
        elif total_dfu <= 180:
            drain_in = 4
            slope_pct = 1.0  # 4-inch can be 1% slope
        else:
            drain_in = 6
            slope_pct = 1.0

        # 2. Water Supply Fixture Units (WSFU)
        total_wsfu = (
            fixtures.water_closet_tank * self.WSFU_VALUES["wc"]
            + fixtures.lavatory * self.WSFU_VALUES["lav"]
            + fixtures.shower * self.WSFU_VALUES["shower"]
            + fixtures.kitchen_sink * self.WSFU_VALUES["sink"]
            + fixtures.washing_machine * self.WSFU_VALUES["wm"]
        )

        # Hunter's Curve Flow Rate (GPM)
        if total_wsfu <= 50:
            flow_gpm = 3.0 * math.sqrt(max(total_wsfu, 1.0))
        elif total_wsfu <= 200:
            flow_gpm = 15.0 + 0.35 * total_wsfu
        else:
            flow_gpm = 40.0 + 0.20 * total_wsfu

        flow_lps = flow_gpm * 0.06309

        # 3. Booster Pump Head Sizing
        h_static = building_height_m
        h_friction = round(0.12 * equivalent_pipe_length_m, 2)
        h_residual = 15.0  # min 1.5 bar at highest outlet
        h_total = round(h_static + h_friction + h_residual, 2)
        h_bar = round(h_total / 10.197, 2)

        # Motor Power: P = (rho * g * Q * H) / (eta_pump * eta_motor * 1000)
        # Q in m3/s = flow_lps / 1000
        q_m3s = flow_lps / 1000.0
        p_hyd_w = 1000.0 * 9.81 * q_m3s * h_total
        efficiency = 0.65 * 0.85  # ~ 55% wire-to-water efficiency
        p_motor_kw_raw = (p_hyd_w / efficiency) / 1000.0

        # Select standard motor kw: 0.75, 1.1, 1.5, 2.2, 3.0, 4.0, 5.5, 7.5 kW
        std_motors = [0.75, 1.1, 1.5, 2.2, 3.0, 4.0, 5.5, 7.5]
        motor_kw = std_motors[-1]
        for sm in std_motors:
            if sm >= p_motor_kw_raw:
                motor_kw = sm
                break

        # Electrical Interface
        voltage = 400.0 if motor_kw >= 2.2 else 230.0
        if voltage == 400.0:
            i_flc = round((motor_kw * 1000.0) / (math.sqrt(3) * 400.0 * 0.82), 1)
        else:
            i_flc = round((motor_kw * 1000.0) / (230.0 * 0.82), 1)

        mcb = 16 if i_flc <= 10.0 else (25 if i_flc <= 16.0 else 32)

        # Structural Sleeve Clearances
        sleeves = [
            {
                "service": "Main Building Drain Outlet",
                "pipe_size": f"{drain_in} inch UPVC",
                "sleeve_size": f"{drain_in + 2} inch Steel / PVC Sleeve",
                "location": "Through Grade Beam GB-01 (Mid-depth, > 200mm from Column C1 face)",
                "waterproofing": "Hydrophilic water-stop ring + mechanical link-seal",
            },
            {
                "service": "Potable Water Main Inlet",
                "pipe_size": "2 inch PPR / Copper",
                "sleeve_size": "3 inch PVC Sleeve",
                "location": "Basement Retaining Wall (Below ground level)",
                "waterproofing": "EPDM Link-Seal modular gasket",
            },
        ]

        notices = [
            f"Civil/Structural Interface: Provide {drain_in + 2}-inch structural pipe sleeve through grade beam. Strictly prohibited to core-drill after concrete casting.",
            f"Electrical Interface: Provide dedicated 3-Phase 400V feeder from Sub-DB to Booster Pump Control Panel (MCA = {round(i_flc * 1.25, 1)}A, MCB = {mcb}A).",
            "Electrical Controls: Low-water dry-run float switch interlock inside break tank connected to pump control panel.",
            "Water Heater Electrical Interface: Provide 20A double-pole switch with neon indicator at +1600mm AFF outside bathroom splash zone.",
        ]

        return PlumbingDesignResult(
            building_tag=building_tag,
            code_used=self.code,
            total_dfu=total_dfu,
            selected_soil_stack_diameter_in=soil_stack_in,
            selected_building_drain_diameter_in=drain_in,
            minimum_drain_slope_pct=slope_pct,
            total_wsfu=total_wsfu,
            design_flow_gpm=round(flow_gpm, 1),
            design_flow_l_per_s=round(flow_lps, 2),
            static_head_m=h_static,
            friction_head_m=h_friction,
            residual_pressure_m=h_residual,
            total_pump_head_m=h_total,
            total_pump_head_bar=h_bar,
            pump_motor_power_kw=motor_kw,
            pump_configuration="Twin Booster Set (1 Duty + 1 Standby with Automatic Alternation)",
            pump_voltage_v=voltage,
            pump_current_amps=i_flc,
            pump_mcb_rating_amps=mcb,
            sleeves_required=sleeves,
            coordination_notices=notices,
        )
