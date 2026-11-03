"""
Complete Multi-Deliverable Runner for Access Control System (ACS) & Security Door Interlocks.
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. AutoCAD Door Elevation & Interlock Schematic Drawing (.dxf)
3. Excel Door Hardware Schedule & Battery Sizing Workbook (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from electrical.low_current_elv.access_control.scripts.design_engine import (
    AccessControlEngine,
    ControlledDoorInput,
    AccessControlDesignResult,
)
from electrical.low_current_elv.access_control.exporters.excel_exporter import AccessControlExcelExporter
from electrical.low_current_elv.access_control.exporters.dxf_exporter import AccessControlDXFExporter


def generate_access_control_package(
    project_name: str,
    doors: List[ControlledDoorInput],
    autonomy_hours: float = 4.0,
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes Access Control design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "access_control")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("electrical/low_current_elv/access_control", code=code)
    active_code = context["active_code"]
    standards = f"NFPA 101 / UL 294 / {active_code} 801"

    # 2. Run Deterministic Access Control Engine
    engine = AccessControlEngine(standard=standards)
    res = engine.design_system(
        project_name=project_name,
        doors=doors,
        autonomy_hours=autonomy_hours,
        dc_voltage_v=12.0,
    )

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    # Build door table rows
    d_rows = []
    for d in res.doors:
        fs_str = "COMPLIANT (Fail-Safe)" if d.failsafe_compliant else "NON-COMPLIANT"
        row = f"| {d.door_tag} | {d.door_name} | {d.lock_type} | {d.lock_count} | {d.lock_holding_force_n} N | {d.reader_type} | {d.lock_current_ma:.0f} mA | {d.peripherals_current_ma:.0f} mA | {d.total_door_current_ma:.0f} mA | {d.power_watts:.1f} W | {fs_str} |"
        d_rows.append(row)
    door_table = "\n".join(d_rows)

    coord_lines = [f"- 🔒 {notice}" for notice in res.coordination_notices]

    sum_doors_ma = sum(d.total_door_current_ma for d in res.doors)
    controllers_overhead_ma = res.total_system_current_ma - sum_doors_ma
    autonomy_margin = round(((res.selected_battery_ah / max(res.calculated_battery_ah, 0.1)) - 1.0) * 100, 1)

    replacements = {
        "{{project_name}}": res.project_name,
        "{{standard_used}}": res.standard_used,
        "{{dc_voltage}}": f"{res.dc_operating_voltage_v:.0f}",
        "{{autonomy_hours}}": f"{autonomy_hours:.1f}",
        "{{door_table_rows}}": door_table,
        "{{sum_doors_ma}}": f"{sum_doors_ma:.0f}",
        "{{controllers_overhead_ma}}": f"{controllers_overhead_ma:.0f}",
        "{{total_system_current_a}}": f"{res.total_system_current_a:.3f}",
        "{{total_system_power_w}}": f"{res.total_system_power_watts:.1f}",
        "{{min_psu_a}}": f"{res.total_system_current_a * 1.25:.2f}",
        "{{psu_rating_a}}": f"{res.recommended_psu_current_a:.0f}",
        "{{psu_rating_w}}": f"{res.recommended_psu_rating_w:.0f}",
        "{{calc_battery_ah}}": f"{res.calculated_battery_ah:.2f}",
        "{{selected_battery_ah}}": f"{res.selected_battery_ah:.1f}",
        "{{autonomy_margin}}": f"{autonomy_margin:.1f}",
        "{{total_doors}}": str(res.total_doors_count),
        "{{controller_type}}": res.controller_type,
        "{{total_controllers}}": str(res.total_controllers_count),
        "{{coordination_checklist}}": "\n".join(coord_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = project_name.lower().replace(" ", "_")
    md_path = out_dir / f"{clean_name}_access_control_calculation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Workbook
    xlsx_path = out_dir / f"{clean_name}_access_control_schedule.xlsx"
    excel_exporter = AccessControlExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF Drawing
    dxf_path = out_dir / f"{clean_name}_access_control_schematic.dxf"
    dxf_exporter = AccessControlDXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    sample_doors = [
        ControlledDoorInput("D-G01", "Main Entrance", "double_leaf", "perimeter_heavy", "maglock_1200lbs", "card_reader"),
        ControlledDoorInput("D-G02", "Emergency Exit Stair 1", "single_leaf", "standard_interior", "maglock_600lbs", "card_reader", on_egress_route=True),
        ControlledDoorInput("D-G03", "Emergency Exit Stair 2", "single_leaf", "standard_interior", "maglock_600lbs", "card_reader", on_egress_route=True),
        ControlledDoorInput("D-G04", "Server Room", "single_leaf", "server_biometric", "maglock_600lbs", "biometric_reader"),
        ControlledDoorInput("D-G05", "Executive Suite", "single_leaf", "standard_interior", "electric_strike", "card_reader"),
    ]
    files = generate_access_control_package("Corporate Headquarters Security", sample_doors)
    print("Access Control Engineering Package successfully generated:")
    for k, p in files.items():
        print(f"  - {k}: {p}")
