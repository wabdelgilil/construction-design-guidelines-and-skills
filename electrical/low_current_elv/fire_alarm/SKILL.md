# Addressable Fire Alarm System Design Skill

## 1. Scope & Objective
Automates the engineering design, device placement, loop allocation, and battery backup calculations for an **Analogue Addressable Fire Alarm System (FACS)** conforming to **NFPA 72**, **SBC 801**, and **EN 54**.

---

## 2. Engineering Principles & Formulations

### 2.1 Smoke & Heat Detector Spacing
Under smooth, flat ceilings:
- **Optical Smoke Detectors**:
  $$S \le 9.1\text{ m (30 ft)}, \quad R_{\text{coverage}} = 6.4\text{ m}, \quad A_{\text{max}} = 81.0\text{ m}^2$$
  At least one detector per room or closed compartment.
  For ceiling heights $H > 3.0\text{ m}$ in heat detection, spacing is derated according to NFPA 72 Table 17.6.5.1.
- **Heat Detectors (Rate-of-Rise / Fixed Temp)**: Used in kitchens, boiler rooms, and car parks:
  $$S \le 7.0\text{ m}, \quad A_{\text{max}} = 49.0\text{ m}^2$$

### 2.2 Manual Call Points (Break Glass / MCP)
- Placed on escape routes and within $1.5\text{ m}$ of each exit door and stair landing.
- Maximum travel distance from any point in the building to the nearest MCP: $\le 30.0\text{ m}$.
- Mounting height: $+1.20\text{ m}$ to $+1.40\text{ m}$ AFF.

### 2.3 Notification Appliances (Sounder & Xenon / LED Strobe)
- Audible: Minimum $75\text{ dBA}$ at bed head or $15\text{ dBA}$ above ambient sound.
- Visual Strobe Candela: Sized by room area ($15\text{ cd}$ for up to $6 \times 6\text{ m}$, $30\text{ cd}$ up to $9 \times 9\text{ m}$, $75\text{ cd}$ up to $12 \times 12\text{ m}$).

### 2.4 Addressable Loop Capacity
$$N_{\text{total\_devices}} = N_{\text{smoke}} + N_{\text{heat}} + N_{\text{mcp}} + N_{\text{modules}} + N_{\text{sounders}}$$
$$N_{\text{loops\_required}} = \left\lceil \frac{N_{\text{total\_devices}}}{N_{\text{max\_per\_loop}} \times (1 - \text{Spare}_{\text{margin}})} \right\rceil$$
Where $N_{\text{max\_per\_loop}} = 127$ and spare margin $= 20\%$ (effective max 101 devices/loop).

### 2.5 FACP Standby Battery Capacity (NFPA 72 Equation)
$$C_{\text{battery}} = 1.25 \times \left( I_{\text{quiescent\_standby}} \times 24\text{ h} + I_{\text{alarm}} \times \frac{15}{60}\text{ h} \right) \quad (\text{Ah})$$
Where:
- $I_{\text{quiescent\_standby}}$: Total quiescent standby current of panel and loop devices in Amps.
- $I_{\text{alarm}}$: Full alarm current with all strobes, sounders, and interface relays active.
- $1.25$: Standard safety factor compensating for battery aging and ambient temperature degradation.

---

## 3. Deliverables
1. **Calculation Note**: `output/fire_alarm/<project>_fire_alarm_calculation.md`
2. **AutoCAD DXF Plan**: `output/fire_alarm/<project>_fire_alarm_layout.dxf` (Detectors, MCPs, sounders, addressable loop circuit path)
3. **Excel Schedule**: `output/fire_alarm/<project>_fire_alarm_schedule.xlsx` (Device list, loop loading table, battery sizing sheet)
