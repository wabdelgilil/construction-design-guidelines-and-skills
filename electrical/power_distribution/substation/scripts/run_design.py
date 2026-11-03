"""
Complete Multi-Deliverable Runner for Substation, Transformer, Generator & MDB Design.
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. AutoCAD Power Single Line Diagram (SLD) (.dxf)
3. Excel Equipment Schedule & Load Calculation Workbook (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from electrical.power_distribution.substation.scripts.design_engine import (
    SubstationEngine,
    BuildingLoadsInput,
    SubstationDesignResult,
)
from electrical.power_distribution.substation.exporters.excel_exporter import SubstationExcelExporter
from electrical.power_distribution.substation.exporters.dxf_exporter import SubstationDXFExporter


def generate_substation_package(
    loads: BuildingLoadsInput,
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes substation design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "substation")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("electrical/power_distribution", code=code)
    active_code = context["active_code"]
    standards = f"IEC 60076 / {active_code} 401 / ISO 8528"

    # 2. Run Deterministic Substation Engine
    engine = SubstationEngine(voltage_v=400.0, standard=standards)
    res = engine.design_substation(loads)

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    coord_lines = [f"- ⚠️ {notice}" for notice in res.coordination_notices]

    replacements = {
        "{{standard_used}}": res.standard_used,
        "{{tx_primary_kv}}": f"{res.transformer_primary_kv:.1f}",
        "{{tx_secondary_v}}": f"{res.transformer_secondary_v:.0f}",
        "{{project_name}}": res.project_name,
        "{{lighting_kw}}": f"{loads.lighting_kw:.1f}",
        "{{sockets_kw}}": f"{loads.sockets_kw:.1f}",
        "{{hvac_kw}}": f"{loads.hvac_kw:.1f}",
        "{{elevators_kw}}": f"{loads.elevators_kw:.1f}",
        "{{pumps_kw}}": f"{loads.pumps_kw:.1f}",
        "{{life_safety_kw}}": f"{loads.life_safety_kw:.1f}",
        "{{it_ups_kw}}": f"{loads.it_ups_kw:.1f}",
        "{{total_kw}}": f"{res.total_connected_kw:.1f}",
        "{{total_kva}}": f"{res.total_connected_kva:.1f}",
        "{{max_demand_kw}}": f"{res.max_demand_kw:.1f}",
        "{{max_demand_kva}}": f"{res.max_demand_kva:.1f}",
        "{{tx_kva}}": str(res.selected_transformer_kva),
        "{{tx_loading_pct}}": f"{res.transformer_loading_pct:.1f}",
        "{{tx_flc_amps}}": f"{res.transformer_flc_amps:.1f}",
        "{{tx_uk}}": f"{res.transformer_uk_pct:.1f}",
        "{{tx_isc_ka}}": f"{res.prospective_short_circuit_ka:.1f}",
        "{{mdb_incomer_amps}}": str(res.mdb_incomer_rating_amps),
        "{{mdb_breaker_type}}": res.mdb_incomer_breaker_type,
        "{{mdb_icu_ka}}": str(res.mdb_incomer_icu_ka),
        "{{emg_kw}}": f"{res.emergency_connected_kw:.1f}",
        "{{emg_kva}}": f"{res.emergency_demand_kva:.1f}",
        "{{motor_inrush_kva}}": f"{res.motor_starting_inrush_kva:.1f}",
        "{{gen_kva}}": str(res.selected_generator_kva),
        "{{gen_amps}}": f"{res.generator_standby_amps:.1f}",
        "{{ats_amps}}": str(res.ats_rating_amps),
        "{{ats_poles}}": str(res.ats_poles),
        "{{coordination_checklist}}": "\n".join(coord_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = loads.project_name.lower().replace(" ", "_")
    md_path = out_dir / f"{clean_name}_substation_calculation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Workbook
    xlsx_path = out_dir / f"{clean_name}_substation_schedule.xlsx"
    excel_exporter = SubstationExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF SLD
    dxf_path = out_dir / f"{clean_name}_power_single_line_diagram.dxf"
    dxf_exporter = SubstationDXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    loads_data = BuildingLoadsInput(
        project_name="Commercial Tower Substation",
        lighting_kw=65.0,
        sockets_kw=110.0,
        hvac_kw=380.0,
        elevators_kw=90.0,
        pumps_kw=45.0,
        life_safety_kw=75.0,
        it_ups_kw=50.0,
        largest_single_motor_kw=45.0,
        future_expansion_pct=15.0,
    )

    files = generate_substation_package(
        loads=loads_data,
        code="SBC",
    )
    print("Substation & Incomer Deliverables Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
