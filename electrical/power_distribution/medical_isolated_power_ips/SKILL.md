# Medical Isolated Power System (IPS / Medical IT) Design Skill

## 1. Scope & Objective
Automates the engineering design of **Group 2 Medical Location Isolated Power Systems (IPS / Medical IT System)** for Hospital Operating Theaters, Cardiac Catheterization Labs, and Intensive Care Units (ICUs) per **IEC 60364-7-710**, **NFPA 99**, and **SBC 401**.

---

## 2. Fundamental Engineering Principles
In Group 2 medical locations, the continuity of electrical power to life-support medical equipment is vital. A first insulation fault must NOT cause automatic disconnection of power.

1. **Unbonded Secondary (IT System)**: The secondary winding of the medical isolation transformer is completely ungrounded (floating relative to earth).
2. **First Fault Non-Tripping**: If an active conductor experiences an insulation fault to ground, no high fault loop current exists; the circuit continues operating safely while the **Insulation Monitoring Device (IMD)** raises audible and visual alarms at $R_F \le 50\text{ k}\Omega$.
3. **Double-Pole Protection**: Because neither secondary line is grounded (no neutral), both conductors are considered active and must be switched simultaneously by 2-Pole (DP) circuit breakers.
4. **Leakage Current Minimization**: Total system capacitive leakage to ground is restricted ($< 0.5\text{ mA}$) by limiting cable lengths ($\le 25\text{ m}$) and using low-capacitance shielded wiring.
5. **Supplementary Equipotential Bonding (POAG)**: All exposed conductive parts within the patient environment (radius of 1.5 m around table) must be bonded to a central Equal Potential Grounding Busbar (EPG / POAG) with resistance $R \le 0.1\ \Omega$.

---

## 3. Mathematical Formulations

### 3.1 Transformer Sizing
$$S_{\text{load}} = \sum P_{\text{equipment}} \times DF \quad (\text{kVA})$$
Select standard medical transformer $S_n \in [3.15, 4.0, 5.0, 6.3, 8.0, 10.0]\text{ kVA}$ such that:
$$S_n \ge 1.20 \times S_{\text{load}}$$

### 3.2 Maximum First Fault Current
$$I_{f1} = \frac{U_0}{Z_{\text{IT}}} \approx \frac{230\text{ V}}{R_{\text{IMD}} \parallel X_C} < 5.0\text{ mA}$$

### 3.3 Touch Voltage & Bonding Resistance
$$U_{\text{touch}} = I_{f1} \times R_{\text{bonding}} \le 0.005\text{ A} \times 0.1\ \Omega = 0.5\text{ mV} \ll 10\text{ mV allowed}$$

---

## 4. Multi-Deliverables
- **Calculation Note**: `output/hospital_ips/OR_IPS_calculation_note.md`
- **AutoCAD DXF SLD**: `output/hospital_ips/OR_IPS_single_line_diagram.dxf`
- **Excel Schedule**: `output/hospital_ips/OR_IPS_panel_schedule.xlsx`
