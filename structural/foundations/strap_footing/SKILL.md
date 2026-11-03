---
name: strap-footing-design
description: Complete deterministic design of reinforced concrete strap (cantilever) footings connecting an eccentric property-line/boundary column to an interior column according to SBC 304, ACI 318, or ECP 203.
---

# Strap / Cantilever Footing Design Skill

## 1. Overview & Purpose
This skill deterministically designs reinforced concrete strap (cantilever) footings for boundary columns on property lines.
It computes:
1. Exterior footing reaction ($R_1$) and interior footing reaction ($R_2$) based on moment equilibrium about the interior column.
2. Geotechnical sizing of Footing 1 ($L_1 \times B_1$) and Footing 2 ($L_2 \times B_2$).
3. Maximum negative bending moment on the connecting strap beam ($M_{u,\text{strap}}$) and maximum shear force ($V_{u,\text{strap}}$).
4. Strap beam concrete cross-section ($b_s \times h_s$), longitudinal top tension steel ($A_s$), and shear stirrup spacing.
5. Transverse reinforcement for both footings.
6. Multi-deliverables generation (Calculation Note, DXF Drawing, Excel BBS/BOQ, and Revit script).

---

## 2. When to Use This Skill
- When a building column is located right on the property line/boundary and the footing cannot project outside the site boundary.
- Input requests such as: *"Design a strap footing for an exterior column 600x300mm carrying 900 kN dead and 450 kN live, connected to an interior column 600x400mm carrying 1400 kN dead and 700 kN live, span 5.5m under SBC 304"*.
