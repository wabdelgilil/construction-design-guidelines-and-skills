# Access Control System (ACS) & Door Security Interlocks Skill

## 1. Scope & Objective
This skill performs the complete electrical and architectural design for **Electronic Access Control Systems (ACS)**, secure door hardware sets, controller sizing, power supply units (PSU), and life safety emergency egress interlocks in compliance with **NFPA 101 (Life Safety Code)**, **UL 294**, and **SBC 801**.

---

## 2. Engineering Principles & Governing Equations

### 2.1 Door Hardware Selection Criteria
1. **Electromagnetic Locks (Maglocks)**:
   - Operating Mode: **Fail-Safe** (loss of power immediately unlocks the door).
   - Interior Doors: $600\text{ lbs}$ holding force ($\approx 2700\text{ N}$), typical draw $500\text{ mA} @ 12\text{V DC}$.
   - Perimeter & High Security: $1200\text{ lbs}$ holding force ($\approx 5300\text{ N}$), typical draw $600\text{ mA} @ 12\text{V DC}$.
2. **Electric Strikes**:
   - Mortised into the door frame; unlatches the latch bolt electronically while permitting manual knob/panic bar egress.
   - Typical draw: $300\text{ mA} @ 12\text{V DC}$.
3. **Peripheral Devices per Controlled Door**:
   - **Ingress**: Proximity Card / Multi-Tech / Biometric Reader ($100-250\text{ mA}$).
   - **Egress**: Request-to-Exit (REX) Motion Sensor / Push Button ($50\text{ mA}$).
   - **Emergency Override**: Green Emergency Break-Glass Unit (BGU) (Double-pole: Pole 1 cuts lock power directly, Pole 2 signals FACP/ACS).
   - **Door Status**: Magnetic Door Contact (DPS) for forced door and held-open alarms.

### 2.2 Life Safety Interlock (Mandatory NFPA 101 / SBC 801)
To prevent trapping occupants during fire emergencies:
$$V_{\text{lock}} = V_{\text{PSU}} \times \text{Relay}_{\text{FACP\_NC}} \times \text{Switch}_{\text{BGU\_NC}}$$
- The FACP interface relay is normally energized (NC). Upon fire alarm activation, the relay drops out, breaking lock power immediately.
- The Break-Glass Unit (BGU) is wired directly in series with the positive lock supply leg at $+1200\text{mm}$ AFF adjacent to the door.

### 2.3 Access Control Power Supply & 4-Hour Battery Sizing
The auxiliary power supply unit (PSU) must support all locks, readers, and controllers, plus maintain 4 hours of backup autonomy during mains failure:
1. **Total Continuous DC Current**:
   $$I_{\text{total}} = \sum I_{\text{locks}} + \sum I_{\text{readers}} + \sum I_{\text{rex}} + \sum I_{\text{controllers}}$$
2. **Minimum Power Supply Rating (A)**:
   $$I_{\text{PSU\_rated}} \ge 1.25 \times I_{\text{total}}$$
3. **Backup Battery Capacity ($C_{\text{Ah}}$)**:
   $$C_{\text{battery\_calc}} = I_{\text{total}} \times t_{\text{standby}} \times 1.25\ (\text{aging factor})$$
   Where $t_{\text{standby}} = 4.0\text{ hours}$.

---

## 3. Standard Field Mounting Heights (AFF)
- **Card / Biometric Reader**: $+1200\text{ mm}$ AFF (unsecured side, latch side).
- **Request to Exit (REX) Button**: $+1200\text{ mm}$ AFF (secured side).
- **Emergency Break Glass Unit (BGU)**: $+1200\text{ mm}$ AFF (secured side, adjacent to REX).
- **Passive Infrared REX (PIR)**: $+2300\text{ mm}$ AFF (centered above door header).
- **Door Controller & PSU Enclosure**: $+1800\text{ mm}$ AFF (in secure Telecom / Electrical room).
