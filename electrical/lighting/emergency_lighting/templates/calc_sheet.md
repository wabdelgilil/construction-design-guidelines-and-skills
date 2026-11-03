# Emergency & Exit Lighting (CBS & Life Safety) Calculation Sheet

## 1. Project & Code Context
- **Discipline**: Electrical Engineering (Lighting Systems - Emergency & Life Safety)
- **Governing Standards**: {{standard_used}}
- **System Architecture**: {{system_architecture}}
- **Required Autonomy Duration**: {{autonomy_minutes}} Minutes ({{autonomy_hours}} Hours)
- **Project Designation**: {{project_name}}

---

## 2. Emergency Luminaire & Exit Sign Allocation
| Space / Zone | Typology | Area ($m^2$) | Min Lux Target | Emergency Fixtures | Exit Signs | Space Load (W) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{{space_table_rows}}

---

## 3. Central Battery System (CBS) Inverter & Battery Sizing
| Parameter | Sized Value | Design Basis / Standard | Status |
| :--- | :--- | :--- | :--- |
| Total Emergency Lighting Load | {{total_watts}} W | Sum of LED luminaires & signs | Sized |
| **Specified CBS Inverter Rating** | **{{inverter_va}} VA** | 125% Inverter Sizing Margin | **OPTIMAL** |
| DC Battery Bus Voltage | {{dc_bus_voltage}} V DC | {{battery_blocks}}x 12V VRLA Blocks in Series | Standard |
| Calculated Minimum Battery Capacity | {{calc_battery_ah}} Ah | $C = (P \times T \times 1.25) / (\eta \times V)$ | Calculated |
| **Specified Battery Pack Rating** | **{{selected_battery_ah}} Ah** | Sealed VRLA Maintenance-Free | **COMPLIANT** |
| Dedicated CBS Branch Circuits | {{cbs_circuits}} Circuits | Max 20 luminaires / 800W per circuit | **SAFE** |

---

## 4. Mandatory Interdisciplinary Coordination Checklist
{{coordination_checklist}}
