"""
Deterministic Addressable Fire Alarm System Design Engine.
Computes detector quantities, strobe candela ratings, addressable loop allocations,
FACP standby battery capacity (NFPA 72 / SBC 801), and cross-discipline trip interfaces.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class FireAlarmSpaceInput:
    space_name: str
    length_m: float
    width_m: float
    space_type: str = "office"  # office, kitchen, corridor, server_room, electrical_room
    has_exit_door: bool = False


@dataclass
class SpaceDeviceAllocation:
    space_name: str
    area_m2: float
    detector_type: str
    detector_count: int
    mcp_count: int
    sounder_strobe_count: int
    strobe_candela_cd: int
    interface_modules: List[str] = field(default_factory=list)


@dataclass
class FireAlarmDesignResult:
    project_name: str
    standard_used: str
    total_area_m2: float
    allocations: List[SpaceDeviceAllocation]
    total_smoke_detectors: int
    total_heat_detectors: int
    total_mcps: int
    total_sounder_strobes: int
    total_control_modules: int
    grand_total_addressable_devices: int
    total_loops_required: int
    devices_per_loop: Dict[str, int]
    loop_spare_capacity_pct: float
    # Battery Calculations
    facp_quiescent_current_amps: float
    facp_alarm_current_amps: float
    standby_duration_hours: float
    alarm_duration_minutes: float
    calculated_battery_capacity_ah: float
    selected_battery_rating_ah: float
    battery_voltage_vdc: float
    # Coordination
    coordination_notices: List[str] = field(default_factory=list)


class FireAlarmEngine:
    """Sizes addressable fire alarm system components and battery backup."""

    SMOKE_MAX_AREA = 81.0  # m2 (9.1m x 9.1m NFPA 72)
    HEAT_MAX_AREA = 49.0   # m2 (7.0m x 7.0m NFPA 72)
    MAX_LOOP_DEVICES = 127
    TARGET_SPARE_PCT = 0.20  # 20% spare capacity per loop

    STANDARD_BATTERIES_AH = [7.0, 12.0, 17.0, 24.0, 38.0, 65.0]

    def __init__(self, standard: str = "NFPA 72 / SBC 801"):
        self.standard = standard

    def design_fire_alarm(
        self,
        project_name: str,
        spaces: List[FireAlarmSpaceInput],
    ) -> FireAlarmDesignResult:
        allocations = []
        total_smoke = 0
        total_heat = 0
        total_mcp = 0
        total_sounders = 0
        total_modules = 0
        total_area = 0.0

        for sp in spaces:
            area = round(sp.length_m * sp.width_m, 2)
            total_area += area

            # 1. Detector Selection
            if sp.space_type in ("kitchen", "boiler_room", "parking"):
                det_type = "Rate-of-Rise Heat Detector"
                det_count = max(math.ceil(area / self.HEAT_MAX_AREA), 1)
                total_heat += det_count
            elif sp.space_type in ("server_room", "ups_room"):
                det_type = "Multi-Criteria Optical/Heat Detector"
                det_count = max(math.ceil(area / self.SMOKE_MAX_AREA), 1)
                total_smoke += det_count
            else:
                det_type = "Optical Smoke Detector"
                det_count = max(math.ceil(area / self.SMOKE_MAX_AREA), 1)
                total_smoke += det_count

            # 2. MCP placement
            mcp_cnt = 1 if sp.has_exit_door else 0
            total_mcp += mcp_cnt

            # 3. Sounder / Strobe Candela sizing
            max_dim = max(sp.length_m, sp.width_m)
            if max_dim <= 6.0:
                candela = 15
            elif max_dim <= 9.0:
                candela = 30
            elif max_dim <= 12.0:
                candela = 75
            else:
                candela = 110

            # Sounders: typically 1 per occupied space or corridor
            sounder_cnt = 1 if area >= 15.0 or sp.space_type == "corridor" else 0
            total_sounders += sounder_cnt

            # 4. Interface Modules
            modules = []
            if sp.space_type in ("office", "meeting_room", "corridor"):
                modules.append("HVAC AHU Shutdown Relay Module")
            if sp.has_exit_door:
                modules.append("Access Control Door Release Relay Module")

            total_modules += len(modules)

            allocations.append(
                SpaceDeviceAllocation(
                    space_name=sp.space_name,
                    area_m2=area,
                    detector_type=det_type,
                    detector_count=det_count,
                    mcp_count=mcp_cnt,
                    sounder_strobe_count=sounder_cnt,
                    strobe_candela_cd=candela,
                    interface_modules=modules,
                )
            )

        grand_total_devices = total_smoke + total_heat + total_mcp + total_sounders + total_modules

        # 5. Loop Allocation (Max 127 devices, 20% spare -> effective max ~ 101)
        effective_capacity = int(self.MAX_LOOP_DEVICES * (1.0 - self.TARGET_SPARE_PCT))
        loops_req = max(math.ceil(grand_total_devices / effective_capacity), 1)

        # Distribute devices across loops
        devices_per_loop = {}
        remaining = grand_total_devices
        for l_num in range(1, loops_req + 1):
            batch = min(remaining, effective_capacity) if l_num < loops_req else remaining
            devices_per_loop[f"Loop {l_num}"] = batch
            remaining -= batch

        spare_pct = round(((loops_req * self.MAX_LOOP_DEVICES - grand_total_devices) / (loops_req * self.MAX_LOOP_DEVICES)) * 100.0, 1)

        # 6. NFPA 72 Standby Battery Capacity Calculation
        # Device quiescent current ~ 0.35 mA each, Alarm ~ 2.5 mA each
        # Sounder strobes ~ 35 mA in alarm
        # Panel base quiescent ~ 150 mA, alarm ~ 500 mA
        iq_total_amps = (0.150) + (grand_total_devices * 0.00035)
        ia_total_amps = (0.500) + (grand_total_devices * 0.0025) + (total_sounders * 0.035)

        # C = 1.25 * (Iq * 24h + Ia * 0.25h)
        standby_ah = iq_total_amps * 24.0
        alarm_ah = ia_total_amps * (15.0 / 60.0)
        c_battery_raw = 1.25 * (standby_ah + alarm_ah)

        # Select standard 24V battery
        selected_ah = self.STANDARD_BATTERIES_AH[-1]
        for b_ah in self.STANDARD_BATTERIES_AH:
            if b_ah >= c_battery_raw:
                selected_ah = b_ah
                break

        notices = [
            "HVAC Mechanical Interface: Connect FACP control modules to AHU starters and motorized fire dampers (MFD) for auto-shutdown upon smoke detection.",
            "Security Interface: Fire alarm relay must cut power to all electromagnetic door locks (fail-safe unlock) upon confirmed alarm.",
            "Elevator Interface: Dedicated monitor/control module installed in elevator motor room for primary and secondary floor recall per NFPA 72 / ASME A17.1.",
            "Plumbing / Fire Protection: Monitor water-flow switches (WFS) on sprinkler zone control valves (ZCV) via addressable monitor modules.",
            "Cabling: Loop wiring must use 2-core 1.5mm² red fire-resistant shielded cable (FP200 / PH120) with fire-rated clips every 300mm.",
        ]

        return FireAlarmDesignResult(
            project_name=project_name,
            standard_used=self.standard,
            total_area_m2=total_area,
            allocations=allocations,
            total_smoke_detectors=total_smoke,
            total_heat_detectors=total_heat,
            total_mcps=total_mcp,
            total_sounder_strobes=total_sounders,
            total_control_modules=total_modules,
            grand_total_addressable_devices=grand_total_devices,
            total_loops_required=loops_req,
            devices_per_loop=devices_per_loop,
            loop_spare_capacity_pct=spare_pct,
            facp_quiescent_current_amps=round(iq_total_amps, 3),
            facp_alarm_current_amps=round(ia_total_amps, 3),
            standby_duration_hours=24.0,
            alarm_duration_minutes=15.0,
            calculated_battery_capacity_ah=round(c_battery_raw, 2),
            selected_battery_rating_ah=selected_ah,
            battery_voltage_vdc=24.0,
            coordination_notices=notices,
        )
