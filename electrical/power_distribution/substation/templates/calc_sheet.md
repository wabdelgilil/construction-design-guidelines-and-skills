# Substation, Transformer, Diesel Generator & MDB Sizing Calculation Note

## 1. Project & Code Context
- **Discipline**: Electrical Engineering (Power Systems & Substations)
- **Governing Standards**: {{standard_used}}
- **Primary Grid Voltage**: {{tx_primary_kv}} kV (Medium Voltage)
- **Secondary Distribution Voltage**: {{tx_secondary_v}} V AC, 3-Phase 4-Wire, 60 Hz
- **Project Designation**: {{project_name}}

---

## 2. Building Load Summary & Maximum Demand
| Load Classification | Connected Power | Assumed PF | Demand Factor | Diversified Demand |
| :--- | :--- | :--- | :--- | :--- |
| Lighting System | {{lighting_kw}} kW | 0.90 | 0.90 | Included in MD |
| General Small Power Sockets | {{sockets_kw}} kW | 0.85 | 0.50 | Included in MD |
| Central HVAC Chillers & AHUs | {{hvac_kw}} kW | 0.85 | 0.85 | Included in MD |
| Vertical Elevators & Escalators | {{elevators_kw}} kW | 0.80 | 0.70 | Included in MD |
| Domestic & Drainage Pumps | {{pumps_kw}} kW | 0.82 | 0.60 | Included in MD |
| Fire Fighting & Life Safety | {{life_safety_kw}} kW | 0.88 | 1.00 | Included in MD |
| Critical IT Data Center / UPS | {{it_ups_kw}} kW | 0.95 | 1.00 | Included in MD |
| **Total Building Connected Load** | **{{total_kw}} kW** | **-** | **-** | **{{total_kva}} kVA** |
| **Diversified Peak Maximum Demand** | **{{max_demand_kw}} kW** | **0.85** | **0.90** | **{{max_demand_kva}} kVA** |

---

## 3. MV/LV Distribution Transformer Sizing
| Transformer Parameter | Sized Value | Standard / Limit | Status |
| :--- | :--- | :--- | :--- |
| **Selected Rating** | **{{tx_kva}} kVA** | Standard Step Rating | **OPTIMAL** |
| Operating Loading Ratio | {{tx_loading_pct}}% | Target $\le 80.0\%$ | **PASS (EFFICIENT)** |
| Secondary Full Load Current ($I_{flc}$) | {{tx_flc_amps}} A | @ 400V 3-Phase | Calculated |
| Short-Circuit Impedance ($u_k\%$) | {{tx_uk}}% | IEC 60076 standard | Factory Data |
| **Prospective Short-Circuit Current ($I_{sc}$)** | **{{tx_isc_ka}} kA** | Calculated at MDB Bus | **VERIFIED** |

---

## 4. Main Distribution Board (MDB) Incomer Protection
| Component | Specification | Breaking Capacity ($I_{cu}$) | Compliance |
| :--- | :--- | :--- | :--- |
| Main Incomer Circuit Breaker | **{{mdb_incomer_amps}}A {{mdb_breaker_type}}** | **{{mdb_icu_ka}} kA** ($\ge 1.25 \times I_{sc}$) | **SAFE & COMPLIANT** |

---

## 5. Standby Emergency Diesel Generator & 4-Pole ATS Sizing
| Parameter | Sized Value | Design Basis | Status |
| :--- | :--- | :--- | :--- |
| Running Emergency Load | {{emg_kw}} kW ({{emg_kva}} kVA) | Life safety + Essential HVAC + Pumps | Sized |
| Largest Motor Starting Inrush | {{motor_inrush_kva}} kVA | 6x DOL inrush multiplier | Transient check |
| **Selected Standby Generator** | **{{gen_kva}} kVA (Prime/Standby)** | ISO 8528 Class G2/G3 rating | **SAFE** |
| Generator Full Load Current | {{gen_amps}} A | @ 400V 3-Phase | Calculated |
| **Automatic Transfer Switch (ATS)** | **{{ats_amps}}A ({{ats_poles}}-Pole)** | Motorized with mechanical interlock | **COMPLIANT** |

---

## 6. Mandatory Interdisciplinary Coordination Checklist
{{coordination_checklist}}
