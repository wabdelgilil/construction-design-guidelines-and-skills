"""
Complete Multi-Deliverable Runner for Strap (Cantilever) Footing Design.
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
from structural.foundations.strap_footing.scripts.design_engine import (
    StrapFootingInput,
    StrapFootingEngine,
    StrapFootingDesignResult,
)
from structural.foundations.strap_footing.exporters.dxf_exporter import StrapFootingDXFExporter
from structural.foundations.strap_footing.exporters.excel_exporter import StrapFootingExcelExporter


def generate_strap_footing_package(
    col1_l_mm: float,
    col1_w_mm: float,
    col1_dead_kn: float,
    col1_live_kn: float,
    col2_l_mm: float,
    col2_w_mm: float,
    col2_dead_kn: float,
    col2_live_kn: float,
    span_m: float,
    soil_capacity_kpa: float = None,
    code: str = None,
    element_id: str = "STRAP-01",
    output_dir: Path = None,
) -> Dict[str, Path]:
    """Executes strap footing design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "strap_footing")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("structural/foundations/strap_footing", code=code)
    rules = context["rules"]
    active_code = context["active_code"]

    # 2. Extract inherited parameters
    q_all = soil_capacity_kpa or rules.get("default_allowable_soil_bearing_capacity_kpa", 200.0)
    fc = rules.get("default_fc_prime_mpa") or rules.get("default_fcu_mpa", 28.0)
    fy = rules.get("default_fy_mpa", 420.0)

    # 3. Deterministic calculation
    inp = StrapFootingInput(
        col1_length_mm=col1_l_mm,
        col1_width_mm=col1_w_mm,
        col1_dead_load_kn=col1_dead_kn,
        col1_live_load_kn=col1_live_kn,
        col2_length_mm=col2_l_mm,
        col2_width_mm=col2_w_mm,
        col2_dead_load_kn=col2_dead_kn,
        col2_live_load_kn=col2_live_kn,
        span_center_to_center_m=span_m,
        allowable_soil_capacity_kpa=q_all,
        fc_prime_mpa=fc,
        fy_mpa=fy,
        code=active_code,
    )
    engine = StrapFootingEngine(inp)
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
        "{{q_all_kpa}}": str(q_all),
        "{{fc_mpa}}": str(fc),
        "{{fy_mpa}}": str(fy),
        "{{r1_service_kn}}": str(res.f1_service_reaction_kn),
        "{{r2_service_kn}}": str(res.f2_service_reaction_kn),
        "{{r1_u_kn}}": str(res.f1_ultimate_reaction_kn),
        "{{r2_u_kn}}": str(res.f2_ultimate_reaction_kn),
        "{{f1_l_m}}": f"{res.f1_length_m:.2f}",
        "{{f1_w_m}}": f"{res.f1_width_m:.2f}",
        "{{f1_t_mm}}": str(int(res.f1_thickness_mm)),
        "{{f1_rebar}}": res.f1_rebar_transverse,
        "{{f1_status}}": res.f1_status,
        "{{f2_l_m}}": f"{res.f2_length_m:.2f}",
        "{{f2_w_m}}": f"{res.f2_width_m:.2f}",
        "{{f2_t_mm}}": str(int(res.f2_thickness_mm)),
        "{{f2_rebar_l}}": res.f2_rebar_l,
        "{{f2_rebar_b}}": res.f2_rebar_b,
        "{{f2_status}}": res.f2_status,
        "{{strap_b_mm}}": str(int(res.strap_width_mm)),
        "{{strap_h_mm}}": str(int(res.strap_depth_mm)),
        "{{strap_moment_knm}}": str(res.strap_max_negative_moment_kn_m),
        "{{strap_shear_kn}}": str(res.strap_max_shear_kn),
        "{{strap_as_mm2}}": str(res.strap_top_steel_as_mm2),
        "{{strap_top_rebar}}": res.strap_top_rebar_desc,
        "{{strap_stirrups}}": res.strap_stirrups_desc,
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
    dxf_exporter = StrapFootingDXFExporter(res, inp)
    dxf_exporter.export(dxf_path)
    generated_files["autocad_dxf"] = dxf_path

    # 6. Generate Excel Calculation Workbook (with BBS and BOQ)
    xlsx_path = out_dir / f"{element_id}_design_book.xlsx"
    excel_exporter = StrapFootingExcelExporter(res, inp)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    return generated_files


if __name__ == "__main__":
    files = generate_strap_footing_package(
        col1_l_mm=600,
        col1_w_mm=300,
        col1_dead_kn=900,
        col1_live_kn=450,
        col2_l_mm=600,
        col2_w_mm=400,
        col2_dead_kn=1400,
        col2_live_kn=700,
        span_m=5.5,
        soil_capacity_kpa=200,
        code="SBC",
        element_id="STRAP-01",
    )
    print("Strap Footing Deliverables Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
