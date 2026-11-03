"""
Complete Multi-Deliverable Runner for Addressable Fire Alarm System Design.
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. AutoCAD Addressable Fire Alarm Plan & Loop Layout (.dxf)
3. Excel Device Schedule & Battery Calculations (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path (5 levels up from scripts)
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from electrical.low_current_elv.fire_alarm.scripts.design_engine import (
    FireAlarmEngine,
    FireAlarmSpaceInput,
    FireAlarmDesignResult,
)
from electrical.low_current_elv.fire_alarm.exporters.excel_exporter import FireAlarmExcelExporter
from electrical.low_current_elv.fire_alarm.exporters.dxf_exporter import FireAlarmDXFExporter


def generate_fire_alarm_package(
    project_name: str,
    spaces: List[FireAlarmSpaceInput],
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes fire alarm system design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "fire_alarm")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("electrical/low_current_elv/fire_alarm", code=code)
    rules = context["rules"]
    standards = " / ".join(rules.get("applicable_standards", ["NFPA 72", "SBC 801"]))

    # 2. Run Deterministic Fire Alarm Engine
    engine = FireAlarmEngine(standard=standards)
    res = engine.design_fire_alarm(project_name=project_name, spaces=spaces)

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    # Build device table rows
    d_rows = []
    for alloc in res.allocations:
        mod_str = ", ".join(alloc.interface_modules) if alloc.interface_modules else "None"
        row = f"| {alloc.space_name} | {alloc.area_m2:.1f} | {alloc.detector_type} | {alloc.detector_count} | {alloc.mcp_count} | {alloc.sounder_strobe_count} | {alloc.strobe_candela_cd} cd | {mod_str} |"
        d_rows.append(row)
    device_table = "\n".join(d_rows)

    coord_lines = [f"- 🚨 {notice}" for notice in res.coordination_notices]

    replacements = {
        "{{standard_used}}": res.standard_used,
        "{{project_name}}": res.project_name,
        "{{total_area_m2}}": f"{res.total_area_m2:.1f}",
        "{{device_table_rows}}": device_table,
        "{{smoke_count}}": str(res.total_smoke_detectors),
        "{{heat_count}}": str(res.total_heat_detectors),
        "{{mcp_count}}": str(res.total_mcps),
        "{{sounder_count}}": str(res.total_sounder_strobes),
        "{{module_count}}": str(res.total_control_modules),
        "{{total_devices}}": str(res.grand_total_addressable_devices),
        "{{total_loops}}": str(res.total_loops_required),
        "{{spare_pct}}": f"{res.loop_spare_capacity_pct:.1f}",
        "{{iq_amps}}": f"{res.facp_quiescent_current_amps:.3f}",
        "{{ia_amps}}": f"{res.facp_alarm_current_amps:.3f}",
        "{{standby_hours}}": f"{res.standby_duration_hours:.0f}",
        "{{alarm_minutes}}": f"{res.alarm_duration_minutes:.0f}",
        "{{calc_battery_ah}}": f"{res.calculated_battery_capacity_ah:.2f}",
        "{{selected_battery_ah}}": f"{res.selected_battery_rating_ah:.1f}",
        "{{coordination_checklist}}": "\n".join(coord_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = project_name.lower().replace(" ", "_")
    md_path = out_dir / f"{clean_name}_fire_alarm_calculation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Workbook
    xlsx_path = out_dir / f"{clean_name}_fire_alarm_schedule.xlsx"
    excel_exporter = FireAlarmExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF Fire Alarm Layout
    dxf_path = out_dir / f"{clean_name}_fire_alarm_layout.dxf"
    dxf_exporter = FireAlarmDXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    sample_spaces = [
        FireAlarmSpaceInput("Open Plan Workstation Office", 12.0, 8.0, "office", False),
        FireAlarmSpaceInput("Staff Cafeteria & Pantry", 6.0, 5.0, "kitchen", False),
        FireAlarmSpaceInput("Main Entrance Lobby & Reception", 8.0, 6.0, "corridor", True),
        FireAlarmSpaceInput("Executive Boardroom", 7.0, 5.0, "office", False),
        FireAlarmSpaceInput("Data Center / Server Room", 5.0, 4.0, "server_room", False),
        FireAlarmSpaceInput("Emergency Exit Corridor & Stair A", 10.0, 2.5, "corridor", True),
    ]

    files = generate_fire_alarm_package(
        project_name="Commercial Tower Level 1",
        spaces=sample_spaces,
        code="SBC",
    )
    print("Addressable Fire Alarm System Deliverables Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
