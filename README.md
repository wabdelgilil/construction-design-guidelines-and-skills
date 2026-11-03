# Construction Design Guidelines and Skills

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/tests-68%20passed-success.svg)](#verification--test-suite)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Disciplines](https://img.shields.io/badge/Disciplines-Structural%20%7C%20Electrical%20%7C%20Mechanical%20%7C%20Architectural-orange.svg)](#-multi-disciplinary-design-skills-matrix)

**Construction Design Guidelines and Skills** is an open-source, collaborative, deterministic multi-disciplinary engineering design engine and AI skills repository for the AEC (Architecture, Engineering, and Construction) industry.

It bridges the gap between building codes, software engineering, and physical construction by translating international building codes (**SBC, ACI, IBC, NFPA, IPC, ECP**) into modular, executable Python design skills that automatically produce **complete engineering deliverables**.

---

## 🌟 Key Highlights

- **📐 4 Disciplines in One Harmonized Engine**:
  - **Structural**: Isolated footings, strap footings, combined footings, reinforced concrete columns.
  - **Electrical**: Small power branch circuits, lighting photometrics (Lumen method), hospital operating room isolated power systems (IPS/IT).
  - **Mechanical**: HVAC cooling load & air distribution, domestic water booster pumps, sanitary drainage stacks.
  - **Architectural**: Room matrix space compliance audits, life safety and emergency egress capacity.
- **⚡ Zero-Hallucination Deterministic Math**: Pure Python formulations based on verified code clauses. No AI guessing, no mental math errors.
- **📦 Tri-Deliverable Generator**: Every skill generates:
  1. **Engineering Calculation Note** (`.md` with full LaTeX math equations).
  2. **AutoCAD Drawing** (`.dxf` with industry-standard ACI layer color conventions via `ezdxf`).
  3. **Engineering Schedule & BOQ** (`.xlsx` with formulas and corporate styling via `openpyxl`).
- **🔗 Cross-Discipline Coordination Subsystem**: An automated registry that prevents site clashes by broadcasting requirements across disciplines (e.g., HVAC units trigger electrical disconnect switches and thermostat conduits; plumbing drains trigger pre-cast structural beam sleeves).
- **🌍 Multi-Code Architecture**: Decouples design logic from code profiles. Parameters for **SBC (Saudi Building Code)**, **ACI / IBC / NFPA (US Standards)**, and **ECP (Egyptian Code of Practice)** are inherited dynamically along the tree.

---

## 🗂️ Multi-Disciplinary Design Skills Matrix

| Discipline | Category | Leaf Skill | Governing Codes | Primary Outputs |
| :--- | :--- | :--- | :--- | :--- |
| **Structural** | Foundations | [`isolated_footing`](structural/foundations/isolated_footing/SKILL.md) | SBC 304, ACI 318, ECP 203 | Calc Note, AutoCAD DXF, Excel BBS & BOQ, Revit placement |
| **Structural** | Foundations | [`strap_footing`](structural/foundations/strap_footing/SKILL.md) | SBC 304, ACI 318 | Cantilever moment diagram, Strap beam shear rebar, DXF, BOQ |
| **Structural** | Foundations | [`combined_footing`](structural/foundations/combined_footing/SKILL.md) | SBC 304, ACI 318 | Soil pressure uniformity, Longitudinal/transverse rebar, DXF, BOQ |
| **Structural** | Columns | [`columns`](structural/vertical_elements/columns/SKILL.md) | SBC 304, ACI 318, ECP 203 | Slenderness check, Tie spacing, Column section detailing DXF |
| **Electrical** | Power | [`sockets`](electrical/power_distribution/sockets/SKILL.md) | SBC 401, IEC 60364, NEC | Circuit grouping, Dedicated appliance circuits, DB schedule, DXF |
| **Electrical** | Lighting | [`lighting`](electrical/lighting/SKILL.md) | SBC 1001, ASHRAE 90.1, IESNA | Lumen method, Reflected ceiling plan DXF, LPD check, (x, y) coordinates |
| **Electrical** | Emergency | [`emergency_lighting`](electrical/lighting/emergency_lighting/SKILL.md) | NFPA 101, BS 5266, SBC 801 | Egress lux, 90m autonomy, Central Battery System (CBS) inverter/Ah, DXF |
| **Electrical** | Substation | [`substation`](electrical/power_distribution/substation/SKILL.md) | IEC 60076, IEEE 141, SBC 401 | Diversified demand, Transformer & Diesel Generator sizing, MDB ACB, DXF |
| **Electrical** | Protection | [`protection_coordination`](electrical/power_distribution/protection_coordination/SKILL.md) | IEC 60909, IEEE 242, SBC 401 | Short-circuit impedance method, LSIG trip units, Log-Log TCC curves DXF |
| **Electrical** | Cables | [`cables`](electrical/cables/SKILL.md) | IEC 60364-5-52, SBC 401 | Continuous current, Derating, Voltage drop, Adiabatic $I_{sc}$, Tray fill DXF |
| **Electrical** | Earthing | [`earthing`](electrical/earthing/SKILL.md) | IEEE 80, IEC 62305, NFPA 780 | Dwight's rod formula, Grid resistance, LPS Rolling Sphere, DXF |
| **Electrical** | Low Current / ELV | [`fire_alarm`](electrical/low_current_elv/fire_alarm/SKILL.md) | NFPA 72, SBC 801 | Addressable detectors, Loop allocation, 24h+15m FACP battery, DXF |
| **Electrical** | Low Current / ELV | [`access_control`](electrical/low_current_elv/access_control/SKILL.md) | NFPA 101, UL 294, SBC 801 | Maglocks, Fail-safe fire relay, BGU, 4h PSU battery Ah, DXF Elevation |
| **Electrical** | Low Current / ELV | [`structured_cabling`](electrical/low_current_elv/structured_cabling/SKILL.md) | ANSI/TIA-568-D, ISO/IEC 11801 | Work Area Outlets, 42U Rack Elevation, OM4 Fiber backbone, UPS, DXF |
| **Electrical** | Security | [`cctv_security`](electrical/cctv_security/SKILL.md) | EN 62676-4, NFPA 730 | DORI optical criteria, Lens focal length, NVR RAID storage, PoE, DXF |
| **Electrical** | Specialized | [`medical_isolated_ips`](electrical/power_distribution/medical_isolated_power_ips/SKILL.md) | IEC 60364-7-710, NFPA 99, SBC 401 | Medical isolation transformer, IMD alarm, POAG busbar, SLD DXF |
| **Mechanical** | HVAC | [`heat_load`](mechanical/hvac/heat_load/SKILL.md) | SBC 501, ASHRAE 62.1 | Sensible/latent heat balance, Tonnage (TR), CFM, Ducting & Diffuser DXF |
| **Mechanical** | Plumbing | [`plumbing`](mechanical/plumbing/SKILL.md) | SBC 701, IPC, ECP | DFU drainage stack, WSFU booster pump (1D+1S), Structural sleeves DXF |
| **Architectural**| Space Planning | [`space_planning`](architectural/space_planning/SKILL.md) | SBC 201, IBC, MoMAH | Area & height compliance, Daylighting ratio, Space layout DXF |
| **Architectural**| Life Safety | [`life_safety`](architectural/life_safety/SKILL.md) | SBC 801, NFPA 101, IBC Ch. 10 | Occupant load, Exit diagonal remoteness, Egress capacity, DXF plan |

---

## 🌳 Repository Architecture

```text
construction-design-guidelines-and-skills/
├── project_root.json              # Level 0: Global code selector (SBC, ACI, ECP)
├── INDEX.md                       # Level 0: Top-level lightweight dispatcher
│
├── structural/                    # Level 1: Structural Engineering
│   ├── rules.json                 # Shared material parameters (fc', fcu, fy, loads)
│   ├── foundations/               # Level 2: Sub-branch
│   │   ├── isolated_footing/      # Level 3: Leaf skill (rules, engine, exporters, calc sheet)
│   │   ├── strap_footing/
│   │   └── combined_footing/
│   └── vertical_elements/
│       └── columns/
│
├── electrical/                    # Level 1: Electrical Engineering
│   ├── rules.json                 # Shared voltage/frequency standards
│   ├── power_distribution/
│   │   ├── sockets/
│   │   └── medical_isolated_power_ips/
│   └── lighting/
│
├── mechanical/                    # Level 1: Mechanical Engineering
│   ├── rules.json                 # Shared comfort setpoints & climate baselines
│   ├── hvac/
│   │   └── heat_load/
│   └── plumbing/
│
├── architectural/                 # Level 1: Architectural Engineering
│   ├── rules.json                 # Shared clear heights & corridor dimensions
│   ├── space_planning/
│   └── life_safety/
│
├── core/                          # Cross-Discipline Engine Core
│   ├── resolver.py                # Hierarchical context inheritance resolver
│   ├── coordination/              # Interdisciplinary interface registry & coordinator
│   ├── cad_engine/                # Architectural polyline parser & Shoelace area solver
│   └── exporters/                 # Universal DXF, Excel, and BOQ/BBS writers
│
├── tests/                         # Full automated test suite (47 unit tests)
└── output/                        # Generated calculation notes, DXFs, and Excel books
```

---

## 🚀 Quick Start

### 1. Clone & Set Up
```bash
git clone https://github.com/wabdelgilil/construction-design-guidelines-and-skills.git
cd construction-design-guidelines-and-skills
pip install -r requirements.txt
```

### 2. Run All Automated Tests
```bash
python -m unittest discover tests
```
*Output: `Ran 47 tests ... OK`*

### 3. Generate a Sample Engineering Deliverable Package
Run any leaf runner to generate all 3 deliverables into `output/`:

```bash
# Generate Structural Isolated Footing package
python structural/foundations/isolated_footing/scripts/run_design.py

# Generate Electrical Lighting layout and coordinates
python electrical/lighting/scripts/run_design.py

# Generate Mechanical HVAC cooling load and air distribution layout
python mechanical/hvac/heat_load/scripts/run_design.py

# Generate Hospital Operating Room Isolated Power System (IPS) SLD
python electrical/power_distribution/medical_isolated_power_ips/scripts/run_design.py
```

Inspect the `output/` folder to see the generated `.md` calculation notes, `.dxf` CAD drawings, and `.xlsx` schedules!

---

## 🤝 Contributing

We welcome contributions from engineers, researchers, and developers worldwide!
- Have a local building code for your region? Codify it in `rules.json`.
- Want to add a new structural element (e.g. Beams, Slabs, Retaining Walls)?
- Want to enhance MEP calculations (e.g. Fire Sprinkler Hydraulic Networks)?

Please read our [**Contributing Guide (CONTRIBUTING.md)**](CONTRIBUTING.md) to get started.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - open for commercial and personal use, modification, and distribution.
