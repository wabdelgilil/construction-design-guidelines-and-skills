"""Unit tests for SMATV & IPTV Distribution Design Engine and Exporters."""

import os
import unittest
from electrical.low_current_elv.smatv_iptv.scripts.design_engine import SMATVIPTVDesignEngine
from electrical.low_current_elv.smatv_iptv.exporters.excel_exporter import SMATVIPTVExcelExporter
from electrical.low_current_elv.smatv_iptv.exporters.dxf_exporter import SMATVIPTVDXFExporter


class TestSMATVIPTVDesign(unittest.TestCase):

    def setUp(self):
        self.engine = SMATVIPTVDesignEngine(code_standard="SBC")
        self.test_outdir = "output/test_smatv_iptv"
        os.makedirs(self.test_outdir, exist_ok=True)

    def test_dish_gain_and_rf_budget(self):
        res = self.engine.size_smatv_system(
            num_floors=8,
            outlets_per_floor=12,
            avg_horizontal_rg6_run_m=30.0
        )
        self.assertIn("satellite_dishes", res)
        self.assertEqual(len(res["satellite_dishes"]), 3)
        for sat in res["satellite_dishes"]:
            # Antenna gain for 1.8-2.4m dish in Ku band should be between 44 and 49 dBi
            self.assertGreater(sat["gain_dbi"], 42.0)
            self.assertLess(sat["gain_dbi"], 52.0)

        # Riser link budget checks
        rf = res["rf_link_budget"]
        self.assertEqual(len(rf["riser_schedule"]), 8)
        self.assertTrue(rf["all_floors_compliant"])
        for flr in rf["riser_schedule"]:
            self.assertGreaterEqual(flr["outlet_signal_level_dbuv"], 60.0)
            self.assertLessEqual(flr["outlet_signal_level_dbuv"], 77.0)

    def test_iptv_multicast_bandwidth(self):
        res = self.engine.size_smatv_system(
            iptv_enabled=True,
            iptv_hd_channels=100,
            iptv_4k_channels=25
        )
        iptv = res["iptv_network"]
        # 100 * 6.0 + 25 * 20.0 = 600 + 500 = 1100 Mbps (1.1 Gbps)
        self.assertEqual(iptv["total_multicast_stream_bw_mbps"], 1100.0)
        self.assertEqual(iptv["total_multicast_stream_bw_gbps"], 1.1)
        self.assertEqual(iptv["recommended_core_uplink"], "10 Gbps SFP+")

    def test_excel_and_dxf_export(self):
        res = self.engine.size_smatv_system(
            num_floors=6,
            outlets_per_floor=10
        )
        excel_path = os.path.join(self.test_outdir, "test_smatv.xlsx")
        dxf_path = os.path.join(self.test_outdir, "test_smatv.dxf")

        excel_exp = SMATVIPTVExcelExporter()
        excel_exp.export(res, excel_path)
        self.assertTrue(os.path.exists(excel_path))
        self.assertGreater(os.path.getsize(excel_path), 1000)

        dxf_exp = SMATVIPTVDXFExporter()
        dxf_exp.export(res, dxf_path)
        self.assertTrue(os.path.exists(dxf_path))
        self.assertGreater(os.path.getsize(dxf_path), 1000)


if __name__ == "__main__":
    unittest.main()
