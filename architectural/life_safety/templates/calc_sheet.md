# Architectural Life Safety & Means of Egress Calculation Note

## 1. Project & Code Context
- **Discipline**: Architectural Engineering & Fire Protection
- **Governing Standard**: {{code_used}} (SBC 801 / NFPA 101 / IBC Ch. 10)
- **Building / Facility**: {{building_name}}
- **Sprinkler Protection**: {{sprinkler_status}}
- **Building Dimensions**: {{bldg_length}} m $\times$ {{bldg_width}} m (Plan Diagonal = {{bldg_diag}} m)
- **Total Design Occupant Load**: **{{total_occupants}} Persons**

---

## 2. Exit Remoteness & Separation
| Parameter | Value | Standard Requirement | Compliance |
| :--- | :--- | :--- | :--- |
| Building Plan Diagonal ($D$) | {{bldg_diag}} m | $\sqrt{L^2 + W^2}$ | Calculated |
| Minimum Required Exit Separation | {{req_separation}} m | $\ge \frac{1}{3} D$ (Sprinklered) | Code Mandate |
| Provided Separation Distance | {{act_separation}} m | Direct Line-of-Sight Distance | **{{separation_status}}** |

---

## 3. Zone Occupant Loads & Egress Capacity
| Zone / Department | Area ($m^2$) | Load Factor | Occupants | Req Exits | Travel Dist (m) | Door Width (Req / Prov) | Stair Width (Req / Prov) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{{zone_table_rows}}

---

## 4. Overall Life Safety Audit Summary
- **Compliance Status**: **{{overall_status}}**
- Travel distances to exit enclosures meet maximum limits ($\le 76.0$ m).
- Egress door widths and stair capacities exceed minimum occupant flow thresholds.

---

## 5. MEP Fire Alarm & Protection Directives
{{mep_directives}}
