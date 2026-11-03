# Mechanical Engineering Index (Level 1 Parent)

This node serves as the parent index and router for all **Mechanical Engineering (MEP)** design skills.
Shared mechanical parameters (comfort setpoints, outdoor design temperatures, supply pressures) are inherited from [`rules.json`](file:///d:/programming/construction%20design/mechanical/rules.json).

---

## Sub-Branch Navigation & Dispatch Table

| Sub-Branch | Directory | Primary Scope | Trigger Keywords |
| :--- | :--- | :--- | :--- |
| **HVAC & Ventilation** | [`hvac/`](file:///d:/programming/construction%20design/mechanical/hvac/INDEX.md) | Cooling/heating thermal loads, airflow (CFM), duct sizing, diffusers, FCU/AHU | `hvac`, `cooling`, `heating`, `air conditioning`, `cfm`, `duct`, `diffuser`, `chiller`, `ahu`, `fcu` |
| **Plumbing & Drainage** | [`plumbing/`](file:///d:/programming/construction%20design/mechanical/plumbing/INDEX.md) | Domestic water supply, booster pumps, water heaters, drainage fixtures (DFU), vent pipes | `plumbing`, `water supply`, `pump`, `pipe`, `drainage`, `dfu`, `wsfu`, `sewer`, `vent` |
| **Fire Fighting** | [`fire_fighting/`](file:///d:/programming/construction%20design/mechanical/fire_fighting/INDEX.md) | Fire sprinklers, hose reels, standpipes, fire pump head and flow calculation | `fire`, `fire fighting`, `sprinkler`, `hose reel`, `standpipe`, `fire pump`, `hydrant`, `nfpa` |

---

## Shared Rules Summary
- **Comfort & Climate**: Indoor temperatures, relative humidity, and regional weather design baselines.
- **Inheritance**: Sub-branches inherit ambient thresholds and code references automatically from [`rules.json`](file:///d:/programming/construction%20design/mechanical/rules.json).
