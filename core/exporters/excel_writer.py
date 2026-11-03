"""
Excel Spreadsheet Exporter Core Utility using openpyxl.
Provides corporate-styled workbooks, calculation tables, and formula formatting.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


class ExcelWriter:
    """Creates styled Excel calculation sheets and BOQs."""

    # Corporate Styling Theme: Deep Navy & Gold
    COLOR_HEADER_BG = "1F4E79"       # Deep Navy Blue
    COLOR_HEADER_TEXT = "FFFFFF"     # White
    COLOR_SUBHEADER_BG = "D9E1F2"    # Soft Ice Blue
    COLOR_SAFE_BG = "E2EFDA"         # Soft Sage Green
    COLOR_SAFE_TEXT = "375623"       # Dark Forest Green
    COLOR_WARN_BG = "FCE4D6"         # Soft Peach Red
    COLOR_WARN_TEXT = "C65911"       # Dark Amber Red

    def __init__(self, title: str = "Structural Calculation"):
        self.wb = openpyxl.Workbook()
        self.ws = self.wb.active
        self.ws.title = title

    def create_sheet(self, title: str):
        """Creates and activates a new worksheet."""
        self.ws = self.wb.create_sheet(title=title)
        return self.ws

    def format_title_banner(self, title: str, subtitle: str, max_col: int = 6):
        """Adds a top corporate title banner."""
        self.ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max_col)
        cell = self.ws.cell(row=1, column=1, value=title)
        cell.font = Font(name="Calibri", size=14, bold=True, color=self.COLOR_HEADER_TEXT)
        cell.fill = PatternFill(start_color=self.COLOR_HEADER_BG, end_color=self.COLOR_HEADER_BG, fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        self.ws.row_dimensions[1].height = 28

        self.ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=max_col)
        sub_cell = self.ws.cell(row=2, column=1, value=subtitle)
        sub_cell.font = Font(name="Calibri", size=10, italic=True, color="595959")
        sub_cell.alignment = Alignment(horizontal="center", vertical="center")
        self.ws.row_dimensions[2].height = 18

    def add_table_header(self, row: int, headers: List[str]):
        """Adds a table header row with corporate styling."""
        thin_border = Side(style="thin", color="D9D9D9")
        border = Border(left=thin_border, right=thin_border, top=thin_border, bottom=thin_border)

        for col_idx, header in enumerate(headers, start=1):
            cell = self.ws.cell(row=row, column=col_idx, value=header)
            cell.font = Font(name="Calibri", size=11, bold=True, color=self.COLOR_HEADER_TEXT)
            cell.fill = PatternFill(start_color=self.COLOR_HEADER_BG, end_color=self.COLOR_HEADER_BG, fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = border
        self.ws.row_dimensions[row].height = 24

    def auto_fit_columns(self, min_width: int = 12, max_width: int = 40):
        """Adjusts column widths based on cell content length."""
        for col in self.ws.columns:
            col_letter = get_column_letter(col[0].column)
            max_len = 0
            for cell in col:
                val = str(cell.value or "")
                if "\n" in val:
                    val = max(val.split("\n"), key=len)
                max_len = max(max_len, len(val))
            adjusted = max(min(max_len + 3, max_width), min_width)
            self.ws.column_dimensions[col_letter].width = adjusted

    def save(self, filepath: Path) -> Path:
        """Saves workbook to disk."""
        target = Path(filepath).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        self.wb.save(str(target))
        return target
