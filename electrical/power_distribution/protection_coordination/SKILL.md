# Short-Circuit Calculation & Protection Discrimination (TCC Curves) Skill

## 1. Scope & Objective
This skill computes prospective symmetrical three-phase short-circuit fault currents along a low-voltage distribution network hierarchy (MDB $\to$ SMDB $\to$ DB), selects switchgear ratings ($I_n, I_{cu}, I_{cs}, I_{cw}$), configures electronic trip unit **LSIG** settings, and validates **Time-Current Characteristic (TCC) coordination** and discrimination under **IEC 60909**, **IEC 60947-2**, **IEEE 242 (Buff Book)**, and **SBC 401**.

---

## 2. Engineering Principles & Governing Equations

### 2.1 Low-Voltage Network Impedance Method (IEC 60909)
The three-phase symmetrical prospective short-circuit current at any bus $k$ is calculated from the cumulative network positive-sequence impedance $Z_k$:

$$I_{sc3\phi} = \frac{c_{\max} \cdot V_{LL}}{\sqrt{3} \cdot Z_k} = \frac{c_{\max} \cdot V_{LL}}{\sqrt{3} \cdot \sqrt{R_k^2 + X_k^2}}$$

Where:
- $c_{\max} = 1.05$ (Voltage factor for maximum short-circuit current).
- $V_{LL}$ = Nominal line-to-line RMS voltage ($400\text{ V}$).

#### 1. Upstream MV Utility Network Impedance
$$Z_{Q} = \frac{c \cdot V_{LL}^2}{S_{sc,grid}}, \quad R_Q \approx 0.1 \cdot X_Q, \quad X_Q \approx 0.995 \cdot Z_Q$$

#### 2. MV/LV Distribution Transformer Impedance
$$Z_T = \frac{u_k\%}{100} \cdot \frac{V_{LL}^2}{S_{rT}}, \quad R_T = \frac{P_{kr}}{3 \cdot I_{r2}^2}, \quad X_T = \sqrt{Z_T^2 - R_T^2}$$

#### 3. Feeder Cable Impedances (MDB $\to$ SMDB $\to$ DB)
For a run of length $L$ (in meters), cross-section $S$ (in $\text{mm}^2$), and $n$ parallel conductors per phase:
$$R_c = \frac{\rho_{20} \cdot 1.25 \cdot L}{n \cdot S} = \frac{0.0225 \cdot L}{n \cdot S}\ [\Omega]$$
$$X_c = \frac{x_L \cdot L}{1000 \cdot n} = \frac{0.08 \cdot L}{1000 \cdot n}\ [\Omega]$$

#### 4. Cumulative Bus Impedance
At any downstream bus $k$:
$$R_k = R_Q + R_T + \sum R_{c,i}, \quad X_k = X_Q + X_T + \sum X_{c,i}$$
$$Z_k = \sqrt{R_k^2 + X_k^2}$$

---

### 2.2 Circuit Breaker Sizing & Breaking Capacity Rules
Every circuit breaker must satisfy two mandatory safety criteria:
1. **Continuous Current**: $I_b \le I_n \le I_z$
2. **Ultimate Breaking Capacity**:
   $$I_{cu} \ge I_{sc3\phi}\ (\text{at breaker incoming terminals})$$
   $$I_{cs} \ge 100\% \cdot I_{cu}\ (\text{for service continuity Category B breakers})$$
3. **Short-Time Withstand (Category B Breakers / ACBs)**:
   $$I_{cw}(1\text{s}) \ge I_{sc3\phi}$$
   Permits delaying the trip unit to achieve total selectivity without damaging the breaker contacts.

---

### 2.3 Electronic Trip Unit (LSIG) Configuration
- **L (Long-Time / Overload)**:
  - Pickup current: $I_r = \text{ratio} \times I_n$
  - Delay: $t_r = 12\text{ s}$ (at $6 \times I_r$)
- **S (Short-Time / Delayed Short Circuit)**:
  - Pickup current: $I_{sd} = \text{ratio} \times I_r$ ($1.5 \text{ to } 10 \times I_r$)
  - Delay: $t_{sd} = 0.1 \text{ to } 0.4\text{ s}$ (Definite time flat delay)
- **I (Instantaneous / High Short Circuit)**:
  - Pickup: $I_i = \text{ratio} \times I_n$ or **OFF** on Upstream ACB to ensure total discrimination up to $I_{cw}$.
- **G (Ground Fault / Earth Leakage)**:
  - Pickup: $I_g = 0.2 \text{ to } 0.6 \times I_n$, delay $t_g = 0.1 \text{ to } 0.3\text{ s}$.

---

### 2.4 Selectivity & Discrimination Verification
For two breakers in series (Upstream ACB/MCCB and Downstream MCCB/MCB):
1. **Current Selectivity**:
   $$I_{sd,up} \ge 1.5 \times I_{sd,down}\quad (\text{or } I_{sd,up} \ge 1.5 \times I_{i,down})$$
2. **Time Selectivity Margin**:
   $$\Delta t = t_{sd,up} - t_{trip,down} \ge 100\text{ ms} = 0.10\text{ s}$$
   This accounts for breaker mechanical unlatching, arcing extinction, and relay tolerance.
3. **Classification**:
   - **Total Discrimination**: Downstream device clears any fault up to $I_{cu,down}$ before upstream initiates trip.
   - **Partial Discrimination**: Discrimination holds up to selectivity limit $I_s$; above $I_s$, both may trip.
   - **No Discrimination**: Curves overlap or $\Delta t < 100\text{ms}$.
