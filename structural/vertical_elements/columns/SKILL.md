---
name: column-design
description: Complete deterministic design of reinforced concrete short and slender tied columns under axial loads and buckling checks according to SBC 304, ACI 318, or ECP 203.
---

# Reinforced Concrete Column Design Skill

## 1. Overview & Purpose
This skill deterministically designs reinforced concrete columns under axial compression loads.
It computes:
1. Factored axial design load ($P_u$).
2. Slenderness ratio ($\lambda = k L_u / r$) and buckling classification (Short Column vs. Slender Column).
3. Moment magnification ($\delta_{ns}$) if slender.
4. Concrete cross-sectional dimensions ($b \times h$).
5. Longitudinal flexural steel reinforcement ($A_{st}$, bar count, bar diameter $\Phi$).
6. Lateral tie spacing ($s$) and tie diameter.
7. Multi-deliverables generation (Calculation Note, DXF Cross-Section, Excel Schedule, and Revit script).

---

## 2. When to Use This Skill
- Designing reinforced concrete building columns supporting floor beams, slabs, and transferring loads to foundations.
- Input requests such as: *"Design an RC column carrying 1200 kN dead load and 600 kN live load with unbraced height 3.5m under SBC 304"*.
