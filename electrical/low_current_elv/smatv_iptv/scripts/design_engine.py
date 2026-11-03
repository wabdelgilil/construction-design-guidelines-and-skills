"""SMATV and IPTV Distribution Design Engine.

Governing Standards:
- EN 50083 / EN 60728: Cable networks for television signals, sound signals and interactive services
- ITU-T J.83: Digital multi-programme television distribution by CATV/SMATV systems
- ISO/IEC 11801 / TIA-568: Generic Cabling Systems for IPTV distribution
- SBC 401: Saudi Building Code Electrical Installations
"""

import math
from typing import Dict, Any, List


class SMATVIPTVDesignEngine:
    """Calculates satellite dish antenna gain, link budget, RF signal attenuation
    from headend to user outlet, multi-switch cascade, and IPTV bandwidth."""

    def __init__(self, code_standard: str = "SBC"):
        self.code_standard = code_standard
        self.min_outlet_level_dbuv = 60.0
        self.max_outlet_level_dbuv = 77.0
        self.target_outlet_level_dbuv = 68.0

        # RF Attenuations (at 862 MHz / 2150 MHz IF band)
        self.cable_atten_rg6_db_per_m = 0.185
        self.cable_atten_rg11_db_per_m = 0.112
        self.outlet_loss_db = 1.5
        self.headend_launch_level_dbuv = 105.0

    def size_smatv_system(
        self,
        num_floors: int = 10,
        outlets_per_floor: int = 16,
        avg_floor_height_m: float = 3.6,
        avg_horizontal_rg6_run_m: float = 35.0,
        satellites: List[Dict[str, Any]] = None,
        iptv_enabled: bool = True,
        iptv_hd_channels: int = 80,
        iptv_4k_channels: int = 20
    ) -> Dict[str, Any]:
        """Calculates RF link budget across multi-switch risers and IPTV multicast bandwidth."""

        if satellites is None:
            satellites = [
                {"name": "Arabsat (BADR-4/5/6/7 @ 26E)", "dish_diameter_m": 2.4, "frequency_ghz": 12.0},
                {"name": "Nilesat (201/301 @ 7W)", "dish_diameter_m": 1.8, "frequency_ghz": 12.0},
                {"name": "Hotbird (13E)", "dish_diameter_m": 1.8, "frequency_ghz": 12.0}
            ]

        # 1. Satellite Dish Gain Calculations
        c = 3.0e8  # speed of light m/s
        eta = 0.65  # parabolic antenna efficiency
        dish_results = []
        for sat in satellites:
            f_hz = sat["frequency_ghz"] * 1e9
            wavelength = c / f_hz
            dia = sat["dish_diameter_m"]
            # Gain = eta * (pi * D / lambda)^2
            gain_linear = eta * ((math.pi * dia) / wavelength) ** 2
            gain_dbi = 10.0 * math.log10(gain_linear)
            # 3dB Beamwidth = 70 * (lambda / D)
            beamwidth_deg = 70.0 * (wavelength / dia)

            dish_results.append({
                "name": sat["name"],
                "dish_diameter_m": dia,
                "frequency_ghz": sat["frequency_ghz"],
                "gain_dbi": round(gain_dbi, 1),
                "beamwidth_deg": round(beamwidth_deg, 2)
            })

        # 2. RF Coaxial Link Budget Analysis (Riser Cascade)
        # Total outlets in building
        total_outlets = num_floors * outlets_per_floor

        # Riser backbone RG-11 cable run from Roof Headend to Floor 1
        riser_levels = []
        current_trunk_level = self.headend_launch_level_dbuv  # Launch from launch amplifier (105 dBuV)

        # Standard multi-switch tap losses per floor to equalize signal
        # Floors near top get higher tap loss (e.g. 20-24 dB), bottom floors get lower tap loss (e.g. 10-12 dB)
        for flr in range(num_floors, 0, -1):
            floor_cable_rg11_m = avg_floor_height_m
            cable_loss_rg11 = floor_cable_rg11_m * self.cable_atten_rg11_db_per_m

            # Tap selection to keep outlet level near 68 dBuV
            # Outlet level = Trunk_level - Tap_loss - (Horizontal_RG6_loss) - Outlet_loss
            horiz_loss = avg_horizontal_rg6_run_m * self.cable_atten_rg6_db_per_m
            desired_tap_loss = current_trunk_level - self.target_outlet_level_dbuv - horiz_loss - self.outlet_loss_db

            # Standard tap values [10, 12, 14, 16, 20, 24]
            available_taps = [10, 12, 14, 16, 20, 24]
            selected_tap = min(available_taps, key=lambda x: abs(x - desired_tap_loss))
            through_loss = 1.8  # Typical tap through-loss in dB

            actual_outlet_level = current_trunk_level - selected_tap - horiz_loss - self.outlet_loss_db
            is_compliant = self.min_outlet_level_dbuv <= actual_outlet_level <= self.max_outlet_level_dbuv

            riser_levels.append({
                "floor_no": flr,
                "trunk_input_dbuv": round(current_trunk_level, 1),
                "tap_loss_db": selected_tap,
                "horizontal_cable_loss_db": round(horiz_loss, 2),
                "outlet_signal_level_dbuv": round(actual_outlet_level, 1),
                "status": "COMPLIANT" if is_compliant else "NON-COMPLIANT"
            })

            # Reduce trunk level for next lower floor
            current_trunk_level = current_trunk_level - cable_loss_rg11 - through_loss

        # 3. Multiswitch Sizing
        # 16 or 24 or 32 port standalone/cascadable multiswitches
        multiswitches_per_floor = math.ceil(outlets_per_floor / 16)
        total_multiswitches = multiswitches_per_floor * num_floors

        # 4. IPTV Multicast Bandwidth Sizing
        # HD Stream: 6.0 Mbps (H.264/H.265)
        # 4K UHD Stream: 20.0 Mbps (HEVC/H.265)
        iptv_hd_bw_mbps = iptv_hd_channels * 6.0
        iptv_4k_bw_mbps = iptv_4k_channels * 20.0
        total_multicast_stream_bw_mbps = iptv_hd_bw_mbps + iptv_4k_bw_mbps
        total_multicast_stream_bw_gbps = total_multicast_stream_bw_mbps / 1000.0

        # Recommended core switch uplink
        if total_multicast_stream_bw_gbps < 1.0:
            rec_uplink = "1 Gbps SFP"
        elif total_multicast_stream_bw_gbps < 8.0:
            rec_uplink = "10 Gbps SFP+"
        else:
            rec_uplink = "40/100 Gbps QSFP"

        return {
            "code_standard": self.code_standard,
            "building_parameters": {
                "num_floors": num_floors,
                "outlets_per_floor": outlets_per_floor,
                "total_outlets": total_outlets,
                "avg_floor_height_m": avg_floor_height_m,
                "avg_horizontal_rg6_run_m": avg_horizontal_rg6_run_m,
            },
            "satellite_dishes": dish_results,
            "rf_link_budget": {
                "headend_launch_level_dbuv": self.headend_launch_level_dbuv,
                "min_allowable_dbuv": self.min_outlet_level_dbuv,
                "max_allowable_dbuv": self.max_outlet_level_dbuv,
                "target_outlet_level_dbuv": self.target_outlet_level_dbuv,
                "riser_schedule": riser_levels,
                "all_floors_compliant": all(item["status"] == "COMPLIANT" for item in riser_levels)
            },
            "hardware_sizing": {
                "multiswitches_per_floor": multiswitches_per_floor,
                "total_multiswitches": total_multiswitches,
                "launch_amplifiers_qty": len(satellites) * 4,  # 4 polarities per satellite (VL, VH, HL, HH)
            },
            "iptv_network": {
                "iptv_enabled": iptv_enabled,
                "hd_channels": iptv_hd_channels,
                "uhd_4k_channels": iptv_4k_channels,
                "total_multicast_stream_bw_mbps": round(total_multicast_stream_bw_mbps, 1),
                "total_multicast_stream_bw_gbps": round(total_multicast_stream_bw_gbps, 2),
                "recommended_core_uplink": rec_uplink,
            }
        }
