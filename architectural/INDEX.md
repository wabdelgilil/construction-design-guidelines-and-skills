# Architectural Engineering Index (Level 1 Parent)

This node serves as the parent index and router for all **Architectural Engineering** design skills.
Shared architectural rules (heights, corridor clearances, stair limits, accessibility standards) are inherited from [`rules.json`](file:///d:/programming/construction%20design/architectural/rules.json).

---

## Sub-Branch Navigation & Dispatch Table

| Sub-Branch | Directory | Primary Scope | Trigger Keywords |
| :--- | :--- | :--- | :--- |
| **Space Planning** | [`space_planning/`](file:///d:/programming/construction%20design/architectural/space_planning/INDEX.md) | Room functional dimensions, spatial adjacency, minimum areas, daylight and natural ventilation | `room`, `area`, `space`, `bedroom`, `living room`, `kitchen`, `ventilation`, `window area` |
| **Life Safety & Egress** | [`life_safety/`](file:///d:/programming/construction%20design/architectural/life_safety/INDEX.md) | Occupant load, egress capacity, exit doors, travel distance, fire stairs, smoke control | `egress`, `exit`, `occupant load`, `travel distance`, `fire door`, `emergency exit`, `escape` |
| **Building Envelope & Facade** | [`building_envelope/`](file:///d:/programming/construction%20design/architectural/building_envelope/INDEX.md) | Thermal insulation (U-values), solar heat gain (SHGC), window-to-wall ratios (WWR), acoustic rating | `facade`, `envelope`, `insulation`, `u-value`, `shgc`, `wwr`, `thermal bridge`, `glazing` |

---

## Shared Rules Summary
- **Clearances**: Habitable room heights ($\ge 2.70 - 2.80\text{ m}$), corridor widths, stair dimensions (riser $\le 175\text{ mm}$, tread $\ge 280\text{ mm}$).
- **Inheritance**: Sub-branches inherit dimensional minimums automatically from [`rules.json`](file:///d:/programming/construction%20design/architectural/rules.json).
