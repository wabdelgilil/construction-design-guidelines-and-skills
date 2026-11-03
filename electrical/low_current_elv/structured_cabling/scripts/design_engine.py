"""
Deterministic Structured Cabling System (SCS) & Telecommunications Rack Design Engine.
Calculates Work Area Outlets (WAO), port counts, patch panels, 48-port PoE switches,
42U rack space allocation, fiber optic backbone cores, and UPS power sizing.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class TelecomZoneInput:
    zone_name: str
    workstations_count: int
    wap_count: int = 2
    cctv_cameras_count: int = 4
    access_control_doors_count: int = 2
    printers_av_count: int = 2
    max_distance_to_idf_m: float = 45.0  # Must be <= 90.0m


@dataclass
class RackItemU:
    u_position: int  # 1 to 42
    u_height: int    # 1U, 2U, 3U
    device_name: str
    category: str    # PatchPanel, CableManager, Switch, FiberLIU, UPS, PDU, Blank
    power_watts: float = 0.0


@dataclass
class StructuredCablingDesignResult:
    project_name: str
    standard_used: str
    zones: List[TelecomZoneInput]
    total_workstation_ports: int
    total_wap_ports: int
    total_cctv_ports: int
    total_acs_ports: int
    total_av_ports: int
    grand_total_horizontal_ports: int
    spare_ports_equipped: int
    total_patch_panel_ports: int
    patch_panels_24p_count: int
    horizontal_cable_managers_count: int
    switches_48p_count: int
    fiber_liu_count: int
    backbone_fiber_type: str
    backbone_fiber_cores: int
    total_42u_racks_count: int
    rack_items: List[RackItemU]
    total_u_utilized: int
    total_u_spare: int
    spare_u_percentage: float
    total_switch_poe_power_w: float
    recommended_ups_va: int
    ups_autonomy_minutes: float
    permanent_link_compliant: bool
    coordination_notices: List[str] = field(default_factory=list)


class StructuredCablingEngine:
    """Calculates structured cabling requirements, rack elevations, and UPS sizing."""

    MAX_PERMANENT_LINK_M = 90.0
    RACK_HEIGHT_U = 42
    STANDARD_UPS_RATINGS_VA = [1000, 1500, 2000, 3000, 5000, 6000, 10000]

    def __init__(self, standard: str = "ANSI/TIA-568-D / ISO/IEC 11801 / SBC 401"):
        self.standard = standard

    def design_system(
        self,
        project_name: str,
        zones: List[TelecomZoneInput],
        spare_ports_margin: float = 0.20,  # 20% spare ports
        ups_autonomy_min: float = 30.0,
    ) -> StructuredCablingDesignResult:
        ws_ports = 0
        wap_ports = 0
        cctv_ports = 0
        acs_ports = 0
        av_ports = 0
        all_compliant = True

        for z in zones:
            if z.max_distance_to_idf_m > self.MAX_PERMANENT_LINK_M:
                all_compliant = False
            ws_ports += z.workstations_count * 2   # 1 Data + 1 Voice per workstation
            wap_ports += z.wap_count * 2           # Dual Cat6A for WiFi 6/7
            cctv_ports += z.cctv_cameras_count * 1 # 1 Cat6A per IP Camera
            acs_ports += z.access_control_doors_count * 1 # 1 RJ45 per ACS controller
            av_ports += z.printers_av_count * 2    # Network printers / smart TVs

        total_active_ports = ws_ports + wap_ports + cctv_ports + acs_ports + av_ports
        spare_ports = math.ceil(total_active_ports * spare_ports_margin)
        total_ports_needed = total_active_ports + spare_ports

        # 24-Port 1U Cat6A Patch Panels sizing
        patch_panels_needed = math.ceil(total_ports_needed / 24.0)
        cable_managers_needed = patch_panels_needed  # 1:1 ratio

        # 48-Port Managed PoE+ Access Switches sizing (each 48-port switch covers 48 ports)
        switches_needed = max(math.ceil(total_active_ports / 48.0), 1)

        # Fiber Backbone: 12-Core OM4 Multi-Mode standard for floor IDF
        fiber_cores = 12
        fiber_type = "12-Core OM4 Laser-Optimized 50/125um MMF"
        fiber_liu_needed = 1

        # Power calculation for Switches: ~450W per 48-port PoE+ switch (switch logic + PoE load)
        total_switch_power_w = switches_needed * 450.0

        # UPS Sizing: Power (W) / 0.8 power factor * 1.25 expansion reserve
        calc_ups_va = (total_switch_power_w / 0.8) * 1.25
        selected_ups_va = next((va for va in self.STANDARD_UPS_RATINGS_VA if va >= calc_ups_va), self.STANDARD_UPS_RATINGS_VA[-1])

        # Rack Equipment Placement (Top to Bottom 42U Allocation)
        rack_items: List[RackItemU] = []
        current_u = 42

        # 1. Fiber Optic Patch Panel (LIU) at very top
        rack_items.append(RackItemU(u_position=current_u, u_height=1, device_name="1U Fiber Optic LIU (12-Core OM4 Duplex LC)", category="FiberLIU", power_watts=0.0))
        current_u -= 1

        # 2. Top Cable Manager
        rack_items.append(RackItemU(u_position=current_u, u_height=1, device_name="1U Horizontal Cable Manager", category="CableManager", power_watts=0.0))
        current_u -= 1

        # 3. Interleaved Patch Panels and Cable Managers
        for p in range(1, patch_panels_needed + 1):
            if current_u < 10:
                break
            rack_items.append(RackItemU(u_position=current_u, u_height=1, device_name=f"1U Cat6A 24-Port Patch Panel (PP-{p:02d})", category="PatchPanel", power_watts=0.0))
            current_u -= 1
            rack_items.append(RackItemU(u_position=current_u, u_height=1, device_name=f"1U Horizontal Cable Manager (HCM-{p:02d})", category="CableManager", power_watts=0.0))
            current_u -= 1

        # 4. Managed PoE Access Switches (with 1U spacers)
        for s in range(1, switches_needed + 1):
            if current_u < 8:
                break
            rack_items.append(RackItemU(u_position=current_u, u_height=1, device_name=f"1U 48-Port Managed PoE+ Gigabit Switch (SW-{s:02d})", category="Switch", power_watts=450.0))
            current_u -= 1
            rack_items.append(RackItemU(u_position=current_u, u_height=1, device_name=f"1U Airflow Spacer / Cable Organizer", category="CableManager", power_watts=0.0))
            current_u -= 1

        # 5. Rackmount UPS at the bottom (heavy weight stability)
        ups_u_height = 2 if selected_ups_va <= 3000 else 3
        rack_items.append(RackItemU(u_position=ups_u_height, u_height=ups_u_height, device_name=f"{ups_u_height}U Online Double-Conversion UPS ({selected_ups_va} VA)", category="UPS", power_watts=total_switch_power_w))

        # 6. PDU: 0U vertical side mounted, with 1U horizontal backup
        rack_items.append(RackItemU(u_position=ups_u_height + 1, u_height=1, device_name="1U Metered Rack PDU (8x C13 Outlets)", category="PDU", power_watts=0.0))

        # Calculate Total U Utilized
        total_u_used = sum(item.u_height for item in rack_items)
        spare_u = max(self.RACK_HEIGHT_U - total_u_used, 0)
        spare_u_pct = round((spare_u / self.RACK_HEIGHT_U) * 100.0, 1)

        total_racks = 1 if total_u_used <= 32 else math.ceil(total_u_used / 28.0)

        notices = [
            f"Permanent Link Limit: Maximum measured run is {max(z.max_distance_to_idf_m for z in zones)}m (ANSI/TIA-568-D limit: 90.0m).",
            "Separation from LV Power: Maintain >= 300mm physical separation from 400V/230V power cables on containment trays.",
            "Fiber Optic Backbone: 12-core OM4 laser-optimized 50/125um terminated with LC duplex ceramic connectors.",
            f"Dedicated Telecom Cooling: Provide continuous 24/7 split unit cooling with heat dissipation of {total_switch_power_w * 3.412:.0f} BTU/hr.",
            "Earthing & Bonding: Ground rack frame to the main building Telecommunications Grounding Busbar (TGB) with 16mm2 green/yellow copper conductor.",
        ]

        return StructuredCablingDesignResult(
            project_name=project_name,
            standard_used=self.standard,
            zones=zones,
            total_workstation_ports=ws_ports,
            total_wap_ports=wap_ports,
            total_cctv_ports=cctv_ports,
            total_acs_ports=acs_ports,
            total_av_ports=av_ports,
            grand_total_horizontal_ports=total_active_ports,
            spare_ports_equipped=spare_ports,
            total_patch_panel_ports=patch_panels_needed * 24,
            patch_panels_24p_count=patch_panels_needed,
            horizontal_cable_managers_count=cable_managers_needed,
            switches_48p_count=switches_needed,
            fiber_liu_count=fiber_liu_needed,
            backbone_fiber_type=fiber_type,
            backbone_fiber_cores=fiber_cores,
            total_42u_racks_count=total_racks,
            rack_items=rack_items,
            total_u_utilized=total_u_used,
            total_u_spare=spare_u,
            spare_u_percentage=spare_u_pct,
            total_switch_poe_power_w=total_switch_power_w,
            recommended_ups_va=selected_ups_va,
            ups_autonomy_minutes=ups_autonomy_min,
            permanent_link_compliant=all_compliant,
            coordination_notices=notices,
        )
