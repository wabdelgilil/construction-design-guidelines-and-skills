# Mechanical Plumbing Drainage & Water Supply Design Skill

## 1. Scope & Objective
Automates sanitary drainage sizing using **Drainage Fixture Units (DFU)** and domestic water supply sizing using **Water Supply Fixture Units (WSFU)** & **Hunter's Curve** per SBC 701, IPC, and ECP. Sizes vertical stacks, building drains, and domestic water booster pumps while generating cross-discipline structural sleeve clearances and electrical power tags.

---

## 2. Engineering Formulations

### 2.1 Sanitary Drainage Sizing (DFU)
$$\text{Total DFU} = \sum (N_i \times DFU_i)$$
- Sizing Soil/Waste Stack:
  - 3" stack: Up to 72 DFU (max 3 floors)
  - 4" stack (110 mm OD): Up to 500 DFU
- Horizontal building drain slope: Minimum $1\%$ (10 mm/m) for $\ge 4"$ pipe; $2\%$ for $\le 3"$.

### 2.2 Domestic Water Supply (WSFU & Hunter's Curve)
$$\text{Total WSFU} = \sum (N_i \times WSFU_i)$$
Approximate continuous design flow from Hunter's Curve (Flush Tank system):
$$Q_{\text{design}} (\text{GPM}) = \begin{cases} 
  3.0 \times \sqrt{\text{WSFU}} & \text{if } \text{WSFU} \le 50 \\
  15.0 + 0.35 \times \text{WSFU} & \text{if } 50 < \text{WSFU} \le 200 \\
  40.0 + 0.20 \times \text{WSFU} & \text{if } \text{WSFU} > 200 
\end{cases}$$
$$Q_{\text{design}} (\text{L/s}) = Q_{\text{design}} (\text{GPM}) \times 0.06309$$

### 2.3 Booster Pump Head Calculation
$$H_{\text{total}} = H_{\text{static}} + H_{\text{friction}} + H_{\text{residual}} \quad (\text{m})$$
Where:
- $H_{\text{static}}$: Vertical height from pump to highest fixture (m).
- $H_{\text{friction}} \approx 0.15 \times \text{Total equivalent pipe length (m)}$.
- $H_{\text{residual}} \ge 15.0\text{ m}$ (approx. $1.5\text{ bar}$ at most remote shower/faucet).

### 2.4 Pump Motor Power
$$P_{\text{hydraulic}} = \frac{\rho \cdot g \cdot Q \cdot H}{1000} \quad (\text{kW})$$
$$P_{\text{motor}} = \frac{P_{\text{hydraulic}}}{\eta_{\text{pump}} \times \eta_{\text{motor}}} \quad (\text{kW})$$

### 2.5 Cross-Discipline Interfaces
- **Civil/Structural**: Pipe sleeves passing through foundation walls or grade beams must have internal clearance $\ge D_{pipe} + 50\text{ mm}$, with water-tight link seals, located at mid-depth of beam away from rebar congestion and $> 200\text{ mm}$ clear of column faces.
- **Electrical**: Booster pump control panel (Duty + Standby) electrical feeder (3-Phase 400V) with dry-run float switch interlock.

---

## 3. Deliverables
1. **Calculation Note**: `output/plumbing/<building>_plumbing_calculation.md`
2. **AutoCAD DXF Riser**: `output/plumbing/<building>_plumbing_riser.dxf`
3. **Excel Schedule**: `output/plumbing/<building>_plumbing_schedule.xlsx`
