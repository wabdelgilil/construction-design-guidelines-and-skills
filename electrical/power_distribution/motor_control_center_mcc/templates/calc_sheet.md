# Motor Control Center (MCC) & Motor Starters Design Note

**Project**: {{project_name}}  
**Governing Standard**: {{standard_used}}  
**Nominal Voltage & Frequency**: {{nominal_voltage}} V / {{frequency}} Hz (3-Phase)  
**MCC Internal Construction**: {{segregation_form}}  

---

## 1. Executive Summary & Motor Load Profile
This calculation note details the electrical sizing of the Motor Control Center (MCC), individual motor starter topologies (DOL, Star-Delta, Soft-Starter, VFD), contactor AC-3 sizing, thermal overload protection, and feeder voltage drop compliance under **IEC 60947-4-1**, **IEC 61439-2**, and **SBC 401**.

- **Total Connected Motor Capacity**: **{{total_kw}} kW ({{total_hp}} HP)**
- **Total Motor Full Load Current**: **{{total_fla}} A**
- **MCC Incomer Breaker**: **{{incomer_rating}} A (4-Pole ACB/MCCB)**
- **MCC Horizontal Busbar**: **{{busbar_rating}} A (Copper Busbar, 50 kA / 1s)**
- **Total MCC Switchboard Columns**: **{{total_columns}} Columns**

---

## 2. Motor Starters & Equipment Schedule

| Tag | Equipment Description | Power (kW) | Power (HP) | FLA (A) | Starter Method | Inrush (A) | Main Contactor | Overload Setting | Breaker (A) | Cable (mm²) | Run VD% | Start VD% |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{{motor_table_rows}}

---

## 3. Engineering Formulation & Design Methodologies

### 3.1 Motor Full-Load Current (FLA)
$$I_{\text{FLA}} = \frac{P_{\text{kW}} \times 1000}{\sqrt{3} \times V_{\text{LL}} \times \eta \times \cos \phi}$$

### 3.2 Starter Topology Criteria
1. **Direct-On-Line (DOL)** ($\le 7.5\text{ kW}$):
   - $I_{\text{start}} = 6.5 \times I_{\text{FLA}}$
   - Contactor AC-3: $I_e \ge I_{\text{FLA}}$
2. **Star-Delta Starter ($\text{Y}-\Delta$)** ($7.5\text{ kW} < P \le 45\text{ kW}$):
   - $I_{\text{start}} = \frac{1}{3} I_{\text{DOL}} \approx 2.3 \times I_{\text{FLA}}$
   - Main & Delta Contactors: $I_e \ge \frac{I_{\text{FLA}}}{\sqrt{3}} \approx 0.58 \times I_{\text{FLA}}$
   - Star Contactor: $I_e \ge \frac{I_{\text{FLA}}}{3} \approx 0.33 \times I_{\text{FLA}}$
3. **Variable Frequency Drive (VFD)** (Variable Speed Pumps & Fans):
   - $I_{\text{start}} \le 1.15 \times I_{\text{FLA}}$ (Smooth ramping, zero starting dip)
   - Contactor / Drive: $I_e \ge I_{\text{FLA}}$

### 3.3 Voltage Drop Verification
$$\Delta V_{\text{run}} = \frac{\sqrt{3} \times I_{\text{FLA}} \times L \times (R \cos \phi + X \sin \phi)}{V_{\text{LL}}} \times 100\% \le 3.0\%$$
$$\Delta V_{\text{start}} = \frac{\sqrt{3} \times I_{\text{start}} \times L \times (R \cos \phi_{\text{start}} + X \sin \phi_{\text{start}})}{V_{\text{LL}}} \times 100\% \le 12.0\%$$

---

## 4. Cross-Discipline Coordination & Commissioning Checklist
{{coordination_checklist}}
