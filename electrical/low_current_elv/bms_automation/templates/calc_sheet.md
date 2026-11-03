# Building Management System (BMS) & DDC Automation Calculation Note

**Project**: {{project_name}}  
**Governing Standard**: {{standard_used}}  
**Primary Network Architecture**: {{primary_protocol}}  
**Field Bus Communication**: {{field_bus_protocol}}  

---

## 1. Executive Summary & Automation Scope
This calculation note details the Building Management System (BMS) / Building Automation and Control System (BACS) engineering, establishing comprehensive MEP physical I/O point schedules (DI, DO, AI, AO), sizing Direct Digital Controllers (DDCs) and expansion modules with mandatory 20% future growth spare capacity, designing High-Level Interfaces (HLI), and configuring network topologies under **ASHRAE 135 (BACnet)**, **ISO 16484**, and **SBC 601**.

### System Hardware Point Summary
- **Active Digital Inputs (DI)**: {{total_di}} Points
- **Active Digital Outputs (DO)**: {{total_do}} Points
- **Active Analog Inputs (AI)**: {{total_ai}} Points
- **Active Analog Outputs (AO)**: {{total_ao}} Points
- **Total Active Hardwired Points**: **{{grand_active}} Points**
- **Equipped Spare Capacity (20%)**: **{{grand_spare}} Points**
- **Grand Total Terminated I/O Capacity**: **{{grand_equipped}} Points**
- **Distributed DDC Control Panels**: **{{total_panels}} Panels**
- **High-Level Gateways (HLI)**: {{total_hli}} Equipment Interfaces (Modbus/BACnet)

---

## 2. MEP Equipment Point Schedule

| Equipment Tag | Description | Location | DI (Status/Alarm) | DO (Command) | AI (Sensors) | AO (Actuators) | Total Points | High-Level Gateway (HLI) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{{equipment_table_rows}}

---

## 3. Distributed DDC Control Panels & Sizing

| Panel Tag | Location | Served Equipment | Active Points | Spare Points (20%) | Equipped Capacity | Base DDC (32-pt) | Expansion Modules (16-pt) | Enclosure Size | Power Supply (W) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{{ddc_panel_rows}}

---

## 4. Central Control Room UPS & Network Architecture
- **BMS Central Server & Workstation Power**: 600 W (Server + Operator dual-screen terminal)
- **Cumulative DDC Panels Power Load**: {{total_ddc_w}} W @ 24V DC
- **Selected Online Double-Conversion UPS**: **{{selected_ups_va}} VA / {{selected_ups_w}} W** (Provides 2.0 hours runtime during mains outage).
- **Network Media**: 1000Base-T Cat6A Ethernet backbone connecting all DDC panels to the BMS central core switch.

---

## 5. Cross-Discipline Coordination Checklist
{{coordination_checklist}}
