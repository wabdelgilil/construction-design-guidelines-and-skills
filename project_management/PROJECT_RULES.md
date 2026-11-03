# Project Rules & Operating Guidelines
## Pure Hierarchical Tree, Multi-Deliverable Engineering Architecture

---

## 1. Core Philosophy: Upstream Master Engine & Pure Tree Hierarchy
1. **Upstream Master Skills Engine**:
   - This project serves as the **Upstream Master Engine & Reference Skills Repository** for downstream engineering tools and specialized vertical systems (such as `ElectricalDesign` and future vertical projects).
   - All modules must be clean, headless, modular, and callable as pure APIs or standalone skills.
2. **Zero Monolithic Files**:
   - There are **NO giant, centralized code files** or monolithic configuration dumps.
   - Any rule, equation, or code constraint is isolated strictly to the specific node to which it belongs.
2. **Strict Node Scoping & Encapsulation**:
   - Rules are strictly encapsulated inside their respective nodes.
   - In Electrical: CCTV camera design rules (`cctv/`) are isolated from power sockets (`sockets/`), which are isolated from lighting design (`lighting/`).
   - In Structural: Isolated footing rules (`isolated_footing/`) are isolated from columns (`columns/`), which are isolated from shear walls (`shear_walls/`).
3. **The Role of Parent Nodes**:
   - A parent node is exclusively an **Indexing and Routing Dispatcher (`INDEX.md`)** for its immediate children.
   - A parent node contains only those rules that are strictly shared across all its children.

---

## 2. Multi-Code & Building Typology Handling
1. **Root-Level Project Declarations (`project_root.json`)**:
   - Root declares global parameters (`active_code`, `building_type`, `unit_system`).
2. **Dedicated Specialized Leaf Nodes**:
   - Edge-case systems (e.g. Hospital Operating Room IPS panels under NFPA 99, or Factory Dynamic Machine Foundations under ACI 351) live in dedicated specialized leaf nodes, keeping standard skills clean.

---

## 3. Cross-Discipline Coordination & Interface Management (التنسيق المشترك بين التخصصات)
1. **Zero Information Loss Across Disciplines**:
   - In construction, engineering elements frequently span discipline boundaries (e.g., HVAC thermostats require Electrical conduit; water heaters require Electrical dedicated switches and Plumbing water feeds; elevator shafts require Structural pits, Mechanical ventilation, and Electrical 3-phase feeds).
   - Knowledge of an interface must **NEVER be lost** when shifting focus between disciplines.
2. **The Central Coordination Registry (`core/coordination/interface_registry.json`)**:
   - Every cross-discipline requirement is codified with: `source_discipline`, `target_discipline`, `element`, `requirement`, and `checklist_trigger`.
3. **Mandatory Interface Gate in Target Skills**:
   - When any leaf skill in the target discipline executes (e.g. Electrical Panels or Sockets), it must query the coordination registry and verify that all dependent interfaces from other disciplines are accommodated.

---

## 4. Mandatory Multi-Deliverable Engineering Package (Deliverable Standards)
A real-world engineering design is NEVER just narrative text. Each actionable design skill must support generating the **Complete Engineering Deliverables Package**:

1. **Structured Calculation Note (`calc_sheet.md`)**:
   - Professional Markdown/LaTeX document stating inputs, active code, equations, and safety verification (`SAFE` / `EXCEEDS LIMIT`).
2. **Native AutoCAD Drawing (`.dxf` via `ezdxf`)**:
   - Direct export of standard AutoCAD `.dxf` files with engineering layers:
     - `S-CONC`: Concrete geometry, plan outlines, and cross-sections.
     - `S-REBAR`: Reinforcement layout, rebar bends, and hooks.
     - `S-DIMS`: Engineering dimension lines.
     - `S-TEXT`: Annotations and callout tags.
3. **BIM / Revit Scripting**:
   - Parameter scripts (pyRevit / Dynamo / IFC parameter mapping) to instantiate 3D BIM families and parameters.
4. **Interactive Excel Calculation Book (`.xlsx` via `openpyxl`)**:
   - Live spreadsheet with active calculation formulas, conditional formatting, and design checks.
5. **Bar Bending Schedule (BBS) & Bill of Quantities (BOQ)**:
   - Sheet detailing rebar shapes, cutting lengths, diameters, weights, and total steel tonnage.
   - Complete itemized bill of quantities (concrete volume $m^3$, formwork $m^2$, rebar tons) and cost estimation.

---

## 4. Deterministic Calculations (Zero AI Hallucination)
1. **Tested Python Scripts Only**:
   - All physical calculations (moments, shear, rebar areas, cable sizing, voltage drops, pipe diameters, lux calculations) are computed by deterministic, unit-tested Python scripts inside `scripts/`.
   - The AI agent never performs mental estimation or guesses engineering quantities.

---

## 5. Output Standards & Documentation Discipline
1. **Standardized Engineering Sheets & SI Units**:
   - SI units used internally (mm, m, kN, MPa, kVA, A).
2. **Project Management Files**:
   - `MASTER_PLAN.md` and `COMPLETED_WORK.md` must be kept updated after every significant task.
