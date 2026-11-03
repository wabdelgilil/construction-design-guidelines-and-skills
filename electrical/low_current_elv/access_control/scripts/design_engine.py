"""
Deterministic Access Control System (ACS) & Security Door Interlocks Design Engine.
Computes door hardware current draws, controller sizing, power supply ratings,
4-hour backup battery Ah capacity, and life safety fail-safe fire release compliance.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class ControlledDoorInput:
    door_tag: str
    door_name: str
    door_type: str  # single_leaf, double_leaf
    security_level: str  # standard_interior, perimeter_heavy, server_biometric
    lock_type: str  # maglock_600lbs, maglock_1200lbs, electric_strike
    reader_type: str = "card_reader"  # card_reader, biometric_reader
    has_rex_button: bool = True
    has_rex_pir: bool = True
    has_bgu: bool = True
    has_dps: bool = True
    on_egress_route: bool = True


@dataclass
class DoorDesignDetail:
    door_tag: str
    door_name: str
    lock_type: str
    lock_count: int
    lock_holding_force_n: int
    reader_type: str
    lock_current_ma: float
    peripherals_current_ma: float
    total_door_current_ma: float
    power_watts: float
    failsafe_compliant: bool


@dataclass
class AccessControlDesignResult:
    project_name: str
    standard_used: str
    dc_operating_voltage_v: float
    doors: List[DoorDesignDetail]
    total_doors_count: int
    total_controllers_count: int
    controller_type: str  # e.g., 4-Door Intelligent Network Controllers
    total_system_current_ma: float
    total_system_current_a: float
    total_system_power_watts: float
    recommended_psu_current_a: float
    recommended_psu_rating_w: float
    calculated_battery_ah: float
    selected_battery_ah: float
    battery_voltage_v: float
    battery_blocks_count: int
    fire_alarm_interlock_mandatory: bool
    coordination_notices: List[str] = field(default_factory=list)


class AccessControlEngine:
    """Calculates power, hardware, controllers, and battery autonomy for access control systems."""

    LOCK_SPECS = {
        "maglock_600lbs": {"ma": 500.0, "force_n": 2700, "failsafe": True},
        "maglock_1200lbs": {"ma": 600.0, "force_n": 5300, "failsafe": True},
        "electric_strike": {"ma": 300.0, "force_n": 4000, "failsafe": True},
    }

    READER_SPECS = {
        "card_reader": 100.0,
        "biometric_reader": 250.0,
    }

    REX_PIR_MA = 50.0
    REX_BUTTON_MA = 0.0  # Passive switch or 20mA LED
    DPS_MA = 0.0         # Passive dry contact
    CONTROLLER_BASE_MA_PER_DOOR = 120.0  # Distributed controller draw allocation

    STANDARD_PSU_AMPS = [3.0, 5.0, 10.0, 15.0, 20.0, 30.0]
    STANDARD_BATTERY_AH = [7.0, 12.0, 17.0, 24.0, 38.0, 65.0]

    def __init__(self, standard: str = "NFPA 101 / UL 294 / SBC 801"):
        self.standard = standard

    def design_system(
        self,
        project_name: str,
        doors: List[ControlledDoorInput],
        autonomy_hours: float = 4.0,
        dc_voltage_v: float = 12.0,
    ) -> AccessControlDesignResult:
        door_details: List[DoorDesignDetail] = []
        sum_doors_current_ma = 0.0

        for d in doors:
            lock_spec = self.LOCK_SPECS.get(d.lock_type, self.LOCK_SPECS["maglock_600lbs"])
            lock_qty = 2 if d.door_type == "double_leaf" and "maglock" in d.lock_type else 1
            lock_ma = lock_spec["ma"] * lock_qty
            force_n = lock_spec["force_n"] * lock_qty

            reader_ma = self.READER_SPECS.get(d.reader_type, 100.0)
            rex_ma = self.REX_PIR_MA if d.has_rex_pir else 0.0
            periph_ma = reader_ma + rex_ma

            tot_door_ma = lock_ma + periph_ma
            sum_doors_current_ma += tot_door_ma

            door_watts = round((tot_door_ma / 1000.0) * dc_voltage_v, 2)

            door_details.append(
                DoorDesignDetail(
                    door_tag=d.door_tag,
                    door_name=d.door_name,
                    lock_type=d.lock_type,
                    lock_count=lock_qty,
                    lock_holding_force_n=force_n,
                    reader_type=d.reader_type,
                    lock_current_ma=lock_ma,
                    peripherals_current_ma=periph_ma,
                    total_door_current_ma=tot_door_ma,
                    power_watts=door_watts,
                    failsafe_compliant=lock_spec["failsafe"] and (d.has_bgu if d.on_egress_route else True),
                )
            )

        total_doors = len(doors)
        # Sizing Controllers: 4-Door intelligent controllers standard
        controllers_needed = max(math.ceil(total_doors / 4.0), 1)
        controller_overhead_ma = total_doors * self.CONTROLLER_BASE_MA_PER_DOOR

        total_system_ma = sum_doors_current_ma + controller_overhead_ma
        total_system_a = round(total_system_ma / 1000.0, 3)
        total_power_w = round(total_system_a * dc_voltage_v, 2)

        # Minimum PSU sizing (with 1.25 continuous operating margin)
        min_psu_a = total_system_a * 1.25
        selected_psu_a = next((a for a in self.STANDARD_PSU_AMPS if a >= min_psu_a), self.STANDARD_PSU_AMPS[-1])
        selected_psu_w = selected_psu_a * dc_voltage_v

        # 4-Hour Battery Sizing (1.25 aging/derating factor)
        calc_battery_ah = total_system_a * autonomy_hours * 1.25
        selected_battery_ah = next((ah for ah in self.STANDARD_BATTERY_AH if ah >= calc_battery_ah), self.STANDARD_BATTERY_AH[-1])

        coordination = [
            "FACP Interface Relay: Dedicated fail-safe fire alarm relay (NC) installed at PSU to cut lock 12V DC power instantly upon general alarm.",
            "Emergency Egress (BGU): Green double-pole emergency break glass unit mounted at +1200mm AFF, wired in series with positive lock supply.",
            "Architectural Coordination: Coordinate door frame preparation, conduit drops inside frames, and electric hinge / flexible door loops.",
            "Network Uplink: Provide 1x Cat6A RJ45 data point per 4-door controller back to the nearest Telecom IDF rack.",
            "Dedicated LV Power: Provide dedicated 230V AC unswitched fused spur (3A) for each Access Control PSU enclosure.",
        ]

        return AccessControlDesignResult(
            project_name=project_name,
            standard_used=self.standard,
            dc_operating_voltage_v=dc_voltage_v,
            doors=door_details,
            total_doors_count=total_doors,
            total_controllers_count=controllers_needed,
            controller_type="4-Door Intelligent TCP/IP Network Controllers",
            total_system_current_ma=round(total_system_ma, 1),
            total_system_current_a=total_system_a,
            total_system_power_watts=total_power_w,
            recommended_psu_current_a=selected_psu_a,
            recommended_psu_rating_w=selected_psu_w,
            calculated_battery_ah=round(calc_battery_ah, 2),
            selected_battery_ah=selected_battery_ah,
            battery_voltage_v=dc_voltage_v,
            battery_blocks_count=1,
            fire_alarm_interlock_mandatory=True,
            coordination_notices=coordination,
        )
