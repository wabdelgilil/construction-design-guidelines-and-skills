# Low Voltage Cable Sizing & Cable Tray Sizing Calculation Note

## 1. Project & Governing Standards
- **Discipline**: Electrical Engineering (Power Distribution & Containment)
- **Governing Standards**: {{standards_used}}
- **System Operating Voltage**: {{system_voltage}} V AC, 3-Phase 400V / 1-Phase 230V, 60 Hz
- **Project Designation**: {{project_name}}

---

## 2. Feeder Cable Sizing Schedule
| Feeder Tag | Description | Load (kW) | $I_b$ (A) | Breaker ($I_n$) | Cable Size | $I_z$ (A) | Length (m) | $\Delta V$ (%) | $I_{sc}$ Withstand (kA) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{{feeder_table_rows}}

---

## 3. Cable Tray Sizing & Fill Ratio Compliance
| Cable Tray Tag | Supported Cables | Total Cables Area ($mm^2$) | Min Required Area | Specified Tray ($W \times D$) | Actual Area ($mm^2$) | Achieved Fill Ratio | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **{{tray_tag}}** | {{cables_count}} Feeders | {{cables_area}} mm$^2$ | {{min_tray_area}} mm$^2$ | **{{tray_width}} mm $\times$ {{tray_depth}} mm** | {{actual_tray_area}} mm$^2$ | **{{achieved_fill}}%** ($\le 40\%$) | **{{tray_status}}** |

---

## 4. Engineering Derating & Sizing Formulations
- **Derating Factors Applied**:
  - Ambient Temperature Correction ($C_a$ @ 45$^\circ$C): {{ca_factor}}
  - Grouping Correction in Perforated Tray ($C_g$): {{cg_factor}}
  - Total Cumulative Derating ($C_{total} = C_a \times C_g$): {{c_total}}
- **Voltage Drop Formula**:
  $$\Delta U = \sqrt{3} \times I_b \times L \times (R \cos\phi + X \sin\phi) \le 2.0\% \text{ for sub-mains}$$
- **Short Circuit Adiabatic Withstand**:
  $$S \ge \frac{I_{sc} \times \sqrt{t}}{k} \quad (\text{where } k=143, t=0.1\text{ s})$$
- **Tray Fill Ratio Criteria**:
  $$\text{Fill Ratio} = \frac{\sum A_{\text{cables}}}{W_{\text{tray}} \times D_{\text{tray}}} \le 40\% \quad (\text{per NEC 392 / SBC 401})$$

---

## 5. Mandatory Interdisciplinary Coordination Checklist
{{coordination_checklist}}
