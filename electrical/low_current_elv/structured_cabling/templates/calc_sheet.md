# Structured Cabling Infrastructure & Telecommunications Rack Calculation Note

**Project**: {{project_name}}  
**Governing Standard**: {{standard_used}}  
**Network Speed Capability**: 10GBASE-T (Category 6A Augmented Class $E_A$, 500 MHz)  
**Standard Rack Specification**: 42U 800mm (W) x 1000mm (D) Server/Network Enclosure  

---

## 1. Executive Summary & Infrastructure Scope
This engineering calculation establishes the horizontal copper distribution, work area outlets (WAO), fiber optic backbone links, network access switches, rack unit (U) utilization, and UPS power sizing for the telecommunications room.

---

## 2. Horizontal Work Area Outlets (WAO) & Port Distribution

| Telecom Zone / Floor Area | Workstations | WAP (WiFi 6/7) | CCTV Cameras | Access Control | Network Printers/AV | Total Horizontal Ports | Max Link Run (m) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{{zone_table_rows}}

### Permanent Link Compliance Check (ANSI/TIA-568-D)
- **Maximum Permissible Permanent Link**: $90.0\text{ meters}$
- **Worst-Case Measured Run**: **{{worst_case_distance}} m**
- **Channel Margin Status**: **{{link_compliance_status}}**

---

## 3. Passive Hardware Sizing (Patch Panels & Fiber Backbone)

### 3.1 Category 6A 24-Port Patch Panels
- **Active Connected Ports**: {{total_active_ports}} ports
- **Equipped Future Expansion Reserve (20%)**: {{spare_ports}} ports
- **Total Terminated Ports Required**: {{total_ports_needed}} ports
- **Selected Patch Panels**: **{{patch_panels_count}}x 1U 24-Port Modular Cat6A Shielded Patch Panels**
- **Horizontal Cable Managers**: **{{cable_managers_count}}x 1U Double-Sided Cable Managers (1:1 Ratio)**

### 3.2 Optical Fiber Backbone
- **Backbone Link**: MDF Server Room to Floor IDF
- **Fiber Cable Type**: **{{fiber_type}}**
- **Total Terminated Cores**: **{{fiber_cores}} Cores** via Duplex LC Adapters in 1U Sliding LIU Patch Drawer.

---

## 4. Active Network Switches & PoE Power Budget
- **Access Switches**: **{{switches_count}}x 48-Port 1U Managed Gigabit/Multi-Gigabit PoE+ Switches (IEEE 802.3at)**
- **Total PoE & System Power Draw**: **{{total_switch_power_w}} W** ({{total_switch_power_kw}} kW)
- **Heat Dissipation**: **{{heat_dissipation_btu}} BTU/hr** (Requires dedicated continuous DX split unit).

---

## 5. 42U Equipment Rack Space Allocation (Elevation)

| U Position | Height | Category | Equipment Description | Power Draw (W) |
| :--- | :--- | :--- | :--- | :--- |
{{rack_table_rows}}

### Rack Capacity Analysis
- **Standard Rack Height**: 42U
- **Total Utilized Space**: **{{total_u_used}}U**
- **Total Spare Space Available**: **{{spare_u}}U ({{spare_u_percentage}}% Reserve)**
- **Compliance**: Exceeds BICSI minimum 25% future growth requirement.

---

## 6. Standby UPS Sizing (30-Minute Autonomy)
Under BICSI TDMM and SBC 401, network access switches supporting VoIP and PoE security cameras must be maintained on battery backup during power outages:

$$S_{\text{UPS}} \ge \frac{P_{\text{switches}}}{\text{pf}} \times 1.25 = \frac{{{total_switch_power_w}}\text{ W}}{0.8} \times 1.25 = {{calc_ups_va}}\text{ VA}$$

- **Selected Rackmount UPS**: **{{selected_ups_va}} VA / {{selected_ups_w}} W Online Double-Conversion UPS**
- **Autonomy Runtime**: **{{ups_autonomy_min}} Minutes** at 100% rated load.

---

## 7. Cross-Discipline Coordination Checklist
{{coordination_checklist}}
