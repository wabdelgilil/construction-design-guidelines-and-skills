# Public Address & Voice Alarm (PA/VA) System Calculation Note

**Project**: {{project_name}}  
**Governing Standard**: {{standard_used}}  
**Audio Distribution Standard**: 100 V Constant-Voltage Line  
**Standby Battery Autonomy**: 24.0 Hours Quiescent + 30 Minutes Full Voice Alarm  

---

## 1. Executive Summary & Life Safety Acoustics
This calculation note details the acoustic coverage, Sound Pressure Level (SPL), Speech Transmission Index (STI), 100V line loudspeaker wattage tapping, A/B dual interleaved circuit allocation, Class-D modular power amplifier sizing ($N+1$), and 24V DC emergency battery backup sizing under **BS 5839-8**, **EN 54-16**, and **SBC 801**.

### Key System Metrics
- **Total Broadcast Zones**: {{total_zones}} Zones
- **Total EN 54-24 Loudspeakers**: {{total_speakers}} Loudspeakers
- **Circuit A / Circuit B Allocation**: {{total_spk_a}} on Circuit A | {{total_spk_b}} on Circuit B (Interleaved)
- **Total Audio Loudspeaker Load**: **{{total_audio_w}} W**
- **Installed Amplifier Capacity**: **{{total_amp_w}} W** ({{main_amps}}x {{amp_rating}}W Active + {{standby_amps}}x {{amp_rating}}W Hot-Standby $N+1$)
- **Standby Battery Sizing**: **{{selected_battery_ah}} Ah @ 24V DC** (2x 12V VRLA Blocks).

---

## 2. Acoustic Zoning & Sound Pressure Level (SPL) Schedule

$$\text{SPL}(d) = \text{SPL}_{1\text{W}@1\text{m}} + 10 \log_{10}(P_{\text{tap}}) - 20 \log_{10}(d)$$
$$L_{\text{target}} = \max\left(L_{\text{ambient}} + 10\text{ dB(A)}, 65\text{ dB(A)}\right)$$

| Zone Name | Category | Area (m²) | Ambient (dBA) | Target SPL | Loudspeaker Type | Tap (W) | Total Qty | Circ A | Circ B | Ear SPL (dBA) | SNR (dBA) | STI | Audio Load (W) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{{zone_table_rows}}

---

## 3. Amplifier Sizing & Hot-Standby Redundancy ($N+1$)
Under EN 54-16, the voice alarm system must incorporate automatic hot-standby amplifier failover:
- **Total Continuous Audio Power**: {{total_audio_w}} W
- **Design Headroom & Cable Line Loss Factor**: $1.20$
- **Calculated Required Power**: {{calc_amp_demand_w}} W
- **Selected Modular Class-D Amplifiers**: **{{main_amps}}x {{amp_rating}}W Active Channels**
- **Standby Reserve ($N+1$)**: **1x {{amp_rating}}W Hot-Standby Amplifier** with automatic pilot-tone line monitoring and transfer within $< 100\text{ ms}$.

---

## 4. Emergency Power Supply & Battery Sizing (BS 5839-8)

$$C_{\text{battery}} = \left( I_{\text{quiescent}} \times 24.0\text{ h} + I_{\text{alarm}} \times 0.5\text{ h} \right) \times K_{\text{aging}}$$
$$C_{\text{battery}} = \left( {{i_quiescent}}\text{ A} \times 24.0\text{ h} + {{i_alarm}}\text{ A} \times 0.5\text{ h} \right) \times 1.25 = {{calc_battery_ah}}\text{ Ah}$$

- **Calculated Battery Capacity**: {{calc_battery_ah}} Ah
- **Selected Sealed Lead-Acid (VRLA) Battery**: **{{selected_battery_ah}} Ah @ 24V DC** (2x 12V Blocks in series).

---

## 5. Cross-Discipline Coordination & Commissioning Checklist
{{coordination_checklist}}
