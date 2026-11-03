# STRUCTURAL DESIGN CALCULATION NOTE
## REINFORCED CONCRETE STRAP (CANTILEVER) FOOTING

---

### 1. General Project & Design Information
- **Active Code**: {{code_used}}
- **Element ID**: {{element_id}}
- **Exterior Column (Col 1 - Boundary)**: {{col1_l}} mm $\times$ {{col1_w}} mm
  - Dead Load: {{col1_dead_kn}} kN | Live Load: {{col1_live_kn}} kN
- **Interior Column (Col 2)**: {{col2_l}} mm $\times$ {{col2_w}} mm
  - Dead Load: {{col2_dead_kn}} kN | Live Load: {{col2_live_kn}} kN
- **Center-to-Center Column Span ($S$)**: {{span_m}} m
- **Allowable Soil Bearing Capacity ($q_{\text{all}}$)**: {{q_all_kpa}} kPa
- **Material Strengths**:
  - Concrete Strength ($f'_c$ / $f_{cu}$): {{fc_mpa}} MPa
  - Steel Yield Strength ($f_y$): {{fy_mpa}} MPa

---

### 2. Overturning Equilibrium & Soil Reactions
- **Exterior Footing Service Reaction ($R_1$)**: {{r1_service_kn}} kN (Amplified due to overturning)
- **Interior Footing Service Reaction ($R_2$)**: {{r2_service_kn}} kN
- **Exterior Footing Factored Reaction ($R_{1u}$)**: {{r1_u_kn}} kN
- **Interior Footing Factored Reaction ($R_{2u}$)**: {{r2_u_kn}} kN

---

### 3. Geotechnical Sizing & Adopted Footing Dimensions
- **Footing 1 (Exterior Boundary Footing)**:
  - Dimensions ($L_1 \times B_1 \times T_1$): **{{f1_l_m}} m $\times$ {{f1_w_m}} m $\times$ {{f1_t_mm}} mm**
  - Transverse Bottom Reinforcement: **{{f1_rebar}}**
  - Soil Pressure Status: **[{{f1_status}}]**
- **Footing 2 (Interior Concentric Footing)**:
  - Dimensions ($L_2 \times B_2 \times T_2$): **{{f2_l_m}} m $\times$ {{f2_w_m}} m $\times$ {{f2_t_mm}} mm**
  - Reinforcement: **{{f2_rebar_l}}** (Long) / **{{f2_rebar_b}}** (Short)
  - Soil Pressure Status: **[{{f2_status}}]**

---

### 4. Strap Beam Structural Design
- **Cross-Section Dimensions**: Width ($b_s$) = **{{strap_b_mm}} mm** | Total Depth ($h_s$) = **{{strap_h_mm}} mm**
- **Maximum Factored Negative Moment ($M_{u,\text{strap}}$)**: **{{strap_moment_knm}} kN$\cdot$m** (Tension on Top)
- **Maximum Factored Shear Force ($V_{u,\text{strap}}$)**: **{{strap_shear_kn}} kN**
- **Top Longitudinal Flexural Reinforcement**:
  - Required Steel Area ($A_s$): {{strap_as_mm2}} mm$^2$
  - **Adopted Top Reinforcement**: **{{strap_top_rebar}}**
- **Shear Stirrup Reinforcement**:
  - **Adopted Stirrups**: **{{strap_stirrups}}**

---

### 5. Final Design Summary
| Component | Dimensions | Reinforcement | Status |
| :--- | :--- | :--- | :--- |
| **Footing 1 (Exterior)** | **{{f1_l_m}} m $\times$ {{f1_w_m}} m $\times$ {{f1_t_mm}} mm** | {{f1_rebar}} | **SAFE** |
| **Footing 2 (Interior)** | **{{f2_l_m}} m $\times$ {{f2_w_m}} m $\times$ {{f2_t_mm}} mm** | {{f2_rebar_l}} | **SAFE** |
| **Strap Beam** | **{{strap_b_mm}} mm $\times$ {{strap_h_mm}} mm** | Top: {{strap_top_rebar}} | **SAFE** |
| **Overall System Status** | **RIGID STRAP ACTION CONFIRMED** | - | **{{overall_status}}** |
