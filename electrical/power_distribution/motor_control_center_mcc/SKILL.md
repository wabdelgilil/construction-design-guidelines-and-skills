# Motor Control Center (MCC) & Motor Feeders / Starters Sizing Skill

## 1. Scope & Objective
This skill performs the complete electrical design, feeder sizing, starter method selection (DOL, Star-Delta, Soft-Starter, VFD), contactor rating (AC-3), overload relay setting, short-circuit protection coordination (**Type 2 Coordination**), and **MCC Panel Cubicle Layout (Form 4b)** in accordance with **IEC 60947-4-1**, **IEC 61439-2**, **SBC 401**, and **NEC Article 430**.

---

## 2. Engineering Principles & Governing Equations

### 2.1 Motor Full-Load Current (FLA / $I_n$)
For a 3-phase induction motor:
$$I_{FLA} = \frac{P_{kW} \times 1000}{\sqrt{3} \times V_{LL} \times \eta \times \cos \phi}$$
Where:
- $V_{LL}$ = Nominal line-to-line RMS voltage ($400\text{ V}$).
- $\eta$ = Motor efficiency at nominal load (typically $0.85 - 0.94$).
- $\cos \phi$ = Operating power factor (typically $0.80 - 0.88$).

### 2.2 Starter Selection Criteria
1. **Direct-On-Line (DOL)**:
   - Permissible for motors with $P \le 7.5\text{ kW}$ (10 HP).
   - Starting Inrush Current: $I_{start} \approx 6.0 - 7.0 \times I_{FLA}$.
   - Starting Torque: $100\%$ nominal.
2. **Star-Delta Starter ($\text{Y}-\Delta$)**:
   - Suitable for motors with $7.5\text{ kW} < P \le 45\text{ kW}$ where low starting torque is acceptable (centrifugal pumps, fans).
   - Inrush Current: $I_{start} \approx \frac{1}{3} I_{DOL} \approx 2.0 - 2.5 \times I_{FLA}$.
   - Starting Torque: $33\%$ nominal.
3. **Solid-State Soft Starter**:
   - Used for high kW constant-speed loads ($> 45\text{ kW}$) to eliminate mechanical shock and water hammer in piping networks.
   - Inrush Current: Adjustable $2.5 - 3.5 \times I_{FLA}$.
4. **Variable Frequency Drive (VFD / Inverter)**:
   - Mandatory for variable torque/flow loads (variable secondary chilled water pumps, AHU supply fans, cooling tower fans).
   - Starting Current: Limited to $1.0 - 1.2 \times I_{FLA}$ (No network voltage dip).
   - Energy Savings: Follows Affinity Laws ($P \propto N^3$).

### 2.3 Contactor AC-3 Utilization Category Sizing (IEC 60947-4-1)
- **DOL Starter**:
  - Main Contactor AC-3 current: $I_e \ge I_{FLA}$.
- **Star-Delta Starter**:
  - Main Contactor (KM1): $I_e \ge \frac{I_{FLA}}{\sqrt{3}} \approx 0.58 \times I_{FLA}$.
  - Delta Contactor (KM2): $I_e \ge \frac{I_{FLA}}{\sqrt{3}} \approx 0.58 \times I_{FLA}$.
  - Star Contactor (KM3): $I_e \ge \frac{I_{FLA}}{3} \approx 0.33 \times I_{FLA}$.

### 2.4 Thermal Overload Relay & Type 2 Coordination
- **Relay Setting**:
  - In DOL or VFD: $I_{setting} = 1.0 \times I_{FLA}$.
  - In Star-Delta (installed under Main Contactor in phase branch): $I_{setting} = \frac{I_{FLA}}{\sqrt{3}} \approx 0.58 \times I_{FLA}$.
- **Type 2 Coordination (IEC 60947-4-1)**:
  - Under short-circuit conditions, the contactor and overload relay must not endanger persons or installations and must remain capable of subsequent operation. Light contact welding is permissible if easily separable.

### 2.5 Motor Feeder Cable & Voltage Drop
- **Continuous Ampacity**:
  $$I_z \ge 1.25 \times I_{FLA}$$
- **Running Voltage Drop**:
  $$\Delta V_{run} \le 3.0\%$$
- **Starting Voltage Drop**:
  $$\Delta V_{start} \le 10.0 - 12.0\%$$
  (To ensure the motor produces sufficient breakaway torque to accelerate the load).
