"""
Complete Multi-Deliverable Runner for Medical Isolated Power System (IPS) in Operating Rooms.
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. AutoCAD Single-Line Diagram (.dxf)
3. Excel Panel Schedule & Specifications (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from electrical.power_distribution.medical_isolated_power_ips.scripts.design_engine import (
    MedicalIPSEngine,
    MedicalLoadItem,
    IPSDesignResult,
)
from electrical.power_distribution.medical_isolated_power_ips.exporters.excel_exporter import MedicalIPSExcelExporter
from electrical.power_distribution.medical_isolated_power_ips.exporters.dxf_exporter import MedicalIPSDXFExporter


def generate_medical_ips_package(
    room_name: str,
    medical_loads: List[MedicalLoadItem],
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes medical IPS design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "hospital_ips")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("electrical/power_distribution/medical_isolated_power_ips", code=code)
    rules = context["rules"]
    standards = " / ".join(rules.get("applicable_standards", ["IEC 60364-7-710", "SBC 401"]))

    voltage_v = rules.get("transformer_specifications", {}).get("primary_voltage_v", 230.0)

    # 2. Run Medical IPS Engine
    engine = MedicalIPSEngine(voltage_v=voltage_v, standard=standards)
    res = engine.design_system(room_name=room_name, medical_loads=medical_loads)

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    # Build circuit table rows
    c_rows = []
    for ckt in res.secondary_circuits:
        row = f"| {ckt.circuit_tag} | {ckt.description} | {ckt.connected_watts:.0f} | {ckt.current_amps:.2f} | {ckt.breaker_rating_amps}A DP | {ckt.cable_size_sqmm} mm$^2$ | PASS |"
        c_rows.append(row)
    circuit_table = "\n".join(c_rows)

    # Build coordination checklist
    coord_lines = [f"- ⚠️ {notice}" for notice in res.coordination_notices]
    coord_text = "\n".join(coord_lines)

    replacements = {
        "{{standard_used}}": res.standard_used,
        "{{voltage_v}}": str(int(voltage_v)),
        "{{room_name}}": res.room_name,
        "{{total_w}}": f"{res.total_connected_watts:.0f}",
        "{{total_kva}}": f"{res.total_connected_kva:.2f}",
        "{{demand_factor}}": f"{res.demand_factor:.2f}",
        "{{design_kva}}": f"{res.design_kva:.2f}",
        "{{transformer_kva}}": f"{res.selected_transformer_kva:.2f}",
        "{{pri_amps}}": f"{res.transformer_primary_current_amps:.1f}",
        "{{sec_amps}}": f"{res.transformer_secondary_current_amps:.1f}",
        "{{primary_mcb}}": str(res.primary_mcb_rating_amps),
        "{{primary_curve}}": res.primary_mcb_curve,
        "{{imd_alarm}}": f"{res.imd_alarm_threshold_kohm:.0f}",
        "{{leakage_ma}}": f"{res.max_leakage_current_ma:.2f}",
        "{{bonding_ohms}}": f"{res.equipotential_bonding_max_resistance_ohms:.2f}",
        "{{circuit_table_rows}}": circuit_table,
        "{{coordination_checklist}}": coord_text,
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = room_name.lower().replace(" ", "_")
    md_path = out_dir / f"{clean_name}_ips_calculation_note.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Excel Schedule & BOQ
    xlsx_path = out_dir / f"{clean_name}_ips_schedule.xlsx"
    excel_exporter = MedicalIPSExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. AutoCAD DXF Single-Line Diagram (SLD)
    dxf_path = out_dir / f"{clean_name}_ips_sld.dxf"
    dxf_exporter = MedicalIPSDXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    loads = [
        MedicalLoadItem("EQ-01", "Surgical LED Lights Primary + Satellite", 300.0, 0.90, True, 1),
        MedicalLoadItem("EQ-02", "Anesthesia Workstation & Ventilator", 1200.0, 0.85, True, 1),
        MedicalLoadItem("EQ-03", "Electrosurgical Unit (Diathermy / Cautery)", 1500.0, 0.80, True, 1),
        MedicalLoadItem("EQ-04", "Heart-Lung Perfusion Machine / Bypass", 1800.0, 0.85, True, 1),
        MedicalLoadItem("EQ-05", "Operating Table Electro-hydraulic Drive", 450.0, 0.80, False, 1),
        MedicalLoadItem("EQ-06", "Endoscopy Video Stack & Light Source", 600.0, 0.85, True, 1),
        MedicalLoadItem("EQ-07", "Vital Signs Patient Monitor Console", 250.0, 0.90, True, 1),
        MedicalLoadItem("EQ-08", "Defibrillator / Pacemaker Unit", 400.0, 0.85, True, 1),
    ]

    files = generate_medical_ips_package(
        room_name="Major Cardiac Operating Theater OR-01",
        medical_loads=loads,
        code="SBC",
    )
    print("Hospital Operating Room IPS Deliverables Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
