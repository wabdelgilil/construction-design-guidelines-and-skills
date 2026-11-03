# Low Current / Extra Low Voltage (ELV) Sub-Branch Index

This branch organizes all building Extra Low Voltage (ELV), Life Safety, and Telecommunication systems under a unified, non-confusing hierarchy.
Shared parameters (operating DC voltages, battery backup autonomy, cable containment clearances) are declared in [`rules.json`](file:///d:/programming/construction%20design/electrical/low_current_elv/rules.json).

---

## Sub-Branch Navigation & Skills

| Sub-System | Directory | Governing Standards | Primary Scope |
| :--- | :--- | :--- | :--- |
| **Addressable Fire Alarm** | [`fire_alarm/`](file:///d:/programming/construction%20design/electrical/low_current_elv/fire_alarm/SKILL.md) | NFPA 72, SBC 801, EN 54 | Smoke/heat detector spacing, sounder/strobe candela, loop loading, FACP battery sizing |
| **Public Address & Voice Alarm (PA/VA)** | [`public_address_pava/`](file:///d:/programming/construction%20design/electrical/low_current_elv/public_address_pava/SKILL.md) | BS 5839-8, EN 54-16, EN 54-24 | Acoustic SPL & STI, 100V line A/B interleaving, N+1 Class-D amplifiers, 24h+30m battery sizing |
| **Access Control & Door Interlocks** | [`access_control/`](file:///d:/programming/construction%20design/electrical/low_current_elv/access_control/SKILL.md) | NFPA 101, UL 294, SBC 801 | Maglocks, card readers, REX, break-glass units, FACP fail-safe release, power supply battery sizing |
| **Structured Cabling & Telecom Racks** | [`structured_cabling/`](file:///d:/programming/construction%20design/electrical/low_current_elv/structured_cabling/SKILL.md) | ANSI/TIA-568, ISO/IEC 11801 | Work Area Outlets (WAO), Cat6A permanent link & channel limits, 42U MDF/IDF rack elevations, PoE switch sizing |
| **Building Management System (BMS)** | [`bms_automation/`](file:///d:/programming/construction%20design/electrical/low_current_elv/bms_automation/SKILL.md) | ASHRAE 135 (BACnet), ISO 16484 | MEP I/O point schedules (DI/DO/AI/AO), 20% spare capacity, DDC sizing, BACnet/IP architecture |

---

## Cross-Discipline Coordination
- **Life Safety Interlock**: All magnetic locks on egress doors MUST interface with the Fire Alarm Control Panel (FACP) via fail-safe dry contacts to release automatically upon general alarm (NFPA 101 / SBC 801).
- **HVAC Interface**: Fire alarm system trips motorized fire/smoke dampers (MFSD) and stops AHUs/FCUs via control modules.
- **Plumbing Interface**: Sprinkler zone control valves (ZCV) and water flow switches monitored by FACP monitor modules.
- **Architectural Coordination**: Door preparation, frame cutouts for electric strikes, reader mounting heights (+1200mm AFF), REX (+2200mm AFF or integral door sensor).
