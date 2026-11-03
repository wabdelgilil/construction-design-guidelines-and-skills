"""
Excel Exporter for CCTV Camera Schedule, Bandwidth Sizing, and Storage Calculations.
"""

from pathlib import Path
from core.exporters.excel_writer import ExcelWriter
from electrical.cctv_security.scripts.design_engine import CCTVSecurityDesignResult


class CCTVSecurityExcelExporter:
    """Exports CCTV camera schedules and storage calculation workbooks to Excel."""

    def __init__(self, result: CCTVSecurityDesignResult):
        self.res = result
        self.writer = ExcelWriter("cctv_schedule.xlsx")

    def export(self, filepath: Path) -> Path:
        wb = self.writer.wb
        ws = wb.active
        ws.title = "Camera Schedule"

        self.writer.format_title_banner(
            title=f"IP CCTV CAMERA SCHEDULE & DORI OPTICS - {self.res.project_name.upper()}",
            subtitle=f"Code: {self.res.standard_used} | Cameras: {self.res.total_cameras_count} | Retention: {self.res.recording_days} Days ({self.res.gross_raid_storage_tb} TB in {self.res.raid_configuration})",
            max_col=9,
        )

        headers = [
            "Tag",
            "Location",
            "Camera Type",
            "Resolution",
            "Target DORI",
            "Target Dist (m)",
            "Lens (mm)",
            "HFOV (°)",
            "Bitrate (Mbps)",
        ]
        self.writer.add_table_header(4, headers)

        for idx, cam in enumerate(self.res.cameras, start=5):
            ws.cell(row=idx, column=1, value=cam.tag)
            ws.cell(row=idx, column=2, value=cam.location)
            ws.cell(row=idx, column=3, value=cam.camera_type)
            ws.cell(row=idx, column=4, value=cam.resolution)
            ws.cell(row=idx, column=5, value=cam.target_dori)
            ws.cell(row=idx, column=6, value=cam.target_distance_m)
            ws.cell(row=idx, column=7, value=f"{cam.selected_focal_length_mm} mm")
            ws.cell(row=idx, column=8, value=f"{cam.horizontal_fov_deg}°")
            ws.cell(row=idx, column=9, value=f"{cam.bitrate_mbps} Mbps")

        self.writer.auto_fit_columns()

        # Tab 2: Storage & Network PoE Sizing
        ws_stor = self.writer.create_sheet("Storage & PoE Sizing")
        self.writer.format_title_banner(
            title="NVR STORAGE & NETWORK POE SWITCH POWER BUDGET",
            subtitle=f"Gross Storage: {self.res.gross_raid_storage_tb} TB | HDDs: {self.res.required_hdd_count}x {self.res.selected_hdd_capacity_tb}TB | PoE Budget: {self.res.total_poe_power_budget_watts}W",
            max_col=5,
        )

        headers2 = ["Item", "System Parameter", "Calculated / Sized Value", "Unit", "Engineering Criteria"]
        self.writer.add_table_header(4, headers2)

        data2 = [
            [1, "Total IP Cameras", self.res.total_cameras_count, "Units", "System Total"],
            [2, "Network Video Bandwidth", f"{self.res.total_network_bandwidth_mbps} Mbps", "Mbps", "Incoming Throughput"],
            [3, "Archive Retention Duration", self.res.recording_days, "Days", "24/7 Continuous"],
            [4, "Net Raw Storage Required", f"{self.res.net_storage_tb} TB", "TB", "Without RAID overhead"],
            [5, "Gross Redundant Storage", f"{self.res.gross_raid_storage_tb} TB", "TB", f"Including {self.res.raid_configuration}"],
            [6, "Surveillance Enterprise Hard Drives", f"{self.res.required_hdd_count}x {self.res.selected_hdd_capacity_tb} TB SATA", "HDDs", "Enterprise 24/7 Rating"],
            [7, "Network Video Recorder (NVR)", f"{self.res.selected_nvr_channels}-Ch ({self.res.selected_nvr_sata_bays} Bays)", "-", "Rack-mounted 4K NVR"],
            [8, "PoE Switch Power Budget", f"{self.res.total_poe_power_budget_watts} W", "Watts", "Includes 25% safety margin"],
        ]

        for r_idx, row_vals in enumerate(data2, start=5):
            for c_idx, val in enumerate(row_vals, start=1):
                ws_stor.cell(row=r_idx, column=c_idx, value=val)

        self.writer.auto_fit_columns()

        return self.writer.save(filepath)
