# Short-Circuit Calculation & Protection Discrimination (TCC Curves) Note

**Project**: {{project_name}}  
**Governing Standard**: {{standard_used}}  
**Transformer Capacity**: {{transformer_rating_kva}} kVA ({{voltage_secondary}} V / $u_k = {{uk_percent}}\%$)  
**System Discrimination Status**: **{{overall_system_discrimination}}**  

---

## 1. Executive Summary & Protection Strategy
This engineering document establishes the prospective symmetrical short-circuit currents across the distribution network hierarchy (MDB $\to$ SMDB $\to$ DB) using the **Impedance Method (IEC 60909)**, verifies switchgear breaking and withstand capacities, configures **LSIG** trip units, and evaluates **Time-Current Characteristic (TCC)** discrimination margins under **IEEE 242** and **SBC 401**.

---

## 2. Low-Voltage Network Impedances & Fault Levels (IEC 60909)

The three-phase symmetrical fault current at each bus $k$ is given by:

$$I_{sc3\phi} = \frac{c_{\max} \cdot V_{LL}}{\sqrt{3} \cdot Z_k} = \frac{1.05 \times {{voltage_secondary}}\text{ V}}{\sqrt{3} \times \sqrt{R_k^2 + X_k^2}}$$

| Bus Name | Hierarchy Level | $R$ ($m\Omega$) | $X$ ($m\Omega$) | $Z$ ($m\Omega$) | Prospective $I_{sc}$ (kA) | Selected Switchgear | $I_n$ (A) | $I_{cu}$ (kA) | Safety Margin |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{{bus_table_rows}}

---

## 3. Switchgear Breaker Selection & LSIG Trip Settings

### 3.1 Main Switchboard Incomer ACB (Level 1)
- **Breaker Frame**: 4-Pole Drawout Air Circuit Breaker (Category B)
- **Rated Ultimate Breaking Capacity ($I_{cu}$)**: **{{acb_icu}} kA** ($I_{cs} = 100\% \cdot I_{cu}$)
- **Short-Time Withstand ($I_{cw}, 1\text{s}$)**: **{{acb_icw}} kA** $\ge I_{sc,MDB}$ (Allows intentional time grading without contact parting)
- **Trip Unit Configuration (LSIG)**:
  - **L (Long Time)**: $I_r = 1.0 \times I_n = {{acb_in}}\text{ A}$, $t_r = 12.0\text{ s}$
  - **S (Short Time)**: $I_{sd} = 4.0 \times I_r = {{acb_isd}}\text{ A}$, $t_{sd} = 0.30\text{ s}$ (Flat Definite Time)
  - **I (Instantaneous)**: **OFF** (Disabled to guarantee full selectivity up to $I_{cw}$)
  - **G (Ground Fault)**: $I_g = 0.4 \times I_n = {{acb_ig}}\text{ A}$, $t_g = 0.20\text{ s}$

### 3.2 Sub-Main Feeder MCCB (Level 2)
- **Breaker Frame**: 4-Pole Fixed Molded Case Circuit Breaker (Category A)
- **Rated Ultimate Breaking Capacity ($I_{cu}$)**: **{{mccb_icu}} kA**
- **Trip Unit Configuration (LSIG)**:
  - **L (Long Time)**: $I_r = 0.9 \times I_n = {{mccb_ir}}\text{ A}$, $t_r = 12.0\text{ s}$
  - **S (Short Time)**: $I_{sd} = 3.0 \times I_r = {{mccb_isd}}\text{ A}$, $t_{sd} = 0.10\text{ s}$
  - **I (Instantaneous)**: $I_i = 10.0 \times I_n = {{mccb_ii}}\text{ A}$

---

## 4. Time-Current Discrimination (TCC) Verification

To prevent spurious tripping of upstream switchboards, two fundamental coordination criteria must be fulfilled simultaneously:
1. **Time Grading Margin**:
   $$\Delta t = t_{sd,\text{upstream}} - t_{\text{downstream}} \ge 100\text{ ms}$$
2. **Current Ratio**:
   $$\frac{I_{sd,\text{upstream}}}{I_{i,\text{downstream}}} \ge 1.5$$

| Upstream Breaker | Downstream Breaker | $I_{sd}$ Upstream (A) | $t_{sd}$ Upstream | Downstream Trip | Time Margin $\Delta t$ | Current Ratio | Selectivity Evaluation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{{selectivity_table_rows}}

---

## 5. Engineering Coordination & Commissioning Checklist
{{coordination_checklist}}
