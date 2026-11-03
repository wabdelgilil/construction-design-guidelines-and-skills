# Central Uninterruptible Power Supply (UPS) & Battery Plant Sizing Skill

## 1. Scope & Objective
This skill designs the building **Central Uninterruptible Power Supply (UPS)** system, sizing 3-phase true online double-conversion units (VFI-SS-111), static bypass and maintenance bypass interlocks, **IEEE 485 constant-power battery discharge calculations** for specified autonomy durations (15m, 30m, 60m), VRLA / Lithium-ion battery string configuration, and **Battery Room Hydrogen Ventilation** compliance under **IEC 62040-3**, **IEEE 485**, **NFPA 111**, and **SBC 401**.

---

## 2. Engineering Principles & Governing Equations

### 2.1 Critical Load Summation & UPS Rating
1. **Total Critical Connected Load**:
   $$P_{\text{critical}} = \sum P_{i}\ [\text{kW}]$$
   $$S_{\text{critical}} = \sum \frac{P_i}{\text{pf}_i}\ [\text{kVA}]$$
2. **UPS Sizing with Future Expansion**:
   $$S_{\text{UPS}} \ge \frac{S_{\text{critical}} \times 1.25}{\text{Load Factor}}\ [\text{kVA}]$$
   Standard modular ratings: $40, 60, 80, 100, 120, 160, 200, 250, 300, 400, 500\text{ kVA}$.

### 2.2 Constant Power Battery Sizing Method (IEEE 485 / IEEE 1184)
Unlike resistive DC loads, a UPS inverter presents a constant-power load to the battery string. As battery voltage decays from nominal down to end-of-discharge, the current drawn increases inversely:

1. **Total DC Power Required from Battery**:
   $$P_{\text{DC}} = \frac{P_{\text{inverter\_kW}}}{\eta_{\text{inverter}}} = \frac{S_{\text{UPS}} \times \text{pf}_{\text{out}}}{\eta_{\text{inv}}}\ [\text{kW}]$$
   Where $\eta_{\text{inverter}} \approx 0.95$ (95% efficiency for modern IGBT 3-level inverters).
2. **Battery String Cell Count ($N_{\text{cells}}$)**:
   For standard $384\text{V DC}$ bus using $12\text{V}$ monoblocs ($6$ cells/block):
   $$N_{\text{blocks}} = 32\ \text{blocks} \implies N_{\text{cells}} = 32 \times 6 = 192\ \text{cells}$$
3. **End-of-Discharge Voltage ($V_{\text{EOD}}$)**:
   $$V_{\text{EOD\_string}} = N_{\text{cells}} \times 1.67\text{ V/cell} = 192 \times 1.67 = 320.6\text{ V DC}$$
4. **Required Watts per Cell ($W/\text{cell}$)**:
   $$W/\text{cell} = \frac{P_{\text{DC}} \times 1000}{N_{\text{cells}}} \times K_{\text{aging}} \times K_{\text{temp}}$$
   Where:
   - $K_{\text{aging}} = 1.25$ (mandatory IEEE 485 factor for battery end-of-life).
   - $K_{\text{temp}} = 1.0$ at $25^\circ\text{C}$ controlled battery room temperature.
5. **Battery Ampere-Hour ($C_{\text{Ah}}$) Equivalence**:
   $$I_{\text{battery\_max}} = \frac{P_{\text{DC}} \times 1000}{V_{\text{EOD\_string}}}$$
   $$C_{\text{Ah}} = I_{\text{battery\_max}} \times \left( \frac{t_{\text{minutes}}}{60} \right) \times K_{\text{aging}}$$

### 2.3 Battery Room Hydrogen Gas Generation (IEEE 484 / NFPA 1)
During float charging and equalization, lead-acid batteries emit hydrogen gas ($H_2$). To prevent explosive gas pockets:
1. **Maximum Hydrogen Generation Rate**:
   $$Q_{\text{H2}} = N_{\text{cells}} \times I_{\text{float}} \times 0.00045\ [\text{m}^3/\text{hr}]$$
2. **Required Continuous Mechanical Extraction Airflow**:
   $$Q_{\text{vent}} \ge \frac{Q_{\text{H2}}}{0.01} = 100 \times Q_{\text{H2}}\ [\text{m}^3/\text{hr}]$$
   Or minimum **$6\text{ Air Changes per Hour (ACH)}$** with explosion-proof exhaust fans interlocked with $H_2$ gas leak detectors.

---

## 3. Four-Pole Isolation & Bypass Architecture
1. **Static Bypass Switch**:
   - High-speed solid-state thyristor switch providing sub-cycle ($< 4\text{ ms}$) transfer between inverter and raw bypass mains during inverter overloads or faults.
2. **Manual Maintenance Bypass Switch (MBP)**:
   - Make-Before-Break mechanically interlocked rotary/castell-keyed bypass switch allowing complete de-energization and isolation of the UPS for servicing without dropping the critical load.
