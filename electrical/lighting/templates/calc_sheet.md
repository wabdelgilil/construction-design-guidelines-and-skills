# Lighting Photometric Calculation Note

## Project & Code Metadata
- **Discipline**: Electrical Engineering (Lighting & Small Power)
- **Design Standard**: {{code_used}} / IESNA / CIBSE
- **Nominal Voltage**: {{voltage_v}} V AC, Single Phase
- **Room / Space Name**: {{room_name}}
- **Space Function / Type**: {{space_type}}

---

## 1. Geometric & Environmental Parameters
| Parameter | Value | Unit |
| :--- | :--- | :--- |
| Room Length ($L$) | {{room_length}} | m |
| Room Width ($W$) | {{room_width}} | m |
| Room Floor Area ($A$) | {{room_area}} | m$^2$ |
| Ceiling Height | {{ceiling_height}} | m |
| Working Plane Height | {{workplane_height}} | m |
| Maintenance Factor ($MF$) | {{mf}} | - |
| Coefficient of Utilization ($CU$) | {{cu}} | - |

---

## 2. Photometric & Fixture Sizing
| Parameter | Value | Unit |
| :--- | :--- | :--- |
| Selected Luminaire | {{fixture_model}} | - |
| Fixture Luminous Flux | {{fixture_lumens}} | Lumens (lm) |
| Fixture Electrical Power | {{fixture_watts}} | W |
| Target Maintained Illuminance ($E_{target}$) | {{target_lux}} | Lux |
| Required Fixture Quantity ($N_{calculated}$) | {{raw_fixtures}} | units |
| Specified Layout Array ($N_{cols} \times N_{rows}$) | {{grid_layout}} | fixtures |
| **Total Fixtures Installed** | **{{total_fixtures}}** | **units** |
| **Achieved Average Illuminance ($E_{achieved}$)** | **{{achieved_lux}}** | **Lux** |

---

## 3. Energy Code Compliance (LPD Check)
| Check | Achieved | Allowed Code Limit | Status |
| :--- | :--- | :--- | :--- |
| Lighting Power Density (LPD) | {{achieved_lpd}} W/m$^2$ | {{allowed_lpd}} W/m$^2$ | **{{lpd_status}}** |
| Illuminance Target Compliance | {{achieved_lux}} Lux | $\ge$ {{target_lux}} Lux | **{{illuminance_status}}** |

---

## 4. Branch Circuit Allocation & Sizing
| Circuit Tag | Fixtures Fed | Total Load (W) | Breaker (MCB) | Conductor Cable | Voltage Drop |
| :--- | :--- | :--- | :--- | :--- | :--- |
| {{circuit_tag}} | {{total_fixtures}} units | {{total_circuit_watts}} W | {{circuit_breaker}} A | {{circuit_cable}} mm$^2$ Cu | {{voltage_drop_pct}}% |

---

## 5. Architectural & MEP Coordination Notices
- Ceiling type & grid compatibility: Fixtures sized for standard 600x600 mm modular acoustic ceiling tile.
- Mechanical HVAC interface: Ensure luminaire locations clear diffusers and return air grilles by min. 300 mm.
- Emergency Lighting: Minimum 1 fixture per 5 fixtures or per room to be connected to central inverter / battery backup.
