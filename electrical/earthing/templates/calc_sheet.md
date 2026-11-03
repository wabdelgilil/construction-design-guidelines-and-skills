# Earthing & Lightning Protection System Calculation Sheet

## 1. Project & Standards Reference
- **Discipline**: Electrical Engineering (Protection & Earthing)
- **Governing Standards**: {{standard_used}}
- **Facility Classification**: {{facility_type}}
- **Project Designation**: {{project_name}}
- **Soil Resistivity ($\rho$)**: {{soil_resistivity}} $\Omega \cdot$m

---

## 2. Earthing Resistance Analysis (IEEE 80 / Dwight's Formula)
| Parameter | Calculated Value | Design Target / Limit | Status |
| :--- | :--- | :--- | :--- |
| Driven Single Rod Resistance ($R_{\text{rod}}$) | {{single_rod_r}} $\Omega$ | Dwight Formulation ($3/4"$ x 3.0m rod) | Calculated |
| Buried Perimeter Loop Resistance ($R_{\text{ring}}$) | {{ring_r}} $\Omega$ | 70 mm$^2$ bare copper @ 0.8m depth | Calculated |
| Quantity of Driven Earth Rods | {{number_of_rods}} Nos. | Equi-spaced around building perimeter | Sized |
| **Combined System Earth Resistance ($R_{\text{net}}$)** | **{{combined_r}} $\Omega$** | **$\le$ {{target_r}} $\Omega$** | **{{compliance_status}}** |

---

## 3. External Lightning Protection System (IEC 62305 / NFPA 780)
| LPS Design Parameter | Specified Value | Standard Requirement | Compliance |
| :--- | :--- | :--- | :--- |
| Lightning Protection Level (LPL) | **{{lps_level}}** | Risk Assessment Classification | **SPECIFIED** |
| Rolling Sphere Radius ($r$) | {{sphere_radius}} m | IEC 62305 Sphere Rolling Envelope | **PROTECTED** |
| Roof Air Terminals (Franklin Rods) | {{air_terminals_count}} Nos. | Height = {{air_terminal_h}} m above roof | **COORDINATED** |
| Down Conductors Quantity | {{down_count}} Nos. | Max Spacing $\le$ {{down_spacing}} m | **COMPLIANT** |
| Down Conductor Test Links | {{test_links_count}} Nos. | Mounted at +1500 mm AFF | **COMPLIANT** |

---

## 4. Earthing & Lightning Material Take-Off (BOQ)
| Item | Material Specification | Quantity | Unit | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Copper-Bonded Steel Earth Rod ($3/4" \times 3.0\text{ m}$) | {{number_of_rods}} | Nos. | Deep Earth Grounding |
| 2 | Heavy-Duty Concrete Inspection Pit ($300 \times 300\text{ mm}$) | {{total_pits}} | Nos. | Periodic Testing & Maintenance |
| 3 | 70 mm$^2$ Bare Hard-Drawn Stranded Copper Conductor | {{copper_70mm_m}} | m | Buried Earth Ring Loop |
| 4 | $25 \times 3\text{ mm}$ Bare Copper Tape | {{copper_tape_m}} | m | Down Conductors & Roof Mesh |
| 5 | Exothermic Weld Connections (Cadweld) | {{cadweld_count}} | Joints | Molecular Rebar & Rod Bonding |

---

## 5. Mandatory Interdisciplinary Coordination Checklist
{{coordination_checklist}}
