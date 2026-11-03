# Central Uninterruptible Power Supply (UPS) & DC Battery Plant Design Calculation Note

**Project**: {{ project_name }}  
**Discipline**: Electrical Power Distribution / Critical Systems  
**Governing Standards**: IEC 62040-3, IEEE 485, IEEE 1184, NFPA 111, SBC 401 / NEC 645  
**Code Standard**: {{ code_standard }}  
**System Voltage**: {{ nominal_voltage_ac }} V AC, 3-Phase, {{ frequency_hz }} Hz  
**Nominal DC Bus**: {{ battery_plant.nominal_dc_bus_v }} V DC  

---

## 1. Executive Summary & Design Scope

The Central UPS and Battery System provides reliable, conditioned, continuous uninterruptible AC power to mission-critical infrastructure, preventing outages, frequency fluctuations, and micro-interruptions. The system configuration is **True Online Double Conversion (VFI-SS-111)** with redundant topology (**{{ redundancy_type }}**).

### Key Sizing Summary:
- **Connected Load**: {{ loads_summary.total_connected_kw }} kW ({{ loads_summary.total_connected_kva }} kVA @ PF {{ loads_summary.overall_pf }})
- **Design Load (with growth margin)**: {{ loads_summary.design_load_kw }} kW / {{ loads_summary.design_load_kva }} kVA
- **Selected UPS Architecture**: {{ ups_module.total_modules }} x {{ ups_module.selected_module_kva }} kVA Modules (Total System Capacity: **{{ ups_module.total_system_kva }} kVA**)
- **Battery Autonomy / Backup Time**: **{{ backup_time_min }} Minutes** at full design load
- **Installed Battery Plant**: {{ battery_plant.num_parallel_strings }} String(s) of {{ battery_plant.blocks_per_string }} x 12V VRLA Blocks (**{{ battery_plant.total_battery_blocks }} Blocks total**), Rated **{{ battery_plant.actual_installed_ah }} Ah @ 12V**

---

## 2. Inverter DC Power & Battery Sizing Formulation (IEEE 485 / IEEE 1184)

The battery bank is sized based on constant power discharge characteristics required by the solid-state PWM inverter:

$$P_{DC} = \frac{P_{Load, kW}}{\eta_{inv}} = \frac{ {{ loads_summary.design_load_kw }} }{ {{ ups_module.inverter_efficiency }} } = {{ battery_plant.dc_power_kw }} \text{ kW}$$

Applying the IEEE 485 recommended aging factor ($k_{aging} = {{ battery_plant.aging_factor }}$) and design margin:

$$P_{DC, design} = P_{DC} \times k_{aging} \times k_{margin} = {{ battery_plant.total_design_dc_watts }} \text{ Watts}$$

For a string of $N_{cells} = {{ battery_plant.total_cells }}$ cells ($V_{nominal} = 2.0\text{ V/cell}$, End-of-Discharge $V_{EOD} = {{ battery_plant.cell_eod_v }}\text{ V/cell}$):

$$W_{per\_cell} = \frac{P_{DC, design}}{N_{cells}} = \frac{ {{ battery_plant.total_design_dc_watts }} }{ {{ battery_plant.total_cells }} } = {{ battery_plant.req_watts_per_cell }} \text{ Watts/cell}$$

At the End-of-Discharge voltage ($V_{min} = N_{cells} \times V_{EOD} = {{ battery_plant.min_dc_bus_voltage }}\text{ V}$), the maximum continuous discharge current is:

$$I_{DC, max} = \frac{P_{DC, design}}{V_{min}} = \frac{ {{ battery_plant.total_design_dc_watts }} }{ {{ battery_plant.min_dc_bus_voltage }} } = {{ battery_plant.i_dc_max }} \text{ A}$$

The calculated capacity requirement for {{ backup_time_min }} minutes backup yields **{{ battery_plant.calc_ah }} Ah**, fulfilled by installing **{{ battery_plant.actual_installed_ah }} Ah** across {{ battery_plant.num_parallel_strings }} parallel string(s).

---

## 3. Switchgear & Protection Coordination

| Location | Breaker Type | Sizing Basis | Nominal Rating (A) |
|---|---|---|---|
| Rectifier Input | 3P MCCB / ACB | $1.25 \times I_{FLC, in}$ (Full load + battery charge) | **{{ breakers.rectifier_input_breaker_a }} A** |
| Inverter Output | 3P MCCB / ACB | $1.15 \times I_{FLC, out}$ | **{{ breakers.inverter_output_breaker_a }} A** |
| Static Bypass | 3P MCCB / ACB | $1.25 \times I_{FLC, out}$ (Overload capability) | **{{ breakers.static_bypass_breaker_a }} A** |
| Battery DC Isolator | 2P DC MCCB (with Shunt Trip) | $1.25 \times I_{DC, max}$ | **{{ breakers.battery_dc_breaker_a }} A** |

---

## 4. Battery Room Hydrogen Ventilation (IEEE 484 / NFPA 1)

During battery float and equalization charging, electrolysis produces hydrogen gas. To maintain $H_2$ concentration safely below 1.0% by volume (25% of the lower explosive limit LFL of 4.0%):

- **Room Volume**: {{ ventilation.room_volume_m3 }} $\text{m}^3$
- **Hydrogen Generation Rate ($Q_{H2}$)**: {{ ventilation.h2_generation_m3_per_hr }} $\text{m}^3/\text{h}$
- **Ventilation for $H_2$ Dilution**: {{ ventilation.req_vent_rate_h2_m3_per_hr }} $\text{m}^3/\text{h}$
- **Ventilation for Code Minimum (6 ACH)**: {{ ventilation.req_vent_rate_ach_m3_per_hr }} $\text{m}^3/\text{h}$
- **Design Dedicated Spark-Proof Exhaust Fan Capacity**: **{{ ventilation.design_exhaust_airflow_m3_per_hr }} $\text{m}^3/\text{h}$ ({{ ventilation.design_exhaust_airflow_cfm }} CFM)**

---

## 5. Connected Load Breakdown

| Tag | Equipment Description | Connected Load (kW) | Power Factor | Demand Load (kVA) |
|---|---|---|---|---|
{% for load in loads_detail %}
| {{ load.id }} | {{ load.name }} | {{ load.load_kw }} kW | {{ load.pf }} | {{ "%.1f"|format(load.load_kw / load.pf) }} kVA |
{% endfor %}

---
*Generated by Antigravity Construction Design Engine - Electrical Central UPS Sizing Skill*
