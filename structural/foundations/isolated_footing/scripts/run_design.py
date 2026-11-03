"""
Complete Multi-Deliverable Runner for Isolated Footing Design.
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. Native AutoCAD 2D Drawing (.dxf)
3. Excel Calculation Workbook + Bar Bending Schedule (BBS) + BOQ (.xlsx)
4. Autodesk Revit Family Placement Script (.py)
"""

import sys
from pathlib import Path
from typing import Dict

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from structural.foundations.isolated_footing.scripts.design_engine import (
    FootingInput,
    IsolatedFootingEngine,
    FootingDesignResult,
)
from structural.foundations.isolated_footing.exporters.dxf_exporter import IsolatedFootingDXFExporter
from structural.foundations.isolated_footing.exporters.excel_exporter import IsolatedFootingExcelExporter
from structural.foundations.isolated_footing.exporters.revit_exporter import IsolatedFootingRevitExporter


def generate_isolated_footing_package(
    col_l_mm: float,
    col_w_mm: float,
    dead_load_kn: float,
    live_load_kn: float,
    soil_capacity_kpa: float = None,
    code: str = None,
    element_id: str = "F-01",
    output_dir: Path = None,
) -> Dict[str, Path]:
    """
    Executes design and outputs all project deliverables into output_dir.
    Returns dictionary with paths to all generated files.
    """
    out_dir = Path(output_dir or (root_dir / "output" / "isolated_footing")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("structural/foundations/isolated_footing", code=code)
    rules = context["rules"]
    active_code = context["active_code"]

    # 2. Extract inherited parameters
    q_all = soil_capacity_kpa or rules.get("default_allowable_soil_bearing_capacity_kpa", 200.0)
    fc = rules.get("default_fc_prime_mpa") or rules.get("default_fcu_mpa", 28.0)
    fy = rules.get("default_fy_mpa", 420.0)
    cover = rules.get("min_concrete_cover_earth_cast_mm", 75.0)
    bar_dia = rules.get("default_bar_diameter_mm", 14)

    # 3. Deterministic calculation
    inp = FootingInput(
        column_length_mm=col_l_mm,
        column_width_mm=col_w_mm,
        dead_load_kn=dead_load_kn,
        live_load_kn=live_load_kn,
        allowable_soil_capacity_kpa=q_all,
        fc_prime_mpa=fc,
        fy_mpa=fy,
        concrete_cover_mm=cover,
        preferred_bar_dia_mm=bar_dia,
        code=active_code,
    )
    engine = IsolatedFootingEngine(inp)
    res = engine.design()

    generated_files = {}

    # 4. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    replacements = {
        "{{code_used}}": str(res.code_used),
        "{{element_id}}": str(element_id),
        "{{col_length}}": str(int(col_l_mm)),
        "{{col_width}}": str(int(col_w_mm)),
        "{{dead_load_kn}}": str(dead_load_kn),
        "{{live_load_kn}}": str(live_load_kn),
        "{{service_load_kn}}": str(round(res.service_load_kn, 1)),
        "{{ultimate_load_kn}}": str(round(res.ultimate_load_kn, 1)),
        "{{fc_mpa}}": str(fc),
        "{{fy_mpa}}": str(fy),
        "{{cover_mm}}": str(int(cover)),
        "{{q_all_kpa}}": str(q_all),
        "{{area_req}}": str(round(res.service_load_kn / q_all, 2)),
        "{{length_m}}": f"{res.length_mm/1000.0:.2f}",
        "{{length_mm}}": str(int(res.length_mm)),
        "{{width_m}}": f"{res.width_mm/1000.0:.2f}",
        "{{width_mm}}": str(int(res.width_mm)),
        "{{thickness_mm}}": str(int(res.thickness_mm)),
        "{{depth_mm}}": str(int(res.effective_depth_mm)),
        "{{actual_soil_pressure}}": str(res.actual_soil_pressure_service_kpa),
        "{{soil_status}}": "SAFE" if res.actual_soil_pressure_service_kpa <= q_all * 1.05 else "EXCEEDED",
        "{{qu_kpa}}": str(res.net_ultimate_soil_pressure_kpa),
        "{{bo_mm}}": str(res.punching_perimeter_bo_mm),
        "{{vu_punch_kn}}": str(res.punching_shear_force_vu_kn),
        "{{stress_punch_mpa}}": str(res.punching_shear_stress_mpa),
        "{{cap_punch_mpa}}": str(res.punching_capacity_mpa),
        "{{punch_ratio}}": str(res.punching_safety_ratio),
        "{{punching_status}}": str(res.punching_status),
        "{{vu_beam_kn}}": str(res.beam_shear_force_vu_kn),
        "{{stress_beam_mpa}}": str(res.beam_shear_stress_mpa),
        "{{cap_beam_mpa}}": str(res.beam_shear_capacity_mpa),
        "{{beam_ratio}}": str(res.beam_shear_safety_ratio),
        "{{beam_shear_status}}": str(res.beam_shear_status),
        "{{moment_l_knm}}": str(res.moment_ul_kn_m),
        "{{as_req_l}}": str(res.as_required_l_mm2),
        "{{as_min_l}}": str(res.as_min_l_mm2),
        "{{as_prov_l}}": str(res.as_provided_l_mm2),
        "{{rebar_l_desc}}": f"{res.bars_l_count} T{res.bar_dia_l_mm} ({res.bars_per_meter_l})",
        "{{spacing_l_mm}}": str(res.bar_spacing_l_mm),
        "{{moment_b_knm}}": str(res.moment_ub_kn_m),
        "{{as_req_b}}": str(res.as_required_b_mm2),
        "{{as_min_b}}": str(res.as_min_b_mm2),
        "{{as_prov_b}}": str(res.as_provided_b_mm2),
        "{{rebar_b_desc}}": f"{res.bars_b_count} T{res.bar_dia_b_mm} ({res.bars_per_meter_b})",
        "{{spacing_b_mm}}": str(res.bar_spacing_b_mm),
        "{{overall_status}}": str(res.overall_status),
    }
    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    md_path = out_dir / f"{element_id}_calculation_note.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 5. Generate AutoCAD DXF Drawing
    dxf_path = out_dir / f"{element_id}_drawing.dxf"
    dxf_exporter = IsolatedFootingDXFExporter(res, col_l_mm, col_w_mm)
    dxf_exporter.export(dxf_path)
    generated_files["autocad_dxf"] = dxf_path

    # 6. Generate Excel Calculation Workbook (with BBS and BOQ)
    xlsx_path = out_dir / f"{element_id}_design_book.xlsx"
    excel_exporter = IsolatedFootingExcelExporter(res, col_l_mm, col_w_mm)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 7. Generate Autodesk Revit Script
    revit_path = out_dir / f"{element_id}_revit_placement.py"
    revit_exporter = IsolatedFootingRevitExporter(res, col_l_mm, col_w_mm)
    revit_exporter.export(revit_path)
    generated_files["revit_script"] = revit_path

    return generated_files


if __name__ == "__main__":
    files = generate_isolated_footing_package(
        col_l_mm=500,
        col_w_mm=300,
        dead_load_kn=800,
        live_load_kn=400,
        soil_capacity_kpa=200,
        code="SBC",
        element_id="F-01",
    )
    print("Complete Engineering Deliverables Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
