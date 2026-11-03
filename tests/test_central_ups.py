"""Unit tests for Central UPS & DC Battery Plant Design Engine and Exporters."""

import os
import unittest
from electrical.power_distribution.central_ups.scripts.design_engine import CentralUPSDesignEngine
from electrical.power_distribution.central_ups.exporters.excel_exporter import CentralUPSExcelExporter
from electrical.power_distribution.central_ups.exporters.dxf_exporter import CentralUPSDXFExporter


class TestCentralUPSDesign(unittest.TestCase):

    def setUp(self):
        self.engine = CentralUPSDesignEngine(code_standard="SBC")
        self.sample_loads = [
            {"id": "SRV-01", "name": "Primary Server Rack", "load_kw": 50.0, "pf": 0.90},
            {"id": "NET-01", "name": "Core Network Switchboard", "load_kw": 20.0, "pf": 0.85},
            {"id": "CCTV-01", "name": "CCTV & Security Headend", "load_kw": 10.0, "pf": 0.80},
        ]
        self.test_outdir = "output/test_central_ups"
        os.makedirs(self.test_outdir, exist_ok=True)

    def test_ups_module_and_redundancy_sizing(self):
        res = self.engine.size_ups_system(
            loads=self.sample_loads,
            backup_time_min=30.0,
            redundancy_type="N+1"
        )
        self.assertIn("ups_module", res)
        ups = res["ups_module"]
        # Connected load is 80 kW, with 20% margin = 96 kW (~108 kVA)
        self.assertGreater(ups["total_system_kva"], 100)
        self.assertGreaterEqual(ups["total_modules"], 2)  # N+1 means at least 2 modules
        self.assertEqual(ups["total_modules"], ups["n_modules"] + 1)

    def test_battery_plant_sizing_ieee485(self):
        res = self.engine.size_ups_system(
            loads=self.sample_loads,
            backup_time_min=30.0,
            redundancy_type="N+1"
        )
        batt = res["battery_plant"]
        # DC bus check
        self.assertEqual(batt["nominal_dc_bus_v"], 384.0)
        self.assertEqual(batt["total_cells"], 192)
        self.assertEqual(batt["blocks_per_string"], 32)
        self.assertGreater(batt["calc_ah"], 0)
        self.assertGreaterEqual(batt["actual_installed_ah"], batt["calc_ah"])
        self.assertEqual(batt["cell_eod_v"], 1.67)
        self.assertAlmostEqual(batt["min_dc_bus_voltage"], 192 * 1.67, delta=1.0)

    def test_hydrogen_ventilation_sizing(self):
        res = self.engine.size_ups_system(
            loads=self.sample_loads,
            backup_time_min=30.0,
            room_dimensions_m={"length": 6.0, "width": 4.0, "height": 3.0}
        )
        vent = res["ventilation"]
        # Room volume 6 x 4 x 3 = 72 m3
        self.assertEqual(vent["room_volume_m3"], 72.0)
        # Minimum 6 ACH means 72 * 6 = 432 m3/h
        self.assertGreaterEqual(vent["design_exhaust_airflow_m3_per_hr"], 432.0)
        self.assertGreater(vent["design_exhaust_airflow_cfm"], 200.0)

    def test_excel_and_dxf_export(self):
        res = self.engine.size_ups_system(
            loads=self.sample_loads,
            backup_time_min=30.0
        )
        excel_path = os.path.join(self.test_outdir, "test_ups.xlsx")
        dxf_path = os.path.join(self.test_outdir, "test_ups.dxf")

        excel_exp = CentralUPSExcelExporter()
        excel_exp.export(res, excel_path)
        self.assertTrue(os.path.exists(excel_path))
        self.assertGreater(os.path.getsize(excel_path), 1000)

        dxf_exp = CentralUPSDXFExporter()
        dxf_exp.export(res, dxf_path)
        self.assertTrue(os.path.exists(dxf_path))
        self.assertGreater(os.path.getsize(dxf_path), 1000)


if __name__ == "__main__":
    unittest.main()
