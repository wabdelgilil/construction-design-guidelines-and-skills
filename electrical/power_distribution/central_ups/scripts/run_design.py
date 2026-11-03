"""CLI runner script for Central UPS & DC Battery Plant Sizing."""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

import argparse
from jinja2 import Template
from electrical.power_distribution.central_ups.scripts.design_engine import CentralUPSDesignEngine
from electrical.power_distribution.central_ups.exporters.excel_exporter import CentralUPSExcelExporter
from electrical.power_distribution.central_ups.exporters.dxf_exporter import CentralUPSDXFExporter


def run_central_ups_design(
    project_name: str,
    output_dir: str,
    code_standard: str = "SBC",
    backup_time_min: float = 30.0,
    redundancy_type: str = "N+1"
):
    os.makedirs(output_dir, exist_ok=True)
    engine = CentralUPSDesignEngine(code_standard=code_standard)

    sample_loads = [
        {"id": "DC-SRV-01", "name": "Tier-III Data Center Blade Server Racks", "load_kw": 85.0, "pf": 0.92},
        {"id": "DC-SAN-01", "name": "Storage Area Network (SAN) & Core Routers", "load_kw": 30.0, "pf": 0.88},
        {"id": "SEC-SOC-01", "name": "Security Operations Center & CCTV Headend", "load_kw": 18.0, "pf": 0.85},
        {"id": "BMS-DDC-01", "name": "Building Management System Central Servers & DDC", "load_kw": 12.0, "pf": 0.80},
        {"id": "TEL-PBX-01", "name": "Telecom IP-PBX & Core Optical Line Terminals", "load_kw": 15.0, "pf": 0.85},
    ]

    result = engine.size_ups_system(
        loads=sample_loads,
        backup_time_min=backup_time_min,
        redundancy_type=redundancy_type,
        future_growth_margin=0.20,
        room_dimensions_m={"length": 7.0, "width": 4.5, "height": 3.4}
    )
    result["project_name"] = project_name

    clean_name = project_name.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")

    # 1. Calculation Note (.md)
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "calc_sheet.md")
    with open(template_path, "r", encoding="utf-8") as f:
        template = Template(f.read())
    calc_note = template.render(result)
    calc_file = os.path.join(output_dir, f"{clean_name}_ups_calculation.md")
    with open(calc_file, "w", encoding="utf-8") as f:
        f.write(calc_note)

    # 2. Excel Schedule & BOQ (.xlsx)
    excel_exporter = CentralUPSExcelExporter()
    excel_file = os.path.join(output_dir, f"{clean_name}_ups_schedule_boq.xlsx")
    excel_exporter.export(result, excel_file)

    # 3. AutoCAD Drawing (.dxf)
    dxf_exporter = CentralUPSDXFExporter()
    dxf_file = os.path.join(output_dir, f"{clean_name}_ups_drawing.dxf")
    dxf_exporter.export(result, dxf_file)

    print(f"Design completed successfully for '{project_name}'!")
    print(f"Outputs written to: {output_dir}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Central UPS & Battery Plant Sizing CLI")
    parser.add_argument("--project", default="Data Center Complex Central UPS", help="Project name")
    parser.add_argument("--outdir", default="output/central_ups", help="Output directory")
    parser.add_argument("--code", default="SBC", choices=["SBC", "NEC", "ECP"], help="Electrical standard")
    parser.add_argument("--backup", type=float, default=30.0, help="Backup autonomy duration in minutes")
    parser.add_argument("--redundancy", default="N+1", choices=["N", "N+1", "2N"], help="Redundancy configuration")

    args = parser.parse_args()
    run_central_ups_design(
        project_name=args.project,
        output_dir=args.outdir,
        code_standard=args.code,
        backup_time_min=args.backup,
        redundancy_type=args.redundancy
    )
