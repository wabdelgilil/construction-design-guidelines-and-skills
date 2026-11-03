# Electrical Engineering Index (Level 1 Parent)

This node serves as the parent index and router for all **Electrical Engineering (MEP)** design skills.
Shared electrical parameters (voltage, frequency, power factor, allowable voltage drop) are inherited from [`rules.json`](file:///d:/programming/construction%20design/electrical/rules.json).

---

## Sub-Branch Navigation & Dispatch Table

| Sub-Branch | Directory | Primary Scope | Trigger Keywords |
| :--- | :--- | :--- | :--- |
| **Power Distribution** | [`power_distribution/`](file:///d:/programming/construction%20design/electrical/power_distribution/INDEX.md) | Branch circuits, power outlets, receptacles, panelboards, breakers, feeders, substations, medical IPS, Motor Control Centers (MCC), short-circuit & protection coordination, APFC capacitor banks | `socket`, `receptacle`, `power`, `circuit`, `breaker`, `panel`, `feeder`, `substation`, `transformer`, `generator`, `medical ips`, `mcc`, `motor`, `starter`, `vfd`, `short circuit`, `selectivity`, `tcc`, `apfc`, `power factor`, `capacitor bank` |
| **Lighting Design** | [`lighting/`](file:///d:/programming/construction%20design/electrical/lighting/INDEX.md) | Indoor photometrics, lux calculations, fixture layouts, emergency & exit lighting (CBS) | `lighting`, `luminaire`, `lux`, `footcandle`, `lpd`, `emergency lighting`, `exit sign`, `cbs` |
| **Low Current / ELV** | [`low_current_elv/`](file:///d:/programming/construction%20design/electrical/low_current_elv/INDEX.md) | Life safety addressable fire alarm, public address, access control, structured cabling | `fire alarm`, `smoke detector`, `heat detector`, `facp`, `elv`, `low current`, `loop` |
| **CCTV & Security Systems** | [`cctv_security/`](file:///d:/programming/construction%20design/electrical/cctv_security/INDEX.md) | CCTV surveillance, camera types, coverage, storage calculation, PoE network | `cctv`, `camera`, `ip camera`, `nvr`, `poe`, `surveillance`, `security`, `storage days` |
| **Cables & Containment** | [`cables/`](file:///d:/programming/construction%20design/electrical/cables/INDEX.md) | Cable sizing, current carrying capacity, derating factors, voltage drop, cable trays | `cable`, `wire`, `cross section`, `cable sizing`, `voltage drop`, `tray`, `conduit` |
| **Earthing & Lightning** | [`earthing/`](file:///d:/programming/construction%20design/electrical/earthing/INDEX.md) | Earth pits, grounding conductors, earth resistance, lightning protection (LPS) | `earth`, `grounding`, `earthing pit`, `lightning`, `lps`, `rolling sphere`, `copper rod` |

---

## Shared Rules Summary
- **Voltages & Frequency**: 230V/400V 60Hz (SBC), 220V/380V 50Hz (ECP), 120V/208V 60Hz (NEC).
- **Inheritance**: Sub-branches inherit voltage standards, power factors, and voltage drop thresholds automatically from [`rules.json`](file:///d:/programming/construction%20design/electrical/rules.json).
