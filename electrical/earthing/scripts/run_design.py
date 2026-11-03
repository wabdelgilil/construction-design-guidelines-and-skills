"""
Complete Multi-Deliverable Runner for Earthing Grid & Lightning Protection System (LPS).
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. AutoCAD Earthing Grid & LPS Roof Layout (.dxf)
3. Excel Resistance Schedule & Material BOQ (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from electrical.earthing.scripts.design_engine import (
    EarthingEngine,
    EarthingProjectInput,
    EarthingDesignResult,
)
from electrical.earthing.exporters.excel_exporter import EarthingExcelExporter
from electrical.earthing.exporters.dxf_exporter import EarthingDXFExporter


def generate_earthing_package(
    input_data: EarthingProjectInput,
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes earthing resistance design, LPS sizing, and outputs all deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "earthing")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("electrical/earthing", code=code)
    active_code = context["active_code"]
    standards = f"IEEE 80 / {active_code} 401 / IEC 62305"

    # 2. Run Deterministic Earthing Engine
    engine = EarthingEngine(standard=standards)
    res = engine.design_earthing_and_lps(input_data)

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    coord_lines = [f"- ⚡ {n}" for n in res.coordination_notices]

    replacements = {
        "{{standard_used}}": res.standard_used,
        "{{facility_type}}": res.facility_type,
        "{{project_name}}": res.project_name,
        "{{soil_resistivity}}": f"{res.soil_resistivity_ohm_m:.1f}",
        "{{single_rod_r}}": f"{res.single_rod_resistance_ohms:.2f}",
        "{{ring_r}}": f"{res.perimeter_ring_resistance_ohms:.2f}",
        "{{number_of_rods}}": str(res.number_of_earth_rods),
        "{{combined_r}}": f"{res.combined_earthing_resistance_ohms:.2f}",
        "{{target_r}}": f"{res.target_resistance_ohms:.1f}",
        "{{compliance_status}}": res.earthing_compliance_status,
        "{{lps_level}}": res.lps_level,
        "{{sphere_radius}}": f"{res.rolling_sphere_radius_m:.1f}",
        "{{air_terminals_count}}": str(res.air_terminals_count),
        "{{air_terminal_h}}": f"{res.air_terminal_height_m:.1f}",
        "{{down_count}}": str(res.down_conductors_count),
        "{{down_spacing}}": f"{res.down_conductor_max_spacing_m:.1f}",
        "{{test_links_count}}": str(res.test_links_count),
        "{{total_pits}}": str(res.total_earth_pits_count),
        "{{copper_70mm_m}}": f"{res.total_70mm2_bare_copper_m:.1f}",
        "{{copper_tape_m}}": f"{res.total_25x3mm_copper_tape_m:.1f}",
        "{{cadweld_count}}": str(res.number_of_earth_rods * 2 + 4),
        "{{coordination_checklist}}": "\n".join(coord_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = input_data.project_name.lower().replace(" ", "_")
    md_path = out_dir / f"{clean_name}_earthing_calculation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Workbook
    xlsx_path = out_dir / f"{clean_name}_earthing_schedule.xlsx"
    excel_exporter = EarthingExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF Earthing Layout
    dxf_path = out_dir / f"{clean_name}_earthing_and_lps_layout.dxf"
    dxf_exporter = EarthingDXFExporter(
        res,
        building_length_m=input_data.building_length_m,
        building_width_m=input_data.building_width_m,
    )
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    inp = EarthingProjectInput(
        project_name="Data Center Substation & Complex",
        facility_type="data_center",
        building_length_m=40.0,
        building_width_m=25.0,
        building_height_m=18.0,
        soil_resistivity_ohm_m=75.0,
        rod_length_m=3.0,
        rod_diameter_m=0.019,
        lps_level="LPL_I",  # Critical Facility
    )

    files = generate_earthing_package(
        input_data=inp,
        code="SBC",
    )
    print("Earthing & Lightning Protection Deliverables Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
