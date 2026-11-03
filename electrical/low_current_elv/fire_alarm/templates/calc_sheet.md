# Addressable Fire Alarm System Calculation Sheet

## 1. Project & Standard Context
- **Discipline**: Electrical Engineering (Low Current / ELV - Fire Life Safety)
- **Governing Standard**: {{standard_used}}
- **Project Designation**: {{project_name}}
- **Total Monitored Area**: {{total_area_m2}} m$^2$

---

## 2. Device Allocation Schedule
| Space Name | Area ($m^2$) | Detector Type | Detectors | MCPs | Sounder/Strobes | Candela (cd) | Interface Modules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{{device_table_rows}}

---

## 3. System Capacity & Loop Loading
| Parameter | Value | Standard Limit | Status |
| :--- | :--- | :--- | :--- |
| Optical Smoke Detectors | {{smoke_count}} Nos. | Area coverage $\le 81\text{ m}^2$ | **COMPLIANT** |
| Thermal Heat Detectors | {{heat_count}} Nos. | Area coverage $\le 49\text{ m}^2$ | **COMPLIANT** |
| Manual Call Points (MCP) | {{mcp_count}} Nos. | Max travel $\le 30\text{ m}$, @ Exits | **COMPLIANT** |
| Sounder / Flashing Strobes | {{sounder_count}} Nos. | Sound $\ge 75\text{ dBA}$ | **COMPLIANT** |
| Interfacing Control Modules | {{module_count}} Nos. | AHU trip & Door release | **COORDINATED** |
| **Grand Total Devices** | **{{total_devices}} Nos.** | System Total | **VERIFIED** |
| **Required Addressable Loops** | **{{total_loops}} Loops** | Max 127 devices/loop | **OPTIMAL** |
| System Spare Margin | {{spare_pct}}% | Min 20% Spare | **PASS** |

---

## 4. NFPA 72 Standby Battery Sizing
| Parameter | Value | Engineering Basis |
| :--- | :--- | :--- |
| FACP Normal Quiescent Standby Current ($I_q$) | {{iq_amps}} A | Base panel + quiescent device draw |
| FACP Full Alarm Current ($I_a$) | {{ia_amps}} A | Active loop devices + all sounder/strobes |
| Required Standby Time | {{standby_hours}} Hours | Code mandate (24h continuous operation) |
| Required Alarm Time | {{alarm_minutes}} Minutes | Full building evacuation duration |
| Battery Aging Derating Factor | 1.25 | NFPA 72 safety factor |
| Calculated Theoretical Battery Capacity | {{calc_battery_ah}} Ah | $C = 1.25 \times (I_q \times 24 + I_a \times 0.25)$ |
| **Specified Battery Pack Rating** | **{{selected_battery_ah}} Ah (24V DC)** | Sealed Lead-Acid (SLA) Maintenance-Free |

---

## 5. Mandatory Interdisciplinary Coordination Checklist
{{coordination_checklist}}
