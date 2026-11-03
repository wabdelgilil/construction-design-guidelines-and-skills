# Public Address & Voice Alarm (PA/VA) Evacuation System Skill

## 1. Scope & Objective
This skill designs the building **Public Address & Voice Alarm (PA/VA) System** for life safety emergency evacuation and commercial paging, acoustic Sound Pressure Level (SPL) sizing, Speech Transmission Index (STI) verification, 100V line loudspeaker tapping and A/B interleaved circuit allocation, modular power amplifier sizing ($N+1$), and 24h standby + 30m emergency battery calculations under **BS 5839-8**, **EN 54-16**, **EN 54-24**, **NFPA 72**, and **SBC 801**.

---

## 2. Engineering Principles & Governing Equations

### 2.1 Acoustic Coverage & Sound Pressure Level (SPL)
1. **Signal-to-Noise Ratio (SNR)**:
   For clear voice intelligibility during emergencies, the alarm broadcast must exceed the ambient background noise:
   $$L_{\text{target}} = \max\left(L_{\text{ambient}} + 10\text{ dB(A)}, 65\text{ dB(A)}\right)$$
   With an upper comfort/safety ceiling:
   $$L_{\text{max}} \le 105\text{ dB(A)}$$
2. **Inverse Square Law**:
   The sound pressure level at distance $d$ from a loudspeaker tapped at power $P_{\text{tap}}$ is:
   $$\text{SPL}(d) = \text{SPL}_{1\text{W}@1\text{m}} + 10 \log_{10}(P_{\text{tap}}) - 20 \log_{10}(d)$$
   Where:
   - $\text{SPL}_{1\text{W}@1\text{m}}$ = Loudspeaker acoustic sensitivity (typically $90 - 93\text{ dB(A)}$ for ceiling speakers, $102\text{ dB(A)}$ for horns).
   - $d$ = Distance from speaker to the listener's ear level ($1.5\text{ m}$ AFF).
3. **Speech Intelligibility Criteria**:
   - **Speech Transmission Index**: $\text{STI} \ge 0.50$ (or Common Intelligibility Scale $\text{CIS} \ge 0.70$).
   - Achieved by avoiding reverberant sound masking through dense placement of low-wattage ceiling speakers rather than sparse high-wattage sources.

### 2.2 100V Constant-Voltage Distributed Line
To eliminate voltage drop along extensive cable runs through high-rise buildings:
- Line step-up transformers at the amplifier output step up audio signals to **$100\text{ V RMS}$** (or $70.7\text{ V}$ in North America).
- Loudspeaker multi-tap transformers step down the voltage to drive the voice coil ($1.5\text{W}, 3\text{W}, 6\text{W}, 15\text{W}, 30\text{W}$).

### 2.3 A/B Interleaved Dual Redundant Circuitry (BS 5839-8 / EN 54-16)
To satisfy life safety continuity of broadcast:
- In all primary escape corridors, stairwells, and major public zones, alternate loudspeakers are wired to **Circuit A** and **Circuit B**.
- If a fire breaks, shorts, or severs Circuit A, Circuit B continues operating independently with a minor $3\text{ dB(A)}$ attenuation, maintaining intelligible evacuation instructions throughout the zone.

### 2.4 Power Amplifier Sizing & Redundancy ($N+1$)
1. **Zone Load Summation**:
   $$P_{\text{zone}} = \sum_{i=1}^{N} P_{\text{tap}, i} \times 1.20\ (\text{headroom and line loss})$$
2. **Amplifier Selection**:
   Modular multi-channel Class-D digital amplifiers ($120\text{W}, 240\text{W}, 480\text{W}, 500\text{W}$).
3. **Hot-Standby Backup**:
   At least one dedicated spare amplifier ($N+1$) with automatic pilot-tone line fault detection and instant electronic transfer within $< 100\text{ ms}$.

### 2.5 Standby Battery Autonomy (24h Standby + 30m Full Voice Alarm)
Under BS 5839-8 / SBC 801:
$$C_{\text{battery}} = \left( I_{\text{quiescent}} \times 24.0\text{ h} + I_{\text{full\_alarm}} \times 0.5\text{ h} \right) \times 1.25\ (\text{aging factor})$$
Where:
- $I_{\text{quiescent}}$ = Idle current draw of controller, routers, and preamps at 24V DC.
- $I_{\text{full\_alarm}}$ = Peak DC current delivered to all amplifier channels at rated speech output.
