# Electrical Lighting Design & Photometric Layout Skill

## 1. Scope & Objective
Automates indoor photometric calculations using the **Lumen (Zonal Cavity) Method**, computes required fixture quantities, arranges luminaires in an optimal $N_{cols} \times N_{rows}$ grid matching room geometry, checks Lighting Power Density (LPD) compliance against energy codes (SBC 1001, ASHRAE 90.1, ECP), and generates AutoCAD DXF ceiling plans, Excel luminaire schedules, and calculation notes.

---

## 2. Mathematical Formulations

### 2.1 Required Luminous Flux
$$\Phi_{\text{required}} = \frac{E_{\text{target}} \times A}{CU \times MF}$$
Where:
- $E_{\text{target}}$: Target maintained illuminance (Lux = lm/m²).
- $A = L \times W$: Room floor area ($m^2$).
- $CU$: Coefficient of Utilization (typically $0.60 - 0.75$ for direct recessed LED fixtures).
- $MF$: Maintenance factor / Light Loss Factor (typically $0.80$ for clean indoor LED installations).

### 2.2 Fixture Count & Array Grid
$$N_{\text{raw}} = \frac{\Phi_{\text{required}}}{\Phi_{\text{fixture}}}$$
$$N_{\text{rows}} = \text{round}\left(\sqrt{\frac{N_{\text{initial}}}{\text{Aspect Ratio}}}\right), \quad N_{\text{cols}} = \left\lceil \frac{N_{\text{initial}}}{N_{\text{rows}}} \right\rceil$$
$$N_{\text{actual}} = N_{\text{rows}} \times N_{\text{cols}}$$

### 2.3 Fixture Spacing & Uniformity
$$S_x = \frac{L}{N_{\text{cols}}}, \quad S_y = \frac{W}{N_{\text{rows}}}$$
$$\text{Wall Offset}_x = \frac{S_x}{2}, \quad \text{Wall Offset}_y = \frac{S_y}{2}$$
Maximum spacing-to-mounting-height ratio: $\frac{S}{H_{rc}} \le 1.5$.

### 2.4 Lighting Power Density (LPD)
$$LPD = \frac{N_{\text{actual}} \times P_{\text{fixture}}}{A} \le LPD_{\text{limit}} \text{ (W/m}^2\text{)}$$

---

## 3. Deliverables
1. **Calculation Sheet**: `output/lighting/<room>_lighting_calculation.md`
2. **AutoCAD DXF**: `output/lighting/<room>_lighting_layout.dxf` (Fixture symbols, ceiling grid, circuit homeruns)
3. **Excel Workbook**: `output/lighting/<room>_lighting_schedule.xlsx` (Luminaire schedule, circuit parameters, LPD check)
