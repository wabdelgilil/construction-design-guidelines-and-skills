"""
Excel Exporter for Structured Cabling Port Schedules, 42U Rack Elevations, and BOQ.
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from electrical.low_current_elv.structured_cabling.scripts.design_engine import StructuredCablingDesignResult


class StructuredCablingExcelExporter:
    """Exports structured cabling schedules, 42U rack elevations, and BOQ workbooks to Excel."""

    def __init__(self, result: StructuredCablingDesignResult):
        self.res = result
        self.writer = ExcelWriter("Structured Cabling")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "Horizontal Ports Schedule"

        self.writer.format_title_banner(
            title=f"STRUCTURED CABLING HORIZONTAL PORTS & WAO SCHEDULE - {self.res.project_name.upper()}",
            subtitle=f"Code: {self.res.standard_used} | Active Ports: {self.res.grand_total_horizontal_ports} | Spare: {self.res.spare_ports_equipped} | Cable: Cat6A LSZH 500MHz",
            max_col=8,
        )

        headers = [
            "Telecom Zone / Area",
            "Workstation Ports (Data+VoIP)",
            "WAP Ports (WiFi 6/7)",
            "CCTV Ports (PoE)",
            "Access Control Ports",
            "Printers / AV Ports",
            "Total Active Ports",
            "Max Link Run (m)",
        ]
        self.writer.add_table_header(4, headers)

        for idx, z in enumerate(self.res.zones, start=5):
            tot_z = (z.workstations_count * 2) + (z.wap_count * 2) + z.cctv_cameras_count + z.access_control_doors_count + (z.printers_av_count * 2)
            ws.cell(row=idx, column=1, value=z.zone_name)
            ws.cell(row=idx, column=2, value=z.workstations_count * 2)
            ws.cell(row=idx, column=3, value=z.wap_count * 2)
            ws.cell(row=idx, column=4, value=z.cctv_cameras_count)
            ws.cell(row=idx, column=5, value=z.access_control_doors_count)
            ws.cell(row=idx, column=6, value=z.printers_av_count * 2)
            ws.cell(row=idx, column=7, value=tot_z)
            ws.cell(row=idx, column=8, value=f"{z.max_distance_to_idf_m:.1f} m")

        self.writer.auto_fit_columns()

        # Tab 2: 42U Rack Elevation Schedule
        ws_rack = self.writer.create_sheet("42U Rack Elevation")
        self.writer.format_title_banner(
            title="42U TELECOMMUNICATIONS EQUIPMENT RACK ELEVATION SCHEDULE",
            subtitle=f"Rack: 800x1000mm 42U | Used: {self.res.total_u_utilized}U | Spare: {self.res.total_u_spare}U ({self.res.spare_u_percentage}%) | UPS: {self.res.recommended_ups_va} VA",
            max_col=5,
        )

        rack_headers = ["U Position", "U Height", "Category", "Equipment Description", "Power Consumption (W)"]
        self.writer.add_table_header(4, rack_headers)

        for idx, item in enumerate(self.res.rack_items, start=5):
            ws_rack.cell(row=idx, column=1, value=f"U{item.u_position:02d}")
            ws_rack.cell(row=idx, column=2, value=f"{item.u_height}U")
            ws_rack.cell(row=idx, column=3, value=item.category)
            ws_rack.cell(row=idx, column=4, value=item.device_name)
            ws_rack.cell(row=idx, column=5, value=f"{item.power_watts:.0f} W" if item.power_watts > 0 else "Passive")

        self.writer.auto_fit_columns()

        # Tab 3: Itemized Bill of Quantities (BOQ)
        ws_boq = self.writer.create_sheet("Structured Cabling BOQ")
        self.writer.format_title_banner(
            title="STRUCTURED CABLING SYSTEM BILL OF QUANTITIES (BOQ)",
            subtitle=f"Project: {self.res.project_name} | Scope: Passive Infrastructure, Active Switches & UPS",
            max_col=5,
        )

        boq_headers = ["Item No.", "Equipment Description", "Specification / Rating", "Quantity", "Unit"]
        self.writer.add_table_header(4, boq_headers)

        total_cable_boxes = max(int((self.res.grand_total_horizontal_ports * 60) / 305.0) + 1, 1)

        boq_items = [
            ("1.01", "Standard 42U Floor-Standing Equipment Rack", "800mm W x 1000mm D, glass door, vertical cable channels", self.res.total_42u_racks_count, "Unit"),
            ("1.02", "1U 24-Port Modular Shielded Cat6A Patch Panel", "Class EA 500MHz, loaded with 24x RJ45 keystone jacks", self.res.patch_panels_24p_count, "Unit"),
            ("1.03", "1U Horizontal Double-Sided Cable Manager", "High capacity finger-duct with hinged front cover", self.res.horizontal_cable_managers_count, "Unit"),
            ("1.04", "1U Optical Fiber LIU Patch Drawer (12-Core)", "Sliding chassis with 6x LC duplex multimode adapters", self.res.fiber_liu_count, "Unit"),
            ("1.05", "48-Port Managed Gigabit/Multi-Gigabit PoE+ Switch", "Layer 2/3, 740W PoE budget, 4x 10G SFP+ uplinks", self.res.switches_48p_count, "Unit"),
            ("1.06", "Online Double-Conversion Rackmount UPS", f"{self.res.recommended_ups_va} VA / {int(self.res.recommended_ups_va * 0.9)} W, 30m runtime at full load", 1, "Unit"),
            ("1.07", "1U Metered Rack Power Distribution Unit (PDU)", "16A 230V AC, 8x IEC C13 outlets, circuit breaker", 2, "Unit"),
            ("1.08", "4-Pair Cat6A F/UTP Horizontal Cable (305m Reel)", "LSZH flame retardant, 500MHz bandwidth", total_cable_boxes, "Reels"),
            ("1.09", "12-Core OM4 Multi-Mode Tight-Buffered Fiber", "50/125um laser optimized, indoor/outdoor riser", 150, "Meters"),
            ("1.10", "Dual-Port RJ45 Cat6A Faceplate Outlets (WAO)", "Bevelled faceplate, shuttered, with labeling window", int(self.res.total_workstation_ports / 2), "Sets"),
            ("1.11", "Cat6A Factory Molded Patch Cords (1m / 2m / 3m)", "50u gold plated pins, LSZH jacket (Equipment + User)", self.res.grand_total_horizontal_ports * 2, "Nos"),
        ]

        for idx, (num, desc, spec, qty, unit) in enumerate(boq_items, start=5):
            ws_boq.cell(row=idx, column=1, value=num)
            ws_boq.cell(row=idx, column=2, value=desc)
            ws_boq.cell(row=idx, column=3, value=spec)
            ws_boq.cell(row=idx, column=4, value=qty)
            ws_boq.cell(row=idx, column=5, value=unit)

        self.writer.auto_fit_columns()
        self.writer.save(filepath)
        return filepath
