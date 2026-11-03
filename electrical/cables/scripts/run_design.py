"""
Complete Multi-Deliverable Runner for Low Voltage Cable Sizing & Cable Tray Sizing.
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. AutoCAD Cable Tray Section & Containment Layout (.dxf)
3. Excel Feeder Schedule & Tray Sizing Workbook (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from electrical.cables.scripts.cable_engine import (
    CableEngine,
    FeederRequest,
    CableSizingResult,
    CableTraySizingResult,
)
from electrical.cables.exporters.excel_exporter import CableExcelExporter
from electrical.cables.exporters.dxf_exporter import CableDXFExporter


def generate_cables_package(
    project_name: str,
    feeders: List[FeederRequest],
    tray_tag: str = "CT-MAIN-01",
    ambient_temp_c: int = 45,
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes multi-feeder cable sizing, tray sizing, and outputs all deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "cables")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("electrical/cables", code=code)
    rules = context["rules"]
    standards = " / ".join(rules.get("applicable_standards", ["IEC 60364-5-52", "SBC 401"]))

    ca = rules.get("ambient_temp_derating_xlpe_in_air", {}).get(str(ambient_temp_c), 0.96)
    num_feeders = len(feeders)
    cg_table = rules.get("grouping_derating_in_perforated_tray", {})
    cg = cg_table.get(str(min(num_feeders, 9)), 0.77)

    # 2. Run Cable Sizing for each Feeder
    sized_feeders = []
    cable_diameters = []

    for f in feeders:
        res = CableEngine.size_cable(
            load_kw=f.load_kw,
            phases=f.phases,
            system_voltage_v=400.0 if f.phases == 3 else 230.0,
            circuit_length_m=f.length_m,
            power_factor=f.power_factor,
            temp_derating_factor=ca,
            grouping_derating_factor=cg,
            is_branch_circuit=f.is_branch_circuit,
        )
        sized_feeders.append({
            "tag": f.tag,
            "description": f.description,
            "result": res,
        })
        cable_diameters.append(res.approx_outer_diameter_mm)

    # 3. Size Cable Tray
    tray_res = CableEngine.size_cable_tray(
        tray_tag=tray_tag,
        cable_diameters_mm=cable_diameters,
        standard_depth_mm=50,
        max_fill_ratio_pct=40.0,
    )

    generated_files = {}

    # 4. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    rows = []
    for item in sized_feeders:
        r = item["result"]
        row = f"| {item['tag']} | {item['description']} | {r.load_kw:.1f} | {r.design_current_ib:.1f} | {r.breaker_rating_in}A | {r.cable_size_sqmm:.0f} mm$^2$ Cu | {r.cable_ampacity_iz:.0f} | {r.circuit_length_m:.0f} | {r.voltage_drop_pct:.2f}% | {r.short_circuit_withstand_ka:.1f} kA | **{r.compliance_status}** |"
        rows.append(row)
    feeder_table = "\n".join(rows)

    coord_notices = [
        "Civil / Structural Interface: Provide wall and slab penetrations (openings) for cable tray CT-MAIN-01 with 100mm clearance on all sides.",
        "Fire Stopping Interface: Install 2-hour certified fire-stop pillows / intumescent sealant where cable tray penetrates fire compartment walls.",
        "Earthing Interface: Bond each 3.0m cable tray section with 16mm² copper grounding jumper and connect main tray to Substation Earth Busbar.",
        "Mechanical Interface: Maintain minimum 300mm clearance between cable tray and chilled water / steam pipes; cable tray must be installed above plumbing pipes.",
    ]
    coord_lines = [f"- ⚠️ {n}" for n in coord_notices]

    replacements = {
        "{{standards_used}}": standards,
        "{{system_voltage}}": "400/230",
        "{{project_name}}": project_name,
        "{{feeder_table_rows}}": feeder_table,
        "{{tray_tag}}": tray_res.tray_tag,
        "{{cables_count}}": str(tray_res.cables_count),
        "{{cables_area}}": f"{tray_res.total_cables_cross_section_mm2:.1f}",
        "{{min_tray_area}}": f"{tray_res.min_required_tray_area_mm2:.1f}",
        "{{tray_width}}": str(tray_res.selected_tray_width_mm),
        "{{tray_depth}}": str(tray_res.selected_tray_depth_mm),
        "{{actual_tray_area}}": f"{tray_res.actual_tray_area_mm2:.0f}",
        "{{achieved_fill}}": f"{tray_res.achieved_fill_ratio_pct:.1f}",
        "{{tray_status}}": tray_res.status,
        "{{ca_factor}}": f"{ca:.2f}",
        "{{cg_factor}}": f"{cg:.2f}",
        "{{c_total}}": f"{(ca * cg):.3f}",
        "{{coordination_checklist}}": "\n".join(coord_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = project_name.lower().replace(" ", "_")
    md_path = out_dir / f"{clean_name}_cable_calculation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 5. Generate Excel Schedule Workbook
    xlsx_path = out_dir / f"{clean_name}_cable_schedule.xlsx"
    excel_exporter = CableExcelExporter(project_name, sized_feeders, tray_res, standards)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 6. Generate AutoCAD DXF Cable Tray Detail
    dxf_path = out_dir / f"{clean_name}_cable_tray_layout.dxf"
    dxf_exporter = CableDXFExporter(project_name, sized_feeders, tray_res, standards)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    feeders_list = [
        FeederRequest("F-01", "Chiller Plant Main Feeder", 120.0, 45.0, 3, 0.85, False),
        FeederRequest("F-02", "Sub-Distribution Board SMDB-01", 65.0, 35.0, 3, 0.88, False),
        FeederRequest("F-03", "Elevators & Escalators Panel", 45.0, 50.0, 3, 0.82, False),
        FeederRequest("F-04", "Domestic & Booster Pumps Panel", 30.0, 25.0, 3, 0.85, False),
        FeederRequest("F-05", "Emergency Lighting & UPS Feeder", 20.0, 60.0, 3, 0.90, False),
    ]

    files = generate_cables_package(
        project_name="Central Commercial Complex",
        feeders=feeders_list,
        tray_tag="CT-MAIN-RISER",
        ambient_temp_c=45,
        code="SBC",
    )
    print("Cable Sizing & Containment Deliverables Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
