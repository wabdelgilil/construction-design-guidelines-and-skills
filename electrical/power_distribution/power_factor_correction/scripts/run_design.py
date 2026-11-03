"""
Complete Multi-Deliverable Runner for Automatic Power Factor Correction (APFC) & Detuned Filter Banks.
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. AutoCAD APFC Panel Front Elevation & Detuned Step Schematic (.dxf)
3. Excel APFC Step Schedule & Power Quality Metrics Workbook (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from electrical.power_distribution.power_factor_correction.scripts.design_engine import (
    PowerFactorCorrectionEngine,
    PFCDesignResult,
)
from electrical.power_distribution.power_factor_correction.exporters.excel_exporter import PFCExcelExporter
from electrical.power_distribution.power_factor_correction.exporters.dxf_exporter import PFC_DXFExporter


def generate_apfc_package(
    project_name: str,
    active_power_kw: float,
    initial_pf: float,
    target_pf: float = 0.96,
    nominal_voltage_v: float = 400.0,
    frequency_hz: float = 60.0,
    detuning_reactor_p_percent: float = 7.0,
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes APFC design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "power_factor_correction")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("electrical/power_distribution/power_factor_correction", code=code)
    active_code = context["active_code"]
    standards = f"IEC 61921 / IEC 60831 / IEEE 519 / {active_code} 401"

    # 2. Run Deterministic APFC Engine
    engine = PowerFactorCorrectionEngine(standard=standards)
    res = engine.calculate_apfc_bank(
        project_name=project_name,
        active_power_kw=active_power_kw,
        initial_pf=initial_pf,
        target_pf=target_pf,
        nominal_voltage_v=nominal_voltage_v,
        frequency_hz=frequency_hz,
        detuning_reactor_p_percent=detuning_reactor_p_percent,
    )

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    # Build step table rows
    s_rows = []
    for s in res.steps:
        row = f"| Step {s.step_number:02d} | {s.step_kvar:.1f} kVAR | {s.effective_kvar:.1f} kVAR | {s.rated_voltage_v:.0f} V | {s.step_nominal_current_a:.1f} A | {s.step_design_current_a:.1f} A | {s.switching_contactor_type} | {s.contactor_rating_ac6b_a:.1f} A | {s.step_fuse_or_mccb_a} A | {s.reactor_inductance_mh:.3f} mH |"
        s_rows.append(row)
    step_table = "\n".join(s_rows)

    coord_lines = [f"- ⚡ {notice}" for notice in res.coordination_notices]

    v_calc = res.nominal_voltage_v / (1.0 - (res.detuned_reactor_percent / 100.0))

    replacements = {
        "{{project_name}}": res.project_name,
        "{{standard_used}}": res.standard_used,
        "{{nominal_voltage}}": f"{res.nominal_voltage_v:.0f}",
        "{{frequency}}": f"{res.frequency_hz:.0f}",
        "{{selected_kvar}}": f"{res.selected_total_kvar:.0f}",
        "{{step_sequence}}": res.step_progression_sequence,
        "{{active_power_kw}}": f"{res.active_power_kw:.1f}",
        "{{initial_pf}}": f"{res.initial_power_factor:.2f}",
        "{{target_pf}}": f"{res.target_power_factor:.2f}",
        "{{calculated_kvar}}": f"{res.calculated_kvar:.1f}",
        "{{initial_kva}}": f"{res.apparent_power_initial_kva:.1f}",
        "{{corrected_kva}}": f"{res.apparent_power_corrected_kva:.1f}",
        "{{released_kva}}": f"{res.apparent_power_released_kva:.1f}",
        "{{current_reduction_a}}": f"{res.line_current_reduction_a:.1f}",
        "{{detuned_p_percent}}": f"{res.detuned_reactor_percent:.1f}",
        "{{detuned_p_decimal}}": f"{res.detuned_reactor_percent / 100.0:.2f}",
        "{{tuning_frequency_hz}}": f"{res.tuning_frequency_hz:.1f}",
        "{{calc_vc}}": f"{v_calc:.1f}",
        "{{cap_rated_voltage}}": f"{res.capacitor_rated_voltage_v:.0f}",
        "{{total_nominal_a}}": f"{res.total_bank_nominal_current_a:.1f}",
        "{{total_design_a}}": f"{res.total_bank_design_current_a:.1f}",
        "{{incomer_mccb}}": str(res.incomer_mccb_rating_a),
        "{{step_table_rows}}": step_table,
        "{{coordination_checklist}}": "\n".join(coord_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = project_name.lower().replace(" ", "_")
    md_path = out_dir / f"{clean_name}_apfc_calculation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Workbook
    xlsx_path = out_dir / f"{clean_name}_apfc_schedule.xlsx"
    excel_exporter = PFCExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF Drawing
    dxf_path = out_dir / f"{clean_name}_apfc_elevation.dxf"
    dxf_exporter = PFC_DXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    files = generate_apfc_package(
        project_name="Central Commercial Complex APFC",
        active_power_kw=800.0,
        initial_pf=0.80,
        target_pf=0.96,
        nominal_voltage_v=400.0,
        frequency_hz=60.0,
        detuning_reactor_p_percent=7.0,
    )
    print("APFC Engineering Package successfully generated:")
    for k, p in files.items():
        print(f"  - {k}: {p}")
