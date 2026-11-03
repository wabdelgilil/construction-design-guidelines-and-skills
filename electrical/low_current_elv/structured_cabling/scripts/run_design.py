"""
Complete Multi-Deliverable Runner for Structured Cabling Infrastructure & Telecom Racks.
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. AutoCAD 42U Telecom Rack Elevation & Fiber Riser Plan (.dxf)
3. Excel Horizontal Port Schedule & Rack Utilization Workbook (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from electrical.low_current_elv.structured_cabling.scripts.design_engine import (
    StructuredCablingEngine,
    TelecomZoneInput,
    StructuredCablingDesignResult,
)
from electrical.low_current_elv.structured_cabling.exporters.excel_exporter import StructuredCablingExcelExporter
from electrical.low_current_elv.structured_cabling.exporters.dxf_exporter import StructuredCablingDXFExporter


def generate_structured_cabling_package(
    project_name: str,
    zones: List[TelecomZoneInput],
    spare_ports_margin: float = 0.20,
    ups_autonomy_min: float = 30.0,
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes Structured Cabling design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "structured_cabling")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("electrical/low_current_elv/structured_cabling", code=code)
    active_code = context["active_code"]
    standards = f"ANSI/TIA-568-D / ISO/IEC 11801 / {active_code} 401"

    # 2. Run Deterministic Structured Cabling Engine
    engine = StructuredCablingEngine(standard=standards)
    res = engine.design_system(
        project_name=project_name,
        zones=zones,
        spare_ports_margin=spare_ports_margin,
        ups_autonomy_min=ups_autonomy_min,
    )

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    # Build Zone table rows
    z_rows = []
    worst_dist = 0.0
    for z in res.zones:
        tot_z = (z.workstations_count * 2) + (z.wap_count * 2) + z.cctv_cameras_count + z.access_control_doors_count + (z.printers_av_count * 2)
        worst_dist = max(worst_dist, z.max_distance_to_idf_m)
        row = f"| {z.zone_name} | {z.workstations_count} ({z.workstations_count * 2} ports) | {z.wap_count} ({z.wap_count * 2} ports) | {z.cctv_cameras_count} | {z.access_control_doors_count} | {z.printers_av_count * 2} | {tot_z} | {z.max_distance_to_idf_m:.1f} m |"
        z_rows.append(row)
    zone_table = "\n".join(z_rows)

    # Build Rack table rows
    r_rows = []
    for item in res.rack_items:
        p_str = f"{item.power_watts:.0f} W" if item.power_watts > 0 else "Passive"
        row = f"| U{item.u_position:02d} | {item.u_height}U | {item.category} | {item.device_name} | {p_str} |"
        r_rows.append(row)
    rack_table = "\n".join(r_rows)

    coord_lines = [f"- 📶 {notice}" for notice in res.coordination_notices]

    replacements = {
        "{{project_name}}": res.project_name,
        "{{standard_used}}": res.standard_used,
        "{{zone_table_rows}}": zone_table,
        "{{worst_case_distance}}": f"{worst_dist:.1f}",
        "{{link_compliance_status}}": "PASS (Under 90.0m Permanent Link Limit)" if res.permanent_link_compliant else "FAIL (Exceeds 90.0m Link Limit)",
        "{{total_active_ports}}": str(res.grand_total_horizontal_ports),
        "{{spare_ports}}": str(res.spare_ports_equipped),
        "{{total_ports_needed}}": str(res.grand_total_horizontal_ports + res.spare_ports_equipped),
        "{{patch_panels_count}}": str(res.patch_panels_24p_count),
        "{{cable_managers_count}}": str(res.horizontal_cable_managers_count),
        "{{fiber_type}}": res.backbone_fiber_type,
        "{{fiber_cores}}": str(res.backbone_fiber_cores),
        "{{switches_count}}": str(res.switches_48p_count),
        "{{total_switch_power_w}}": f"{res.total_switch_poe_power_w:.0f}",
        "{{total_switch_power_kw}}": f"{res.total_switch_poe_power_w / 1000.0:.2f}",
        "{{heat_dissipation_btu}}": f"{res.total_switch_poe_power_w * 3.412:.0f}",
        "{{rack_table_rows}}": rack_table,
        "{{total_u_used}}": str(res.total_u_utilized),
        "{{spare_u}}": str(res.total_u_spare),
        "{{spare_u_percentage}}": f"{res.spare_u_percentage:.1f}",
        "{{calc_ups_va}}": f"{(res.total_switch_poe_power_w / 0.8) * 1.25:.0f}",
        "{{selected_ups_va}}": str(res.recommended_ups_va),
        "{{selected_ups_w}}": f"{res.recommended_ups_va * 0.9:.0f}",
        "{{ups_autonomy_min}}": f"{res.ups_autonomy_minutes:.0f}",
        "{{coordination_checklist}}": "\n".join(coord_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = project_name.lower().replace(" ", "_")
    md_path = out_dir / f"{clean_name}_structured_cabling_calculation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Workbook
    xlsx_path = out_dir / f"{clean_name}_structured_cabling_schedule.xlsx"
    excel_exporter = StructuredCablingExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF Drawing
    dxf_path = out_dir / f"{clean_name}_telecom_rack_elevation.dxf"
    dxf_exporter = StructuredCablingDXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    sample_zones = [
        TelecomZoneInput("Level 1 Open Office Area A", workstations_count=24, wap_count=3, cctv_cameras_count=6, access_control_doors_count=2, max_distance_to_idf_m=42.0),
        TelecomZoneInput("Level 1 Executive & Meeting Rooms", workstations_count=12, wap_count=2, cctv_cameras_count=4, access_control_doors_count=3, printers_av_count=4, max_distance_to_idf_m=58.0),
        TelecomZoneInput("Level 1 Service & Public Corridors", workstations_count=4, wap_count=2, cctv_cameras_count=8, access_control_doors_count=4, max_distance_to_idf_m=65.0),
    ]
    files = generate_structured_cabling_package("Commercial Tower Floor 1 Telecom", sample_zones)
    print("Structured Cabling Engineering Package successfully generated:")
    for k, p in files.items():
        print(f"  - {k}: {p}")
