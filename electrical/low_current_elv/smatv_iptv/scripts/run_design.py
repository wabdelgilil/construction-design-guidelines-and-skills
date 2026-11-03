"""CLI runner script for SMATV & IPTV Distribution Design."""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

import argparse
from jinja2 import Template
from electrical.low_current_elv.smatv_iptv.scripts.design_engine import SMATVIPTVDesignEngine
from electrical.low_current_elv.smatv_iptv.exporters.excel_exporter import SMATVIPTVExcelExporter
from electrical.low_current_elv.smatv_iptv.exporters.dxf_exporter import SMATVIPTVDXFExporter


def run_smatv_iptv_design(
    project_name: str,
    output_dir: str,
    num_floors: int = 12,
    outlets_per_floor: int = 16,
    code_standard: str = "SBC"
):
    os.makedirs(output_dir, exist_ok=True)
    engine = SMATVIPTVDesignEngine(code_standard=code_standard)

    result = engine.size_smatv_system(
        num_floors=num_floors,
        outlets_per_floor=outlets_per_floor,
        avg_floor_height_m=3.6,
        avg_horizontal_rg6_run_m=35.0,
        iptv_enabled=True,
        iptv_hd_channels=80,
        iptv_4k_channels=20
    )
    result["project_name"] = project_name

    clean_name = project_name.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")

    # 1. Calculation Note (.md)
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "calc_sheet.md")
    with open(template_path, "r", encoding="utf-8") as f:
        template = Template(f.read())
    calc_note = template.render(result)
    calc_file = os.path.join(output_dir, f"{clean_name}_smatv_calculation.md")
    with open(calc_file, "w", encoding="utf-8") as f:
        f.write(calc_note)

    # 2. Excel Schedule & BOQ (.xlsx)
    excel_exporter = SMATVIPTVExcelExporter()
    excel_file = os.path.join(output_dir, f"{clean_name}_smatv_schedule_boq.xlsx")
    excel_exporter.export(result, excel_file)

    # 3. AutoCAD Drawing (.dxf)
    dxf_exporter = SMATVIPTVDXFExporter()
    dxf_file = os.path.join(output_dir, f"{clean_name}_smatv_drawing.dxf")
    dxf_exporter.export(result, dxf_file)

    print(f"SMATV & IPTV design completed successfully for '{project_name}'!")
    print(f"Outputs written to: {output_dir}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SMATV & IPTV Distribution Design CLI")
    parser.add_argument("--project", default="Luxury Residential Tower SMATV/IPTV", help="Project name")
    parser.add_argument("--outdir", default="output/smatv_iptv", help="Output directory")
    parser.add_argument("--floors", type=int, default=12, help="Number of building floors")
    parser.add_argument("--outlets", type=int, default=16, help="Outlets per floor")
    parser.add_argument("--code", default="SBC", choices=["SBC", "NEC", "ECP"], help="Standard code")

    args = parser.parse_args()
    run_smatv_iptv_design(
        project_name=args.project,
        output_dir=args.outdir,
        num_floors=args.floors,
        outlets_per_floor=args.outlets,
        code_standard=args.code
    )
