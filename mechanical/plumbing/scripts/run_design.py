"""
Complete Multi-Deliverable Runner for Plumbing Drainage & Water Supply Design.
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. AutoCAD Drainage Riser & Booster Schematic (.dxf)
3. Excel Schedule & Structural Sleeves Schedule (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, Optional

# Add project root to path (5 levels up from scripts)
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from mechanical.plumbing.scripts.design_engine import (
    PlumbingEngine,
    PlumbingFixturesSchedule,
    PlumbingDesignResult,
)
from mechanical.plumbing.exporters.excel_exporter import PlumbingExcelExporter
from mechanical.plumbing.exporters.dxf_exporter import PlumbingDXFExporter


def generate_plumbing_package(
    building_tag: str,
    fixtures: PlumbingFixturesSchedule,
    building_height_m: float = 12.0,
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes plumbing design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "plumbing")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("mechanical/plumbing", code=code)
    active_code = context["active_code"]

    # 2. Compute plumbing calculations
    engine = PlumbingEngine(code=active_code)
    res = engine.design_plumbing(
        building_tag=building_tag,
        fixtures=fixtures,
        building_height_m=building_height_m,
    )

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    coord_lines = [f"- ⚠️ {n}" for n in res.coordination_notices]

    replacements = {
        "{{code_used}}": active_code,
        "{{building_tag}}": res.building_tag,
        "{{total_dfu}}": f"{res.total_dfu:.1f}",
        "{{soil_stack_in}}": str(res.selected_soil_stack_diameter_in),
        "{{soil_stack_mm}}": str(res.selected_soil_stack_diameter_in * 25),
        "{{drain_in}}": str(res.selected_building_drain_diameter_in),
        "{{drain_mm}}": str(res.selected_building_drain_diameter_in * 25),
        "{{drain_slope}}": f"{res.minimum_drain_slope_pct:.1f}",
        "{{drain_fall}}": f"{res.minimum_drain_slope_pct * 10.0:.0f}",
        "{{total_wsfu}}": f"{res.total_wsfu:.1f}",
        "{{flow_gpm}}": f"{res.design_flow_gpm:.1f}",
        "{{flow_lps}}": f"{res.design_flow_l_per_s:.2f}",
        "{{static_head}}": f"{res.static_head_m:.1f}",
        "{{friction_head}}": f"{res.friction_head_m:.1f}",
        "{{residual_pressure}}": f"{res.residual_pressure_m:.1f}",
        "{{total_head_m}}": f"{res.total_pump_head_m:.1f}",
        "{{total_head_bar}}": f"{res.total_pump_head_bar:.2f}",
        "{{pump_kw}}": f"{res.pump_motor_power_kw:.2f}",
        "{{pump_voltage}}": str(int(res.pump_voltage_v)),
        "{{pump_current}}": f"{res.pump_current_amps:.1f}",
        "{{pump_mcb}}": str(res.pump_mcb_rating_amps),
        "{{sleeve_drain}}": res.sleeves_required[0]["sleeve_size"],
        "{{sleeve_potable}}": res.sleeves_required[1]["sleeve_size"],
        "{{coordination_checklist}}": "\n".join(coord_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = building_tag.lower().replace(" ", "_").replace("-", "_")
    md_path = out_dir / f"{clean_name}_plumbing_calculation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Workbook
    xlsx_path = out_dir / f"{clean_name}_plumbing_schedule.xlsx"
    excel_exporter = PlumbingExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF Riser
    dxf_path = out_dir / f"{clean_name}_plumbing_riser.dxf"
    dxf_exporter = PlumbingDXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    fixtures = PlumbingFixturesSchedule(
        water_closet_tank=8,
        lavatory=8,
        shower=4,
        kitchen_sink=4,
        washing_machine=2,
        floor_drain=6,
    )
    files = generate_plumbing_package(
        building_tag="Residential Villa Complex V-01",
        fixtures=fixtures,
        building_height_m=12.0,
        code="SBC",
    )
    print("Plumbing Deliverables Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
