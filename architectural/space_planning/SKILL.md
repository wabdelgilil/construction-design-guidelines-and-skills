# Architectural Space Planning & Compliance Audit Skill

## 1. Scope & Objective
Automates architectural room dimension and area audits against building typology rules (SBC 201, IBC, MoMAH, ECP). Evaluates room geometric widths, areas, ceiling heights, fenestration daylight/ventilation ratios, and exports unified MEP requirements (lighting fixture count, socket counts, and HVAC loads) into multi-discipline packages.

---

## 2. Mathematical & Algorithmic Rules

### 2.1 Polygon Area & Perimeter Evaluation
For arbitrary polyline room boundaries:
$$\text{Area} = \frac{1}{2} \left| \sum_{i=0}^{n-1} (x_i y_{i+1} - x_{i+1} y_i) \right|$$

### 2.2 Clearance & Code Compliance Checks
1. Floor Area: $A_{\text{actual}} \ge A_{\text{code\_min}}$
2. Narrowest Dimension: $W_{\text{actual}} \ge W_{\text{code\_min}}$
3. Clear Ceiling Height: $H_{\text{actual}} \ge H_{\text{code\_min}}$
4. Natural Daylighting Ratio: $\frac{A_{\text{window}}}{A_{\text{floor}}} \ge \text{Ratio}_{\text{min}} \text{ (typically } 8\% - 10\%)$

---

## 3. Deliverables
1. **Calculation Note**: `output/architectural/<project>_space_compliance_note.md`
2. **AutoCAD DXF**: `output/architectural/<project>_space_layout.dxf` (Room polygons, dimensional callouts, door clearances)
3. **Excel Workbook**: `output/architectural/<project>_space_schedule.xlsx` (Space audit matrix, code tolerances, MEP design baselines)
