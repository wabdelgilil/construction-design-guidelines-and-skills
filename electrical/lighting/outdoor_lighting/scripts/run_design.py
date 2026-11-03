"""CLI runner script for Outdoor Roadway & Street Lighting Design."""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

import argparse
from jinja2 import Template
from electrical.lighting.outdoor_lighting.scripts.design_engine import OutdoorLightingDesignEngine
from electrical.lighting.outdoor_lighting.exporters.excel_exporter import OutdoorLightingExcelExporter
from electrical.lighting.outdoor_lighting.exporters.dxf_exporter import OutdoorLightingDXFExporter


def run_outdoor_lighting_design(
    project_name: str,
    output_dir: str,
    road_length_m: float = 600.0,
    road_width_m: float = 10.5,
    road_class: str = "M3",
    pole_arrangement: str = "single_sided",
    mounting_height_m: float = 10.0,
    luminaire_power_w: float = 150.0,
    luminaire_lumens: float = 21500.0,
    feeder_cable_csa_mm2: float = 16.0,
    code_standard: str = "SBC"
):
    os.makedirs(output_dir, exist_ok=True)
    engine = OutdoorLightingDesignEngine(code_standard=code_standard)

    result = engine.design_roadway_lighting(
        road_length_m=road_length_m,
        road_width_m=road_width_m,
        number_of_lanes=3,
        road_class=road_class,
        pole_arrangement=pole_arrangement,
        luminaire_power_w=luminaire_power_w,
        luminaire_lumens=luminaire_lumens,
        mounting_height_m=mounting_height_m,
        feeder_cable_length_m=road_length_m * 1.10,
        feeder_conductor_csa_mm2=feeder_cable_csa_mm2
    )
    result["project_name"] = project_name

    clean_name = project_name.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")

    # 1. Calculation Note (.md)
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "calc_sheet.md")
    with open(template_path, "r", encoding="utf-8") as f:
        template = Template(f.read())
    calc_note = template.render(result)
    calc_file = os.path.join(output_dir, f"{clean_name}_roadway_lighting_calc.md")
    with open(calc_file, "w", encoding="utf-8") as f:
        f.write(calc_note)

    # 2. Excel Schedule & BOQ (.xlsx)
    excel_exporter = OutdoorLightingExcelExporter()
    excel_file = os.path.join(output_dir, f"{clean_name}_roadway_lighting_boq.xlsx")
    excel_exporter.export(result, excel_file)

    # 3. AutoCAD Drawing (.dxf)
    dxf_exporter = OutdoorLightingDXFExporter()
    dxf_file = os.path.join(output_dir, f"{clean_name}_roadway_lighting_drawing.dxf")
    dxf_exporter.export(result, dxf_file)

    print(f"Roadway lighting design completed successfully for '{project_name}'!")
    print(f"Outputs written to: {output_dir}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Outdoor Roadway Lighting Design CLI")
    parser.add_argument("--project", default="King Abdullah Road Lighting Sector 4", help="Project name")
    parser.add_argument("--outdir", default="output/outdoor_lighting", help="Output directory")
    parser.add_argument("--length", type=float, default=600.0, help="Road length in meters")
    parser.add_argument("--width", type=float, default=10.5, help="Road width in meters")
    parser.add_argument("--roadclass", default="M3", choices=["M1", "M2", "M3", "M4", "M5"], help="CIE road class")
    parser.add_argument("--arrangement", default="single_sided", choices=["single_sided", "staggered", "opposite", "median_twin"])
    parser.add_argument("--height", type=float, default=10.0, help="Pole mounting height in meters")
    parser.add_argument("--csa", type=float, default=16.0, help="Cable conductor cross section mm2")

    args = parser.parse_args()
    run_outdoor_lighting_design(
        project_name=args.project,
        output_dir=args.outdir,
        road_length_m=args.length,
        road_width_m=args.width,
        road_class=args.roadclass,
        pole_arrangement=args.arrangement,
        mounting_height_m=args.height,
        feeder_cable_csa_mm2=args.csa
    )
