"""
Complete Multi-Deliverable Runner for HVAC Cooling Load & Air Distribution.
Generates:
1. Markdown Calculation Note (.md)
2. AutoCAD Ducting & Diffuser Layout Plan (.dxf)
3. Excel Heat Load & MEP Coordination Matrix (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from mechanical.hvac.heat_load.scripts.design_engine import (
    CoolingLoadEngine,
    HVACSpaceInput,
    HVACDesignResult,
)
from mechanical.hvac.heat_load.exporters.excel_exporter import HVACExcelExporter
from mechanical.hvac.heat_load.exporters.dxf_exporter import HVACDXFExporter


def generate_hvac_package(
    space_input: HVACSpaceInput,
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes HVAC cooling load design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "hvac")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("mechanical/hvac/heat_load", code=code)
    active_code = context["active_code"]

    # 2. Compute cooling load
    engine = CoolingLoadEngine(code=active_code)
    res = engine.compute_cooling_load(space_input)

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    gt = max(res.grand_total_heat_w, 1.0)
    coord_lines = [f"- ⚠️ {n}" for n in res.coordination_notices]

    replacements = {
        "{{code_used}}": active_code,
        "{{space_name}}": res.space_name,
        "{{area_m2}}": f"{res.area_m2:.2f}",
        "{{volume_m3}}": f"{res.volume_m3:.2f}",
        "{{envelope_w}}": f"{res.envelope_heat_gain_w:.1f}",
        "{{envelope_pct}}": f"{res.envelope_heat_gain_w/gt*100:.1f}",
        "{{solar_w}}": f"{res.glass_solar_gain_w:.1f}",
        "{{solar_pct}}": f"{res.glass_solar_gain_w/gt*100:.1f}",
        "{{occ_total_w}}": f"{res.occupant_sensible_gain_w + res.occupant_latent_gain_w:.1f}",
        "{{occ_sensible_w}}": f"{res.occupant_sensible_gain_w:.1f}",
        "{{occ_latent_w}}": f"{res.occupant_latent_gain_w:.1f}",
        "{{occ_pct}}": f"{(res.occupant_sensible_gain_w + res.occupant_latent_gain_w)/gt*100:.1f}",
        "{{lights_w}}": f"{res.lighting_gain_w:.1f}",
        "{{lights_pct}}": f"{res.lighting_gain_w/gt*100:.1f}",
        "{{equip_w}}": f"{res.equipment_gain_w:.1f}",
        "{{equip_pct}}": f"{res.equipment_gain_w/gt*100:.1f}",
        "{{vent_total_w}}": f"{res.ventilation_sensible_w + res.ventilation_latent_w:.1f}",
        "{{vent_sensible_w}}": f"{res.ventilation_sensible_w:.1f}",
        "{{vent_latent_w}}": f"{res.ventilation_latent_w:.1f}",
        "{{vent_pct}}": f"{(res.ventilation_sensible_w + res.ventilation_latent_w)/gt*100:.1f}",
        "{{grand_total_w}}": f"{res.grand_total_heat_w:.1f}",
        "{{sensible_w}}": f"{res.total_sensible_heat_w:.1f}",
        "{{latent_w}}": f"{res.total_latent_heat_w:.1f}",
        "{{shr}}": f"{res.sensible_heat_ratio_shr:.2f}",
        "{{total_btu}}": f"{res.grand_total_cooling_btu_hr:.0f}",
        "{{req_tr}}": f"{res.required_cooling_tons_tr:.2f}",
        "{{selected_tr}}": f"{res.selected_unit_tons_tr:.1f}",
        "{{supply_cfm}}": f"{res.supply_airflow_cfm:.0f}",
        "{{diffusers_count}}": str(res.supply_diffusers_count),
        "{{cfm_per_diffuser}}": f"{res.cfm_per_diffuser:.0f}",
        "{{return_count}}": str(res.return_grilles_count),
        "{{elec_voltage}}": str(int(res.electrical_voltage_v)),
        "{{elec_mca}}": f"{res.electrical_mca_amps:.1f}",
        "{{elec_mop}}": str(res.electrical_mop_amps),
        "{{thermostat_aff}}": f"{res.thermostat_height_aff_m:.2f}",
        "{{isolator_aff}}": f"{res.isolator_height_aff_m:.2f}",
        "{{coordination_checklist}}": "\n".join(coord_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = space_input.space_name.lower().replace(" ", "_")
    md_path = out_dir / f"{clean_name}_cooling_load_note.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Workbook
    xlsx_path = out_dir / f"{clean_name}_hvac_schedule.xlsx"
    excel_exporter = HVACExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF Layout
    dxf_path = out_dir / f"{clean_name}_hvac_layout.dxf"
    dxf_exporter = HVACDXFExporter(res, room_length_m=space_input.length_m, room_width_m=space_input.width_m)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    inp = HVACSpaceInput(
        space_name="Corporate Meeting Room",
        length_m=8.0,
        width_m=6.0,
        height_m=3.0,
        space_type="office",
        occupant_count=8,
        lighting_power_watts=280.0,
        equipment_power_watts=800.0,
        external_wall_area_m2=18.0,
        glass_window_area_m2=6.0,
        roof_exposed=False,
    )
    files = generate_hvac_package(inp, code="SBC")
    print("HVAC Cooling Load & Air Distribution Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
