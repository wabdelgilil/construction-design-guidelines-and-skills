---
name: smatv_iptv
description: Satellite Master Antenna TV (SMATV) & IPTV Headend / Distribution Engineering Design Skill complying with EN 50083 and EN 60728.
discipline: electrical
sub_branch: low_current_elv
deliverables:
  - markdown_calc_note: SMATV RF link budget, dish gain, multi-switch cascading, tap attenuation, and IPTV multicast bandwidth calculations.
  - excel_boq_schedule: TV outlet schedule, riser tap schedule, headend equipment list, and priced BOQ.
  - dxf_drawing: SMATV / IPTV System Architecture Riser Diagram, Satellite Headend Dish array, and floor distribution layout.
---

# SMATV & IPTV Distribution Engineering Design Skill

## Overview
This skill executes comprehensive engineering design for Satellite Master Antenna Television (SMATV), Hybrid Fiber-Coaxial (HFC), and IP-based Television (IPTV) distribution networks in compliance with **EN 50083**, **EN 60728**, and **ITU-T J.83**.

## Key Technical Formulations
1. **Satellite Dish & LNB Antenna Gain**:
   - Parabolic dish antenna gain: $G = \eta \left(\frac{\pi D}{\lambda}\right)^2$ (where $\eta \approx 0.65$ efficiency).
   - Carrier-to-Noise Ratio: $C/N \ge 12\text{ dB}$ for digital DVB-S2 satellite signals.
2. **RF Coaxial Link Budget**:
   - Signal level at user outlet constrained strictly between $60.0 \text{ dB}\mu\text{V}$ and $77.0 \text{ dB}\mu\text{V}$ (EN 50083-7).
   - Coaxial cable attenuation ($RG-6$: $18.5\text{ dB}/100\text{m} @ 862\text{MHz}$, $RG-11$: $11.2\text{ dB}/100\text{m}$).
   - Passive tap and splitter loss calculation through multi-floor risers.
3. **IPTV Headend & Multicast Bandwidth**:
   - DVB-S/S2 to IP Gateway Streamers (IGMP v2/v3 Multicast).
   - Bandwidth sizing for 4K UHD ($15-25\text{ Mbps}$) and FHD 1080p ($5-8\text{ Mbps}$) concurrent streams.
   - Core switch IGMP Snooping and querier configuration.
