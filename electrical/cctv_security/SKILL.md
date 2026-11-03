# CCTV Video Surveillance & Storage Sizing Skill

## 1. Scope & Objective
Automates IP video surveillance camera selection, DORI optical coverage zoning (**Detection, Observation, Recognition, Identification per EN 62676-4**), Network Video Recorder (NVR) storage capacity calculations, PoE network power budgeting, and generates scaled AutoCAD coverage cones, Excel camera schedules, and engineering calculation notes.

---

## 2. Engineering Formulations

### 2.1 DORI Optical Resolution Criteria (EN 62676-4)
$$\text{Max Distance for DORI Target } (m) = \frac{\text{Camera Horizontal Pixels}}{\text{Required PPM} \times 2 \times \tan(\text{HFOV} / 2)}$$
Where:
- **Identification (250 PPM)**: Face/ID recognition at entrances and gates.
- **Recognition (125 PPM)**: High confidence verification at corridors and reception desks.
- **Observation (62.5 PPM)**: Activity and clothing observation in parking lots and courtyards.
- **Detection (25 PPM)**: Vehicle or human presence in perimeter zones.

### 2.2 Lens Focal Length ($f$) & Field of View
$$f = \frac{h_{\text{sensor}} \times D}{W_{\text{target}}} \quad (\text{mm})$$
$$\text{HFOV}^\circ = 2 \times \arctan\left(\frac{h_{\text{sensor}}}{2 f}\right) \times \frac{180}{\pi}$$

### 2.3 NVR Storage Capacity (Terabytes)
$$\text{Storage Required (TB)} = \frac{\sum (N_i \times \text{Bitrate}_i \text{ Mbps}) \times 3600 \times 24 \times \text{Days} \times (1 + \text{Overhead})}{8 \times 10^6 \times \text{RAID Efficiency}}$$
Where:
- $\text{Overhead} \approx 0.10$ for file system indexing and audio.
- $\text{RAID Efficiency} = 0.80$ for RAID 5 or $0.70$ for RAID 6.
- Hard drive selection: Enterprise surveillance HDDs (e.g., 8 TB, 12 TB, 16 TB, 20 TB SATA).

### 2.4 PoE Switch Power Budget
$$P_{\text{PoE\_total}} = \sum (N_{\text{dome}} \times 15.4\text{W} + N_{\text{ptz}} \times 30.0\text{W}) \times 1.25 \quad (\text{Watts})$$

---

## 3. Deliverables
1. **Calculation Note**: `output/cctv/<project>_cctv_calculation.md`
2. **AutoCAD DXF Plan**: `output/cctv/<project>_cctv_layout.dxf` (Camera symbols, directional FOV coverage cones, DORI reach tags)
3. **Excel Workbook**: `output/cctv/<project>_cctv_schedule.xlsx` (Camera schedule, bandwidth & storage calculator, PoE budget)
