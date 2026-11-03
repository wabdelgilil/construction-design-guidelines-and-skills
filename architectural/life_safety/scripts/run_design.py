"""
Complete Multi-Deliverable Runner for Architectural Life Safety & Means of Egress.
Generates:
1. Markdown Life Safety Calculation Note (.md)
2. AutoCAD Means of Egress & Separation Plan (.dxf)
3. Excel Occupant Load & Egress Schedule (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path (5 levels up from scripts)
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from architectural.life_safety.scripts.design_engine import (
    LifeSafetyEngine,
    EgressZoneInput,
    LifeSafetyProjectResult,
)
from architectural.life_safety.exporters.excel_exporter import LifeSafetyExcelExporter
from architectural.life_safety.exporters.dxf_exporter import LifeSafetyDXFExporter


def generate_life_safety_package(
    building_name: str,
    building_length_m: float,
    building_width_m: float,
    actual_exit_separation_m: float,
    zones_data: List[EgressZoneInput],
    is_sprinklered: bool = True,
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes life safety egress design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "life_safety")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("architectural/life_safety", code=code)
    active_code = context["active_code"]
    rules = context["rules"]

    load_factors = rules.get("occupant_load_factors_m2_per_person", {})

    # 2. Compute Life Safety Calculations
    engine = LifeSafetyEngine(is_sprinklered=is_sprinklered, code=active_code)
    res = engine.compute_life_safety(
        building_name=building_name,
        building_length_m=building_length_m,
        building_width_m=building_width_m,
        actual_exit_separation_m=actual_exit_separation_m,
        zones_data=zones_data,
        load_factors=load_factors,
    )

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    # Build zone table rows
    z_rows = []
    for z in res.zones:
        door_str = f"{z.door_capacity_width_required_mm:.0f} / {z.door_clear_width_provided_mm:.0f} mm"
        stair_str = f"{z.stair_width_required_mm:.0f} / {z.stair_width_provided_mm:.0f} mm"
        row = f"| {z.zone_name} | {z.area_m2:.1f} | {z.occupant_load_factor_m2:.1f} m$^2$/p | {z.calculated_occupants} | {z.min_exits_required} | {z.longest_travel_distance_m:.1f} m | {door_str} | {stair_str} | **{z.overall_status}** |"
        z_rows.append(row)
    zone_table = "\n".join(z_rows)

    mep_lines = [f"- 🚨 {notice}" for notice in res.mep_fire_safety_notices]

    replacements = {
        "{{code_used}}": active_code,
        "{{building_name}}": res.building_name,
        "{{sprinkler_status}}": "Fully Sprinklered (NFPA 13)" if res.is_sprinklered else "Unsprinklered",
        "{{bldg_length}}": f"{res.building_length_m:.1f}",
        "{{bldg_width}}": f"{res.building_width_m:.1f}",
        "{{bldg_diag}}": f"{res.building_diagonal_m:.1f}",
        "{{total_occupants}}": str(res.total_building_occupants),
        "{{req_separation}}": f"{res.min_exit_separation_required_m:.1f}",
        "{{act_separation}}": f"{res.actual_exit_separation_m:.1f}",
        "{{separation_status}}": "PASS (Adequately Remote)" if res.separation_pass else "VIOLATION (Too Close)",
        "{{zone_table_rows}}": zone_table,
        "{{overall_status}}": res.overall_status,
        "{{mep_directives}}": "\n".join(mep_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = building_name.lower().replace(" ", "_")
    md_path = out_dir / f"{clean_name}_life_safety_note.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Workbook
    xlsx_path = out_dir / f"{clean_name}_life_safety_schedule.xlsx"
    excel_exporter = LifeSafetyExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF Egress Plan
    dxf_path = out_dir / f"{clean_name}_egress_plan.dxf"
    dxf_exporter = LifeSafetyDXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    zones = [
        EgressZoneInput("Ground Floor Open Office", 450.0, "business_office", 28.0),
        EgressZoneInput("Multi-Purpose Training Auditorium", 180.0, "assembly_unconcentrated", 18.0),
        EgressZoneInput("Executive Meeting Suites", 120.0, "business_office", 15.0),
    ]

    files = generate_life_safety_package(
        building_name="Regional Commercial Headquarters",
        building_length_m=35.0,
        building_width_m=20.0,
        actual_exit_separation_m=22.0,
        zones_data=zones,
        is_sprinklered=True,
        code="SBC",
    )
    print("Architectural Life Safety Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
