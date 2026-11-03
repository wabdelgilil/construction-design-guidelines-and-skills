# Contributing to Construction Design Guidelines and Skills

Welcome! We are building the **world's first collaborative, deterministic, multi-disciplinary AEC engineering design guidelines and skills repository**.

Whether you are a **Structural Engineer, Electrical Engineer, Mechanical/HVAC Engineer, Architect, or Software Developer**, your contributions are warmly welcomed!

---

## 🏛️ Core Architectural Principles

When contributing to this repository, please adhere to our core project commandments:

1. **Deterministic Calculations Only**: Engineering formulas must be deterministic code (pure Python math). Zero hallucination. Zero arbitrary estimations.
2. **Decouple Logic from Code Profiles**: Engineering methodology is universal. Local building codes (SBC, ACI, ECP, IBC, NFPA) are codified as parameter sets inside `rules.json`.
3. **Hierarchical Tree Structure**: All design modules reside in a clean tree hierarchy:
   `discipline/ -> category/ -> leaf_skill/`
4. **Standard Multi-Deliverables**: Every leaf skill must be capable of generating:
   - **Engineering Calculation Sheet** (`.md` with LaTeX formulas).
   - **AutoCAD CAD Drawing** (`.dxf` via `ezdxf` on standard engineering layers).
   - **Calculation Workbook & BOQ** (`.xlsx` via `openpyxl`).
5. **Cross-Discipline Coordination**: If a module has interdisciplinary dependencies (e.g., HVAC requires electrical power and wall thermostat; plumbing pipes penetrate structural beams), it must register the interface in `core/coordination/interface_registry.json`.

---

## 🛠️ How to Add a New Engineering Leaf Skill

Follow this standardized 5-step checklist to introduce a new design skill:

### Step 1: Create the Skill Directory
Navigate to the appropriate discipline and sub-branch:
```bash
# Example for a new structural skill (e.g., Cantilever Retaining Wall)
mkdir -p structural/retaining_elements/cantilever_wall
cd structural/retaining_elements/cantilever_wall
```

### Step 2: Define `rules.json` and `SKILL.md`
- **`rules.json`**: Codify specific parameters across supported codes (SBC, ACI, ECP, etc.).
- **`SKILL.md`**: Document the engineering scope, mathematical formulations, assumptions, and required inputs/outputs.

### Step 3: Implement Deterministic Engine (`scripts/design_engine.py`)
- Use pure Python dataclasses (`@dataclass`) for input/output definitions.
- Write clean, transparent math functions with references to code clause numbers.

### Step 4: Implement Exporters
- `templates/calc_sheet.md`: Markdown template with `{{PLACEHOLDER}}` tags.
- `exporters/dxf_exporter.py`: Uses `core.exporters.dxf_writer.DXFWriter` to create scaled drawings.
- `exporters/excel_exporter.py`: Uses `core.exporters.excel_writer.ExcelWriter` to build styled workbooks.
- `scripts/run_design.py`: Automated runner generating all 3 files.

### Step 5: Add Unit Tests
Add comprehensive tests under `tests/test_<your_skill>.py`:
- Test code boundary limits.
- Test failure/warning thresholds.
- Verify that deliverable files are generated successfully.

Run test suite:
```bash
python -m unittest discover tests
```

---

## 📬 Pull Request (PR) Guidelines

1. **Fork the repository** and create a feature branch (`git checkout -b feature/continuous-beams`).
2. Ensure all existing tests pass:
   ```bash
   python -m unittest discover tests
   ```
3. Commit with clean, descriptive messages:
   ```bash
   git commit -m "feat(structural): add continuous beam flexure and shear leaf skill"
   ```
4. Push to your fork and submit a Pull Request describing:
   - The design standard(s) covered.
   - The verified engineering formulas used.
   - Sample outputs generated.

---

## 💬 Community & Discussion
Feel free to open an **Issue** to discuss new discipline trees, propose code profile additions for your country, or suggest exporter improvements!
