"""
Complete Multi-Deliverable Runner for Short-Circuit Calculation & Protection Discrimination (TCC Curves).
Generates:
1. Markdown Engineering Calculation Sheet (.md)
2. AutoCAD Single-Line Diagram & Log-Log TCC Discrimination Curve Drawing (.dxf)
3. Excel Network Impedance, Breaker LSIG Schedule, and Selectivity Matrix (.xlsx)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.resolver import resolver
from electrical.power_distribution.protection_coordination.scripts.design_engine import (
    ProtectionCoordinationEngine,
    TransformerInput,
    FeederCableInput,
    ProtectionCoordinationDesignResult,
)
from electrical.power_distribution.protection_coordination.exporters.excel_exporter import ProtectionCoordinationExcelExporter
from electrical.power_distribution.protection_coordination.exporters.dxf_exporter import ProtectionCoordinationDXFExporter


def generate_protection_coordination_package(
    project_name: str,
    transformer: TransformerInput,
    smdb_feeder: FeederCableInput,
    db_feeder: FeederCableInput,
    grid_sc_mva: float = 500.0,
    code: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """Executes Protection Coordination design and outputs all project deliverables."""
    out_dir = Path(output_dir or (root_dir / "output" / "protection_coordination")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Resolve context along the tree
    context = resolver.resolve_context("electrical/power_distribution/protection_coordination", code=code)
    active_code = context["active_code"]
    standards = f"IEC 60909 / IEC 60947-2 / IEEE 242 / {active_code} 401"

    # 2. Run Deterministic Protection Coordination Engine
    engine = ProtectionCoordinationEngine(standard=standards)
    res = engine.calculate_coordination(
        project_name=project_name,
        transformer=transformer,
        smdb_feeder=smdb_feeder,
        db_feeder=db_feeder,
        grid_sc_mva=grid_sc_mva,
    )

    generated_files = {}

    # 3. Generate Markdown Calculation Note
    template_path = Path(__file__).resolve().parent.parent / "templates" / "calc_sheet.md"
    with open(template_path, "r", encoding="utf-8") as f:
        calc_note = f.read()

    # Build bus table rows
    b_rows = []
    for b in res.bus_faults:
        row = f"| {b.bus_name} | {b.hierarchy_level} | {b.r_mohm:.3f} | {b.x_mohm:.3f} | {b.z_mohm:.3f} | {b.isc_sym_ka:.2f} kA | {b.selected_breaker_type} | {b.rated_current_in_a} A | {b.rated_breaking_capacity_icu_ka:.0f} kA | +{b.safety_margin_percent:.1f}% |"
        b_rows.append(row)
    bus_table = "\n".join(b_rows)

    # Build selectivity table rows
    s_rows = []
    for s in res.selectivity_pairs:
        row = f"| {s.upstream_device} | {s.downstream_device} | {s.upstream_isd_a:.0f} A | {s.upstream_tsd_s:.2f} s | {s.downstream_clear_time_s:.2f} s | {s.time_margin_ms:.0f} ms | {s.current_ratio:.2f}x | **{s.selectivity_status}** |"
        s_rows.append(row)
    selectivity_table = "\n".join(s_rows)

    coord_lines = [f"- ⚡ {notice}" for notice in res.coordination_notices]

    mdb_bus = res.bus_faults[0]
    smdb_bus = res.bus_faults[1]

    replacements = {
        "{{project_name}}": res.project_name,
        "{{standard_used}}": res.standard_used,
        "{{transformer_rating_kva}}": f"{res.transformer.rating_kva:.0f}",
        "{{voltage_secondary}}": f"{res.transformer.voltage_secondary_v:.0f}",
        "{{uk_percent}}": f"{res.transformer.uk_percent:.1f}",
        "{{overall_system_discrimination}}": res.overall_system_discrimination,
        "{{bus_table_rows}}": bus_table,
        "{{acb_icu}}": f"{mdb_bus.rated_breaking_capacity_icu_ka:.0f}",
        "{{acb_icw}}": f"{mdb_bus.rated_withstand_icw_ka:.0f}",
        "{{acb_in}}": str(mdb_bus.rated_current_in_a),
        "{{acb_isd}}": f"{mdb_bus.rated_current_in_a * 4.0:.0f}",
        "{{acb_ig}}": f"{mdb_bus.rated_current_in_a * 0.4:.0f}",
        "{{mccb_icu}}": f"{smdb_bus.rated_breaking_capacity_icu_ka:.0f}",
        "{{mccb_ir}}": f"{smdb_bus.rated_current_in_a * 0.9:.0f}",
        "{{mccb_isd}}": f"{smdb_bus.rated_current_in_a * 0.9 * 3.0:.0f}",
        "{{mccb_ii}}": f"{smdb_bus.rated_current_in_a * 10.0:.0f}",
        "{{selectivity_table_rows}}": selectivity_table,
        "{{coordination_checklist}}": "\n".join(coord_lines),
    }

    for placeholder, val in replacements.items():
        calc_note = calc_note.replace(placeholder, val)

    clean_name = project_name.lower().replace(" ", "_")
    md_path = out_dir / f"{clean_name}_protection_coordination_calculation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(calc_note)
    generated_files["calc_note_md"] = md_path

    # 4. Generate Excel Workbook
    xlsx_path = out_dir / f"{clean_name}_protection_coordination_schedule.xlsx"
    excel_exporter = ProtectionCoordinationExcelExporter(res)
    excel_exporter.export(xlsx_path)
    generated_files["excel_workbook"] = xlsx_path

    # 5. Generate AutoCAD DXF Drawing
    dxf_path = out_dir / f"{clean_name}_protection_coordination_tcc.dxf"
    dxf_exporter = ProtectionCoordinationDXFExporter(res)
    dxf_exporter.export(dxf_path)
    generated_files["dxf_drawing"] = dxf_path

    return generated_files


if __name__ == "__main__":
    tr = TransformerInput(rating_kva=1500.0, voltage_primary_v=13800.0, voltage_secondary_v=400.0, uk_percent=6.0, cu_loss_kw=16.0)
    smdb_feed = FeederCableInput("MDB to SMDB-01", "MDB", "SMDB-01", length_m=45.0, csa_mm2=300.0, runs_per_phase=3)
    db_feed = FeederCableInput("SMDB-01 to DB-Lighting", "SMDB-01", "DB-Lighting", length_m=35.0, csa_mm2=16.0, runs_per_phase=1)

    files = generate_protection_coordination_package("Commercial Tower Substation & Distribution", tr, smdb_feed, db_feed)
    print("Protection Coordination Engineering Package successfully generated:")
    for k, p in files.items():
        print(f"  - {k}: {p}")
