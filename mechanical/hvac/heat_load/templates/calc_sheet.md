# Mechanical HVAC Cooling Load & Air Distribution Calculation Note

## 1. Project & Governing Codes
- **Discipline**: Mechanical Engineering (HVAC)
- **Governing Code**: {{code_used}} (SBC 501 / ASHRAE 55 & 62.1)
- **Space Designation**: {{space_name}}
- **Floor Area ($A$)**: {{area_m2}} m$^2$ | **Volume ($V$)**: {{volume_m3}} m$^3$

---

## 2. Space Heat Gain Breakdown
| Component | Heat Gain (Watts) | Sensible (W) | Latent (W) | Percentage |
| :--- | :--- | :--- | :--- | :--- |
| Building Envelope Conduction | {{envelope_w}} W | {{envelope_w}} W | - | {{envelope_pct}}% |
| Window Solar Radiation | {{solar_w}} W | {{solar_w}} W | - | {{solar_pct}}% |
| Occupancy Heat Gain | {{occ_total_w}} W | {{occ_sensible_w}} W | {{occ_latent_w}} W | {{occ_pct}}% |
| Artificial Lighting Heat Gain | {{lights_w}} W | {{lights_w}} W | - | {{lights_pct}}% |
| Office Equipment / Plug Loads | {{equip_w}} W | {{equip_w}} W | - | {{equip_pct}}% |
| Outdoor Air Fresh Ventilation | {{vent_total_w}} W | {{vent_sensible_w}} W | {{vent_latent_w}} W | {{vent_pct}}% |
| **Totals** | **{{grand_total_w}} W** | **{{sensible_w}} W** | **{{latent_w}} W** | **100.0%** |

---

## 3. Psychrometric & Tonnage Summary
| Metric | Value | Unit | Engineering Evaluation |
| :--- | :--- | :--- | :--- |
| Sensible Heat Ratio ($SHR$) | {{shr}} | - | Normal Comfort Range (0.75 - 0.85) |
| Total Heat Removal Rate | {{total_btu}} | BTU/hr | Calculated Space Peak Demand |
| Required Cooling Capacity | {{req_tr}} | TR | Theoretical Minimum Tonnage |
| **Specified Equipment Tonnage** | **{{selected_tr}}** | **TR** | Standard Equipment Selection |
| **Total Supply Airflow** | **{{supply_cfm}}** | **CFM** | Sized at $\Delta T = 20^\circ$F |
| Supply Air Diffusers | {{diffusers_count}} units | 4-Way Square | {{cfm_per_diffuser}} CFM / Diffuser ($NC \le 30$) |
| Return Air Grilles | {{return_count}} units | Egg-crate Ceiling | Grille Face Velocity $\le 400$ FPM |

---

## 4. Multi-Discipline MEP Coordination Interface
| Interface Target | Engineering Requirement | Design Specification |
| :--- | :--- | :--- |
| **Electrical Power** | Dedicated Outdoor Unit Feeder | {{elec_voltage}} V, MCA = {{elec_mca}} A, MOP = {{elec_mop}} A |
| **Electrical Controls** | Wall Room Thermostat Conduit | Flush Box @ +{{thermostat_aff}} m AFF (isolated from diffusers) |
| **Electrical Safety** | Outdoor Weatherproof Isolator | IP65 Rotary Isolator @ +{{isolator_aff}} m AFF |
| **Civil / Structural** | Rooftop Equipment Plinth | Concrete Pad + Anti-Vibration Springs |
| **Plumbing Drainage** | Condensate Drain | 25 mm Insulated UPVC with P-Trap to Stack |

---

## 5. Mandatory Coordination Action Items
{{coordination_checklist}}
