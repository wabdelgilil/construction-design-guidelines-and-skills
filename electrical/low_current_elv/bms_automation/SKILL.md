# Building Management System (BMS) & DDC Automation Control Skill

## 1. Scope & Objective
This skill performs the complete engineering design for the **Building Management System (BMS) / Building Automation and Control System (BACS)**, formulating comprehensive MEP I/O Point Schedules (DI, DO, AI, AO), sizing Direct Digital Controllers (DDCs) and expansion modules with mandatory spare capacity, designing network architecture (**BACnet/IP & BACnet MS/TP**), and detailing DDC control panel assemblies under **ASHRAE Standard 135 (BACnet)**, **ISO 16484**, **SBC 601 (Energy Conservation)**, and **SBC 401**.

---

## 2. Engineering Principles & Governing Classifications

### 2.1 Four Standard Hardware I/O Point Types
Every MEP equipment interface falls into one of four standard input/output classes:
1. **Digital Input (DI) [Status & Alarms]**:
   - Potential-free volt-free dry contacts monitored by the DDC.
   - Examples: Fan Run Status (via differential pressure switch DPS), Pump Trip Alarm (overload contact), Air Filter Dirty Status, Low Water Level Float Switch, Fire Alarm Shutdown Interlock.
2. **Digital Output (DO) [Commands]**:
   - Form-C relay dry contacts rated $24\text{V AC/DC}$ (or $230\text{V AC} / 2\text{A}$) driven by DDC algorithms.
   - Examples: Fan Start/Stop Command, Chilled Water Pump Start/Stop, Lighting Zone Contactor Trigger.
3. **Analog Input (AI) [Sensor Measurements]**:
   - Continuously varying physical sensor signals ($0-10\text{V DC}$, $4-20\text{ mA}$, or resistive RTD/NTC).
   - Examples: Supply Air Temperature, Chilled Water Flow Temperature, Duct Static Pressure, Ambient Air CO2 ppm, Water Flow Rate.
4. **Analog Output (AO) [Modulating Control]**:
   - Proportional control signals ($0-10\text{V DC}$ or $4-20\text{ mA}$) sent to electronic actuators and inverters.
   - Examples: 2-Way Chilled Water Modulating Valve Actuator ($0-100\%$), VFD Speed Reference Frequency ($0-100\% / 0-50/60\text{ Hz}$), Modulating Fresh Air Damper Actuator.

### 2.2 DDC Controller Capacity & Sizing Formulation
For each mechanical equipment or floor zone:
$$N_{\text{total}} = N_{\text{DI}} + N_{\text{DO}} + N_{\text{AI}} + N_{\text{AO}}$$
With mandatory 20% future growth spare capacity:
$$N_{\text{equipped}} = \lceil 1.20 \times N_{\text{total}} \rceil$$

Modular DDC configurations:
- **Base DDC Unit**: Typically 16 universal I/O points (e.g. 8 UI, 4 DO, 4 AO).
- **Expansion Modules**: 8-point / 16-point I/O expansion modules connected via high-speed internal bus.
- Number of DDC panels sized based on physical proximity (e.g., AHU room DDC panel, Chiller plant central DDC panel, Floor VAV network).

### 2.3 System Network Architecture (BACnet Pyramid)
1. **Management & Supervisory Level**:
   - Central BMS Server, redundant database, and Web Workstations communicating over 1 Gbps Ethernet TCP/IP LAN.
2. **Control & Automation Level (BACnet/IP)**:
   - Primary plant DDCs (Chillers, Boilers, AHUs, Substations) equipped with native 10/100 Ethernet ports connected to the building ELV network switch infrastructure.
3. **Field & Terminal Unit Level (BACnet MS/TP)**:
   - Master-Slave/Token-Passing RS-485 daisy-chain bus for distributed zone terminal controllers (VAV boxes, FCUs).
   - Maximum segment length: $1200\text{ meters}$ with shielded twisted pair ($2 \times 0.75 - 1.0\text{ mm}^2$), max 32 devices per segment without repeater.

### 2.4 High-Level Interfaces (HLI / Gateway Integrations)
Instead of wiring physical hardwired I/O points for complex packaged equipment, high-level software gateways (Modbus RTU / Modbus TCP / BACnet/IP) extract comprehensive telemetry:
- **Variable Frequency Drives (VFDs)**: Running frequency, motor current, motor kW, cumulative kWh, fault codes.
- **Multifunction Power Meters (MDB)**: Line voltages, 3-phase currents, power factor, active kW, total harmonic distortion (THD).
- **Chillers Package Units**: Evaporator/condenser pressures, compressor runtime hours, COP/EER efficiency.
- **Addressable Fire Alarm Control Panel (FACP)**: General fire alarm status, floor evacuation zone status.
