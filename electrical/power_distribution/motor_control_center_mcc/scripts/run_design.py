"""
Complete Multi-Deliverable Runner for Motor Control Center (MCC) & Motor Starters.
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. AutoCAD MCC Physical Elevation & Starter Wiring Schematic Drawing (.dxf)
3. Excel Motor Schedule, Contactor Ratings, and BOQ Workbook (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from electrical.power_distribution.motor_control_center_mcc.scripts.design_engine import (
    MotorControlCenterEngine,
    MotorLoadInput,
    MCCDesignResult,
)
from electrical.power_distribution.motor_control_center_mcc.exporters.excel_exporter import MCCExcelExporter
from electrical.power_distribution.motor_control_center_mcc.exporters.dxf_exporter import MCCDXFExporter


def generate_mcc_package(
    project_name: str,
    motors: List[MotorLoadInput],
    nominal_voltage_v: float = 400.0,
    frequency_hz: float = 60.0,
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes MCC design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "mcc")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("electrical/power_distribution/motor_control_center_mcc", code=code)
    active_code = context["active_code"]
    standards = f"IEC 60947-4-1 / IEC 61439-2 / {active_code} 401"

    # 2. Run Deterministic Motor Control Center Engine
    engine = MotorControlCenterEngine(standard=standards)
    res = engine.design_mcc(
        project_name=project_name,
        motors=motors,
        nominal_voltage_v=nominal_voltage_v,
        frequency_hz=frequency_hz,
    )

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    # Build motor table rows
    m_rows = []
    for m in res.motors:
        row = f"| {m.tag} | {m.description} | {m.rated_kw:.1f} | {m.rated_hp:.1f} | {m.fla_a:.1f} | {m.starting_method} | {m.starting_current_a:.1f} | {m.contactor_main_ac3_a:.1f} A | {m.overload_setting_a:.1f} A | {m.mcp_breaker_rating_a} A | {m.feeder_cable_csa_mm2} mm² | {m.run_voltage_drop_pct:.2f}% | {m.start_voltage_drop_pct:.2f}% |"
        m_rows.append(row)
    motor_table = "\n".join(m_rows)

    coord_lines = [f"- ⚙️ {notice}" for notice in res.coordination_notices]

    replacements = {
        "{{project_name}}": res.project_name,
        "{{standard_used}}": res.standard_used,
        "{{nominal_voltage}}": f"{res.nominal_voltage_v:.0f}",
        "{{frequency}}": f"{res.frequency_hz:.0f}",
        "{{segregation_form}}": res.segregation_form,
        "{{total_kw}}": f"{res.total_connected_kw:.1f}",
        "{{total_hp}}": f"{res.total_connected_hp:.1f}",
        "{{total_fla}}": f"{res.total_full_load_current_a:.1f}",
        "{{incomer_rating}}": str(res.mcc_main_incomer_rating_a),
        "{{busbar_rating}}": str(res.mcc_main_busbar_rating_a),
        "{{total_columns}}": str(res.total_columns_count),
        "{{motor_table_rows}}": motor_table,
        "{{coordination_checklist}}": "\n".join(coord_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = project_name.lower().replace(" ", "_")
    md_path = out_dir / f"{clean_name}_mcc_calculation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Workbook
    xlsx_path = out_dir / f"{clean_name}_mcc_schedule.xlsx"
    excel_exporter = MCCExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF Drawing
    dxf_path = out_dir / f"{clean_name}_mcc_elevation.dxf"
    dxf_exporter = MCCDXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    sample_motors = [
        MotorLoadInput("CHWP-01", "Primary Chilled Water Pump 1", rated_kw=37.0, application_type="constant_speed", feeder_length_m=35.0),
        MotorLoadInput("CHWP-02", "Primary Chilled Water Pump 2 (Standby)", rated_kw=37.0, application_type="constant_speed", feeder_length_m=38.0),
        MotorLoadInput("SCHWP-01", "Secondary Chilled Water Pump 1 (VFD)", rated_kw=45.0, application_type="variable_speed", feeder_length_m=45.0),
        MotorLoadInput("CWP-01", "Condenser Water Pump 1", rated_kw=55.0, application_type="constant_speed", feeder_length_m=40.0),
        MotorLoadInput("AHU-SF-01", "AHU Supply Air Fan 1 (VFD)", rated_kw=22.0, application_type="variable_speed", feeder_length_m=50.0),
        MotorLoadInput("SEF-01", "Smoke Exhaust Fan 1 (High Inertia)", rated_kw=30.0, application_type="high_inertia_fan", feeder_length_m=60.0),
        MotorLoadInput("PUMP-DOM-01", "Domestic Water Booster Pump 1", rated_kw=5.5, application_type="constant_speed", feeder_length_m=25.0),
        MotorLoadInput("PUMP-DOM-02", "Domestic Water Booster Pump 2", rated_kw=5.5, application_type="constant_speed", feeder_length_m=28.0),
    ]

    files = generate_mcc_package("Central Utility Plant Motor Control Center", sample_motors)
    print("MCC Engineering Package successfully generated:")
    for k, p in files.items():
        print(f"  - {k}: {p}")
