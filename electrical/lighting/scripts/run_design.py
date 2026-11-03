"""
Complete Multi-Deliverable Runner for Indoor Lighting Design.
Generates:
1. Photometric Calculation Note (.md)
2. AutoCAD Reflected Ceiling & Lighting Plan (.dxf)
3. Excel Luminaire Schedule & Coordinates (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from electrical.lighting.scripts.lumen_engine import LumenEngine, LightingFixture, LightingDesignResult
from electrical.lighting.exporters.excel_exporter import LightingExcelExporter
from electrical.lighting.exporters.dxf_exporter import LightingDXFExporter


def generate_lighting_package(
    room_name: str,
    length_m: float,
    width_m: float,
    space_type: str = "office_general",
    ceiling_height_m: float = 3.0,
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes lighting photometric design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "lighting")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("electrical/lighting", code=code)
    rules = context["rules"]
    active_code = context["active_code"]

    target_lux = rules.get("target_illuminance_lux", {}).get(space_type, 400.0)
    allowed_lpd_dict = rules.get("max_lpd_watts_per_m2", {}).get(active_code, {})
    allowed_lpd = allowed_lpd_dict.get(space_type.split("_")[0], 9.5)

    mf = rules.get("default_maintenance_factor", 0.80)
    cu = rules.get("default_cu", 0.65)
    voltage_v = rules.get("nominal_voltage_1phase_v", 230.0)

    # 2. Run Lumen Engine
    fixture = LightingFixture(
        model_name="600x600 LED Panel 36W",
        lumens_per_fixture=3600.0,
        power_watts=36.0,
    )

    res = LumenEngine.design_room_lighting(
        room_name=room_name,
        length_m=length_m,
        width_m=width_m,
        target_lux=target_lux,
        ceiling_height_m=ceiling_height_m,
        workplane_height_m=0.80,
        maintenance_factor=mf,
        coefficient_of_utilization=cu,
        fixture=fixture,
    )

    generated_files = {}

    # 3. Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    lpd_status = "PASS (Energy Compliant)" if res.lighting_power_density_w_per_m2 <= allowed_lpd else "EXCEEDED"
    illuminance_status = "PASS (Adequate Illuminance)" if res.achieved_lux >= target_lux * 0.95 else "INSUFFICIENT"

    # Circuit sizing
    c_rules = rules.get("circuits", {})
    mcb = c_rules.get("default_breaker_amps", 10)
    cable = c_rules.get("default_cable_size_sqmm", 1.5)
    # Voltage drop approx (Ib = P / V, distance approx L + W)
    ib = res.total_power_watts / (voltage_v * 0.90)
    dist = length_m + width_m + 10.0
    vd_v = 2.0 * ib * (14.8 * dist / 1000.0)
    vd_pct = round((vd_v / voltage_v) * 100.0, 2)

    replacements = {
        "{{code_used}}": str(active_code),
        "{{voltage_v}}": str(int(voltage_v)),
        "{{room_name}}": res.room_name,
        "{{space_type}}": space_type.replace("_", " ").title(),
        "{{room_length}}": f"{res.room_length_m:.2f}",
        "{{room_width}}": f"{res.room_width_m:.2f}",
        "{{room_area}}": f"{res.room_area_m2:.2f}",
        "{{ceiling_height}}": f"{ceiling_height_m:.2f}",
        "{{workplane_height}}": "0.80",
        "{{mf}}": f"{mf:.2f}",
        "{{cu}}": f"{cu:.2f}",
        "{{fixture_model}}": res.fixture_model,
        "{{fixture_lumens}}": f"{fixture.lumens_per_fixture:.0f}",
        "{{fixture_watts}}": f"{fixture.power_watts:.0f}",
        "{{target_lux}}": f"{target_lux:.0f}",
        "{{raw_fixtures}}": str(round((target_lux * res.room_area_m2) / (cu * mf * fixture.lumens_per_fixture), 2)),
        "{{grid_layout}}": f"{res.grid_columns} x {res.grid_rows}",
        "{{total_fixtures}}": str(res.total_fixtures_count),
        "{{achieved_lux}}": f"{res.achieved_lux:.1f}",
        "{{achieved_lpd}}": f"{res.lighting_power_density_w_per_m2:.2f}",
        "{{allowed_lpd}}": f"{allowed_lpd:.2f}",
        "{{lpd_status}}": lpd_status,
        "{{illuminance_status}}": illuminance_status,
        "{{circuit_tag}}": "CKT-L01",
        "{{total_circuit_watts}}": f"{res.total_power_watts:.0f}",
        "{{circuit_breaker}}": str(mcb),
        "{{circuit_cable}}": str(cable),
        "{{voltage_drop_pct}}": f"{vd_pct:.2f}",
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = room_name.lower().replace(" ", "_")
    md_path = out_dir / f"{clean_name}_lighting_calculation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Excel Schedule
    xlsx_path = out_dir / f"{clean_name}_lighting_schedule.xlsx"
    excel_exporter = LightingExcelExporter(res, code=active_code)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. AutoCAD DXF Layout
    dxf_path = out_dir / f"{clean_name}_lighting_layout.dxf"
    dxf_exporter = LightingDXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    files = generate_lighting_package(
        room_name="Engineering Open Office",
        length_m=10.0,
        width_m=6.0,
        space_type="office_general",
        ceiling_height_m=3.0,
        code="SBC",
    )
    print("Lighting Deliverables Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
