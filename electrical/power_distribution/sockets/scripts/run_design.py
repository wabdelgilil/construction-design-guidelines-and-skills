"""
Complete Multi-Deliverable Runner for Small Power Sockets Design.
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. Excel Distribution Board Schedule + BOQ (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from electrical.power_distribution.sockets.scripts.design_engine import (
    SocketGroupRequest,
    SocketCircuitEngine,
    SocketDesignResult,
)
from electrical.power_distribution.sockets.exporters.excel_exporter import SocketExcelExporter
from electrical.power_distribution.sockets.exporters.dxf_exporter import SocketDXFExporter


def generate_socket_package(
    requests: List[SocketGroupRequest],
    code: str = None,
    output_dir: Path = None,
) -> Dict[str, Path]:
    """Executes socket circuit design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "sockets")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("electrical/power_distribution/sockets", code=code)
    rules = context["rules"]
    active_code = context["active_code"]

    voltage_v = rules.get("nominal_voltage_1phase_v", 230.0)

    # 2. Deterministic calculation
    engine = SocketCircuitEngine(voltage_v=voltage_v, code=active_code)
    res = engine.design_sockets(requests)

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    # Build circuit table rows
    circuit_rows = []
    for ckt in res.circuits:
        row = f"| {ckt.circuit_tag} | {ckt.description} | {ckt.outlet_count} | {ckt.total_watts:.0f} W | {ckt.breaker_rating_amps} A | {ckt.cable_size_sqmm} mm$^2$ | {ckt.voltage_drop_pct:.2f}% | {ckt.status} |"
        circuit_rows.append(row)
    circuit_table = "\n".join(circuit_rows)

    # Build coordination notices
    notices_lines = [f"- ⚠️ {n}" for n in res.coordination_notices] if res.coordination_notices else ["- ✅ No pending cross-discipline interface actions."]
    notices_text = "\n".join(notices_lines)

    replacements = {
        "{{code_used}}": str(res.code_used),
        "{{voltage_v}}": str(int(voltage_v)),
        "{{std_breaker}}": str(engine.std_breaker),
        "{{std_cable}}": str(engine.std_cable),
        "{{max_outlets}}": str(engine.max_sockets),
        "{{total_circuits}}": str(res.total_circuits_count),
        "{{total_kw}}": f"{res.total_connected_watts/1000.0:.2f}",
        "{{total_kva}}": f"{res.total_connected_kva:.2f}",
        "{{circuit_table_rows}}": circuit_table,
        "{{coordination_notices_list}}": notices_text,
        "{{overall_status}}": res.overall_status,
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    md_path = out_dir / "small_power_calculation_note.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Calculation Workbook (Schedule + BOQ)
    xlsx_path = out_dir / "small_power_schedule_and_boq.xlsx"
    excel_exporter = SocketExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF Schematic & Schedule
    dxf_path = out_dir / "small_power_schematic.dxf"
    dxf_exporter = SocketDXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_schematic"] = dxf_path

    return generated_files


if __name__ == "__main__":
    reqs = [
        SocketGroupRequest("Master Bedroom", 6, ["room_ac_split"]),
        SocketGroupRequest("Living Room", 12, ["room_ac_split"]),
        SocketGroupRequest("Kitchen", 8, ["refrigerator", "microwave", "dishwasher"]),
        SocketGroupRequest("Bathroom", 2, ["water_heater"]),
    ]
    files = generate_socket_package(reqs, code="SBC")
    print("Small Power Sockets Deliverables Package Generated:")
    for k, v in files.items():
        print(f"  [{k}]: {v}")
