# Mechanical HVAC Cooling Load & Air Distribution Design Skill

## 1. Scope & Objective
Automates space cooling load estimation, sensible and latent heat balance, supply air airflow rate ($CFM$), equipment tonnage ($TR$), diffuser counts, and generates cross-discipline MEP coordination tags for electrical power demand and structural equipment pads.

---

## 2. Engineering Formulations

### 2.1 Heat Gain Components
1. **Building Envelope Conduction**:
   $$Q_{\text{envelope}} = \sum (U \times A \times \Delta T) \quad (\text{W})$$
2. **Solar Radiation through Fenestration**:
   $$Q_{\text{solar}} = A_{\text{glass}} \times SHGF \times SC \quad (\text{W})$$
3. **Internal Heat Gains**:
   - Occupants: $Q_{\text{occ}} = N \times (q_{\text{sensible}} + q_{\text{latent}})$
   - Lighting: $Q_{\text{lights}} = P_{\text{lighting}} \times 1.0$
   - Equipment / Plug Loads: $Q_{\text{equipment}} = P_{\text{appliances}} \times 1.0$
4. **Outdoor Air Ventilation**:
   $$Q_{\text{vent\_sensible}} = 1.08 \times CFM_{\text{oa}} \times (T_{\text{outdoor}} - T_{\text{indoor}})$$
   $$Q_{\text{vent\_latent}} = 4840 \times CFM_{\text{oa}} \times (W_{\text{outdoor}} - W_{\text{indoor}})$$

### 2.2 Total Cooling Capacity & Tonnage
$$Q_{\text{total\_btu}} = (Q_{\text{sensible\_total}} + Q_{\text{latent\_total}}) \times 3.412 \text{ BTU/h per W}$$
$$\text{Capacity (TR)} = \frac{Q_{\text{total\_btu}}}{12,000 \text{ BTU/h/TR}}$$

### 2.3 Airflow Requirements
$$CFM_{\text{supply}} = \frac{Q_{\text{sensible\_btu}}}{1.08 \times \Delta T_{\text{air}}} \quad (\text{where } \Delta T_{\text{air}} = 20^\circ\text{F})$$

### 2.4 Electrical Coordination (Cross-Discipline Interface)
$$\text{Electrical Input Power } (kW) \approx \text{Capacity (TR)} \times 1.2 \text{ kW/TR (for Inverter VRF / Split)}$$
$$\text{MCA (Minimum Circuit Ampacity)} = 1.25 \times I_{\text{compressor}} + \sum I_{\text{fan\_motors}}$$
$$\text{MOP (Maximum Overcurrent Protection)} = 2.25 \times I_{\text{compressor}} + \sum I_{\text{fan\_motors}}$$

---

## 3. Deliverables
1. **Calculation Note**: `output/hvac/<room>_cooling_load_note.md`
2. **AutoCAD DXF**: `output/hvac/<room>_hvac_layout.dxf` (FCU outline, supply & return diffusers, duct runs, electrical disconnect tag)
3. **Excel Schedule**: `output/hvac/<room>_hvac_schedule.xlsx` (Heat load breakdown, equipment schedule, electrical coordination matrix)
