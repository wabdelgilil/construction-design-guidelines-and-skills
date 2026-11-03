# Medical Isolated Power System (IPS / Medical IT) Calculation Sheet

## 1. Space & Project Standards
- **Facility / Department**: Healthcare Facility - Surgical Suite
- **Location Classification**: Group 2 Medical Location (Operating Theater)
- **Governing Codes**: {{standard_used}}
- **Nominal Operating Voltage**: {{voltage_v}} V AC, 1-Phase, 60 Hz
- **Room / Suite**: {{room_name}}

---

## 2. Transformer & Power Sizing
| Parameter | Sized Value | Design Criteria |
| :--- | :--- | :--- |
| Connected Total Load | {{total_w}} W / {{total_kva}} kVA | Sum of all medical outlets |
| Operating Demand Factor | {{demand_factor}} | Diversity in surgery |
| Required Design Load | {{design_kva}} kVA | Including 20% future capacity |
| **Selected Medical Transformer** | **{{transformer_kva}} kVA** | IEC/NFPA Class H Isolation |
| Primary Rated Current ($I_{pri}$) | {{pri_amps}} A | @ {{voltage_v}} V |
| Secondary Rated Current ($I_{sec}$) | {{sec_amps}} A | Isolated 230V Floating |
| Primary Overcurrent Protection | {{primary_mcb}} A ({{primary_curve}}) | Min 12x inrush withstand |

---

## 3. Insulation Monitoring Device (IMD) Parameters
| Parameter | Value | Code Limit / Standard | Status |
| :--- | :--- | :--- | :--- |
| IMD Alarm Response Level | {{imd_alarm}} k$\Omega$ | $\le 50\text{ k}\Omega$ (IEC 60364-7-710) | **PASS** |
| Max Internal Test Current | 1.0 mA DC | $\le 1.0\text{ mA}$ DC | **PASS** |
| Internal AC Impedance | $\ge 100\text{ k}\Omega$ | Min $100\text{ k}\Omega$ | **PASS** |
| Maximum System Leakage Current | {{leakage_ma}} mA | $< 0.5\text{ mA}$ | **PASS** |
| Remote Annunciator | Required | Acoustic & Optical in OR | **COMPLIANT** |

---

## 4. Supplementary Equipotential Bonding (POAG)
| Parameter | Value | Allowed Limit | Status |
| :--- | :--- | :--- | :--- |
| Equipotential Earth Resistance ($R_{ep}$) | $\le$ {{bonding_ohms}} $\Omega$ | Max $0.10\ \Omega$ | **COMPLIANT** |
| Patient Environment Protective Leads | 6 mm$^2$ Cu (Green/Yellow) | Min 6 mm$^2$ | **COMPLIANT** |
| Main POAG Busbar Trunking Conductor | 16 mm$^2$ Cu | Min 16 mm$^2$ | **COMPLIANT** |

---

## 5. Branch Circuit Schedule (2-Pole Double Break)
| Circuit Tag | Description | Load (W) | Design Current (A) | Breaker | Conductor | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{{circuit_table_rows}}

---

## 6. Mandatory Interdisciplinary Coordination Checklist
{{coordination_checklist}}
