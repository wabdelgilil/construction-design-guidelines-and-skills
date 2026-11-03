"""
Deterministic Building Management System (BMS) & DDC Automation Control Design Engine.
Formulates comprehensive MEP I/O point schedules (DI, DO, AI, AO), sizes Direct Digital Controllers (DDC)
with 20% mandatory spare capacity, determines panel locations, and establishes BACnet/IP network architecture.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class MEPEquipmentBMSInput:
    equipment_tag: str
    equipment_type: str  # ahu, chiller, pump, fan, substation_mdb, water_tank, fcu_vav
    description: str
    location: str
    quantity: int = 1
    has_vfd: bool = True


@dataclass
class EquipmentPointBreakdown:
    equipment_tag: str
    description: str
    location: str
    di_count: int
    do_count: int
    ai_count: int
    ao_count: int
    total_hardwired_points: int
    hli_integration_type: str  # Modbus RTU, BACnet/IP, None
    point_descriptions: List[str] = field(default_factory=list)


@dataclass
class DDCPanelAllocation:
    panel_tag: str
    panel_location: str
    served_equipment: List[str]
    sum_di: int
    sum_do: int
    sum_ai: int
    sum_ao: int
    active_points: int
    spare_points: int
    equipped_capacity_points: int
    base_ddc_units_count: int
    expansion_modules_count: int
    enclosure_size_mm: str
    psu_power_w: float


@dataclass
class BMSDesignResult:
    project_name: str
    standard_used: str
    primary_protocol: str  # BACnet/IP
    field_bus_protocol: str  # BACnet MS/TP
    equipment_points: List[EquipmentPointBreakdown]
    ddc_panels: List[DDCPanelAllocation]
    total_active_di: int
    total_active_do: int
    total_active_ai: int
    total_active_ao: int
    grand_total_active_points: int
    grand_total_spare_points: int
    grand_total_equipped_points: int
    total_ddc_panels_count: int
    total_hli_gateways_count: int
    recommended_ups_va: int
    coordination_notices: List[str] = field(default_factory=list)


class BMSDesignEngine:
    """Generates MEP point schedules, sizes DDC controllers, and establishes BMS architecture."""

    DDC_BASE_CAPACITY = 32        # 32-Point High Performance BACnet/IP DDC Controller
    EXPANSION_MODULE_CAPACITY = 16 # 16-Point Universal I/O Expansion Module
    SPARE_MARGIN = 0.20           # 20% Spare I/O as per ASHRAE 135 & SBC 601

    def __init__(self, standard: str = "ASHRAE 135 (BACnet) / ISO 16484 / SBC 601"):
        self.standard = standard

    def generate_bms_design(
        self,
        project_name: str,
        equipment_list: List[MEPEquipmentBMSInput],
    ) -> BMSDesignResult:
        equip_points: List[EquipmentPointBreakdown] = []

        for eq in equipment_list:
            di, do, ai, ao = 0, 0, 0, 0
            p_desc = []
            hli = "None"

            t = eq.equipment_type.lower()
            if t == "ahu":
                di = 4   # Fan Run Status (DPS), Fan Trip (OL), Filter Dirty (DPS), Fire Damper Status
                do = 2   # Fan Start/Stop, Damper Actuator Enable
                ai = 4   # Supply Air Temp, Return Air Temp, Return Air CO2 ppm, Duct Static Pressure
                ao = 2 if eq.has_vfd else 1 # Chilled Water Valve (0-10V), Fan VFD Speed (0-10V)
                p_desc = [
                    "DI: Supply Fan Run Status (DPS)",
                    "DI: Supply Fan Trip Alarm",
                    "DI: Air Filter Dirty Alarm (DPS)",
                    "DI: Fire Smoke Damper Open/Close",
                    "DO: Supply Fan Start/Stop Command",
                    "DO: Fresh Air Damper Open/Close",
                    "AI: Supply Air Temperature (°C)",
                    "AI: Return Air Temperature (°C)",
                    "AI: Space Air Quality (CO2 ppm)",
                    "AI: Duct Static Air Pressure (Pa)",
                    "AO: Chilled Water 2-Way Modulating Valve (0-100%)",
                ]
                if eq.has_vfd:
                    p_desc.append("AO: Fan VFD Speed Control (0-100%)")
                hli = "VFD Modbus RTU"

            elif t == "chiller":
                di = 3   # Run, Trip, Water Flow Switch
                do = 1   # Enable/Disable
                ai = 4   # CHW Supply Temp, CHW Return Temp, CW Supply Temp, CW Return Temp
                ao = 1   # Demand Limit / Setpoint
                p_desc = [
                    "DI: Chiller Running Status",
                    "DI: Chiller Common Alarm/Trip",
                    "DI: Evaporator Water Flow Switch",
                    "DO: Chiller Remote Enable Command",
                    "AI: Chilled Water Supply Temp (°C)",
                    "AI: Chilled Water Return Temp (°C)",
                    "AI: Condenser Water Entering Temp (°C)",
                    "AI: Condenser Water Leaving Temp (°C)",
                    "AO: Chiller Capacity Demand Reset (0-10V)",
                ]
                hli = "BACnet/IP Gateway (Chiller Microprocessor)"

            elif t == "pump":
                di = 3   # Run, Trip, HOA in Auto
                do = 1   # Start/Stop
                ai = 2   # Suction Pressure, Discharge Pressure
                ao = 1 if eq.has_vfd else 0 # VFD Speed
                p_desc = [
                    "DI: Pump Running Status (DPS)",
                    "DI: Pump Motor Trip Alarm",
                    "DI: Local HOA Switch in Auto Status",
                    "DO: Pump Remote Start/Stop Command",
                    "AI: Suction Line Pressure (bar)",
                    "AI: Discharge Line Pressure (bar)",
                ]
                if eq.has_vfd:
                    p_desc.append("AO: Pump VFD Frequency Speed Command (0-10V)")
                hli = "VFD Modbus RTU" if eq.has_vfd else "None"

            elif t == "substation_mdb":
                di = 4   # Incomer Closed, Incomer Trip, Surge Arrester Healthy, Phase Fail
                do = 0
                ai = 0
                ao = 0
                p_desc = [
                    "DI: Main Incomer ACB Closed Status",
                    "DI: Main Incomer ACB Trip Alarm",
                    "DI: Surge Protection Device (SPD) Status",
                    "DI: Phase Sequence / Under-Voltage Relay",
                ]
                hli = "Power Meter Modbus RTU (V, I, kW, pf, THD)"

            elif t == "water_tank":
                di = 2   # High Level, Low Level (Dry Run)
                do = 0
                ai = 1   # Ultrasonic Water Level (0-100%)
                ao = 0
                p_desc = [
                    "DI: High Water Level Overflow Alarm",
                    "DI: Low Water Level Dry-Run Alarm",
                    "AI: Potable Tank Water Level Transmitter (0-100%)",
                ]
                hli = "None"

            elif t == "fan":
                di = 2   # Run, Trip
                do = 1   # Start/Stop
                ai = 0
                ao = 0
                p_desc = [
                    "DI: Fan Running Status (Airflow Switch)",
                    "DI: Fan Motor Overload Trip Alarm",
                    "DO: Fan Remote Start/Stop Command",
                ]
                hli = "None"

            else:
                di, do, ai, ao = 2, 1, 1, 1
                p_desc = ["DI: Status", "DO: Command", "AI: Temp", "AO: Position"]

            tot_eq = (di + do + ai + ao) * eq.quantity
            equip_points.append(
                EquipmentPointBreakdown(
                    equipment_tag=eq.equipment_tag,
                    description=eq.description,
                    location=eq.location,
                    di_count=di * eq.quantity,
                    do_count=do * eq.quantity,
                    ai_count=ai * eq.quantity,
                    ao_count=ao * eq.quantity,
                    total_hardwired_points=tot_eq,
                    hli_integration_type=hli,
                    point_descriptions=p_desc,
                )
            )

        # -------------------------------------------------------------
        # DDC Panel Grouping by Physical Location
        # -------------------------------------------------------------
        locations = sorted(list(set(e.location for e in equip_points)))
        panels: List[DDCPanelAllocation] = []

        tot_di, tot_do, tot_ai, tot_ao = 0, 0, 0, 0

        for idx, loc in enumerate(locations, start=1):
            loc_equips = [e for e in equip_points if e.location == loc]
            loc_di = sum(e.di_count for e in loc_equips)
            loc_do = sum(e.do_count for e in loc_equips)
            loc_ai = sum(e.ai_count for e in loc_equips)
            loc_ao = sum(e.ao_count for e in loc_equips)

            tot_di += loc_di
            tot_do += loc_do
            tot_ai += loc_ai
            tot_ao += loc_ao

            active = loc_di + loc_do + loc_ai + loc_ao
            spare = math.ceil(active * self.SPARE_MARGIN)
            equipped = active + spare

            # Base DDC + Expansions
            base_ddc = 1
            rem_points = max(equipped - self.DDC_BASE_CAPACITY, 0)
            exp_modules = math.ceil(rem_points / self.EXPANSION_MODULE_CAPACITY)

            pnl_tag = f"DDC-P{idx:02d}"
            enclosure = "800(H) x 600(W) x 250(D) mm IP54" if exp_modules <= 2 else "1000(H) x 800(W) x 300(D) mm IP54"
            psu_w = round(60.0 + (exp_modules * 15.0) + (loc_do * 5.0), 0)

            panels.append(
                DDCPanelAllocation(
                    panel_tag=pnl_tag,
                    panel_location=loc,
                    served_equipment=[e.equipment_tag for e in loc_equips],
                    sum_di=loc_di,
                    sum_do=loc_do,
                    sum_ai=loc_ai,
                    sum_ao=loc_ao,
                    active_points=active,
                    spare_points=spare,
                    equipped_capacity_points=equipped,
                    base_ddc_units_count=base_ddc,
                    expansion_modules_count=exp_modules,
                    enclosure_size_mm=enclosure,
                    psu_power_w=psu_w,
                )
            )

        grand_active = tot_di + tot_do + tot_ai + tot_ao
        grand_spare = sum(p.spare_points for p in panels)
        grand_equipped = grand_active + grand_spare

        hli_cnt = sum(1 for e in equip_points if e.hli_integration_type != "None")

        # BMS Central Control Room UPS Sizing (Server + Workstation + DDCs)
        total_ddc_w = sum(p.psu_power_w for p in panels)
        ups_demand_va = ((total_ddc_w + 600.0) / 0.8) * 1.25  # 600W for Server & dual LCD workstations
        selected_ups_va = next((v for v in [1000, 1500, 2000, 3000, 5000] if v >= ups_demand_va), 3000)

        notices = [
            f"Spare I/O Capacity: Every DDC panel equipped with >= 20% spare points ({grand_spare} physical spare points reserved across the project).",
            "BACnet/IP Backbone: Native 10/100 Ethernet RJ45 uplinks from each DDC panel back to the nearest Telecom IDF switch.",
            "High-Level Interface (HLI): High-speed Modbus/BACnet gateways integrated for VFD telemetry, chiller internal diagnostics, and MDB energy meters.",
            "Life Safety Interlock: Fire Alarm Control Panel (FACP) sends hardwired priority dry contacts to immediately override and shutdown AHUs and activate smoke exhaust fans.",
            "Fail-Safe Actuators: Chilled water modulating valve and fresh air dampers equipped with spring-return fail-safe electronic actuators.",
        ]

        return BMSDesignResult(
            project_name=project_name,
            standard_used=self.standard,
            primary_protocol="BACnet/IP (ANSI/ASHRAE 135)",
            field_bus_protocol="BACnet MS/TP (RS-485)",
            equipment_points=equip_points,
            ddc_panels=panels,
            total_active_di=tot_di,
            total_active_do=tot_do,
            total_active_ai=tot_ai,
            total_active_ao=tot_ao,
            grand_total_active_points=grand_active,
            grand_total_spare_points=grand_spare,
            grand_total_equipped_points=grand_equipped,
            total_ddc_panels_count=len(panels),
            total_hli_gateways_count=hli_cnt,
            recommended_ups_va=selected_ups_va,
            coordination_notices=notices,
        )
