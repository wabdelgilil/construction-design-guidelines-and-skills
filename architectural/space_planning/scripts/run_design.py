"""
Complete Multi-Deliverable Runner for Architectural Space Planning & Room Matrix Audit.
Generates:
1. Markdown Space Compliance Note (.md)
2. AutoCAD Architectural Space Plan (.dxf)
3. Excel Space Schedule & MEP Directives (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path (5 levels up from scripts)
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from architectural.space_planning.scripts.design_engine import (
    SpacePlanningEngine,
    RoomDefinition,
    ProjectSpaceAuditResult,
)
from architectural.space_planning.exporters.excel_exporter import SpacePlanningExcelExporter
from architectural.space_planning.exporters.dxf_exporter import SpacePlanningDXFExporter


def generate_space_planning_package(
    project_name: str,
    rooms: List[RoomDefinition],
    typology: str = "residential",
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes space planning compliance audit and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "space_planning")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("architectural/space_planning", code=code)
    active_code = context["active_code"]
    rules = context["rules"]

    code_rules = rules.get("typology_requirements", {}).get(typology, {})

    # 2. Run Space Planning Audit Engine
    engine = SpacePlanningEngine(typology=typology, code=active_code)
    res = engine.audit_spaces(project_name=project_name, rooms=rooms, code_rules=code_rules)

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    # Build room rows
    rows = []
    for rm in res.rooms_audited:
        row = f"| {rm.tag} | {rm.name} | {rm.space_type} | {rm.length_m:.1f}x{rm.width_m:.1f}x{rm.height_m:.1f}m | {rm.area_m2:.1f} | {rm.min_area_required_m2:.1f} | {'PASS' if rm.width_pass else 'FAIL'} | {'PASS' if rm.height_pass else 'FAIL'} | {'PASS' if rm.glazing_pass else 'FAIL'} | **{rm.overall_status}** |"
        rows.append(row)
    room_table = "\n".join(rows)

    mep_lines = [f"- 📌 {rec}" for rec in res.mep_recommendations]

    replacements = {
        "{{code_used}}": active_code,
        "{{building_typology}}": typology.replace("_", " ").title(),
        "{{project_name}}": res.project_name,
        "{{total_gross_m2}}": f"{res.total_gross_area_m2:.1f}",
        "{{total_habitable_m2}}": f"{res.total_habitable_area_m2:.1f}",
        "{{room_table_rows}}": room_table,
        "{{overall_project_status}}": "PASSED ALL CODE CRITERIA" if res.all_rooms_pass else "VIOLATIONS DETECTED",
        "{{mep_directives}}": "\n".join(mep_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = project_name.lower().replace(" ", "_")
    md_path = out_dir / f"{clean_name}_space_compliance_note.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Workbook
    xlsx_path = out_dir / f"{clean_name}_space_schedule.xlsx"
    excel_exporter = SpacePlanningExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF Space Layout
    dxf_path = out_dir / f"{clean_name}_space_layout.dxf"
    dxf_exporter = SpacePlanningDXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    test_rooms = [
        RoomDefinition("R-01", "Master Bedroom Suite", "master_bedroom", 5.0, 4.0, 3.0, 3.5),
        RoomDefinition("R-02", "Secondary Bedroom", "secondary_bedroom", 4.0, 3.2, 3.0, 2.0),
        RoomDefinition("R-03", "Living & Dining Hall", "living_room", 6.5, 4.5, 3.0, 4.5),
        RoomDefinition("R-04", "En-suite Master Bathroom", "bathroom", 2.8, 1.8, 2.6, 0.8),
        RoomDefinition("R-05", "Kitchen & Pantry", "kitchen", 3.8, 2.5, 2.8, 1.5),
        RoomDefinition("R-06", "Guest Powder Room", "powder_room", 1.8, 1.4, 2.6, 0.4),
    ]

    files = generate_space_planning_package(
        project_name="Luxury Modern Villa",
        rooms=test_rooms,
        typology="residential",
        code="SBC",
    )
    print("Architectural Space Planning Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
