"""Unit tests for Outdoor Roadway Lighting Design Engine and Exporters."""

import os
import unittest
from electrical.lighting.outdoor_lighting.scripts.design_engine import OutdoorLightingDesignEngine
from electrical.lighting.outdoor_lighting.exporters.excel_exporter import OutdoorLightingExcelExporter
from electrical.lighting.outdoor_lighting.exporters.dxf_exporter import OutdoorLightingDXFExporter


class TestOutdoorLightingDesign(unittest.TestCase):

    def setUp(self):
        self.engine = OutdoorLightingDesignEngine(code_standard="SBC")
        self.test_outdir = "output/test_outdoor_lighting"
        os.makedirs(self.test_outdir, exist_ok=True)

    def test_roadway_lighting_calculation(self):
        res = self.engine.design_roadway_lighting(
            road_length_m=500.0,
            road_width_m=10.5,
            number_of_lanes=3,
            road_class="M3",
            pole_arrangement="single_sided",
            luminaire_power_w=150.0,
            luminaire_lumens=21500.0,
            mounting_height_m=10.0
        )
        self.assertIn("road_geometry", res)
        geo = res["road_geometry"]
        photo = res["photometrics"]
        elec = res["electrical_feeder"]

        # Pole count check
        self.assertGreater(geo["num_poles"], 5)
        self.assertEqual(geo["num_poles"], geo["num_luminaires"])
        # S/H ratio around 3.3
        self.assertAlmostEqual(geo["spacing_to_height_ratio"], 3.3, delta=0.5)

        # Photometrics check
        self.assertGreater(photo["e_avg_lux"], 10.0)
        self.assertGreater(photo["l_avg_cd_m2"], 0.75)
        self.assertTrue(photo["lavg_compliant"])
        self.assertTrue(photo["u0_compliant"])

        # Electrical feeder check
        self.assertGreater(elec["total_lighting_load_kw"], 0)
        self.assertGreater(elec["flc_amps_3ph"], 0)
        self.assertLess(elec["v_drop_percent"], 5.0)
        self.assertTrue(elec["v_drop_compliant"])

    def test_median_twin_arrangement(self):
        res = self.engine.design_roadway_lighting(
            road_length_m=600.0,
            road_width_m=20.0,
            road_class="M2",
            pole_arrangement="median_twin",
            mounting_height_m=12.0
        )
        geo = res["road_geometry"]
        # Median twin has 2 luminaires per pole
        self.assertEqual(geo["num_luminaires"], geo["num_poles"] * 2)

    def test_excel_and_dxf_export(self):
        res = self.engine.design_roadway_lighting(
            road_length_m=400.0,
            road_width_m=10.5,
            road_class="M3"
        )
        excel_path = os.path.join(self.test_outdir, "test_road_lighting.xlsx")
        dxf_path = os.path.join(self.test_outdir, "test_road_lighting.dxf")

        excel_exp = OutdoorLightingExcelExporter()
        excel_exp.export(res, excel_path)
        self.assertTrue(os.path.exists(excel_path))
        self.assertGreater(os.path.getsize(excel_path), 1000)

        dxf_exp = OutdoorLightingDXFExporter()
        dxf_exp.export(res, dxf_path)
        self.assertTrue(os.path.exists(dxf_path))
        self.assertGreater(os.path.getsize(dxf_path), 1000)


if __name__ == "__main__":
    unittest.main()
