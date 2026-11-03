"""
Complete Multi-Deliverable Runner for Combined Footing Design.
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. Native AutoCAD 2D Drawing (.dxf)
3. Excel Calculation Workbook + Bar Bending Schedule (BBS) + BOQ (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from structural.foundations.combined_footing.scripts.design_engine import (
    CombinedFootingInput,
    CombinedFootingEngine,
    CombinedFootingDesignResult,
)
from structural.foundations.combined_footing.exporters.dxf_exporter import CombinedFootingDXFExporter
from structural.foundations.combined_footing.exporters.excel_exporter import CombinedFootingExcelExporter


def generate_combined_footing_package(
    col1_l_mm: float,
    col1_w_mm: float,
    col1_dead_kn: float,
    col1_live_kn: float,
    col2_l_mm: float,
    col2_w_mm: float,
    col2_dead_kn: float,
    col2_live_kn: float,
    span_m: float,
    d1_m: float = 0.30,
    soil_capacity_kpa: float = None,
    code: str = None,
    element_id: str = "COMB-01",
    output_dir: Path = None,
) -> Dict[str, Path]:
    """Executes combined footing design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "combined_footing")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("structural/foundations/combined_footing", code=code)
    rules = context["rules"]
    active_code = context["active_code"]

    # 2. Extract inherited parameters
    q_all = soil_capacity_kpa or rules.get("default_allowable_soil_bearing_capacity_kpa", 200.0)
    fc = rules.get("default_fc_prime_mpa") or rules.get("default_fcu_mpa", 28.0)
    fy = rules.get("default_fy_mpa", 420.0)

    # 3. Deterministic calculation
    inp = CombinedFootingInput(
        col1_length_mm=col1_l_mm,
        col1_width_mm=col1_w_mm,
        col1_dead_load_kn=col1_dead_kn,
        col1_live_load_kn=col1_live_kn,
        col2_length_mm=col2_l_mm,
        col2_width_mm=col2_w_mm,
        col2_dead_load_kn=col2_dead_kn,
        col2_live_load_kn=col2_live_kn,
        span_center_to_center_m=span_m,
        col1_edge_distance_m=d1_m,
        allowable_soil_capacity_kpa=q_all,
        fc_prime_mpa=fc,
        fy_mpa=fy,
        code=active_code,
    )
    engine = CombinedFootingEngine(inp)
    res = engine.design()

    generated_files = {}

    # 4. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    replacements = {
        "{{code_used}}": str(res.code_used),
        "{{element_id}}": str(element_id),
        "{{col1_l}}": str(int(col1_l_mm)),
        "{{col1_w}}": str(int(col1_w_mm)),
        "{{col1_dead_kn}}": str(col1_dead_kn),
        "{{col1_live_kn}}": str(col1_live_kn),
        "{{col2_l}}": str(int(col2_l_mm)),
        "{{col2_w}}": str(int(col2_w_mm)),
        "{{col2_dead_kn}}": str(col2_dead_kn),
        "{{col2_live_kn}}": str(col2_live_kn),
        "{{span_m}}": f"{span_m:.2f}",
        "{{d1_m}}": f"{d1_m:.2f}",
        "{{q_all_kpa}}": str(q_all),
        "{{fc_mpa}}": str(fc),
        "{{fy_mpa}}": str(fy),
        "{{service_load_kn}}": str(res.total_service_load_kn),
        "{{ultimate_load_kn}}": str(res.total_ultimate_load_kn),
        "{{length_m}}": f"{res.length_m:.2f}",
        "{{width_m}}": f"{res.width_m:.2f}",
        "{{thickness_mm}}": str(int(res.thickness_mm)),
        "{{depth_mm}}": str(int(res.effective_depth_mm)),
        "{{actual_soil_pressure}}": str(res.actual_service_soil_pressure_kpa),
        "{{qu_kpa}}": str(res.net_ultimate_soil_pressure_kpa),
        "{{zero_shear_m}}": str(res.zero_shear_point_from_left_m),
        "{{max_neg_moment_knm}}": str(res.max_negative_moment_kn_m),
        "{{max_shear_kn}}": str(res.max_shear_force_kn),
        "{{punching_status}}": res.punching_status,
        "{{punch_r1}}": str(res.punching_ratio_col1),
        "{{punch_r2}}": str(res.punching_ratio_col2),
        "{{beam_shear_status}}": res.beam_shear_status,
        "{{beam_shear_ratio}}": str(res.beam_shear_ratio),
        "{{top_steel_desc}}": res.top_longitudinal_rebar_desc,
        "{{bot_steel_desc}}": res.bottom_longitudinal_rebar_desc,
        "{{trans1_desc}}": res.transverse_rebar_col1_desc,
        "{{trans2_desc}}": res.transverse_rebar_col2_desc,
        "{{overall_status}}": res.overall_status,
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    md_path = out_dir / f"{element_id}_calculation_note.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 5. Generate AutoCAD DXF Drawing
    dxf_path = out_dir / f"{element_id}_drawing.dxf"
    dxf_exporter = CombinedFootingDXFExporter(res, inp)
    dxf_exporter.export(dxf_path)
    generated_files["autocad_dxf"] = dxf_path

    # 6. Generate Excel Calculation Workbook (with BBS and BOQ)
    xlsx_path = out_dir / f"{element_id}_design_book.xlsx"
    excel_exporter = CombinedFootingExcelExporter(res, inp)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    return generated_files


if __name__ == "__main__":
    files = generate_combined_footing_package(
        col1_l_mm=500,
        col1_w_mm=300,
        col1_dead_kn=700,
        col1_live_kn=350,
        col2_l_mm=600,
        col2_w_mm=400,
        col2_dead_kn=1100,
        col2_live_kn=550,
        span_m=4.5,
        d1_m=0.35,
        soil_capacity_kpa=200,
        code="SBC",
        element_id="COMB-01",
    )
    print("Combined Footing Deliverables Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
