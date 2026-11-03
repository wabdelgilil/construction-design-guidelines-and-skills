---
name: isolated-footing-design
description: Complete deterministic design of reinforced concrete isolated pad footings under concentric axial loads according to SBC 304, ACI 318, or ECP 203.
---

# Isolated Footing Design Skill

## 1. Overview & Purpose
This skill deterministically designs reinforced concrete isolated pad footings under axial column loads.
It computes:
1. Footing plan dimensions ($L \times B$) to ensure allowable soil bearing capacity is not exceeded.
2. Equal projections/cantilevers in both directions.
3. Total thickness ($T$) and effective depth ($d$) iteratively to guarantee two-way punching shear and one-way beam shear capacities are satisfied.
4. Flexural design moments ($M_{uL}, M_{uB}$) and required bottom steel reinforcement ($A_s$, bar counts, spacing, and minimum code steel).
5. Detailed engineering calculation note with verification ratios.

---

## 2. When to Use This Skill
- Designing a single isolated pad footing under a reinforced concrete column.
- Input requests such as: *"Design an isolated footing for a 500x300mm column carrying 1200 kN dead and 600 kN live load with soil bearing capacity 200 kPa under SBC 304"*.

---

## 3. Operational Protocol for AI Agents
1. **Resolve Inherited Parameters**:
   - Use `core/resolver.py` to inherit:
     - $f'_c$ / $f_y$ from `structural/rules.json`.
     - $q_{\text{all}}$, cover, and minimum thickness from `structural/foundations/rules.json`.
     - Code factors from local `rules.json`.
2. **Execute Deterministic Python Engine**:
   - Never compute moments, shears, or rebar mentally.
   - Run `structural/foundations/isolated_footing/scripts/design_engine.py`.
3. **Format Deliverables**:
   - Present the structured calculation note using `templates/calc_sheet.md`.
   - Ensure all safety check statuses (`SAFE` / `REVISE`) are explicitly shown.
