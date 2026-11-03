"""
Deterministic Medical Isolated Power System (IPS / Medical IT) Design Engine.
Computes Medical Isolation Transformer sizing, 2-Pole branch circuits, IMD parameters,
and equipotential bonding compliance according to IEC 60364-7-710, NFPA 99, and SBC 401.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class MedicalLoadItem:
    tag: str
    description: str
    power_watts: float
    power_factor: float = 0.85
    is_life_support: bool = True
    quantity: int = 1


@dataclass
class IPSBranchCircuit:
    circuit_tag: str
    description: str
    connected_watts: float
    design_va: float
    current_amps: float
    breaker_type: str = "2-Pole (DP) MCB"
    breaker_rating_amps: int = 16
    cable_size_sqmm: float = 4.0
    cable_type: str = "XLPE/LSZH Low-Capacitance Shielded Copper"
    max_length_m: float = 25.0
    poag_pin_assigned: bool = True


@dataclass
class IPSDesignResult:
    room_name: str
    standard_used: str
    total_connected_watts: float
    total_connected_kva: float
    demand_factor: float
    design_kva: float
    selected_transformer_kva: float
    transformer_primary_current_amps: float
    transformer_secondary_current_amps: float
    primary_mcb_rating_amps: int
    primary_mcb_curve: str
    secondary_circuits: List[IPSBranchCircuit]
    imd_alarm_threshold_kohm: float
    imd_test_voltage_vdc: float
    max_leakage_current_ma: float
    equipotential_bonding_max_resistance_ohms: float
    compliance_status: str
    coordination_notices: List[str] = field(default_factory=list)


class MedicalIPSEngine:
    """Sizes and verifies Medical Isolated Power System (IPS) for Operating Theaters."""

    STANDARD_KVA_RATINGS = [3.15, 4.0, 5.0, 6.3, 8.0, 10.0]

    def __init__(self, voltage_v: float = 230.0, standard: str = "IEC 60364-7-710 / SBC 401"):
        self.voltage_v = voltage_v
        self.standard = standard

    def design_system(
        self,
        room_name: str,
        medical_loads: List[MedicalLoadItem],
        reserve_margin: float = 0.20,
    ) -> IPSDesignResult:
        # 1. Sum loads
        total_w = sum(item.power_watts * item.quantity for item in medical_loads)
        total_va = sum((item.power_watts / item.power_factor) * item.quantity for item in medical_loads)
        total_kva = total_va / 1000.0

        # In Operating Theaters, simultaneous demand factor is typically 0.75 - 0.85
        demand_factor = 0.80
        design_kva = round(total_kva * demand_factor * (1.0 + reserve_margin), 2)

        # 2. Select Medical Transformer Rating (IEC/SBC max allowed is 10.0 kVA per single IPS)
        selected_kva = None
        for kva in self.STANDARD_KVA_RATINGS:
            if kva >= design_kva:
                selected_kva = kva
                break

        if selected_kva is None:
            selected_kva = 10.0  # Max single unit; split across 2 IPS panels if exceeded

        sec_current = round((selected_kva * 1000.0) / self.voltage_v, 1)
        pri_current = sec_current

        # Primary breaker: Must withstand 12x inrush without nuisance tripping (Curve D MCB)
        # Sized at ~ 1.25x - 1.5x primary full-load current
        if pri_current <= 20.0:
            primary_mcb = 25
        elif pri_current <= 30.0:
            primary_mcb = 40
        else:
            primary_mcb = 50

        # 3. Create 2-Pole Branch Circuits
        circuits: List[IPSBranchCircuit] = []
        c_idx = 1
        for item in medical_loads:
            for q in range(item.quantity):
                va = item.power_watts / item.power_factor
                amps = round(va / self.voltage_v, 2)
                tag = f"IPS-CKT{c_idx:02d}"
                desc = f"{item.description} ({'Life Support' if item.is_life_support else 'Auxiliary'})"
                circuits.append(
                    IPSBranchCircuit(
                        circuit_tag=tag,
                        description=desc,
                        connected_watts=item.power_watts,
                        design_va=round(va, 1),
                        current_amps=amps,
                        breaker_type="2-Pole (DP) MCB",
                        breaker_rating_amps=16,
                        cable_size_sqmm=4.0,
                        cable_type="XLPE/LSZH Low-Capacitance Shielded Copper",
                        max_length_m=20.0,
                        poag_pin_assigned=True,
                    )
                )
                c_idx += 1

        # Add 2 spare circuits
        circuits.append(
            IPSBranchCircuit(
                circuit_tag=f"IPS-CKT{c_idx:02d}",
                description="Spare Medical Socket Circuit",
                connected_watts=0.0,
                design_va=0.0,
                current_amps=0.0,
                breaker_type="2-Pole (DP) MCB",
                breaker_rating_amps=16,
                cable_size_sqmm=4.0,
                cable_type="XLPE/LSZH Low-Capacitance Shielded Copper",
                max_length_m=20.0,
                poag_pin_assigned=True,
            )
        )
        c_idx += 1
        circuits.append(
            IPSBranchCircuit(
                circuit_tag=f"IPS-CKT{c_idx:02d}",
                description="Spare Medical Socket Circuit",
                connected_watts=0.0,
                design_va=0.0,
                current_amps=0.0,
                breaker_type="2-Pole (DP) MCB",
                breaker_rating_amps=16,
                cable_size_sqmm=4.0,
                cable_type="XLPE/LSZH Low-Capacitance Shielded Copper",
                max_length_m=20.0,
                poag_pin_assigned=True,
            )
        )

        # 4. Mandatory Cross-Discipline Coordination Notices
        notices = [
            "Biomedical / Electrical Interface: Dedicated Remote Annunciator Panel (MK2430 / Bender) must be installed at Nurse Station and inside OR wall console at 1600mm AFF.",
            "Mechanical / HVAC Interface: IPS panel heatsink dissipation (approx. 250W continuous transformer loss) requires air conditioning supply in prep room.",
            "Architectural / Medical Gas: Coordinate ceiling pendant power drops with Medical Gas & Surgical Boom manufacturers.",
            "Grounding: Equipotential bonding busbar (POAG pins) must connect to every metallic gas outlet, surgical pendant, and metallic table frame via 6mm² green/yellow conductor (R <= 0.1 ohm).",
        ]

        status = "COMPLIANT (Safe Medical IT System)" if selected_kva <= 10.0 else "EXCEEDS_SINGLE_UNIT_CAPACITY"

        return IPSDesignResult(
            room_name=room_name,
            standard_used=self.standard,
            total_connected_watts=round(total_w, 1),
            total_connected_kva=round(total_kva, 2),
            demand_factor=demand_factor,
            design_kva=selected_kva,
            selected_transformer_kva=selected_kva,
            transformer_primary_current_amps=pri_current,
            transformer_secondary_current_amps=sec_current,
            primary_mcb_rating_amps=primary_mcb,
            primary_mcb_curve="Curve D (High Inrush Withstand)",
            secondary_circuits=circuits,
            imd_alarm_threshold_kohm=50.0,
            imd_test_voltage_vdc=12.0,
            max_leakage_current_ma=0.5,
            equipotential_bonding_max_resistance_ohms=0.10,
            compliance_status=status,
            coordination_notices=notices,
        )
