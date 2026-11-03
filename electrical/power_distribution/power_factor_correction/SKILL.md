# Automatic Power Factor Correction (APFC) & Detuned Filter Sizing Skill

## 1. Scope & Objective
This skill sizes **Automatic Power Factor Correction (APFC)** capacitor banks, harmonic detuned series iron-core reactors (7% / 14%), capacitor cell ratings, step progression sequences, switching contactors, and protection devices in compliance with **IEC 61921**, **IEC 60831-1/2**, **IEEE 519**, and **SBC 401**.

---

## 2. Engineering Principles & Governing Equations

### 2.1 Reactive Power Compensation Equation ($Q_c$)
To elevate a facility's operating power factor from initial $\cos \phi_1$ to target $\cos \phi_2$:
$$Q_c = P_{\text{kW}} \times \left( \tan \phi_1 - \tan \phi_2 \right)$$
Where:
- $\phi_1 = \arccos(\text{pf}_1)$ (facility uncorrected power factor, typically $0.78 - 0.85$).
- $\phi_2 = \arccos(\text{pf}_2)$ (target power factor, typically $0.95 - 0.98$).
- $Q_c$ = Total required capacitive reactive power in **kVAR**.

### 2.2 Harmonic Detuning Reactor Factor ($p\%$)
When non-linear loads (VFDs, UPS, IT equipment) are present, capacitors form a parallel resonance circuit with the upstream transformer:
$$f_r = f_1 \times \sqrt{\frac{S_{sc}}{Q_c}}$$
If $f_r$ coincides with a prominent harmonic order ($h=5, 7, 11$), catastrophic voltage resonance and capacitor destruction occur.
- **7% Detuned Reactor ($p = 0.07$)**:
  - Tuning Frequency: $f_{res} = \frac{f_1}{\sqrt{p}} = \frac{60}{\sqrt{0.07}} \approx 227\text{ Hz}$ ($189\text{ Hz}$ at $50\text{ Hz}$).
  - Safely sits below the 5th harmonic ($300\text{ Hz} / 250\text{ Hz}$), preventing resonance and blocking harmonic currents.
- **14% Detuned Reactor ($p = 0.14$)**:
  - Tuning Frequency: $f_{res} \approx 160\text{ Hz}$ ($134\text{ Hz}$ at $50\text{ Hz}$), blocking 3rd harmonic.

### 2.3 Voltage Boost & Heavy-Duty Capacitor Sizing
The series inductive reactor creates an intentional fundamental voltage rise across the capacitor terminals:
$$V_{\text{cap}} = \frac{V_n}{1 - p\%}$$
For a $400\text{V}$ system with $p = 7\%$:
$$V_{\text{cap}} = \frac{400}{1 - 0.07} = 430.1\text{ V}$$
Consequently, standard $400\text{V}$ capacitors will suffer premature dielectric puncture. Heavy-duty capacitors with a minimum nominal rating of **$480\text{V}$ or $525\text{V}$** are mandatory:
$$Q_{\text{effective}} = Q_{\text{rated}} \times \left( \frac{V_n}{V_{\text{rated}}} \right)^2 \times \frac{1}{1 - p}$$

### 2.4 Modular Step Configuration
- Microprocessor-controlled automatic power factor controller with circular or sequential switching algorithm.
- Common step progression:
  $$Q_{\text{step}} = [25, 25, 50, 50, 50, 50]\text{ kVAR} \quad (\text{Total } 250\text{ kVAR})$$
  $$Q_{\text{step}} = [50, 50, 50, 50, 50, 50]\text{ kVAR} \quad (\text{Total } 300\text{ kVAR})$$

### 2.5 Overcurrent & Cable Sizing
Under IEC 61921 and IEC 60831:
$$I_n = \frac{Q_c}{\sqrt{3} \times V_n}$$
Continuous withstand rating must accommodate harmonic overcurrents ($+30\%$) and manufacturing capacitance tolerance ($+10\%$):
$$I_{\text{design}} \ge 1.43 \times I_n$$
Switchgear (MCCBs) and feeder conductors must be sized for $I_{\text{design}}$.
