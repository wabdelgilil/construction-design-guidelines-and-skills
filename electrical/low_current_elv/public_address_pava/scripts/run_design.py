"""
Complete Multi-Deliverable Runner for Public Address & Voice Alarm (PA/VA) System.
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. AutoCAD Zone A/B Ceiling Layout & 19" Rack Elevation Drawing (.dxf)
3. Excel Acoustic Schedule, Amplifier Sizing, and BOQ Workbook (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from electrical.low_current_elv.public_address_pava.scripts.design_engine import (
    PAVADesignEngine,
    PAVAZoneInput,
    PAVADesignResult,
)
from electrical.low_current_elv.public_address_pava.exporters.excel_exporter import PAVAExcelExporter
from electrical.low_current_elv.public_address_pava.exporters.dxf_exporter import PAVADXFExporter


def generate_pava_package(
    project_name: str,
    zones: List[PAVAZoneInput],
    line_voltage_v: float = 100.0,
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes PA/VA design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "public_address_pava")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("electrical/low_current_elv/public_address_pava", code=code)
    active_code = context["active_code"]
    standards = f"BS 5839-8 / EN 54-16 / EN 54-24 / {active_code} 801"

    # 2. Run Deterministic PA/VA Engine
    engine = PAVADesignEngine(standard=standards)
    res = engine.design_system(
        project_name=project_name,
        zones=zones,
        line_voltage_v=line_voltage_v,
    )

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    # Build zone table rows
    z_rows = []
    for z in res.zones:
        row = f"| {z.zone_name} | {z.zone_category} | {z.area_m2:.1f} | {z.ambient_noise_dba:.0f} | {z.target_spl_dba:.0f} | {z.speaker_type} | {z.tapping_watts:.1f} | {z.speakers_count} | {z.circuit_a_count} | {z.circuit_b_count} | {z.calculated_spl_at_ear_dba:.1f} | {z.snr_achieved_dba:.1f} | {z.sti_estimate:.2f} | {z.zone_nominal_load_w:.1f} W |"
        z_rows.append(row)
    zone_table = "\n".join(z_rows)

    coord_lines = [f"- 📢 {notice}" for notice in res.coordination_notices]

    replacements = {
        "{{project_name}}": res.project_name,
        "{{standard_used}}": res.standard_used,
        "{{total_zones}}": str(res.total_zones_count),
        "{{total_speakers}}": str(res.total_speakers_count),
        "{{total_spk_a}}": str(res.total_circuit_a_speakers),
        "{{total_spk_b}}": str(res.total_circuit_b_speakers),
        "{{total_audio_w}}": f"{res.grand_total_audio_load_w:.1f}",
        "{{total_amp_w}}": str(res.grand_total_amplifier_capacity_w),
        "{{main_amps}}": str(res.main_amplifiers_count),
        "{{standby_amps}}": str(res.standby_amplifiers_count),
        "{{amp_rating}}": str(res.amplifier_rating_per_unit_w),
        "{{calc_amp_demand_w}}": f"{res.grand_total_audio_load_w * 1.20:.1f}",
        "{{i_quiescent}}": f"{res.quiescent_current_dc_a:.2f}",
        "{{i_alarm}}": f"{res.alarm_current_dc_a:.2f}",
        "{{calc_battery_ah}}": f"{res.calculated_battery_ah:.2f}",
        "{{selected_battery_ah}}": f"{res.selected_battery_ah:.1f}",
        "{{zone_table_rows}}": zone_table,
        "{{coordination_checklist}}": "\n".join(coord_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = project_name.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")
    md_path = out_dir / f"{clean_name}_pava_calculation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Workbook
    xlsx_path = out_dir / f"{clean_name}_pava_schedule.xlsx"
    excel_exporter = PAVAExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF Drawing
    dxf_path = out_dir / f"{clean_name}_pava_layout.dxf"
    dxf_exporter = PAVADXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    sample_zones = [
        PAVAZoneInput("Main Entrance Grand Lobby", "lobby", length_m=25.0, width_m=16.0, ceiling_height_m=4.5, speaker_type="ceiling", is_emergency_egress=True),
        PAVAZoneInput("Level 1 Primary Evacuation Corridor", "corridor", length_m=40.0, width_m=2.4, ceiling_height_m=3.0, speaker_type="ceiling", is_emergency_egress=True),
        PAVAZoneInput("Level 1 Open Office Area", "office", length_m=30.0, width_m=20.0, ceiling_height_m=3.2, speaker_type="ceiling", is_emergency_egress=False),
        PAVAZoneInput("Fire Exit Stairwell East", "stairwell", length_m=15.0, width_m=3.0, ceiling_height_m=3.0, speaker_type="wall_projector", is_emergency_egress=True),
        PAVAZoneInput("Basement Central Plant & Chiller Room", "plant_room", length_m=30.0, width_m=18.0, ceiling_height_m=4.2, speaker_type="weatherproof_horn", is_emergency_egress=True),
    ]

    files = generate_pava_package("Commercial Tower Complex PA/VA", sample_zones)
    print("PA/VA Engineering Package successfully generated:")
    for k, p in files.items():
        print(f"  - {k}: {p}")
