"""
Deterministic CCTV Surveillance & NVR Storage Sizing Engine.
Computes DORI optical focal lengths, field-of-view (HFOV), H.265 network bandwidth,
NVR hard drive capacity with RAID redundancy, and PoE switch power budgets (EN 62676-4).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class CameraRequirement:
    tag: str
    location: str
    camera_type: str  # fixed_dome, outdoor_bullet, ptz_dome
    resolution: str   # 2mp_1080p, 4mp_1440p, 4k_8mp
    target_dori: str  # identification, recognition, observation, detection
    target_distance_m: float
    is_outdoor: bool = False


@dataclass
class SizedCameraResult:
    tag: str
    location: str
    camera_type: str
    resolution: str
    target_dori: str
    target_distance_m: float
    selected_focal_length_mm: float
    horizontal_fov_deg: float
    dori_identification_dist_m: float
    dori_recognition_dist_m: float
    bitrate_mbps: float
    poe_class_watts: float


@dataclass
class CCTVSecurityDesignResult:
    project_name: str
    standard_used: str
    total_cameras_count: int
    cameras: List[SizedCameraResult]
    total_network_bandwidth_mbps: float
    recording_days: int
    compression_format: str
    net_storage_tb: float
    gross_raid_storage_tb: float
    raid_configuration: str
    selected_hdd_capacity_tb: int
    required_hdd_count: int
    selected_nvr_channels: int
    selected_nvr_sata_bays: int
    total_poe_power_budget_watts: float
    coordination_notices: List[str] = field(default_factory=list)


class CCTVSecurityEngine:
    """Calculates DORI optics, camera bandwidth, NVR storage, and PoE load."""

    STANDARD_FOCALS = [2.8, 4.0, 6.0, 8.0, 12.0]
    SENSOR_WIDTH_MM = 5.2  # 1/2.8" sensor width

    RES_PIXELS = {
        "2mp_1080p": 1920,
        "4mp_1440p": 2560,
        "4k_8mp": 3840,
    }

    RES_BITRATE_H265 = {
        "2mp_1080p": 1.5,
        "4mp_1440p": 2.5,
        "4k_8mp": 4.0,
    }

    DORI_PPM = {
        "identification": 250,
        "recognition": 125,
        "observation": 62.5,
        "detection": 25,
    }

    def __init__(self, standard: str = "EN 62676-4 / NFPA 730"):
        self.standard = standard

    def design_cctv_system(
        self,
        project_name: str,
        camera_requests: List[CameraRequirement],
        recording_days: int = 31,
        raid_type: str = "RAID_5",
    ) -> CCTVSecurityDesignResult:
        sized_cams = []
        total_bandwidth = 0.0
        total_poe = 0.0

        for cam in camera_requests:
            h_pixels = self.RES_PIXELS.get(cam.resolution, 2560)
            bitrate = self.RES_BITRATE_H265.get(cam.resolution, 2.5)

            # Target target width for target DORI: W = H_pixels / Required_PPM
            req_ppm = self.DORI_PPM.get(cam.target_dori, 125)
            target_scene_width = h_pixels / req_ppm

            # Focal length: f = (sensor_width * distance) / target_scene_width
            f_ideal = (self.SENSOR_WIDTH_MM * cam.target_distance_m) / max(target_scene_width, 1.0)

            # Select nearest standard focal length >= f_ideal (or 2.8 if wide)
            selected_f = self.STANDARD_FOCALS[0]
            for f_val in self.STANDARD_FOCALS:
                if f_val >= f_ideal:
                    selected_f = f_val
                    break
            else:
                selected_f = self.STANDARD_FOCALS[-1]

            # Horizontal Field of View (HFOV)
            hfov = 2.0 * math.atan(self.SENSOR_WIDTH_MM / (2.0 * selected_f)) * (180.0 / math.pi)

            # DORI Max Distances with this selected focal length:
            # D = (f * (H_pixels / PPM)) / sensor_width
            d_id = round((selected_f * (h_pixels / 250.0)) / self.SENSOR_WIDTH_MM, 1)
            d_rec = round((selected_f * (h_pixels / 125.0)) / self.SENSOR_WIDTH_MM, 1)

            # PoE Power: 30W for PTZ, 15.4W for standard dome/bullet
            poe_w = 30.0 if "ptz" in cam.camera_type else 15.4

            total_bandwidth += bitrate
            total_poe += poe_w

            sized_cams.append(
                SizedCameraResult(
                    tag=cam.tag,
                    location=cam.location,
                    camera_type=cam.camera_type.replace("_", " ").title(),
                    resolution=cam.resolution.upper(),
                    target_dori=cam.target_dori.title(),
                    target_distance_m=cam.target_distance_m,
                    selected_focal_length_mm=selected_f,
                    horizontal_fov_deg=round(hfov, 1),
                    dori_identification_dist_m=d_id,
                    dori_recognition_dist_m=d_rec,
                    bitrate_mbps=bitrate,
                    poe_class_watts=poe_w,
                )
            )

        # 2. NVR Storage Calculation (TB)
        # Storage = (Bandwidth_mbps * 3600 * 24 * Days * 1.10) / (8 * 1,000,000)
        total_seconds = recording_days * 86400
        net_tb_raw = (total_bandwidth * total_seconds * 1.10) / (8.0 * 1000000.0)
        net_tb = round(net_tb_raw, 2)

        # RAID Efficiency: RAID 5 ~ 80%, RAID 6 ~ 70%
        raid_efficiency = 0.80 if raid_type == "RAID_5" else 0.70
        gross_tb = round(net_tb / raid_efficiency, 2)

        # HDD Sizing: Select 8TB, 12TB, or 16TB Enterprise SATA
        hdd_capacity = 10  # 10 TB drives standard
        hdd_count = max(math.ceil(gross_tb / hdd_capacity), 2)
        if raid_type == "RAID_5" and hdd_count < 3:
            hdd_count = 3  # Min 3 drives for RAID 5
        elif raid_type == "RAID_6" and hdd_count < 4:
            hdd_count = 4  # Min 4 drives for RAID 6

        # NVR Channel Sizing: 16-Ch, 32-Ch, 64-Ch
        total_cam_count = len(camera_requests)
        if total_cam_count <= 16:
            nvr_channels = 16
            nvr_bays = 4
        elif total_cam_count <= 32:
            nvr_channels = 32
            nvr_bays = 8
        else:
            nvr_channels = 64
            nvr_bays = 16

        # PoE Budget with 20% safety headroom
        total_poe_budget = round(total_poe * 1.25, 1)

        notices = [
            f"Telecommunications Interface: All camera horizontal runs require Cat6A 23AWG shielded (F/UTP) cabling, strictly limited to <= 90 meters channel length from telecom rack.",
            f"Network Switch Interface: Provide 24-Port Gigabit Managed PoE+ Switch with minimum {total_poe_budget}W continuous PoE power budget.",
            f"NVR Storage Retention: {total_cam_count} cameras recording continuous H.265 20FPS require {gross_tb} TB gross storage ({hdd_count}x {hdd_capacity}TB HDDs in {raid_type}) for {recording_days} days archive.",
            "Electrical / UPS Interface: Dedicated 2.0 kVA Online Double-Conversion UPS required for CCTV rack to ensure minimum 30 minutes runtime during power loss.",
            "Security Control Room: Provide dual 4K ultra-narrow bezel 55-inch video wall monitors connected to NVR HDMI 2.0 outputs.",
        ]

        return CCTVSecurityDesignResult(
            project_name=project_name,
            standard_used=self.standard,
            total_cameras_count=total_cam_count,
            cameras=sized_cams,
            total_network_bandwidth_mbps=round(total_bandwidth, 2),
            recording_days=recording_days,
            compression_format="H.265 / Smart Codec",
            net_storage_tb=net_tb,
            gross_raid_storage_tb=gross_tb,
            raid_configuration=raid_type,
            selected_hdd_capacity_tb=hdd_capacity,
            required_hdd_count=hdd_count,
            selected_nvr_channels=nvr_channels,
            selected_nvr_sata_bays=nvr_bays,
            total_poe_power_budget_watts=total_poe_budget,
            coordination_notices=notices,
        )
