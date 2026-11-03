# Cable Sizing, Derating Factors & Cable Tray Containment Skill

## 1. Scope & Objective
Automates low-voltage cable sizing for feeders and sub-mains, computes cumulative derating factors ($C_a, C_g, C_s, C_i$), checks iterative voltage drop compliance ($VD\% \le 2\% - 3\%$), validates adiabatic short-circuit thermal capacity, and sizes perforated cable trays / ladders based on physical bundle cross-sections and maximum 40% fill ratio according to **IEC 60364-5-52**, **SBC 401**, and **BS 7671**.

---

## 2. Engineering Formulations

### 2.1 Design Current ($I_b$)
- **Three-Phase Circuits**:
  $$I_b = \frac{P_{\text{load}} \text{ (Watts)}}{\sqrt{3} \times V_{\text{line}} \times \cos\phi}$$
- **Single-Phase Circuits**:
  $$I_b = \frac{P_{\text{load}} \text{ (Watts)}}{V_{\text{phase}} \times \cos\phi}$$

### 2.2 Protective Device Rating ($I_n$)
Select nominal breaker rating such that:
$$I_b \le I_n \le I_z$$

### 2.3 Required Continuous Cable Ampacity ($I_z$)
$$I_z \ge \frac{I_n}{C_{\text{total}}} = \frac{I_n}{C_a \times C_g \times C_s \times C_i}$$
Where:
- $C_a$: Ambient temperature correction factor.
- $C_g$: Grouping / proximity correction factor.
- $C_s$: Soil thermal resistivity factor (for buried cables).
- $C_i$: Installation method factor (tray, conduit, ladder, trench).

### 2.4 Voltage Drop Formulation ($VD$)
- **Three-Phase Circuits**:
  $$\Delta U = \sqrt{3} \times I_b \times L \times (R \cos\phi + X \sin\phi) \quad (\text{V})$$
- **Single-Phase Circuits**:
  $$\Delta U = 2 \times I_b \times L \times (R \cos\phi + X \sin\phi) \quad (\text{V})$$
$$\%VD = \frac{\Delta U}{U_{\text{nominal}}} \times 100 \le \%VD_{\text{allowed}}$$
If $\%VD > \%VD_{\text{allowed}}$, iteratively increment conductor size until compliant.

### 2.5 Short Circuit Thermal Capacity (Adiabatic Equation)
$$S_{\text{min}} = \frac{I_{\text{sc}} \times \sqrt{t}}{k} \quad (\text{mm}^2)$$
Where $k = 143$ for copper XLPE conductors, $t$ is fault clearance time (typically $0.1 - 0.2\text{ s}$).

### 2.6 Cable Tray Sizing
$$\text{Area}_{\text{cables}} = \sum \frac{\pi \cdot D_i^2}{4}$$
$$\text{Required Tray Cross-Section} = \frac{\text{Area}_{\text{cables}}}{\text{Max Fill Ratio (0.40)}} \times (1 + \text{Spare}_{\text{future}})$$
Select standard tray: $\text{Width} \times \text{Depth} \ge \text{Required Tray Cross-Section}$.

---

## 3. Deliverables
1. **Calculation Note**: `output/cables/<feeder>_cable_calculation.md`
2. **AutoCAD DXF Drawing**: `output/cables/<feeder>_cable_tray_layout.dxf` (Tray cross-section, cable layout, fill ratio, ladder elevation)
3. **Excel Workbook**: `output/cables/<feeder>_cable_schedule.xlsx` (Full feeder schedule, derating matrix, tray sizing sheet)
