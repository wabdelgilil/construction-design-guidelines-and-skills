# Earthing (Grounding) & Lightning Protection System (LPS) Skill

## 1. Scope & Objective
Automates soil resistivity analysis, driven rod earthing resistance calculations via **Dwight's Formulation**, parallel mesh grid resistance sizing via **Sverak / Laurent Equation (IEEE 80 / IEC 60364)**, and external Lightning Protection System design using the **Rolling Sphere Method (IEC 62305 / NFPA 780)**.

---

## 2. Engineering Principles & Formulations

### 2.1 Single Vertical Earth Rod Resistance (Dwight's Equation)
$$R_{\text{rod}} = \frac{\rho}{2 \pi L} \left[ \ln\left(\frac{4L}{d}\right) - 1 \right] \quad (\Omega)$$
Where:
- $\rho$: Measured or design soil resistivity ($\Omega \cdot m$).
- $L$: Driven length of rod in contact with earth (m).
- $d$: Diameter of the earth rod (m).

### 2.2 Multiple Interconnected Rods in Parallel
For $N$ identical rods interconnected by buried copper tape at spacing $S \ge 2L$:
$$R_{\text{parallel}} = \frac{R_{\text{rod}}}{N \times \eta} \quad (\Omega)$$
Where $\eta \approx 0.85 - 0.95$ is the grouping efficiency factor.
Target limit:
$$R_{\text{system}} \le R_{\text{target}} \quad (1.0\ \Omega \text{ for substation / data center, } 5.0\ \Omega \text{ for LV buildings})$$

### 2.3 Buried Loop / Grid Conductor Resistance
$$R_{\text{ring}} = \frac{\rho}{\pi^2 L_{\text{ring}}} \left[ \ln\left(\frac{2 L_{\text{ring}}}{\sqrt{2 d_{\text{cond}} h}}\right) \right] \quad (\Omega)$$
Where $h$ is burial depth (typically $0.80\text{ m}$ below ground level) and $L_{\text{ring}}$ is perimeter length.

### 2.4 External Lightning Protection (IEC 62305 Rolling Sphere Method)
- **Air Terminals (Franklin Rods)**: Mounted at highest roof points. The protected zone is the volume not penetrated by a sphere of radius $r$ rolling over the structure:
  $$r = \begin{cases}
    20\text{ m} & \text{for Level I (Hospitals, Explosive facilities)} \\
    30\text{ m} & \text{for Level II} \\
    45\text{ m} & \text{for Level III (Standard commercial/residential)} \\
    60\text{ m} & \text{for Level IV}
  \end{cases}$$
- **Down Conductors**: Number of down conductors:
  $$N_{\text{down}} = \max\left( \left\lceil \frac{\text{Perimeter (m)}}{\text{Max Spacing (m)}} \right\rceil, 2 \right)$$
  Each down conductor terminates in an inspection earth pit with a test link at $+1.5\text{ m}$ AFF.

---

## 3. Deliverables
1. **Calculation Note**: `output/earthing/<project>_earthing_calculation.md`
2. **AutoCAD DXF Plan**: `output/earthing/<project>_earthing_and_lps_layout.dxf` (Earth pits, buried 70mm² copper loop, roof air terminals, rolling sphere radius, down conductors)
3. **Excel Workbook**: `output/earthing/<project>_earthing_schedule.xlsx` (Soil resistance analysis, rod schedule, LPS risk assessment, copper BOQ)
