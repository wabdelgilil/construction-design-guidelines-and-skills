"""
Bill of Quantities (BOQ) & Bar Bending Schedule (BBS) Core Engine.
Computes deterministic material take-offs, steel weights, and cost estimations.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List


def rebar_weight_per_meter(diameter_mm: float) -> float:
    """Calculates linear weight of steel rebar in kg/m (D^2 / 162)."""
    return (diameter_mm**2) / 162.0


@dataclass
class BarScheduleItem:
    bar_mark: str
    description: str
    bar_diameter_mm: int
    number_of_bars: int
    cutting_length_m: float
    shape_code: str  # e.g., "00" (Straight), "21" (U-shape / with hooks)
    total_length_m: float = 0.0
    total_weight_kg: float = 0.0

    def __post_init__(self):
        self.total_length_m = round(self.number_of_bars * self.cutting_length_m, 2)
        weight_per_m = rebar_weight_per_meter(self.bar_diameter_mm)
        self.total_weight_kg = round(self.total_length_m * weight_per_m, 2)


@dataclass
class BOQItem:
    item_no: int
    description: str
    unit: str  # m3, m2, ton, etc.
    quantity: float
    unit_rate: float
    currency: str = "SAR"
    total_amount: float = 0.0

    def __post_init__(self):
        self.total_amount = round(self.quantity * self.unit_rate, 2)


class BOQEngine:
    """Calculates comprehensive civil material take-offs and cost estimations."""

    # Default commercial unit rates (Saudi Market Baseline in SAR)
    DEFAULT_RATES_SAR = {
        "excavation_m3": 25.0,
        "backfill_m3": 20.0,
        "blinding_concrete_m3": 240.0,
        "rc_concrete_m3": 320.0,
        "formwork_m2": 45.0,
        "steel_rebar_ton": 3200.0,
        "bitumen_insulation_m2": 18.0,
    }

    @staticmethod
    def calculate_footing_boq(
        length_m: float,
        width_m: float,
        thickness_m: float,
        blinding_thickness_m: float = 0.10,
        blinding_offset_m: float = 0.10,
        excavation_depth_m: float = 1.80,
        currency: str = "SAR",
        custom_rates: Dict[str, float] = None,
    ) -> Dict[str, Any]:
        """Calculates material quantities and cost for a single footing excavation, concrete, and forms."""
        rates = dict(BOQEngine.DEFAULT_RATES_SAR)
        if custom_rates:
            rates.update(custom_rates)

        # 1. Plain Concrete (Blinding)
        pc_l = length_m + 2 * blinding_offset_m
        pc_w = width_m + 2 * blinding_offset_m
        vol_pc = pc_l * pc_w * blinding_thickness_m

        # 2. Reinforced Concrete
        vol_rc = length_m * width_m * thickness_m

        # 3. Formwork Area
        formwork_area = 2 * (length_m + width_m) * thickness_m

        # 4. Bitumen Insulation Area (top of footing + 4 vertical sides)
        insulation_area = (length_m * width_m) + formwork_area

        # 5. Excavation Volume (with 0.5m working space)
        exc_l = pc_l + 1.0
        exc_w = pc_w + 1.0
        vol_excavation = exc_l * exc_w * excavation_depth_m

        # 6. Backfill Volume
        vol_backfill = max(vol_excavation - (vol_pc + vol_rc), 0.0)

        return {
            "blinding_concrete_m3": round(vol_pc, 2),
            "reinforced_concrete_m3": round(vol_rc, 2),
            "formwork_area_m2": round(formwork_area, 2),
            "insulation_area_m2": round(insulation_area, 2),
            "excavation_m3": round(vol_excavation, 2),
            "backfill_m3": round(vol_backfill, 2),
            "rates_used": rates,
            "currency": currency,
        }
