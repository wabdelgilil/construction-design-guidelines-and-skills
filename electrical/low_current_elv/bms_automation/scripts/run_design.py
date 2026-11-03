"""
Complete Multi-Deliverable Runner for Building Management System (BMS) & DDC Automation Control.
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. AutoCAD BMS Three-Tier Architecture & AHU DDC Control Hookup Drawing (.dxf)
3. Excel MEP I/O Point Schedule, DDC Panel Sizing, and BOQ Workbook (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from electrical.low_current_elv.bms_automation.scripts.design_engine import (
    BMSDesignEngine,
    MEPEquipmentBMSInput,
    BMSDesignResult,
)
from electrical.low_current_elv.bms_automation.exporters.excel_exporter import BMSExcelExporter
from electrical.low_current_elv.bms_automation.exporters.dxf_exporter import BMSDXFExporter


def generate_bms_package(
    project_name: str,
    equipment_list: List[MEPEquipmentBMSInput],
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes BMS design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "bms_automation")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("electrical/low_current_elv/bms_automation", code=code)
    active_code = context["active_code"]
    standards = f"ASHRAE 135 (BACnet) / ISO 16484 / {active_code} 601"

    # 2. Run Deterministic BMS Engine
    engine = BMSDesignEngine(standard=standards)
    res = engine.generate_bms_design(
        project_name=project_name,
        equipment_list=equipment_list,
    )

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    # Build equipment table rows
    eq_rows = []
    for eq in res.equipment_points:
        row = f"| {eq.equipment_tag} | {eq.description} | {eq.location} | {eq.di_count} | {eq.do_count} | {eq.ai_count} | {eq.ao_count} | {eq.total_hardwired_points} | {eq.hli_integration_type} |"
        eq_rows.append(row)
    equip_table = "\n".join(eq_rows)

    # Build DDC panel table rows
    pnl_rows = []
    for p in res.ddc_panels:
        served = ", ".join(p.served_equipment)
        row = f"| {p.panel_tag} | {p.panel_location} | {served} | {p.active_points} | {p.spare_points} | {p.equipped_capacity_points} | {p.base_ddc_units_count} | {p.expansion_modules_count} | {p.enclosure_size_mm} | {p.psu_power_w:.0f} W |"
        pnl_rows.append(row)
    ddc_panel_table = "\n".join(pnl_rows)

    coord_lines = [f"- 🖥️ {notice}" for notice in res.coordination_notices]

    clean_name = project_name.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")

    replacements = {
        "{{project_name}}": res.project_name,
        "{{standard_used}}": res.standard_used,
        "{{primary_protocol}}": res.primary_protocol,
        "{{field_bus_protocol}}": res.field_bus_protocol,
        "{{total_di}}": str(res.total_active_di),
        "{{total_do}}": str(res.total_active_do),
        "{{total_ai}}": str(res.total_active_ai),
        "{{total_ao}}": str(res.total_active_ao),
        "{{grand_active}}": str(res.grand_total_active_points),
        "{{grand_spare}}": str(res.grand_total_spare_points),
        "{{grand_equipped}}": str(res.grand_total_equipped_points),
        "{{total_panels}}": str(res.total_ddc_panels_count),
        "{{total_hli}}": str(res.total_hli_gateways_count),
        "{{equipment_table_rows}}": equip_table,
        "{{ddc_panel_rows}}": ddc_panel_table,
        "{{total_ddc_w}}": f"{sum(p.psu_power_w for p in res.ddc_panels):.0f}",
        "{{selected_ups_va}}": str(res.recommended_ups_va),
        "{{selected_ups_w}}": str(int(res.recommended_ups_va * 0.9)),
        "{{coordination_checklist}}": "\n".join(coord_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    md_path = out_dir / f"{clean_name}_bms_calculation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Workbook
    xlsx_path = out_dir / f"{clean_name}_bms_schedule.xlsx"
    excel_exporter = BMSExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF Drawing
    dxf_path = out_dir / f"{clean_name}_bms_architecture.dxf"
    dxf_exporter = BMSDXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    sample_equipment = [
        MEPEquipmentBMSInput("AHU-ROOF-01", "ahu", "Roof Air Handling Unit 1", "Roof Plant Room", quantity=1, has_vfd=True),
        MEPEquipmentBMSInput("AHU-ROOF-02", "ahu", "Roof Air Handling Unit 2", "Roof Plant Room", quantity=1, has_vfd=True),
        MEPEquipmentBMSInput("CHILLER-01", "chiller", "Water-Cooled Centrifugal Chiller 1", "Basement Chiller Plant", quantity=1),
        MEPEquipmentBMSInput("CHILLER-02", "chiller", "Water-Cooled Centrifugal Chiller 2", "Basement Chiller Plant", quantity=1),
        MEPEquipmentBMSInput("CHWP-01", "pump", "Primary Chilled Water Pump 1", "Basement Chiller Plant", quantity=1, has_vfd=False),
        MEPEquipmentBMSInput("CHWP-02", "pump", "Primary Chilled Water Pump 2", "Basement Chiller Plant", quantity=1, has_vfd=False),
        MEPEquipmentBMSInput("SCHWP-01", "pump", "Secondary Chilled Water Pump 1 (VFD)", "Basement Chiller Plant", quantity=1, has_vfd=True),
        MEPEquipmentBMSInput("MDB-MAIN", "substation_mdb", "Main LV Switchboard MDB", "Substation Room", quantity=1),
        MEPEquipmentBMSInput("TANK-DOM-01", "water_tank", "Domestic Potable Water Break Tank", "Basement Tank Room", quantity=1),
    ]

    files = generate_bms_package("Commercial Tower Automation BMS", sample_equipment)
    print("BMS Engineering Package successfully generated:")
    for k, p in files.items():
        print(f"  - {k}: {p}")
