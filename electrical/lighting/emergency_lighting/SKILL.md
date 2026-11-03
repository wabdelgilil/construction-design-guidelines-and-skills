# Emergency & Exit Lighting (Central Battery System & Self-Contained) Skill

## 1. Scope & Objective
Automates emergency lighting layout along means of egress, exit sign placement, compliance checks against minimum lux standards ($\ge 1.0\text{ Lux}$ on escape routes per **NFPA 101 / BS 5266 / SBC 801**), Central Battery System (CBS) inverter/battery sizing, and cable circuit allocation with fire-resistant wiring.

---

## 2. Engineering Principles & Formulations

### 2.1 Illuminance Criteria along Escape Routes
- **Escape Routes up to 2m width**: $\ge 1.0\text{ Lux}$ along the centerline, and $\ge 0.5\text{ Lux}$ across the central band.
- **Open Anti-Panic Areas ($> 60\text{ m}^2$)**: $\ge 0.5\text{ Lux}$ across core area.
- **Safety Equipment Points**: $\ge 5.0\text{ Lux}$ vertical illumination at manual fire alarm call points, first aid kits, and firefighting equipment.

### 2.2 Luminaire Spacing Along Corridors
$$S_{\text{luminaire}} \le \text{Mounting Height } (H) \times k_{\text{distribution}} \quad (\text{typically } 3.0 \times H \text{ to } 3.5 \times H \text{ for LED emergency optics})$$
Maximum distance from luminaire to exit door or corridor change of direction: $\le 2.0\text{ m}$.

### 2.3 Central Battery System (CBS) Inverter & Battery Capacity
$$P_{\text{emergency\_total}} = \sum (N_i \times P_{\text{luminaire\_i}}) \times (1 + \text{Spare}_{\text{future}})$$
$$C_{\text{battery}} = \frac{P_{\text{emergency\_total}} \times T_{\text{autonomy}} \text{ (hours)}}{\eta_{\text{inverter}} \times V_{\text{battery\_dc}}} \times 1.25 \quad (\text{Ah})$$
Where:
- $T_{\text{autonomy}} = 1.5\text{ hours}$ (90 minutes for NFPA 101 / SBC 801) or $3.0\text{ hours}$ (BS 5266).
- $V_{\text{battery\_dc}} = 220\text{ V DC}$ (or $110\text{ V DC}$).
- $1.25$ is the aging safety factor.

---

## 3. Deliverables
1. **Calculation Note**: `output/emergency_lighting/<project>_emergency_lighting_calculation.md`
2. **AutoCAD DXF Plan**: `output/emergency_lighting/<project>_emergency_lighting_layout.dxf` (Emergency luminaires, illuminated exit signs, CBS circuit homeruns)
3. **Excel Schedule**: `output/emergency_lighting/<project>_cbs_schedule.xlsx` (Luminaire schedule, sub-circuit loading, CBS battery sizing)
