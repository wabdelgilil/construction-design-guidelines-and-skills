"""
Complete Multi-Deliverable Runner for Emergency & Exit Lighting (CBS & Self-Contained).
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. AutoCAD Emergency Lighting & Exit Signs Plan (.dxf)
3. Excel CBS Schedule & Inverter Sizing Workbook (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from electrical.lighting.emergency_lighting.scripts.design_engine import (
    EmergencyLightingEngine,
    EmergencySpaceInput,
    EmergencyLightingDesignResult,
)
from electrical.lighting.emergency_lighting.exporters.excel_exporter import EmergencyLightingExcelExporter
from electrical.lighting.emergency_lighting.exporters.dxf_exporter import EmergencyLightingDXFExporter


def generate_emergency_lighting_package(
    project_name: str,
    spaces: List[EmergencySpaceInput],
    system_architecture: str = "Central Battery System (CBS)",
    autonomy_hours: float = 1.5,
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes emergency lighting design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "emergency_lighting")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("electrical/lighting", code=code)
    active_code = context["active_code"]
    standards = f"NFPA 101 / BS 5266 / {active_code} 801"

    # 2. Run Deterministic Emergency Lighting Engine
    engine = EmergencyLightingEngine(standard=standards)
    res = engine.design_emergency_lighting(
        project_name=project_name,
        spaces=spaces,
        system_architecture=system_architecture,
        autonomy_hours=autonomy_hours,
        dc_bus_voltage_v=220.0,
    )

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    # Build space table rows
    s_rows = []
    for alloc in res.allocations:
        row = f"| {alloc.space_name} | {alloc.space_type} | {alloc.area_m2:.1f} | {alloc.target_illuminance_lux:.1f} Lux | {alloc.emergency_luminaires_count} | {alloc.exit_signs_count} | {alloc.total_watts:.1f} W |"
        s_rows.append(row)
    space_table = "\n".join(s_rows)

    coord_lines = [f"- 💡 {notice}" for notice in res.coordination_notices]

    replacements = {
        "{{standard_used}}": res.standard_used,
        "{{system_architecture}}": res.system_architecture,
        "{{autonomy_minutes}}": f"{res.autonomy_hours * 60:.0f}",
        "{{autonomy_hours}}": f"{res.autonomy_hours:.1f}",
        "{{project_name}}": res.project_name,
        "{{space_table_rows}}": space_table,
        "{{total_watts}}": f"{res.total_emergency_load_watts:.1f}",
        "{{inverter_va}}": str(res.cbs_inverter_rated_va),
        "{{dc_bus_voltage}}": f"{res.cbs_battery_dc_bus_v:.0f}",
        "{{battery_blocks}}": str(res.cbs_battery_blocks_12v_count),
        "{{calc_battery_ah}}": f"{res.cbs_calculated_battery_ah:.2f}",
        "{{selected_battery_ah}}": f"{res.cbs_selected_battery_ah:.1f}",
        "{{cbs_circuits}}": str(res.total_cbs_circuits_count),
        "{{coordination_checklist}}": "\n".join(coord_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = project_name.lower().replace(" ", "_")
    md_path = out_dir / f"{clean_name}_emergency_lighting_calculation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Workbook
    xlsx_path = out_dir / f"{clean_name}_cbs_schedule.xlsx"
    excel_exporter = EmergencyLightingExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF Layout
    dxf_path = out_dir / f"{clean_name}_emergency_lighting_layout.dxf"
    dxf_exporter = EmergencyLightingDXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    sample_spaces = [
        EmergencySpaceInput("Ground Floor Main Escape Corridor", "escape_corridor", 36.0, 2.4, 3.0, True),
        EmergencySpaceInput("Fire Exit Stairwell A", "fire_staircase", 8.0, 4.0, 3.0, True),
        EmergencySpaceInput("Fire Exit Stairwell B", "fire_staircase", 8.0, 4.0, 3.0, True),
        EmergencySpaceInput("Central Reception & Elevator Lobby", "open_hall", 12.0, 8.0, 3.2, True),
    ]

    files = generate_emergency_lighting_package(
        project_name="Commercial Tower Emergency Egress",
        spaces=sample_spaces,
        system_architecture="Central Battery System (CBS)",
        autonomy_hours=1.5,
        code="SBC",
    )
    print("Emergency Lighting Deliverables Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
