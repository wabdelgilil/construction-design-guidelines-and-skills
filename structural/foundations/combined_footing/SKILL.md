---
name: combined-footing-design
description: Complete deterministic design of reinforced concrete rectangular combined footings supporting two adjacent columns according to SBC 304, ACI 318, or ECP 203.
---

# Combined Footing Design Skill

## 1. Overview & Purpose
This skill deterministically designs reinforced concrete combined footings supporting two columns.
It computes:
1. Resultant of column loads and exact geometric positioning ($L = 2 x_R$) to ensure a uniform soil pressure distribution.
2. Required contact width ($B$) and area.
3. Shear force diagram (SFD) and maximum negative bending moment ($M_{u,\max}$) at the zero shear point between columns.
4. Required thickness ($T$) and effective depth ($d$) iteratively to satisfy two-way punching shear and one-way beam shear.
5. Continuous top longitudinal reinforcement ($A_s$), bottom longitudinal reinforcement, and transverse reinforcement bands under each column.
6. Multi-deliverables generation (Calculation Note, DXF Drawing, Excel BBS/BOQ, and Revit script).

---

## 2. When to Use This Skill
- When two columns are closely spaced such that individual isolated footings would overlap.
- When an exterior column is near a property line and a strap beam is not suitable.
