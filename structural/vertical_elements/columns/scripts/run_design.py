"""
Complete Multi-Deliverable Runner for Reinforced Concrete Column Design.
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
from structural.vertical_elements.columns.scripts.design_engine import (
    ColumnInput,
    ColumnEngine,
    ColumnDesignResult,
)
from structural.vertical_elements.columns.exporters.dxf_exporter import ColumnDXFExporter
from structural.vertical_elements.columns.exporters.excel_exporter import ColumnExcelExporter


def generate_column_package(
    dead_load_kn: float,
    live_load_kn: float,
    unbraced_len_m: float = 3.20,
    k_factor: float = 1.0,
    pref_width_mm: float = 250.0,
    code: str = None,
    element_id: str = "C-01",
    output_dir: Path = None,
) -> Dict[str, Path]:
    """Executes column design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "columns")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("structural/vertical_elements/columns", code=code)
    rules = context["rules"]
    active_code = context["active_code"]

    # 2. Extract inherited parameters
    fc = rules.get("default_fc_prime_mpa") or rules.get("default_fcu_mpa", 28.0)
    fy = rules.get("default_fy_mpa", 420.0)
    cover = rules.get("concrete_cover_mm", 40.0)

    # 3. Deterministic calculation
    inp = ColumnInput(
        dead_load_kn=dead_load_kn,
        live_load_kn=live_load_kn,
        unbraced_length_m=unbraced_len_m,
        effective_length_factor_k=k_factor,
        preferred_width_mm=pref_width_mm,
        fc_prime_mpa=fc,
        fy_mpa=fy,
        concrete_cover_mm=cover,
        code=active_code,
    )
    engine = ColumnEngine(inp)
    res = engine.design()

    generated_files = {}

    # 4. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    r_gyr = round(0.30 * res.width_mm, 1)

    replacements = {
        "{{code_used}}": str(res.code_used),
        "{{element_id}}": str(element_id),
        "{{dead_load_kn}}": str(dead_load_kn),
        "{{live_load_kn}}": str(live_load_kn),
        "{{service_load_kn}}": str(res.service_load_kn),
        "{{ultimate_load_kn}}": str(res.ultimate_load_kn),
        "{{unbraced_len_m}}": f"{unbraced_len_m:.2f}",
        "{{k_factor}}": f"{k_factor}",
        "{{fc_mpa}}": str(fc),
        "{{fy_mpa}}": str(fy),
        "{{cover_mm}}": str(int(cover)),
        "{{r_gyration_mm}}": str(r_gyr),
        "{{slenderness_lambda}}": str(res.slenderness_ratio_lambda),
        "{{slenderness_limit}}": str(res.slenderness_limit),
        "{{classification}}": res.classification,
        "{{magnified_moment_knm}}": str(res.magnified_moment_kn_m),
        "{{col_b_mm}}": str(int(res.width_mm)),
        "{{col_l_mm}}": str(int(res.length_mm)),
        "{{gross_area_mm2}}": str(int(res.gross_area_ag_mm2)),
        "{{design_axial_capacity_kn}}": str(res.design_axial_capacity_kn),
        "{{capacity_ratio}}": f"{res.capacity_ratio * 100:.1f}%",
        "{{axial_status}}": "SAFE" if res.capacity_ratio <= 1.0 else "EXCEEDED",
        "{{as_req_mm2}}": str(res.as_required_mm2),
        "{{as_min_mm2}}": str(int(res.gross_area_ag_mm2 * 0.01)),
        "{{as_prov_mm2}}": str(res.as_provided_mm2),
        "{{steel_ratio_pct}}": str(res.actual_steel_ratio_pct),
        "{{longitudinal_rebar_desc}}": res.longitudinal_rebar_desc,
        "{{tie_desc}}": res.tie_desc,
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
    dxf_exporter = ColumnDXFExporter(res, inp)
    dxf_exporter.export(dxf_path)
    generated_files["autocad_dxf"] = dxf_path

    # 6. Generate Excel Calculation Workbook (with BBS and BOQ)
    xlsx_path = out_dir / f"{element_id}_design_book.xlsx"
    excel_exporter = ColumnExcelExporter(res, inp)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    return generated_files


if __name__ == "__main__":
    files = generate_column_package(
        dead_load_kn=1000,
        live_load_kn=500,
        unbraced_len_m=3.5,
        pref_width_mm=250,
        code="SBC",
        element_id="C-01",
    )
    print("Column Deliverables Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
