# STRUCTURAL DESIGN CALCULATION NOTE
## REINFORCED CONCRETE RECTANGULAR COMBINED FOOTING

---

### 1. General Project & Design Information
- **Active Code**: {{code_used}}
- **Element ID**: {{element_id}}
- **Column 1 (Left / Exterior)**: {{col1_l}} mm $\times$ {{col1_w}} mm
  - Loads: $P_{1D} = {{col1_dead_kn}} \text{ kN}$ | $P_{1L} = {{col1_live_kn}} \text{ kN}$
- **Column 2 (Right / Interior)**: {{col2_l}} mm $\times$ {{col2_w}} mm
  - Loads: $P_{2D} = {{col2_dead_kn}} \text{ kN}$ | $P_{2L} = {{col2_live_kn}} \text{ kN}$
- **Center-to-Center Column Span ($S$)**: {{span_m}} m
- **Distance from Left Edge to Column 1 Center ($d_1$)**: {{d1_m}} m
- **Allowable Soil Bearing Capacity ($q_{\text{all}}$)**: {{q_all_kpa}} kPa
- **Material Strengths**:
  - Concrete Strength ($f'_c$ / $f_{cu}$): {{fc_mpa}} MPa
  - Steel Yield Strength ($f_y$): {{fy_mpa}} MPa

---

### 2. Resultant Location & Geotechnical Dimensions (Uniform Soil Pressure)
- **Total Service Load ($P_{\text{service}}$)**: {{service_load_kn}} kN
- **Factored Ultimate Load ($P_u$)**: {{ultimate_load_kn}} kN
- **Adopted Footing Dimensions**:
  - Length ($L$): **{{length_m}} m**
  - Width ($B$): **{{width_m}} m**
  - Total Thickness ($T$): **{{thickness_mm}} mm**
  - Effective Depth ($d$): **{{depth_mm}} mm**
- **Actual Service Soil Pressure**: $q_{\text{act}} = {{actual_soil_pressure}} \text{ kPa} \le {{q_all_kpa}} \text{ kPa}$ $\longrightarrow$ **[SAFE]**
- **Net Ultimate Upward Pressure ($q_u$)**: $q_u = {{qu_kpa}} \text{ kPa}$

---

### 3. Critical Structural Actions (SFD & BMD)
- **Zero Shear Point from Left Edge**: **{{zero_shear_m}} m** (between columns)
- **Maximum Factored Negative Bending Moment ($M_{u,\max}$)**: **{{max_neg_moment_knm}} kN$\cdot$m** (Tension on Top)
- **Maximum Factored One-Way Shear Force ($V_{u,\max}$)**: **{{max_shear_kn}} kN**

---

### 4. Shear Safety Checks
- **Two-Way Punching Shear Status**: **[{{punching_status}}]** (Col 1 Ratio: {{punch_r1}}, Col 2 Ratio: {{punch_r2}})
- **One-Way Beam Shear Status**: **[{{beam_shear_status}}]** (Demand/Capacity Ratio: {{beam_shear_ratio}})

---

### 5. Flexure & Reinforcement Detailing
- **Top Longitudinal Steel (Resisting Negative Moment)**:
  - **{{top_steel_desc}}**
- **Bottom Longitudinal Steel (Resisting Positive Moment)**:
  - **{{bot_steel_desc}}**
- **Transverse Reinforcement Bands**:
  - Under Column 1: **{{trans1_desc}}**
  - Under Column 2: **{{trans2_desc}}**

---

### 6. Final Design Summary
| Parameter | Value | Status |
| :--- | :--- | :--- |
| **Combined Footing Size** | **{{length_m}} m $\times$ {{width_m}} m $\times$ {{thickness_mm}} mm** | **SAFE** |
| **Top Longitudinal Steel** | {{top_steel_desc}} | **SAFE** |
| **Bottom Longitudinal Steel**| {{bot_steel_desc}} | **SAFE** |
| **Overall Design Status** | **{{overall_status}}** | **CONFIRMED** |
