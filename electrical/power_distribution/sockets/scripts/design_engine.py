"""
Deterministic Design Engine for Small Power Sockets & Dedicated Appliance Branch Circuits.
Supports automatic circuit grouping, dedicated appliance feeds, cross-discipline MEP checks,
breaker sizing, cable sizing, and voltage drop compliance.
Supports SBC 401, NEC, and ECP.
Zero mental math, zero hallucination.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from core.coordination.coordinator import coordinator


@dataclass
class SocketGroupRequest:
    room_name: str
    general_socket_count: int
    dedicated_appliances: List[str] = field(default_factory=list)  # e.g. ['refrigerator', 'water_heater', 'room_ac_split']
    farthest_distance_m: float = 25.0


@dataclass
class SizedBranchCircuit:
    circuit_tag: str
    description: str
    total_watts: float
    total_va: float
    outlet_count: int
    breaker_rating_amps: int
    cable_size_sqmm: float
    voltage_drop_pct: float
    is_dedicated: bool
    status: str


@dataclass
class SocketDesignResult:
    total_circuits_count: int
    circuits: List[SizedBranchCircuit]
    total_connected_watts: float
    total_connected_kva: float
    coordination_notices: List[str]
    code_used: str
    overall_status: str
    summary: Dict[str, Any] = field(default_factory=dict)


class SocketCircuitEngine:
    """Computes branch circuits, appliance dedicated feeds, and sizes breakers and cables."""

    STANDARD_VA_PER_SOCKET = 180.0  # NEC/SBC standard

    APPLIANCE_WATTS = {
        "refrigerator": 500.0,
        "microwave": 1500.0,
        "dishwasher": 2000.0,
        "washing_machine": 2000.0,
        "water_heater": 1500.0,
        "room_ac_split": 2500.0,
    }

    def __init__(self, voltage_v: float = 230.0, code: str = "SBC"):
        self.voltage_v = voltage_v
        self.code = code.upper()
        self.max_sockets = 8 if self.code == "NEC" else 10
        self.std_breaker = 20 if self.code == "NEC" else 16
        self.std_cable = 3.31 if self.code == "NEC" else 2.5

    def design_sockets(self, requests: List[SocketGroupRequest]) -> SocketDesignResult:
        circuits: List[SizedBranchCircuit] = []
        c_idx = 1
        coordination_notices: List[str] = []

        all_appliances = []

        for req in requests:
            all_appliances.extend(req.dedicated_appliances)

            # 1. Group general convenience sockets
            remaining_sockets = req.general_socket_count
            grp_num = 1

            while remaining_sockets > 0:
                batch = min(remaining_sockets, self.max_sockets)
                remaining_sockets -= batch

                batch_va = batch * self.STANDARD_VA_PER_SOCKET
                batch_watts = batch_va * 0.85
                ib = batch_va / self.voltage_v

                # Voltage drop over 2.5 mm2 copper (R = 8.87 ohm/km)
                r_total = (8.87 * req.farthest_distance_m) / 1000.0
                vd_v = 2.0 * ib * r_total * 0.85
                vd_pct = round((vd_v / self.voltage_v) * 100.0, 2)

                tag = f"CKT-P{c_idx:02d}"
                c_idx += 1
                desc = f"{req.room_name} General Outlets ({batch} Sockets)"
                circuits.append(
                    SizedBranchCircuit(
                        circuit_tag=tag,
                        description=desc,
                        total_watts=batch_watts,
                        total_va=batch_va,
                        outlet_count=batch,
                        breaker_rating_amps=self.std_breaker,
                        cable_size_sqmm=self.std_cable,
                        voltage_drop_pct=vd_pct,
                        is_dedicated=False,
                        status="SAFE" if vd_pct <= 3.0 else "EXCEEDED_VD",
                    )
                )
                grp_num += 1

            # 2. Add dedicated appliance circuits
            for app in req.dedicated_appliances:
                app_w = self.APPLIANCE_WATTS.get(app.lower(), 1500.0)
                app_va = app_w / 0.85
                ib = app_va / self.voltage_v

                # Sizing breaker: min 16A or 20A
                breaker = 20 if (ib > 13.0 or app.lower() in ("room_ac_split", "dishwasher")) else 16
                cable = 4.0 if breaker > 16 else self.std_cable

                r_per_km = 5.52 if cable == 4.0 else 8.87
                r_total = (r_per_km * req.farthest_distance_m) / 1000.0
                vd_v = 2.0 * ib * r_total * 0.85
                vd_pct = round((vd_v / self.voltage_v) * 100.0, 2)

                tag = f"CKT-P{c_idx:02d}"
                c_idx += 1
                desc = f"{req.room_name} Dedicated: {app.replace('_', ' ').title()}"
                circuits.append(
                    SizedBranchCircuit(
                        circuit_tag=tag,
                        description=desc,
                        total_watts=app_w,
                        total_va=round(app_va, 1),
                        outlet_count=1,
                        breaker_rating_amps=breaker,
                        cable_size_sqmm=cable,
                        voltage_drop_pct=vd_pct,
                        is_dedicated=True,
                        status="SAFE" if vd_pct <= 3.0 else "EXCEEDED_VD",
                    )
                )

        # 3. Cross-Discipline Coordination Check
        if any("ac" in a.lower() for a in all_appliances):
            interfaces = coordinator.query_interfaces("electrical", keywords=["ac", "thermostat"])
            for itm in interfaces:
                coordination_notices.append(f"[{itm['id']}] {itm['title']}: {itm['requirement_for_target']}")

        if any("water_heater" in a.lower() for a in all_appliances):
            interfaces = coordinator.query_interfaces("electrical", keywords=["water heater"])
            for itm in interfaces:
                coordination_notices.append(f"[{itm['id']}] {itm['title']}: {itm['requirement_for_target']}")

        total_watts = sum(c.total_watts for c in circuits)
        total_va = sum(c.total_va for c in circuits)
        all_safe = all(c.status == "SAFE" for c in circuits)

        return SocketDesignResult(
            total_circuits_count=len(circuits),
            circuits=circuits,
            total_connected_watts=round(total_watts, 1),
            total_connected_kva=round(total_va / 1000.0, 2),
            coordination_notices=coordination_notices,
            code_used=self.code,
            overall_status="SAFE" if all_safe else "REVISE",
            summary={
                "circuits_count": len(circuits),
                "total_connected_kw": f"{total_watts/1000.0:.2f} kW",
                "total_connected_kva": f"{total_va/1000.0:.2f} kVA",
                "coordination_alerts": len(coordination_notices),
            },
        )
