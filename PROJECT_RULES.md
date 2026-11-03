# Project Rules (Summary)

For the complete, binding project rules and engineering constitution, see:
👉 **[PROJECT_RULES.md](file:///d:/programming/construction%20design/project_management/PROJECT_RULES.md)**

### Key Tenets:
1. **Pure Tree Hierarchy & Strict Node Isolation**: No monolithic code files. Rules for CCTV cameras are isolated from sockets, isolated from lighting, isolated from footings.
2. **Node-Scoped Code & Building Typology**: Active code and building type are declared at Root (`project_root.json`).
3. **Dedicated Specialized Leaf Nodes**: Special systems (e.g. Hospital IPS panels, Factory Machine Foundations) live in isolated specialized leaves.
4. **Complete Engineering Deliverables Package**: Every design skill must be capable of exporting:
   - Markdown/LaTeX Calculation Notes.
   - Native AutoCAD `.dxf` drawings (via `ezdxf`) with standard layers (Plan & Section detailing).
   - Interactive Excel `.xlsx` calculation books (via `openpyxl`).
   - Bar Bending Schedule (BBS) and Bill of Quantities (BOQ) with cost estimation.
   - BIM / Revit parameter scripts.
5. **Deterministic Python Calculations**: Zero LLM hallucination for engineering math.
6. **Documentation Integrity**: Keep `MASTER_PLAN.md` and `COMPLETED_WORK.md` updated after every milestone.
