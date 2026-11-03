# Automatic Power Factor Correction (APFC) & Detuned Filter Calculation Note

**Project**: {{project_name}}  
**Governing Standard**: {{standard_used}}  
**Operating Voltage & Frequency**: {{nominal_voltage}} V / {{frequency}} Hz  
**Total Selected Bank Capacity**: **{{selected_kvar}} kVAR** ({{step_sequence}})  

---

## 1. Executive Summary & Power Quality Improvements
This calculation note details the sizing of the Automatic Power Factor Correction (APFC) capacitor bank equipped with series iron-core detuned anti-resonance reactors, capacitor cell voltage ratings, contactor AC-6b sizing, and feeder protection under **IEC 61921**, **IEC 60831**, and **IEEE 519**.

### Facility Power Improvement Metrics
- **Active Load ($P$)**: {{active_power_kw}} kW
- **Uncorrected Power Factor ($\cos \phi_1$)**: {{initial_pf}}
- **Target Power Factor ($\cos \phi_2$)**: **{{target_pf}}**
- **Calculated Reactive Deficit ($Q_c$)**: {{calculated_kvar}} kVAR
- **Apparent Power Reduction**: From {{initial_kva}} kVA down to {{corrected_kva}} kVA (**{{released_kva}} kVA Released**)
- **Main Feeder Current Reduction**: **{{current_reduction_a}} A** (Reduces $I^2R$ copper losses and avoids utility low-pf penalties).

---

## 2. Harmonic Detuning & Anti-Resonance Protection
To protect capacitors against catastrophic harmonic resonance caused by non-linear loads:
- **Detuned Reactor Factor ($p\%$)**: **{{detuned_p_percent}}\%** Series Iron-Core Reactor
- **Series Resonance Tuning Frequency**: **{{tuning_frequency_hz}} Hz** (Sits safely below 5th harmonic).
- **Fundamental Voltage Rise across Capacitor**:
  $$V_c = \frac{V_n}{1 - p\%} = \frac{{{nominal_voltage}}}{1 - {{detuned_p_decimal}}} = {{calc_vc}}\text{ V}$$
- **Selected Capacitor Cell Nominal Rating**: **{{cap_rated_voltage}} V AC Heavy-Duty** (Gas-impregnated, self-healing metallized polypropylene).

---

## 3. Modular Step Progression & Switchgear Schedule

| Step No. | Step Rating (kVAR) | Effective (kVAR) | Rated Voltage | Nominal Current (A) | Design Current (A) | Contactor Type | Contactor Rating (A) | Step Breaker (A) | Reactor Inductance (mH) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{{step_table_rows}}

---

## 4. APFC Switchboard Incomer & Busbar Sizing
Under IEC 61921, the incoming protection device and internal busbars must accommodate continuous harmonic currents ($+30\%$) and manufacturing capacitance tolerance ($+10\%$):

$$I_{\text{design}} \ge 1.43 \times I_{\text{nominal}} = 1.43 \times {{total_nominal_a}}\text{ A} = {{total_design_a}}\text{ A}$$

- **Selected Incomer Breaker**: **{{incomer_mccb}} A 4-Pole MCCB (Category A, $I_{cu} \ge 36\text{ kA}$)**
- **Main Busbar Sizing**: {{incomer_mccb}} A Tinned Copper Busbar.

---

## 5. Engineering Coordination & Commissioning Checklist
{{coordination_checklist}}
