"""
Excel Exporter for Small Power Socket Circuits.
Generates styled Distribution Board (DB) circuit schedule and itemized electrical BOQ.
"""

from pathlib import Path
import openpyxl
from core.exporters.excel_writer import ExcelWriter
from electrical.power_distribution.sockets.scripts.design_engine import SocketDesignResult


class SocketExcelExporter:
    """Creates a multi-tab Excel workbook for electrical branch circuits."""

    def __init__(self, result: SocketDesignResult):
        self.res = result

    def export(self, filepath: Path) -> Path:
        writer = ExcelWriter(title="Circuit Schedule")

        # =========================================================================
        # TAB 1: CIRCUIT SCHEDULE
        # =========================================================================
        ws1 = writer.ws
        writer.format_title_banner(
            "BRANCH CIRCUIT SCHEDULE (DISTRIBUTION BOARD)",
            f"Small Power & Dedicated Feeds | Active Code: {self.res.code_used}",
            max_col=8,
        )

        headers = [
            "Circuit Tag",
            "Description of Load",
            "Outlets",
            "Connected Watts (W)",
            "Connected VA",
            "Breaker (A)",
            "Cable Size (mm2)",
            "Voltage Drop (%)",
        ]
        writer.add_table_header(4, headers)

        for idx, ckt in enumerate(self.res.circuits, start=5):
            ws1.cell(row=idx, column=1, value=ckt.circuit_tag)
            ws1.cell(row=idx, column=2, value=ckt.description)
            ws1.cell(row=idx, column=3, value=ckt.outlet_count)
            ws1.cell(row=idx, column=4, value=ckt.total_watts)
            ws1.cell(row=idx, column=5, value=ckt.total_va)
            ws1.cell(row=idx, column=6, value=f"{ckt.breaker_rating_amps} A")
            ws1.cell(row=idx, column=7, value=f"{ckt.cable_size_sqmm} mm2")
            ws1.cell(row=idx, column=8, value=f"{ckt.voltage_drop_pct}%")

        sum_row = len(self.res.circuits) + 5
        ws1.cell(row=sum_row, column=2, value="TOTAL CONNECTED LOAD")
        ws1.cell(row=sum_row, column=2).font = openpyxl.styles.Font(bold=True)
        ws1.cell(row=sum_row, column=4, value=f"=SUM(D5:D{sum_row-1})")
        ws1.cell(row=sum_row, column=4).font = openpyxl.styles.Font(bold=True)
        ws1.cell(row=sum_row, column=5, value=f"=SUM(E5:E{sum_row-1})")
        ws1.cell(row=sum_row, column=5).font = openpyxl.styles.Font(bold=True)

        writer.auto_fit_columns()

        # =========================================================================
        # TAB 2: ELECTRICAL BOQ & COST ESTIMATION
        # =========================================================================
        ws2 = writer.create_sheet("Electrical BOQ")
        writer.format_title_banner(
            "ELECTRICAL BILL OF QUANTITIES (BOQ)",
            "Small Power Receptacles, Switches, and Cabling (Currency: SAR)",
            max_col=6,
        )

        boq_headers = ["Item No.", "Description of Electrical Works", "Unit", "Quantity", "Unit Rate (SAR)", "Total Amount (SAR)"]
        writer.add_table_header(4, boq_headers)

        total_sockets = sum(c.outlet_count for c in self.res.circuits if not c.is_dedicated)
        total_dedicated = sum(1 for c in self.res.circuits if c.is_dedicated)
        est_wire_m = len(self.res.circuits) * 35.0  # avg 35m per circuit
        est_conduit_m = est_wire_m * 0.9

        items = [
            (1, "13A Duplex Switched Socket Outlets (Type G - BS 1363)", "ea", total_sockets, 45.0),
            (2, "20A Double-Pole (DP) Isolator Switch with Neon Indicator", "ea", total_dedicated, 65.0),
            (3, "3x2.5 mm2 Cu/XLPE/PVC Building Wire in Conduits", "m", round(est_wire_m, 1), 5.5),
            (4, "3x4.0 mm2 Cu/XLPE/PVC Building Wire for Heavy Loads", "m", 70.0, 8.5),
            (5, "20mm Heavy Duty PVC Electrical Conduits & Accessories", "m", round(est_conduit_m, 1), 6.0),
            (6, "Miniature Circuit Breakers (MCB 16A / 20A 1P 10kA)", "ea", len(self.res.circuits), 35.0),
        ]

        for r_i, itm in enumerate(items, start=5):
            ws2.cell(row=r_i, column=1, value=itm[0])
            ws2.cell(row=r_i, column=2, value=itm[1])
            ws2.cell(row=r_i, column=3, value=itm[2])
            ws2.cell(row=r_i, column=4, value=itm[3])
            ws2.cell(row=r_i, column=5, value=itm[4])
            ws2.cell(row=r_i, column=6, value=f"=D{r_i}*E{r_i}")

        total_boq_row = len(items) + 5
        ws2.cell(row=total_boq_row, column=2, value="TOTAL ESTIMATED ELECTRICAL COST (SAR)")
        ws2.cell(row=total_boq_row, column=2).font = openpyxl.styles.Font(bold=True, size=11)
        ws2.cell(row=total_boq_row, column=6, value=f"=SUM(F5:F{total_boq_row-1})")
        ws2.cell(row=total_boq_row, column=6).font = openpyxl.styles.Font(bold=True, size=11, color="1F4E79")

        writer.auto_fit_columns()

        return writer.save(filepath)
