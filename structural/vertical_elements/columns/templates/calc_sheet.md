# STRUCTURAL DESIGN CALCULATION NOTE
## REINFORCED CONCRETE TIED COLUMN

---

### 1. General Project & Design Information
- **Active Code**: {{code_used}}
- **Element ID**: {{element_id}}
- **Service Column Loads**:
  - Unfactored Dead Load ($P_D$): {{dead_load_kn}} kN
  - Unfactored Live Load ($P_L$): {{live_load_kn}} kN
  - Total Service Load ($P_{\text{service}}$): {{service_load_kn}} kN
- **Factored Ultimate Axial Load ($P_u$)**: **{{ultimate_load_kn}} kN**
- **Unbraced Clear Height ($L_u$)**: {{unbraced_len_m}} m (Effective Length Factor $k = {{k_factor}}$)
- **Material Strengths**:
  - Concrete Strength ($f'_c$ / $f_{cu}$): {{fc_mpa}} MPa
  - Rebar Yield Strength ($f_y$): {{fy_mpa}} MPa
  - Concrete Cover: {{cover_mm}} mm

---

### 2. Slenderness & Buckling Classification
- **Radius of Gyration ($r$)**: {{r_gyration_mm}} mm
- **Slenderness Ratio ($\lambda = \frac{k L_u}{r}$)**: **{{slenderness_lambda}}**
- **Slenderness Threshold Limit**: {{slenderness_limit}}
- **Structural Classification**: **{{classification}}**
- **Design Magnified Moment ($M_c$)**: {{magnified_moment_knm}} kN$\cdot$m

---

### 3. Cross-Section Dimensions & Axial Capacity
- **Adopted Dimensions**:
  - Width ($b$): **{{col_b_mm}} mm**
  - Length ($h$): **{{col_l_mm}} mm**
  - Gross Concrete Area ($A_g$): {{gross_area_mm2}} mm$^2$
- **Design Axial Strength ($\phi P_n$)**: **{{design_axial_capacity_kn}} kN**
- **Axial Demand/Capacity Ratio**: **{{capacity_ratio}}** $\longrightarrow$ **[{{axial_status}}]**

---

### 4. Reinforcement Detailing
- **Longitudinal Reinforcement**:
  - Required Steel Area ($A_{st,\text{req}}$): {{as_req_mm2}} mm$^2$ (Min 1.0% = {{as_min_mm2}} mm$^2$)
  - Provided Steel Area ($A_{st,\text{prov}}$): **{{as_prov_mm2}} mm$^2$** (Steel Ratio: **{{steel_ratio_pct}}%**)
  - **Adopted Longitudinal Bars**: **{{longitudinal_rebar_desc}}**
- **Lateral Ties (Stirrups)**:
  - **Adopted Ties**: **{{tie_desc}}**

---

### 5. Final Design Summary
| Parameter | Value | Status |
| :--- | :--- | :--- |
| **Column Cross-Section** | **{{col_b_mm}} mm $\times$ {{col_l_mm}} mm** | **SAFE** |
| **Longitudinal Bars** | **{{longitudinal_rebar_desc}}** | **SAFE** |
| **Lateral Ties** | **{{tie_desc}}** | **SAFE** |
| **Overall Design Status** | **{{overall_status}}** | **CONFIRMED** |
