# STRUCTURAL DESIGN CALCULATION NOTE
## REINFORCED CONCRETE ISOLATED FOOTING

---

### 1. General Project & Design Information
- **Active Code**: {{code_used}}
- **Element ID**: {{element_id}}
- **Column Dimensions**: {{col_length}} mm $\times$ {{col_width}} mm
- **Service Column Loads**:
  - Unfactored Dead Load ($P_D$): {{dead_load_kn}} kN
  - Unfactored Live Load ($P_L$): {{live_load_kn}} kN
  - Total Service Load with Self-Weight ($P_{\text{service}}$): {{service_load_kn}} kN
- **Factored Ultimate Load ($P_u$)**: {{ultimate_load_kn}} kN
- **Material Strengths**:
  - Concrete Strength ($f'_c$ / $f_{cu}$): {{fc_mpa}} MPa
  - Rebar Yield Strength ($f_y$): {{fy_mpa}} MPa
  - Concrete Cover: {{cover_mm}} mm
- **Allowable Soil Bearing Capacity ($q_{\text{all}}$)**: {{q_all_kpa}} kPa

---

### 2. Footing Dimensions & Geotechnical Sizing
- **Required Contact Area**: $A_{\text{req}} = \frac{P_{\text{service}}}{q_{\text{all}}} = {{area_req}} \text{ m}^2$
- **Adopted Dimensions**:
  - Length ($L$): **{{length_m}} m** ({{length_mm}} mm)
  - Width ($B$): **{{width_m}} m** ({{width_mm}} mm)
  - Total Thickness ($T$): **{{thickness_mm}} mm**
  - Effective Depth ($d$): **{{depth_mm}} mm**
- **Actual Service Soil Pressure**: $q_{\text{act}} = {{actual_soil_pressure}} \text{ kPa} \le {{q_all_kpa}} \text{ kPa}$ $\longrightarrow$ **[{{soil_status}}]**
- **Net Ultimate Soil Pressure ($q_u$)**: $q_u = {{qu_kpa}} \text{ kPa}$

---

### 3. Shear Safety Checks

#### A. Two-Way Punching Shear
- Critical perimeter ($b_o$ at $d/2$): {{bo_mm}} mm
- Punching Shear Force ($V_u$): {{vu_punch_kn}} kN
- Applied Punching Stress ($v_u$): {{stress_punch_mpa}} MPa
- Permissible Punching Capacity ($\phi v_c$): {{cap_punch_mpa}} MPa
- Safety Demand/Capacity Ratio: **{{punch_ratio}}** $\longrightarrow$ **[{{punching_status}}]**

#### B. One-Way Beam Shear
- Critical Section: at distance $d$ from column face
- Beam Shear Force ($V_u$): {{vu_beam_kn}} kN
- Applied Shear Stress ($v_u$): {{stress_beam_mpa}} MPa
- Permissible Concrete Shear Capacity ($\phi v_c$): {{cap_beam_mpa}} MPa
- Safety Demand/Capacity Ratio: **{{beam_ratio}}** $\longrightarrow$ **[{{beam_shear_status}}]**

---

### 4. Flexure & Steel Reinforcement

#### Long Direction (L):
- Design Factored Moment ($M_{uL}$): {{moment_l_knm}} kN$\cdot$m
- Required Reinforcement ($A_s$): {{as_req_l}} mm$^2$ (Min: {{as_min_l}} mm$^2$)
- Provided Reinforcement ($A_s$): **{{as_prov_l}} mm$^2$**
- **Adopted Reinforcement**: **{{rebar_l_desc}}** (Bottom Layer)
- Spacing ($s$): {{spacing_l_mm}} mm c/c

#### Short Direction (B):
- Design Factored Moment ($M_{uB}$): {{moment_b_knm}} kN$\cdot$m
- Required Reinforcement ($A_s$): {{as_req_b}} mm$^2$ (Min: {{as_min_b}} mm$^2$)
- Provided Reinforcement ($A_s$): **{{as_prov_b}} mm$^2$**
- **Adopted Reinforcement**: **{{rebar_b_desc}}** (Bottom Layer)
- Spacing ($s$): {{spacing_b_mm}} mm c/c

---

### 5. Final Design Summary
| Parameter | Value | Status |
| :--- | :--- | :--- |
| **Footing Dimensions** | **{{length_m}} m $\times$ {{width_m}} m $\times$ {{thickness_mm}} mm** | **SAFE** |
| **Long Dir Reinforcement** | **{{rebar_l_desc}}** | **SAFE** |
| **Short Dir Reinforcement** | **{{rebar_b_desc}}** | **SAFE** |
| **Overall Design Status** | **{{overall_status}}** | **CONFIRMED** |
