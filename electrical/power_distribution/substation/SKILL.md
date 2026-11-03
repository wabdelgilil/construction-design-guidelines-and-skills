# Substation, Transformer, Diesel Generator & MDB Design Skill

## 1. Scope & Objective
Automates building maximum demand calculation using standard diversity factors, sizes MV/LV oil/dry-type distribution transformers (13.8kV/400V), computes prospective symmetrical short-circuit current ($I_{sc}$), sizes the Main Distribution Board (MDB) incomer breaker (ACB/MCCB), calculates emergency standby diesel generator capacity (NFPA 110 / ISO 8528) with motor starting inrush checks, and specifies the 4-Pole Automatic Transfer Switch (ATS).

---

## 2. Engineering Formulations

### 2.1 Building Maximum Demand Load
$$\text{Demand Load (kVA)} = \sum \left( \frac{P_i}{\text{PF}_i} \times DF_i \right) \times DF_{\text{overall}}$$
Where:
- $DF_i$: Load-category demand factor (e.g. $0.90$ lighting, $0.50$ sockets, $0.85$ HVAC).
- $DF_{\text{overall}}$: Inter-system diversity factor (typically $0.90$).

### 2.2 Distribution Transformer Sizing & Loading
$$S_{\text{tx\_required}} = \frac{\text{Demand Load (kVA)}}{\text{Target Loading Ratio (0.80)}} \times (1 + \text{Spare}_{\text{future}})$$
Select standard rating $S_n \in [500, 630, 800, 1000, 1250, 1500, 1600, 2000, 2500]\text{ kVA}$.
$$I_{\text{sec\_flc}} = \frac{S_n \times 1000}{\sqrt{3} \times V_{\text{line}}} \quad (\text{A})$$

### 2.3 Prospective 3-Phase Short Circuit Current ($I_{sc}$)
Assuming infinite MV source capacity at transformer primary:
$$I_{sc} = \frac{I_{\text{sec\_flc}}}{u_k\% / 100} = \frac{S_n \times 1000}{\sqrt{3} \times V_{\text{line}} \times (u_k / 100)} \quad (\text{kA})$$
The Main Incomer Breaker breaking capacity must satisfy:
$$I_{cu} \ge 1.25 \times I_{sc}$$

### 2.4 Standby Diesel Generator Sizing
$$\text{Running Emergency Load} = \sum S_{\text{essential}}$$
Largest Motor Starting Inrush:
$$kVA_{\text{start}} = kVA_{\text{largest\_motor}} \times 6.0$$
$$kVA_{\text{gen\_transient}} = \frac{kVA_{\text{start}}}{\%VD_{\text{allowed}} / 100 \times k_{\text{alt}}} \approx 2.0 \times kVA_{\text{start}}$$
$$\text{Required Generator Rating} = \max\left( \frac{\text{Running Emergency Load}}{0.80}, kVA_{\text{gen\_transient}} \right)$$

---

## 3. Deliverables
1. **Calculation Note**: `output/substation/<project>_substation_calculation.md`
2. **AutoCAD DXF SLD**: `output/substation/<project>_power_single_line_diagram.dxf` (Transformer, Generator, ATS, Interlocking, MDB busbar and branch feeders)
3. **Excel Workbook**: `output/substation/<project>_substation_schedule.xlsx` (Load summary, transformer specs, generator sizing, short circuit table)
