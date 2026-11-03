"""
AutoCAD DXF Exporter for CCTV Surveillance Layout and DORI Coverage Cones.
Generates scaled camera symbols, directional fields of view (FOV), and security equipment schedules.
"""

from pathlib import Path
import math
from ezdxf.enums import TextEntityAlignment
from core.exporters.dxf_writer import DXFWriter
from electrical.cctv_security.scripts.design_engine import CCTVSecurityDesignResult


class CCTVSecurityDXFExporter:
    """Exports CCTV camera layout and FOV coverage cones to AutoCAD .dxf format."""

    def __init__(self, result: CCTVSecurityDesignResult):
        self.res = result
        self.writer = DXFWriter("cctv_layout.dxf")

    def export(self, filepath: Path) -> Path:
        plan_w = 14000.0
        plan_h = 10000.0
        margin = 1000.0

        # Sheet Border
        self.writer.add_rectangle(-margin, -margin, plan_w + 2 * margin + 2500, plan_h + 2 * margin, layer="S-TITLEBLOCK")

        # Title Block
        self.writer.add_text("CCTV VIDEO SURVEILLANCE & DORI COVERAGE PLAN", (0, plan_h + 650), height=180, layer="E-TEXT")
        self.writer.add_text(
            f"Standards: {self.res.standard_used} | Total Cameras: {self.res.total_cameras_count} | Retention: {self.res.recording_days} Days ({self.res.gross_raid_storage_tb} TB in {self.res.raid_configuration})",
            (0, plan_h + 350),
            height=110,
            layer="E-TEXT",
        )

        # 1. Outer Building Walls
        self.writer.add_rectangle(0, 0, plan_w, plan_h, layer="S-COLUMN")

        # 2. Security Control Room & NVR Rack
        sec_x, sec_y = 400.0, 500.0
        self.writer.add_rectangle(sec_x, sec_y, 600.0, 600.0, layer="E-POWR-PANL")
        self.writer.add_text("CCTV RACK / NVR", (sec_x + 300, sec_y + 300), height=65, layer="E-TEXT", align=TextEntityAlignment.MIDDLE_CENTER)

        # 3. Draw Camera Locations and DORI Coverage Cones
        # Define 4 perimeter / entrance positions
        cam_positions = [
            (200.0, plan_h - 200.0, 45.0),      # Top-Left corner, aiming 45 deg down-right
            (plan_w - 200.0, plan_h - 200.0, 135.0), # Top-Right, aiming down-left
            (plan_w / 2.0, 200.0, 0.0),          # Main Entrance center, aiming outward
            (200.0, 200.0, -45.0),               # Bottom-Left, aiming up-right
        ]

        for idx, cam in enumerate(self.res.cameras[:4]):
            px, py, angle_deg = cam_positions[idx % len(cam_positions)]

            # Camera Base Symbol (Circle with arrow)
            self.writer.msp.add_circle((px, py), radius=100, dxfattribs={"layer": "E-POWR-SCKT"})
            self.writer.add_text(cam.tag, (px, py + 250), height=70, layer="E-TEXT", align=TextEntityAlignment.BOTTOM_CENTER)

            # Draw DORI Coverage Cone
            reach_m = cam.target_distance_m
            cone_length = reach_m * 1000.0 * 0.4  # Scaled for clear drawing visibility
            half_fov_rad = math.radians(cam.horizontal_fov_deg / 2.0)
            center_angle_rad = math.radians(angle_deg)

            left_angle = center_angle_rad - half_fov_rad
            right_angle = center_angle_rad + half_fov_rad

            p_left = (px + cone_length * math.cos(left_angle), py + cone_length * math.sin(left_angle))
            p_right = (px + cone_length * math.cos(right_angle), py + cone_length * math.sin(right_angle))

            # Draw cone boundary lines
            self.writer.add_line((px, py), p_left, layer="E-POWR-CIRC")
            self.writer.add_line((px, py), p_right, layer="E-POWR-CIRC")
            self.writer.add_line(p_left, p_right, layer="E-POWR-CIRC")

            # Label on cone
            cone_mid = (px + (cone_length * 0.7) * math.cos(center_angle_rad), py + (cone_length * 0.7) * math.sin(center_angle_rad))
            self.writer.add_text(
                f"{cam.target_dori} ({cam.selected_focal_length_mm}mm)",
                cone_mid,
                height=55,
                layer="S-TEXT",
                align=TextEntityAlignment.MIDDLE_CENTER,
            )

        # 4. Security System Legend & Summary Box
        leg_x = plan_w + 300
        leg_y = plan_h
        self.writer.add_rectangle(leg_x, leg_y - 4500, 2000, 4500, layer="S-TITLEBLOCK")
        self.writer.add_text("CCTV SYSTEM LEGEND", (leg_x + 100, leg_y - 250), height=100, layer="E-TEXT")

        legend_items = [
            (f"Total Cameras: {self.res.total_cameras_count} Nos.", "IP 4K/4MP Network Cameras"),
            (f"NVR Configuration: {self.res.selected_nvr_channels}-Ch NVR", f"{self.res.selected_nvr_sata_bays} SATA Bays"),
            (f"Gross Storage: {self.res.gross_raid_storage_tb} TB", f"{self.res.raid_configuration} Array"),
            (f"Hard Drives: {self.res.required_hdd_count}x {self.res.selected_hdd_capacity_tb}TB", "Enterprise 24/7 SATA"),
            (f"Retention Mandate: {self.res.recording_days} Days", "Continuous 20 FPS H.265"),
            (f"PoE Power Budget: {self.res.total_poe_power_budget_watts} W", "Gigabit Managed PoE Switch"),
            ("Cabling: Cat6A 23AWG F/UTP", "Max 90m Channel Length"),
            ("UPS Backup: 2.0 kVA Online", "Min 30 Minutes Autonomy"),
        ]

        for idx, (sym, desc) in enumerate(legend_items):
            self.writer.add_text(f"{sym}", (leg_x + 100, leg_y - 650 - (idx * 300)), height=70, layer="E-TEXT")
            self.writer.add_text(f"  - {desc}", (leg_x + 100, leg_y - 750 - (idx * 300)), height=55, layer="S-TEXT")

        return self.writer.save(filepath)
