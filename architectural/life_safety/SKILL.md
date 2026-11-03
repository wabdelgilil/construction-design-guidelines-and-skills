# Architectural Life Safety & Means of Egress Skill

## 1. Scope & Objective
Automates life safety and emergency egress computations per **SBC 801**, **NFPA 101**, and **IBC Chapter 10**. Determines design occupant load, minimum number of fire exits, exit separation distances, required stair and door egress capacities (mm/occupant), travel distances, and produces cross-discipline fire alarm and emergency lighting coordination schedules.

---

## 2. Engineering Formulations

### 2.1 Design Occupant Load
$$\text{Occupant Load} = \sum \left\lceil \frac{\text{Floor Area } (m^2)}{\text{Load Factor } (m^2/\text{person})} \right\rceil$$

### 2.2 Minimum Required Number of Exits
- $1 - 49$ occupants: Minimum $1$ exit (if travel distance and common path limits met)
- $50 - 500$ occupants: Minimum $2$ independent exits
- $501 - 1000$ occupants: Minimum $3$ independent exits
- $> 1000$ occupants: Minimum $4$ independent exits

### 2.3 Exit Separation & Remoteness (Diagonal Rule)
$$D_{\text{separation}} \ge \begin{cases}
  \frac{1}{3} \times D_{\text{building\_diagonal}} & \text{if fully sprinklered} \\
  \frac{1}{2} \times D_{\text{building\_diagonal}} & \text{if unsprinklered}
\end{cases}$$

### 2.4 Egress Width Capacity
$$W_{\text{doors}} = \max(N \times f_{\text{door}}, W_{\text{min\_code}}) \quad (\text{where } W_{\text{min\_code}} = 900\text{ mm})$$
$$W_{\text{stairs}} = \max(N \times f_{\text{stair}}, W_{\text{min\_code}}) \quad (\text{where } W_{\text{min\_code}} = 1120\text{ mm})$$

---

## 3. Deliverables
1. **Calculation Note**: `output/life_safety/<project>_life_safety_note.md`
2. **AutoCAD DXF**: `output/life_safety/<project>_egress_plan.dxf` (Exit doors, egress travel paths, illuminated exit signs, fire alarm manual stations)
3. **Excel Workbook**: `output/life_safety/<project>_life_safety_schedule.xlsx` (Occupant load schedule, egress width calculations, MEP fire alarm matrices)
