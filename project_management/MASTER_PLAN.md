# Master Implementation Plan (Detailed Roadmap & Work Breakdown)
## Hierarchical Multi-Disciplinary Engineering Design Tree (Master Engine)

---

## Architecture & Governance Reference
- **Core Strategy**: Level-by-Level Top-Down Construction (Level 0 Root $\to$ Level 1 Parents $\to$ Level 2 Sub-branches $\to$ Level 3 Leaf Skills).
- **Core Decoupling**: Universal Engineering Design Logic decoupled from Node-Scoped Code Profiles (`rules.json` per node) and Building Typologies (`project_root.json`).
- **Complete Deliverables Package**: Every leaf skill produces:
  1. Technical Calculation Note (`calc_sheet.md` with LaTeX formulas).
  2. Native AutoCAD 2D Drawing (`.dxf` via `ezdxf` with standard engineering layers).
  3. Interactive Excel Workbook (`.xlsx` via `openpyxl` with live formulas, BBS, and BOQ).
  4. Autodesk Revit Parameter Placement Script (`.py`).
- **Language Policy**: Project files, code, and documentation in English; conversation in Arabic.

---

## SECTION 1: COMPLETED PHASES (FOUNDATION & PROTOTYPE) [100% DONE]

### [x] Phase 1: Level 0 (Root) & Level 1 (Discipline Parents) + Context Engine
- [x] **1.1 Project Root (`project_root.json` & `INDEX.md`)**:
  - [x] Global configuration file declaring `active_code` ("SBC"), `building_type` ("residential"), and `unit_system` ("SI").
  - [x] Top-level dispatcher routing user queries to the 4 main discipline parents.
- [x] **1.2 The Four Discipline Parents (Level 1)**:
  - [x] `structural/`: `INDEX.md` dispatcher + `rules.json` (material strengths $f'_c, f_{cu}, f_y$, concrete densities, load factors).
  - [x] `electrical/`: `INDEX.md` dispatcher + `rules.json` (nominal voltages 230V/400V, 220V/380V, 120V/208V, frequency, power factor).
  - [x] `mechanical/`: `INDEX.md` dispatcher + `rules.json` (indoor comfort setpoints, regional outdoor design temperatures, supply pressures).
  - [x] `architectural/`: `INDEX.md` dispatcher + `rules.json` (ceiling heights, corridor clearances, stair risers/treads, accessibility slopes).
- [x] **1.3 Core Hierarchical Context Resolver (`core/resolver.py`)**:
  - [x] Dynamic context inheritance traversing root $\to$ parent $\to$ branch $\to$ leaf.
  - [x] Automated unit test suite (`tests/test_resolver.py` - 6 tests passed).

### [x] Phase 2: Structural Foundations Sub-Branch & Isolated Footing Leaf Skill
- [x] **2.1 Foundations Sub-Branch (`structural/foundations/`)**:
  - [x] `INDEX.md`: Sub-branch dispatcher routing between standard pad footings, combined, strap, raft, piles, and machine foundations.
  - [x] `rules.json`: Code-partitioned foundation rules ($q_{\text{all}}$, soil cover, minimum blinding thickness).
- [x] **2.2 Isolated Footing Universal Leaf Skill (`structural/foundations/isolated_footing/`)**:
  - [x] `SKILL.md`: AI operational guidance and prompt protocol.
  - [x] `rules.json`: Node-scoped limits for punching, shear, and flexure factors (SBC, ACI, ECP).
  - [x] `scripts/design_engine.py`: Deterministic engine with equal cantilever sizing, iterative thickness selection, and flexural detailing.
  - [x] `templates/calc_sheet.md`: Markdown and LaTeX engineering calculation note template.
  - [x] Automated benchmark unit tests (`tests/test_isolated_footing.py` - 3 tests passed).

### [x] Phase 3: Complete Engineering Deliverables Subsystem (CAD, Excel, BOQ & Revit)
- [x] **3.1 Core Exporters (`core/exporters/`)**:
  - [x] `dxf_writer.py`: Standardized AutoCAD `.dxf` drawing generator with ACI color layers (`S-CONC`, `S-REBAR`, `S-COLUMN`, `S-DIMS`, `S-TEXT`).
  - [x] `excel_writer.py`: Corporate styled `.xlsx` workbook generator with corporate banners and live formulas.
  - [x] `boq_engine.py`: Reusable civil material take-off, steel rebar unit weights, and Bar Bending Schedule (BBS) engine.
- [x] **3.2 Isolated Footing Concrete Exporters**:
  - [x] `exporters/dxf_exporter.py`: AutoCAD 2D drawing (Plan View + Longitudinal Section + Cross-Section + Hooks).
  - [x] `exporters/excel_exporter.py`: 3-tab Excel workbook (Design Calculation + Bar Bending Schedule + Itemized BOQ).
  - [x] `exporters/revit_exporter.py`: Python script for Autodesk Revit family instantiation.
  - [x] `scripts/run_design.py`: End-to-end multi-deliverables generation pipeline.
  - [x] Exporters verification test suite (`tests/test_exporters.py` - 3 tests passed).

### [x] Phase 4: Upstream Master Engines & Knowledge Memory Bank
- [x] **4.1 Upstream Knowledge & Heuristics Memory (`core/memory/`)**:
  - [x] `domain_heuristics.json`: Field-tested engineering rules across all 4 disciplines.
  - [x] `scripting_tricks.json`: Tested CAD, ezdxf, openpyxl, and geometry tricks.
- [x] **4.2 Cross-Discipline Coordination & Interface Subsystem (`core/coordination/`)**:
  - [x] `interface_registry.json`: Codified cross-discipline interface bus (HVAC $\to$ Electrical thermostats/isolators, Plumbing $\to$ Electrical water heaters/pumps, Plumbing $\to$ Structural pipe sleeves, Elevator structural pits).
  - [x] `coordinator.py`: Automated query engine and checklist generator preventing cross-discipline omissions.
  - [x] Unit test suite (`tests/test_coordination.py` - 3 tests passed).
- [x] **4.3 Universal CAD Space & Geometry Extractor (`core/cad_engine/`)**:
  - [x] `space_extractor.py`: Point-in-Polygon (Ray Casting) & Shoelace area parser extracting room boundaries, areas, and centroid coordinates.
- [x] **4.4 Universal Electrical Design Engines**:
  - [x] `electrical/power_distribution/scripts/panel_balancer.py`: 3-Phase load balancing algorithm.
  - [x] `electrical/lighting/scripts/lumen_engine.py`: Lumen method room fixture count and coordinate grid generator.
  - [x] `electrical/cables/scripts/cable_engine.py`: Cable ampacity sizing and iterative voltage drop compliance.
  - [x] Automated test suite (total 19 tests in repository passing in 0.141s).

---

## SECTION 2: DETAILED EXECUTION ROADMAP (CURRENT & UPCOMING PHASES)

```text
Target Tree Milestones:
├── TRACK A: STRUCTURAL ENGINEERING (Next Steps)
│   ├── A1: Strap Footing (Property Line / Cantilever Footing) [Phase 5]
│   ├── A2: Combined Footings (Two-Column Symmetrical & Trapezoidal) [Phase 6]
│   └── A3: Columns (Short Columns, Slenderness, Interaction Diagrams) [Phase 7]
│
├── TRACK B: ELECTRICAL ENGINEERING (Next Steps)
│   ├── B1: Small Power & Socket Circuit Leaf Skill [Phase 8]
│   ├── B2: Lighting Design & Switching Layout Leaf Skill [Phase 9]
│   └── B3: [Specialized] Hospital Operating Room IPS Panel [Phase 10]
│
├── TRACK C: MECHANICAL ENGINEERING (Next Steps)
│   ├── C1: HVAC Room Heat Load & Airflow (CFM) Calculation [Phase 11]
│   └── C2: Plumbing Water Supply & Drainage Fixture Units (WSFU/DFU) [Phase 12]
│
└── TRACK D: ARCHITECTURAL ENGINEERING (Next Steps)
    ├── D1: Space Planning & Daylight/Ventilation Compliance [Phase 13]
    └── D2: Life Safety, Occupant Load & Egress Capacity [Phase 14]
```

---

### [x] Phase 5: Structural - Strap Footing Design Skill (قواعد الجار والشدادات)
- [x] **Task 5.1: Sub-Branch Scaffolding & Rules**
  - [x] Create `structural/foundations/strap_footing/`
  - [x] Create `rules.json`: Code parameters for strap beam depth/width, cantilever moment distribution, shear limits.
  - [x] Create `SKILL.md`: AI operational guidance for boundary column constraints.
- [x] **Task 5.2: Deterministic Calculation Engine (`scripts/design_engine.py`)**
  - [x] Calculate exterior and interior footing reactions taking moments about interior column center.
  - [x] Size exterior footing (eccentric) and interior footing (concentric) areas to equalize soil contact pressures.
  - [x] Compute negative bending moment diagram and shear force along the connecting strap beam.
  - [x] Size strap beam cross-section ($b \times h$) and top longitudinal flexural reinforcement ($A_s$).
  - [x] Design shear stirrups for strap beam.
- [x] **Task 5.3: Multi-Deliverable Exporters**
  - [x] Create `templates/calc_sheet.md`: Markdown/LaTeX calculation note.
  - [x] Create `exporters/dxf_exporter.py`: AutoCAD drawing showing plan layout of both footings and strap beam + section showing top rebar and stirrups.
  - [x] Create `exporters/excel_exporter.py`: Excel workbook with BBS and BOQ.
  - [x] Create `scripts/run_design.py`: End-to-end multi-deliverables generation pipeline.
- [x] **Task 5.4: Unit Tests & Verification**
  - [x] Create `tests/test_strap_footing.py`: Verify overturning stability, soil pressures, and strap beam shear capacity (2 tests passed).

---

### [x] Phase 6: Structural - Combined Footing Design Skill (القواعد المشتركة)
- [x] **Task 6.1: Sub-Branch Scaffolding & Rules**
  - [x] Create `structural/foundations/combined_footing/`
  - [x] Create `rules.json`: Code parameters for longitudinal beam action and transverse cantilever action.
  - [x] Create `SKILL.md`: AI operational prompt.
- [x] **Task 6.2: Deterministic Calculation Engine (`scripts/design_engine.py`)**
  - [x] Locate resultant of column loads $R = P_1 + P_2$ and centroid of loads $\bar{x}$.
  - [x] Set footing length $L = 2 \bar{x}$ to achieve uniform soil pressure distribution.
  - [x] Calculate required width $B = R / (L \times q_{\text{all}})$.
  - [x] Draw shear force diagram (SFD) and bending moment diagram (BMD) along length $L$.
  - [x] Calculate maximum negative moment between columns and positive moments under columns.
  - [x] Verify two-way punching shear under each column and one-way beam shear at critical sections.
  - [x] Design longitudinal top and bottom steel + transverse reinforcement under each column.
- [x] **Task 6.3: Multi-Deliverable Exporters**
  - [x] Create `templates/calc_sheet.md`, `exporters/dxf_exporter.py`, `exporters/excel_exporter.py`, `scripts/run_design.py`.
- [x] **Task 6.4: Unit Tests & Verification**
  - [x] Create `tests/test_combined_footing.py`: Verify shear diagrams, soil uniformity, and reinforcement areas (2 tests passed).

---

### [x] Phase 7: Structural - Reinforced Concrete Columns (تصميم الأعمدة الخرسانية)
- [x] **Task 7.1: Sub-Branch Scaffolding & Rules**
  - [x] Create `structural/vertical_elements/columns/`
  - [x] Create `rules.json`: Reinforcement ratios ($\rho_{\min} = 1.0\%$, $\rho_{\max} = 4.0\% - 6.0\%$), tie spacing rules, and buckling reduction factors.
  - [x] Create `SKILL.md`: AI operational prompt.
- [x] **Task 7.2: Deterministic Calculation Engine (`scripts/design_engine.py`)**
  - [x] Axial load capacity of short tied columns: $P_n = 0.80 \phi [0.85 f'_c (A_g - A_{st}) + f_y A_{st}]$.
  - [x] Slenderness ratio check: $k L_u / r$ vs non-sway / sway limits to evaluate buckling and moment magnification ($\delta_{ns} M_2$).
  - [x] Concrete section sizing ($b \times h$).
  - [x] Longitudinal bar arrangement and tie/link spacing.
- [x] **Task 7.3: Multi-Deliverable Exporters**
  - [x] Create `templates/calc_sheet.md`, `exporters/dxf_exporter.py` (Column cross-section detailing), `exporters/excel_exporter.py`, `scripts/run_design.py`.
- [x] **Task 7.4: Unit Tests & Verification**
  - [x] Create `tests/test_columns.py`: Test short concentric column, slender column moment magnification, and ECP code (3 tests passed).

---

### [x] Phase 8: Electrical - Small Power & Socket Circuit Design Skill (الأفياش والمخارج)
*Goal: Automatic branch circuit design, socket grouping, mounting heights, and dedicated kitchen/wet area feeds.*
- [x] **Task 8.1: Leaf Skill Scaffolding & Rules**
  - [x] Create `electrical/power_distribution/sockets/`
  - [x] Create `rules.json`: Maximum outlets per circuit (10 for SBC/IEC, 8 for NEC), standard mounting heights, IP ratings for wet areas.
  - [x] Create `SKILL.md`: AI operational guidance.
- [x] **Task 8.2: Deterministic Design Engine (`scripts/design_engine.py`)**
  - [x] Group general sockets into branch circuits (max 10 outlets or 1800 VA).
  - [x] Assign dedicated branch circuits for water heaters, kitchen appliances, and AC units.
  - [x] Calculate circuit design current $I_b$, select breaker rating $I_n$, and cable size.
  - [x] Check voltage drop for farthest socket.
- [x] **Task 8.3: Multi-Deliverable Exporters**
  - [x] Create `templates/calc_sheet.md`, `exporters/dxf_exporter.py` (Distribution board schematic & socket symbols), `exporters/excel_exporter.py` (Panel schedule & BOQ), `scripts/run_design.py`.
- [x] **Task 8.4: Unit Tests**
  - [x] Create `tests/test_sockets.py`: Validate circuit grouping limits and dedicated appliance allocation (4 tests passed).

---

### [x] Phase 9: Electrical - Lighting Layout & Circuiting (الإنارة وتوزيع الدوائر)
*Goal: Turn LumenEngine calculations into complete CAD layouts, switching controls, and circuit connections.*
- [x] **Task 9.1: Leaf Skill Scaffolding & Rules**
  - [x] Create `electrical/lighting/` complete skill files.
  - [x] Create `rules.json`: Code lux standards, maximum Lighting Power Density (LPD W/m²) for SBC, ASHRAE, ECP.
  - [x] Create `SKILL.md`: AI operational prompt.
- [x] **Task 9.2: Complete CAD & Schedule Generation**
  - [x] Connect `lumen_engine.py` to `dxf_writer.py` to place standard fixture blocks, coordinates, dimensions, and homerun lines.
  - [x] Generate Excel lighting fixture schedule with wattage, CCT, lumens, LPD check, and exact ceiling coordinates.
  - [x] Create `templates/calc_sheet.md` and `scripts/run_design.py`.
- [x] **Task 9.3: Unit Tests**
  - [x] Create `tests/test_lighting_skill.py`: Validate Lumen calculations and deliverables (2 tests passed).

---

### [x] Phase 10: Electrical [Specialized] - Hospital Operating Room IPS Panel (لوحات العزل الطبي)
*Goal: Dedicated specialized leaf for hospital operating rooms and ICUs under NFPA 99, IEC 60364-7-710, and SBC 401.*
- [x] **Task 10.1: Specialized Leaf Scaffolding**
  - [x] Create `electrical/power_distribution/medical_isolated_power_ips/`
  - [x] Create `rules.json`: Medical isolation transformer capacity (3.15 kVA - 10 kVA), insulation monitoring device (IMD) threshold (50 k$\Omega$), maximum touch voltage, equipotential bonding ($R \le 0.1\ \Omega$).
  - [x] Create `SKILL.md`: AI operational guidance.
- [x] **Task 10.2: Calculation Engine (`scripts/design_engine.py`)**
  - [x] Calculate operating theater total connected load (surgical lights, bypass machines, electrocautery, monitors).
  - [x] Size isolation transformer, primary Curve D breaker, and 2-Pole double break branch circuits.
  - [x] Verify leakage current ($< 0.5\text{ mA}$) and POAG equipotential bonding pins.
- [x] **Task 10.3: Multi-Deliverables & Tests**
  - [x] Calculation note `templates/calc_sheet.md`, Single Line Diagram (SLD) `exporters/dxf_exporter.py`, Excel schedule `exporters/excel_exporter.py`, `scripts/run_design.py`.
  - [x] Create `tests/test_medical_ips.py`: (3 tests passed).

---

### [x] Phase 11: Mechanical - HVAC Room Heat Load & CFM Sizing (الأحمال الحرارية والتكييف)
*Goal: Room-by-room sensible and latent heat gain calculation and supply air CFM / cooling ton sizing.*
- [x] **Task 11.1: Leaf Skill Scaffolding & Rules**
  - [x] Create `mechanical/hvac/heat_load/`
  - [x] Create `rules.json`: Envelope U-values, occupancy heat dissipation (sensible 75W, latent 55W), lighting heat, equipment heat, outdoor design conditions.
  - [x] Create `SKILL.md`: AI operational prompt.
- [x] **Task 11.2: Deterministic Calculation Engine (`scripts/design_engine.py`)**
  - [x] Wall/Roof conductive heat gain: $Q = U \times A \times \Delta T$.
  - [x] Solar heat gain through glass: $Q = A \times \text{SHGF} \times SC$.
  - [x] Internal heat gain: People + Lighting + Equipment.
  - [x] Fresh air ventilation sensible and latent load (ASHRAE 62.1 / SBC 501).
  - [x] Total cooling load in Tons of Refrigeration (TR) and Supply Airflow CFM ($Q_s = 1.08 \times \text{CFM} \times \Delta T$).
  - [x] Sizing 4-way square diffusers and return air grilles.
  - [x] Electrical feed coordination (kW, MCA, MOP) and thermostat/isolator mounting heights.
- [x] **Task 11.3: Multi-Deliverables & Tests**
  - [x] Calculation note `templates/calc_sheet.md`, HVAC Schedule & MEP Interface Excel `exporters/excel_exporter.py`, AutoCAD Ducting & Diffusers DXF `exporters/dxf_exporter.py`, `scripts/run_design.py`.
  - [x] Unit tests in `tests/test_hvac.py`: (3 tests passed).

---

### [x] Phase 12: Mechanical - Plumbing Water Supply & Drainage (التغذية والصرف الصحي)
*Goal: Domestic water booster pump head/flow sizing and drainage pipe sizing via WSFU / DFU.*
- [x] **Task 12.1: Leaf Skill Scaffolding & Rules**
  - [x] Create `mechanical/plumbing/` skill files.
  - [x] Create `rules.json`: Water Supply Fixture Units (WSFU) per fixture, Drainage Fixture Units (DFU), minimum trap sizes, stack capacities.
  - [x] Create `SKILL.md`: AI operational guidance.
- [x] **Task 12.2: Calculation Engine (`scripts/design_engine.py`)**
  - [x] Sum WSFU and convert to peak flow (GPM / L/s) using Hunter's Curve.
  - [x] Friction head loss and total pump head ($H_{\text{static}} + H_{\text{friction}} + H_{\text{residual}}$).
  - [x] Booster pump flow ($Q$), head ($H$), and motor kW (Duty + Standby).
  - [x] Drainage stack and building drain sizing from cumulative DFU.
  - [x] Civil/Structural pipe sleeve coordination callouts (grade beam penetrations, link-seals, column clearance $> 200\text{ mm}$).
- [x] **Task 12.3: Multi-Deliverables & Tests**
  - [x] Calculation note `templates/calc_sheet.md`, Plumbing Riser Schedule Excel `exporters/excel_exporter.py`, AutoCAD Plumbing Riser & Sleeves DXF `exporters/dxf_exporter.py`, `scripts/run_design.py`.
  - [x] Unit tests in `tests/test_plumbing.py`: (3 tests passed).

---

### [x] Phase 13: Architectural - Space Planning & Area Compliance (تخطيط الفراغات)
*Goal: Audit room areas, aspect ratios, daylight ratios, ceiling heights, and natural ventilation against typology codes.*
- [x] **Task 13.1: Leaf Skill Scaffolding & Rules**
  - [x] Create `architectural/space_planning/` skill files.
  - [x] Create `rules.json`: Minimum room areas, linear widths, ceiling heights, and glazing ratios for Residential and Commercial Office typologies.
  - [x] Create `SKILL.md`: AI operational prompt.
- [x] **Task 13.2: Calculation Engine (`scripts/design_engine.py`)**
  - [x] Audits net area, narrowest dimension, clear ceiling height, and daylight/ventilation glazing ratios.
  - [x] Generates upstream MEP preliminary sizing directives (lighting circuits, HVAC cooling capacity, wet area coordinates).
- [x] **Task 13.3: Multi-Deliverables & Tests**
  - [x] Space Compliance Calculation Note `templates/calc_sheet.md`, Space Schedule Excel `exporters/excel_exporter.py`, AutoCAD Space Layout DXF `exporters/dxf_exporter.py`, `scripts/run_design.py`.
  - [x] Unit tests in `tests/test_space_planning.py`: (3 tests passed).

---

### [x] Phase 14: Architectural - Life Safety & Egress Capacity (كود البناء والسلامة)
*Goal: Calculate occupant load, egress width capacity, number of required exits, exit remoteness, and travel distances.*
- [x] **Task 14.1: Leaf Skill Scaffolding & Rules**
  - [x] Create `architectural/life_safety/` skill files.
  - [x] Create `rules.json`: Occupant load factors ($m^2/\text{person}$), egress width capacity factors ($3.8 - 5.1\text{ mm/person}$ doors, $5.1 - 7.6\text{ mm/person}$ stairs), maximum travel distances (76m sprinklered, 61m unsprinklered).
  - [x] Create `SKILL.md`: AI operational prompt.
- [x] **Task 14.2: Calculation Engine (`scripts/design_engine.py`)**
  - [x] Calculate total occupant load per floor/zone.
  - [x] Determine minimum required exits ($1$ for $\le 49$, $2$ for $50-500$, $3$ for $501-1000$, $4$ for $>1000$).
  - [x] Sizing minimum exit door clear widths and stair widths.
  - [x] Remoteness check using Diagonal Rule ($D_{\text{separation}} \ge \frac{1}{3} D_{\text{diagonal}}$).
  - [x] Cross-discipline fire protection directives (illuminated EXIT signs, manual pull stations, fire sprinkler densities).
- [x] **Task 14.3: Multi-Deliverables & Tests**
  - [x] Life Safety Calculation Note `templates/calc_sheet.md`, Egress Schedule Excel `exporters/excel_exporter.py`, AutoCAD Egress & Separation Plan DXF `exporters/dxf_exporter.py`, `scripts/run_design.py`.
  - [x] Unit tests in `tests/test_life_safety.py`: (3 tests passed).

---

## SECTION 3: PROJECT MONITORING MATRIX

| Track | Discipline | Level 2 Branch | Level 3 Leaf Skill | Status | Deliverables |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | Structural | `foundations/` | `isolated_footing/` | **COMPLETED** | Calc Note, DXF, XLSX (BBS+BOQ), Revit |
| **A** | Structural | `foundations/` | `strap_footing/` | **COMPLETED** | Calc Note, DXF, XLSX (BBS+BOQ) |
| **A** | Structural | `foundations/` | `combined_footing/` | **COMPLETED** | Calc Note, DXF, XLSX (BBS+BOQ) |
| **A** | Structural | `vertical/` | `columns/` | **COMPLETED** | Calc Note, DXF, XLSX |
| **B** | Electrical | `power/` | `sockets/` | **COMPLETED** | Calc Note, DXF, XLSX |
| **B** | Electrical | `lighting/` | `lighting_layout/` | **COMPLETED** | Calc Note, DXF, XLSX (LPD+Coords) |
| **B** | Electrical | `power/` | `medical_isolated_ips/`| **COMPLETED** | Calc Note, SLD DXF, XLSX Schedule |
| **B** | Electrical | `cables/` | `cable_and_tray/` | **COMPLETED** | Calc Note, DXF Tray, XLSX Schedule |
| **B** | Electrical | `substation/` | `transformer_generator_mdb/` | **COMPLETED** | Calc Note, DXF Layout, XLSX Schedule |
| **B** | Electrical | `earthing/` | `grid_and_lps/` | **COMPLETED** | Calc Note, DXF Grid, XLSX Schedule |
| **B** | Electrical | `elv_fire_alarm/` | `addressable_loop/` | **COMPLETED** | Calc Note, DXF Plan, XLSX Schedule |
| **B** | Electrical | `cctv_security/` | `dori_and_storage/` | **COMPLETED** | Calc Note, DXF Layout, XLSX Schedule |
| **B** | Electrical | `emergency_lighting/` | `egress_and_cbs/` | **COMPLETED** | Calc Note, DXF Plan, XLSX Schedule |
| **C** | Mechanical | `hvac/` | `heat_load/` | **COMPLETED** | Calc Note, DXF Layout, XLSX Schedule |
| **C** | Mechanical | `plumbing/` | `water_drainage/` | **COMPLETED** | Calc Note, DXF Riser, XLSX Schedule |
| **D** | Architectural| `planning/` | `space_compliance/` | **COMPLETED** | Calc Note, DXF Layout, XLSX Schedule |
| **D** | Architectural| `life_safety/`| `egress_capacity/` | **COMPLETED** | Calc Note, DXF Egress, XLSX Schedule |
