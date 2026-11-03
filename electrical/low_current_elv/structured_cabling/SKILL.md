# Structured Cabling System (SCS) & Telecommunications Racks Skill

## 1. Scope & Objective
This skill designs the complete **Structured Cabling Infrastructure (SCS)**, horizontal Cat6A distribution, optical fiber backbone links, patch panels, 24/48-port PoE access switches, and **42U Telecommunications Rack Elevations** in compliance with **ANSI/TIA-568-D**, **ISO/IEC 11801**, **BICSI TDMM**, and **SBC 401**.

---

## 2. Engineering Principles & Governing Equations

### 2.1 Horizontal Cabling Link Rules
1. **Permanent Link Rule**: The physical horizontal copper run from the telecom room patch panel to the wall/floor outlet faceplate must not exceed **$90\text{ meters}$**:
   $$L_{\text{permanent\_link}} \le 90.0\text{ m}$$
2. **Channel Rule**: The cumulative electrical channel (Permanent Link + work area patch cord + equipment room patch cord) must not exceed **$100\text{ meters}$**:
   $$L_{\text{channel}} = L_{\text{permanent}} + L_{\text{patch\_user}} + L_{\text{patch\_rack}} \le 100.0\text{ m}$$
3. **Cable Specification**: Category 6A (Augmented Class $E_A$, $500\text{ MHz}$, supporting 10GBASE-T up to 100m) with Low Smoke Zero Halogen (LSZH) jacket.

### 2.2 Work Area Outlets (WAO) & Field Sizing
- **Standard Office Desk**: 2x RJ45 Cat6A ports (1x Data, 1x VoIP).
- **Wireless Access Point (WAP)**: 2x RJ45 Cat6A ports (supporting dual 2.5G/5G multi-gigabit PoE uplink for WiFi 6/7).
- **IP CCTV Security Cameras**: 1x RJ45 Cat6A PoE port.
- **Access Control Controller**: 1x RJ45 Cat6A network uplink port.
- **Smart Meeting Room / AV**: 4x RJ45 Cat6A ports.

### 2.3 Optical Fiber Backbone
- **Indoor Building Backbone (MDF to IDF)**: 12-Core or 24-Core OM4 Laser-Optimized Multi-Mode (50/125 $\mu$m) fiber terminated with duplex LC connectors in a 1U Light Interface Unit (LIU).
- **Campus / Long Distance Backbone ($> 300\text{ m}$)**: OS2 Single-Mode (9/125 $\mu$m) fiber.

### 2.4 42U Network Rack Space Allocation & Elevation
Each standard standard equipment rack has $42\text{U}$ of vertical mounting space ($1\text{U} = 44.45\text{ mm} = 1.75\text{ in}$):
1. **Patch Panels**: 24-port (1U) or 48-port (2U or high-density 1U).
2. **Horizontal Cable Managers**: 1U per patch panel ($1:1$ ratio).
3. **Managed Access Switches**: 1U per 24 or 48 ports (with 1U airflow spacing/cable manager).
4. **Fiber LIU**: 1U optical patch drawer.
5. **Rackmount UPS**: 2U or 3U Online Double-Conversion UPS (sized for total network switch and controller loads for $\ge 30\text{ minutes}$ runtime).
6. **Rack Spare Capacity Requirement**:
   $$\text{Spare } U \% = \frac{42 - U_{\text{utilized}}}{42} \times 100 \ge 25\%$$
   If utilized U exceeds $75\%$ ($> 31\text{U}$), a second adjacent 42U rack is automatically added.

---

## 3. Electrical & Mechanical Coordination
- **Rack Power Distribution Unit (PDU)**: Dual redundant vertical 0U / horizontal 1U Metered PDUs (Circuit A from Essential LV Board, Circuit B from UPS).
- **Telecom Room Cooling**: Continuous 24/7 dedicated split DX unit maintaining $20^\circ\text{C} - 24^\circ\text{C}$ room ambient temperature and $40-60\%$ relative humidity (ASHRAE TC 9.9 Thermal Guidelines for Data Processing Environments).
