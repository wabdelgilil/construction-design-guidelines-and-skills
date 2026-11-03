"""Central Uninterruptible Power Supply (UPS) & DC Battery Plant Design Engine.

Governing Standards:
- IEC 62040-3: Uninterruptible power systems (UPS) - Method of specifying the performance and test requirements
- IEEE 485: Recommended Practice for Sizing Lead-Acid Batteries for Stationary Applications
- IEEE 1184: Guide for the Selection and Sizing of Batteries for UPS Systems
- NFPA 111: Standard on Stored Electrical Energy Emergency and Standby Power Systems
- SBC 401 / NEC Article 645 / Article 708: Critical Operations Power Systems
"""

import math
from typing import Dict, Any, List


class CentralUPSDesignEngine:
    """Calculates Central UPS rating, battery bank sizing (constant-power IEEE 485),
    breaker ratings, cable sizing, and battery room hydrogen ventilation."""

    STANDARD_UPS_KVA_RATINGS = [
        10, 20, 30, 40, 60, 80, 100, 120, 160, 200, 250, 300, 400, 500, 600, 800, 1000
    ]

    def __init__(self, code_standard: str = "SBC"):
        self.code_standard = code_standard
        if code_standard == "NEC":
            self.nominal_voltage_ac = 480.0
            self.frequency_hz = 60.0
            self.inverter_eff = 0.95
            self.nominal_dc_bus_v = 480.0
        elif code_standard == "ECP":
            self.nominal_voltage_ac = 380.0
            self.frequency_hz = 50.0
            self.inverter_eff = 0.94
            self.nominal_dc_bus_v = 384.0
        else:  # SBC / IEC default
            self.nominal_voltage_ac = 400.0
            self.frequency_hz = 60.0
            self.inverter_eff = 0.95
            self.nominal_dc_bus_v = 384.0

        self.cell_nominal_v = 2.0
        self.cell_eod_v = 1.67
        self.cells_per_12v_block = 6
        self.aging_factor = 1.25  # IEEE 485 recommended (80% EOL capacity)
        self.temp_derate_factor = 1.0  # At 25 deg C design temperature
        self.design_margin = 1.10  # 10% design margin

    def size_ups_system(
        self,
        loads: List[Dict[str, Any]],
        backup_time_min: float = 30.0,
        redundancy_type: str = "N+1",
        future_growth_margin: float = 0.20,
        room_dimensions_m: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """Sizes UPS modules, battery plant, breakers, cables, and battery room ventilation.

        loads format:
        [
          {"id": "SRV-01", "name": "Data Center Server Racks", "load_kw": 80.0, "pf": 0.90},
          {"id": "NET-01", "name": "Core Network Switches & SAN", "load_kw": 25.0, "pf": 0.85},
          {"id": "BMS-01", "name": "BMS & Security Operations Center", "load_kw": 15.0, "pf": 0.80}
        ]
        """
        if not loads:
            raise ValueError("Load list cannot be empty.")

        # 1. Connected & Design Load
        total_connected_kw = sum(load["load_kw"] for load in loads)
        total_connected_kvar = sum(
            load["load_kw"] * math.tan(math.acos(load.get("pf", 0.90))) for load in loads
        )
        total_connected_kva = math.sqrt(total_connected_kw**2 + total_connected_kvar**2)
        overall_pf = total_connected_kw / total_connected_kva if total_connected_kva > 0 else 0.90

        # Design Load with Future Growth
        design_load_kw = total_connected_kw * (1.0 + future_growth_margin)
        design_load_kva = design_load_kw / overall_pf

        # 2. Select UPS Module Size and Count
        # If N+1, size modules such that N modules carry design load
        selected_module_kva = None
        for std_kva in self.STANDARD_UPS_KVA_RATINGS:
            if std_kva >= design_load_kva:
                selected_module_kva = std_kva
                break
        if selected_module_kva is None:
            selected_module_kva = self.STANDARD_UPS_KVA_RATINGS[-1]

        if redundancy_type == "N+1":
            n_modules = math.ceil(design_load_kva / (selected_module_kva * 0.80))
            if n_modules < 1:
                n_modules = 1
            total_modules = n_modules + 1
            total_system_kva = total_modules * selected_module_kva
        elif redundancy_type == "2N":
            n_modules = 1
            total_modules = 2
            total_system_kva = 2 * selected_module_kva
        else:  # 'N' standalone
            n_modules = 1
            total_modules = 1
            total_system_kva = selected_module_kva

        # Output current per module and system at full rating
        sqrt3 = math.sqrt(3)
        module_flc_ac = (selected_module_kva * 1000.0) / (sqrt3 * self.nominal_voltage_ac)
        system_flc_ac = (total_system_kva * 1000.0) / (sqrt3 * self.nominal_voltage_ac)

        # 3. Battery Bank Constant-Power Sizing (IEEE 485 / IEEE 1184)
        # Total DC power needed at inverter input
        # P_dc = P_kw / eta_inv
        dc_power_kw = design_load_kw / self.inverter_eff
        dc_power_w = dc_power_kw * 1000.0

        # Number of cells in series
        # Standard 384V DC bus uses 192 cells (32 blocks of 12V VRLA)
        # Standard 480V DC bus uses 240 cells (40 blocks of 12V VRLA)
        total_cells = int(round(self.nominal_dc_bus_v / self.cell_nominal_v))
        total_12v_blocks_per_string = total_cells // self.cells_per_12v_block

        # Required Watts per Cell:
        # W_per_cell = (P_dc * Aging * DesignMargin) / (total_cells * TempDerate)
        total_design_dc_watts = dc_power_w * self.aging_factor * self.design_margin / self.temp_derate_factor
        req_watts_per_cell = total_design_dc_watts / total_cells

        # End of discharge minimum DC bus voltage
        min_dc_bus_voltage = total_cells * self.cell_eod_v

        # Maximum DC discharge current at end of discharge:
        # I_dc_max = P_dc / V_min
        i_dc_max = (dc_power_w * self.design_margin) / min_dc_bus_voltage

        # Battery Ampere-Hour (Ah) Estimate:
        # For typical VRLA discharging in backup_time_min:
        # Peukert factor and empirical C-rate approximation:
        # Ah ~ (I_dc_max * (backup_time_min / 60)) * K_rate
        # For 15 min: C_15 ~ 0.55 * C_10 -> K_rate ~ 1.8
        # For 30 min: C_30 ~ 0.70 * C_10 -> K_rate ~ 1.45
        # For 60 min: C_60 ~ 0.85 * C_10 -> K_rate ~ 1.2
        if backup_time_min <= 15.0:
            k_rate = 1.80
        elif backup_time_min <= 30.0:
            k_rate = 1.45
        elif backup_time_min <= 60.0:
            k_rate = 1.20
        else:
            k_rate = 1.05

        calc_ah = (i_dc_max * (backup_time_min / 60.0)) * k_rate * self.aging_factor
        # Select standard VRLA block capacity (12V monoblocs: 65, 100, 120, 150, 200, 250 Ah)
        standard_block_ah = [65, 100, 120, 150, 200, 250]
        selected_block_ah = None
        num_parallel_strings = 1
        for ah in standard_block_ah:
            if ah >= calc_ah:
                selected_block_ah = ah
                num_parallel_strings = 1
                break
        if selected_block_ah is None:
            # Need parallel strings
            for ah in reversed(standard_block_ah):
                strings = math.ceil(calc_ah / ah)
                if strings <= 4:
                    num_parallel_strings = strings
                    selected_block_ah = ah
                    break
            if selected_block_ah is None:
                selected_block_ah = 200
                num_parallel_strings = math.ceil(calc_ah / 200)

        total_battery_blocks = total_12v_blocks_per_string * num_parallel_strings
        actual_installed_ah = selected_block_ah * num_parallel_strings

        # 4. Protection & Cable Sizing
        # Input AC Breaker (Rectifier input + battery recharge capacity ~ 1.25 * FLC)
        input_breaker_rating_a = self._select_standard_breaker(module_flc_ac * 1.25)
        output_breaker_rating_a = self._select_standard_breaker(module_flc_ac * 1.15)
        bypass_breaker_rating_a = self._select_standard_breaker(module_flc_ac * 1.25)
        battery_dc_breaker_rating_a = self._select_standard_breaker(i_dc_max * 1.25)

        # 5. Battery Room Hydrogen Ventilation (IEEE 484 / NFPA 1 / SBC 401)
        # During float/boost charge, lead-acid batteries emit hydrogen:
        # Max H2 generated: Q_H2 = N_cells * I_charge_float * 0.00045 m3/h per cell (IEEE 484)
        # Float charge current approx 0.002 x C10 Ah, Boost charge ~ 0.01 x C10 Ah
        if room_dimensions_m is None:
            room_dimensions_m = {"length": 6.0, "width": 4.0, "height": 3.2}

        room_volume_m3 = (
            room_dimensions_m.get("length", 6.0)
            * room_dimensions_m.get("width", 4.0)
            * room_dimensions_m.get("height", 3.2)
        )
        total_cells_all_strings = total_cells * num_parallel_strings
        boost_charge_current_a = 0.01 * selected_block_ah
        h2_generation_m3_per_hr = total_cells_all_strings * boost_charge_current_a * 0.00045

        # Ventilation rate to keep H2 concentration <= 1% (NFPA 1 / SBC 401 limit is 1%, safety margin 25% of LFL 4%)
        # Q_vent = (Q_H2 / 0.01) = 100 * Q_H2
        req_vent_rate_h2_m3_per_hr = h2_generation_m3_per_hr * 100.0
        # Code minimum air change rate (typically 6 ACH for dedicated battery rooms)
        req_vent_rate_ach_m3_per_hr = room_volume_m3 * 6.0
        design_exhaust_airflow_m3_per_hr = max(req_vent_rate_h2_m3_per_hr, req_vent_rate_ach_m3_per_hr)
        design_exhaust_airflow_cfm = design_exhaust_airflow_m3_per_hr / 1.699

        return {
            "code_standard": self.code_standard,
            "nominal_voltage_ac": self.nominal_voltage_ac,
            "frequency_hz": self.frequency_hz,
            "backup_time_min": backup_time_min,
            "redundancy_type": redundancy_type,
            "loads_summary": {
                "total_connected_kw": round(total_connected_kw, 2),
                "total_connected_kva": round(total_connected_kva, 2),
                "overall_pf": round(overall_pf, 3),
                "design_load_kw": round(design_load_kw, 2),
                "design_load_kva": round(design_load_kva, 2),
            },
            "ups_module": {
                "selected_module_kva": selected_module_kva,
                "n_modules": n_modules,
                "total_modules": total_modules,
                "total_system_kva": total_system_kva,
                "module_flc_ac": round(module_flc_ac, 1),
                "system_flc_ac": round(system_flc_ac, 1),
                "inverter_efficiency": self.inverter_eff,
            },
            "battery_plant": {
                "nominal_dc_bus_v": self.nominal_dc_bus_v,
                "total_cells": total_cells,
                "cells_per_12v_block": self.cells_per_12v_block,
                "blocks_per_string": total_12v_blocks_per_string,
                "num_parallel_strings": num_parallel_strings,
                "total_battery_blocks": total_battery_blocks,
                "cell_eod_v": self.cell_eod_v,
                "min_dc_bus_voltage": round(min_dc_bus_voltage, 1),
                "dc_power_kw": round(dc_power_kw, 2),
                "total_design_dc_watts": round(total_design_dc_watts, 2),
                "req_watts_per_cell": round(req_watts_per_cell, 2),
                "i_dc_max": round(i_dc_max, 1),
                "calc_ah": round(calc_ah, 1),
                "selected_block_ah": selected_block_ah,
                "actual_installed_ah": actual_installed_ah,
                "aging_factor": self.aging_factor,
            },
            "breakers": {
                "rectifier_input_breaker_a": input_breaker_rating_a,
                "inverter_output_breaker_a": output_breaker_rating_a,
                "static_bypass_breaker_a": bypass_breaker_rating_a,
                "battery_dc_breaker_a": battery_dc_breaker_rating_a,
            },
            "ventilation": {
                "room_volume_m3": round(room_volume_m3, 2),
                "h2_generation_m3_per_hr": round(h2_generation_m3_per_hr, 4),
                "req_vent_rate_h2_m3_per_hr": round(req_vent_rate_h2_m3_per_hr, 1),
                "req_vent_rate_ach_m3_per_hr": round(req_vent_rate_ach_m3_per_hr, 1),
                "design_exhaust_airflow_m3_per_hr": round(design_exhaust_airflow_m3_per_hr, 1),
                "design_exhaust_airflow_cfm": round(design_exhaust_airflow_cfm, 1),
            },
            "loads_detail": loads
        }

    @staticmethod
    def _select_standard_breaker(calc_amps: float) -> int:
        standard_breakers = [
            16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400,
            500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000
        ]
        for b in standard_breakers:
            if b >= calc_amps:
                return b
        return standard_breakers[-1]
