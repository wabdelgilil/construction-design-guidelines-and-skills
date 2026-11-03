"""
Excel Exporter for Architectural Space Planning Schedule & Compliance Audit.
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from architectural.space_planning.scripts.design_engine import ProjectSpaceAuditResult


class SpacePlanningExcelExporter:
    """Exports room matrix audit data to Excel."""

    def __init__(self, result: ProjectSpaceAuditResult):
        self.res = result
        self.writer = ExcelWriter("space_planning_schedule.xlsx")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "Space Schedule"

        self.writer.format_title_banner(
            title=f"ARCHITECTURAL SPACE AUDIT & ROOM MATRIX - {self.res.project_name.upper()}",
            subtitle=f"Code: {self.res.code_used} | Typology: {self.res.building_typology.upper()} | Gross Area: {self.res.total_gross_area_m2} m²",
            max_col=8,
        )

        headers = [
            "Tag",
            "Space Name",
            "Dimensions (L x W x H)",
            "Area (m²)",
            "Min Code Area (m²)",
            "Daylight Glazing",
            "Height (m)",
            "Compliance",
        ]
        self.writer.add_table_header(4, headers)

        for idx, rm in enumerate(self.res.rooms_audited, start=5):
            dim_str = f"{rm.length_m:.2f} x {rm.width_m:.2f} x {rm.height_m:.2f} m"
            glz_str = f"{rm.glazing_ratio*100:.1f}% ({'PASS' if rm.glazing_pass else 'LOW'})"
            ws.cell(row=idx, column=1, value=rm.tag)
            ws.cell(row=idx, column=2, value=rm.name)
            ws.cell(row=idx, column=3, value=dim_str)
            ws.cell(row=idx, column=4, value=rm.area_m2)
            ws.cell(row=idx, column=5, value=rm.min_area_required_m2)
            ws.cell(row=idx, column=6, value=glz_str)
            ws.cell(row=idx, column=7, value=rm.height_m)
            ws.cell(row=idx, column=8, value=rm.overall_status)

        self.writer.auto_fit_columns()

        # Tab 2: MEP Sizing Directives
        ws_mep = self.writer.create_sheet("MEP Sizing Directives")
        self.writer.format_title_banner(
            title="ARCHITECTURAL TO MEP DESIGN DIRECTIVES",
            subtitle="Preliminary HVAC, Electrical, and Plumbing Space Loading",
            max_col=4,
        )
        self.writer.add_table_header(4, ["Item", "Discipline", "Directive / Requirement", "Status"])
        for m_idx, directive in enumerate(self.res.mep_recommendations, start=5):
            disc = "Electrical" if "Electrical" in directive else ("HVAC" if "HVAC" in directive else "Plumbing")
            ws_mep.cell(row=m_idx, column=1, value=m_idx - 4)
            ws_mep.cell(row=m_idx, column=2, value=disc)
            ws_mep.cell(row=m_idx, column=3, value=directive)
            ws_mep.cell(row=m_idx, column=4, value="ACTIVE")

        self.writer.auto_fit_columns()

        return self.writer.save(filepath)
