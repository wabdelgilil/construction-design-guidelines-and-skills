# Electronic Access Control System (ACS) & Security Door Interlocks Calculation Note

**Project**: {{project_name}}  
**Governing Standard**: {{standard_used}}  
**System Operating Voltage**: {{dc_voltage}} V DC  
**Backup Autonomy Duration**: {{autonomy_hours}} Hours (Mains Failure)  

---

## 1. System Overview & Hardware Architecture
The Access Control System regulates and monitors entry and egress through controlled doors using smart credentials, motorized/electromagnetic locking hardware, request-to-exit devices, and centralized network door controllers.

### Life Safety & Emergency Release Interlock (NFPA 101 / SBC 801)
To ensure unhindered egress during emergency evacuations:
1. **Fire Alarm Interlock (FACP)**: The 12V DC power distribution to all magnetic locks is routed through a supervised Normally Closed (NC) dry contact driven by the building Fire Alarm Control Panel. Upon any confirmed fire alarm, power is cut immediately, unlocking all fail-safe doors automatically.
2. **Local Emergency Break Glass (BGU)**: A green emergency break glass unit is installed on the secured side of each exit door at $+1200\text{ mm}$ AFF, wired directly in series with the positive lock supply leg to guarantee positive mechanical power cutoff even in the event of an electronic controller failure.

---

## 2. Controlled Doors Hardware Schedule & Current Budget

| Door Tag | Description | Lock Type | Locks Qty | Holding Force | Reader Type | Lock mA | Peripherals mA | Total Door mA | Power (W) | Fail-Safe Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{{door_table_rows}}

---

## 3. Electrical Load Sizing & Power Supply Unit (PSU)

### 3.1 Total DC System Current Demand
$$I_{\text{total}} = \sum I_{\text{doors}} + I_{\text{controllers\_overhead}}$$
- **Total Doors Demand**: {{sum_doors_ma}} mA
- **Controllers Base Demand**: {{controllers_overhead_ma}} mA
- **Total Continuous System Current**: **{{total_system_current_a}} A** ({{total_system_power_w}} W)

### 3.2 Auxiliary Power Supply Unit Selection
$$I_{\text{PSU\_required}} = I_{\text{total}} \times 1.25 = {{min_psu_a}}\text{ A}$$
- **Selected Power Supply Unit Rating**: **{{psu_rating_a}} A @ {{dc_voltage}}V DC ({{psu_rating_w}} W)**
- **Mains AC Supply Feed**: 230V AC / 1-Phase / 50-60Hz via 3A Unswitched Fused Spur.

---

## 4. 4-Hour Standby Battery Capacity Calculation

Under NFPA 101 / SBC 801, access control systems on designated escape routes must remain powered for a minimum of 4.0 hours during primary power outages:

$$C_{\text{battery}} = I_{\text{total}} \times t_{\text{standby}} \times K_{\text{aging}}$$
$$C_{\text{battery}} = {{total_system_current_a}}\text{ A} \times {{autonomy_hours}}\text{ h} \times 1.25 = {{calc_battery_ah}}\text{ Ah}$$

- **Selected Sealed Lead-Acid (SLA) Battery**: **{{selected_battery_ah}} Ah @ {{dc_voltage}}V DC** (1x 12V Block).
- **Available Autonomy Margin**: {{autonomy_margin}}% surplus reserve.

---

## 5. Network Architecture & Controller Allocation
- **Total Controlled Doors**: {{total_doors}} doors.
- **Controller Type**: {{controller_type}}.
- **Required Controller Units**: **{{total_controllers}} unit(s)**.
- **Communication Protocol**: TCP/IP 10/100 Ethernet with AES-256 encrypted bus to readers (OSDP v2).

---

## 6. Cross-Discipline Coordination Checklist
{{coordination_checklist}}
