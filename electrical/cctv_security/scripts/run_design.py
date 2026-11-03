"""
Complete Multi-Deliverable Runner for CCTV Video Surveillance & NVR Storage Sizing.
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. AutoCAD CCTV Layout & DORI Coverage Cones (.dxf)
3. Excel Camera Schedule & NVR Storage Workbook (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from electrical.cctv_security.scripts.design_engine import (
    CCTVSecurityEngine,
    CameraRequirement,
    CCTVSecurityDesignResult,
)
from electrical.cctv_security.exporters.excel_exporter import CCTVSecurityExcelExporter
from electrical.cctv_security.exporters.dxf_exporter import CCTVSecurityDXFExporter


def generate_cctv_package(
    project_name: str,
    cameras: List[CameraRequirement],
    recording_days: int = 31,
    raid_type: str = "RAID_5",
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes CCTV surveillance design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "cctv")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("electrical/cctv_security", code=code)
    rules = context["rules"]
    standards = " / ".join(rules.get("applicable_standards", ["EN 62676-4", "NFPA 730"]))

    # 2. Run Deterministic CCTV Engine
    engine = CCTVSecurityEngine(standard=standards)
    res = engine.design_cctv_system(
        project_name=project_name,
        camera_requests=cameras,
        recording_days=recording_days,
        raid_type=raid_type,
    )

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    # Build camera table rows
    c_rows = []
    for cam in res.cameras:
        row = f"| {cam.tag} | {cam.location} | {cam.camera_type} | {cam.resolution} | {cam.target_dori} | {cam.target_distance_m:.1f} m | {cam.selected_focal_length_mm:.1f} mm | {cam.horizontal_fov_deg:.1f} deg | {cam.dori_identification_dist_m:.1f} m | {cam.bitrate_mbps:.1f} Mbps |"
        c_rows.append(row)
    camera_table = "\n".join(c_rows)

    coord_lines = [f"- 📹 {notice}" for notice in res.coordination_notices]

    replacements = {
        "{{standard_used}}": res.standard_used,
        "{{project_name}}": res.project_name,
        "{{recording_days}}": str(res.recording_days),
        "{{camera_table_rows}}": camera_table,
        "{{total_cameras}}": str(res.total_cameras_count),
        "{{total_bandwidth}}": f"{res.total_network_bandwidth_mbps:.1f}",
        "{{net_storage_tb}}": f"{res.net_storage_tb:.2f}",
        "{{gross_storage_tb}}": f"{res.gross_raid_storage_tb:.2f}",
        "{{raid_config}}": res.raid_configuration,
        "{{hdd_count}}": str(res.required_hdd_count),
        "{{hdd_capacity}}": str(res.selected_hdd_capacity_tb),
        "{{nvr_channels}}": str(res.selected_nvr_channels),
        "{{nvr_bays}}": str(res.selected_nvr_sata_bays),
        "{{poe_raw}}": f"{sum(c.poe_class_watts for c in res.cameras):.1f}",
        "{{poe_budget}}": f"{res.total_poe_power_budget_watts:.1f}",
        "{{coordination_checklist}}": "\n".join(coord_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = project_name.lower().replace(" ", "_")
    md_path = out_dir / f"{clean_name}_cctv_calculation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Workbook
    xlsx_path = out_dir / f"{clean_name}_cctv_schedule.xlsx"
    excel_exporter = CCTVSecurityExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF Layout
    dxf_path = out_dir / f"{clean_name}_cctv_layout.dxf"
    dxf_exporter = CCTVSecurityDXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    cams = [
        CameraRequirement("CAM-01", "Main Building Gate / Vehicle Entry", "outdoor_bullet", "4k_8mp", "identification", 15.0, True),
        CameraRequirement("CAM-02", "Reception & Visitors Registration", "fixed_dome", "4mp_1440p", "identification", 6.0, False),
        CameraRequirement("CAM-03", "Ground Floor Main Corridor", "fixed_dome", "2mp_1080p", "recognition", 12.0, False),
        CameraRequirement("CAM-04", "Outdoor Parking Lot & Yard", "ptz_dome", "4k_8mp", "observation", 35.0, True),
    ]

    files = generate_cctv_package(
        project_name="Regional Headquarters Security",
        cameras=cams,
        recording_days=31,
        raid_type="RAID_5",
        code="SBC",
    )
    print("CCTV Security Surveillance Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
