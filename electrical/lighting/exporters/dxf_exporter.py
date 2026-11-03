"""
AutoCAD DXF Exporter for Lighting Ceiling Layout and Fixture Arrays.
Generates scaled ceiling plans, luminaire symbols at exact coordinates, and circuit homeruns.
"""

from pathlib import Path
from ezdxf.enums import TextEntityAlignment
from core.exporters.dxf_writer import DXFWriter
from electrical.lighting.scripts.lumen_engine import LightingDesignResult


class LightingDXFExporter:
    """Exports lighting ceiling layout to AutoCAD .dxf format."""

    def __init__(self, result: LightingDesignResult):
        self.res = result
        self.writer = DXFWriter("lighting_layout.dxf")

    def export(self, filepath: Path) -> Path:
        """Draws the ceiling plan and saves the file."""
        # Convert dimensions to millimeters for CAD standard
        scale = 1000.0  # 1m = 1000mm
        l_mm = self.res.room_length_m * scale
        w_mm = self.res.room_width_m * scale

        # 1. Draw Title Block / Sheet Border
        margin = 500.0
        self.writer.add_rectangle(-margin, -margin, l_mm + 2 * margin + 800, w_mm + 2 * margin, layer="S-TITLEBLOCK")
        self.writer.add_text(
            f"REFLECTED CEILING & LIGHTING PLAN - {self.res.room_name.upper()}",
            (0, w_mm + 350),
            height=60,
            layer="E-TEXT",
        )
        self.writer.add_text(
            f"Dimensions: {self.res.room_length_m}m x {self.res.room_width_m}m | Target: {self.res.target_lux} Lux | Achieved: {self.res.achieved_lux} Lux",
            (0, w_mm + 200),
            height=35,
            layer="E-TEXT",
        )
        self.writer.add_text(
            f"Fixtures: {self.res.total_fixtures_count}x ({self.res.fixture_model}) | LPD: {self.res.lighting_power_density_w_per_m2} W/m2",
            (0, w_mm + 80),
            height=30,
            layer="E-TEXT",
        )

        # 2. Draw Room Perimeter Wall
        self.writer.add_rectangle(0, 0, l_mm, w_mm, layer="S-COLUMN")

        # 3. Draw Fixtures
        fixture_size = 600.0  # 600x600 mm fixture
        half_fix = fixture_size / 2.0

        for idx, (x_m, y_m) in enumerate(self.res.fixture_coordinates, 1):
            fx_mm = x_m * scale
            fy_mm = y_m * scale

            # Draw 600x600 recessed fixture box
            self.writer.add_rectangle(
                fx_mm - half_fix,
                fy_mm - half_fix,
                fixture_size,
                fixture_size,
                layer="E-LITE-FIXT",
            )
            # Draw diagonal cross inside fixture
            self.writer.add_line(
                (fx_mm - half_fix, fy_mm - half_fix),
                (fx_mm + half_fix, fy_mm + half_fix),
                layer="E-LITE-FIXT",
            )
            self.writer.add_line(
                (fx_mm - half_fix, fy_mm + half_fix),
                (fx_mm + half_fix, fy_mm - half_fix),
                layer="E-LITE-FIXT",
            )

            # Fixture Tag
            self.writer.add_text(
                f"L{idx:02d}",
                (fx_mm, fy_mm + half_fix + 40),
                height=25,
                layer="E-TEXT",
                align=TextEntityAlignment.BOTTOM_CENTER,
            )

        # 4. Draw Circuit Homerun line
        if len(self.res.fixture_coordinates) > 1:
            for i in range(len(self.res.fixture_coordinates) - 1):
                p1 = (self.res.fixture_coordinates[i][0] * scale, self.res.fixture_coordinates[i][1] * scale)
                p2 = (self.res.fixture_coordinates[i + 1][0] * scale, self.res.fixture_coordinates[i + 1][1] * scale)
                self.writer.add_line(p1, p2, layer="E-LITE-CIRC")

        # 5. Dimensions
        self.writer.add_linear_dimension((0, 0), (l_mm, 0), (l_mm / 2, -150), layer="S-DIMS")
        self.writer.add_linear_dimension((0, 0), (0, w_mm), (-150, w_mm / 2), layer="S-DIMS")

        # 6. Luminaire Legend Box
        legend_x = l_mm + 150
        legend_y = w_mm
        self.writer.add_rectangle(legend_x, legend_y - 400, 550, 400, layer="S-TITLEBLOCK")
        self.writer.add_text("LUMINAIRE LEGEND", (legend_x + 30, legend_y - 50), height=35, layer="E-TEXT")
        self.writer.add_text(f"Type: {self.res.fixture_model}", (legend_x + 30, legend_y - 120), height=25, layer="E-TEXT")
        self.writer.add_text("Mounting: Recessed Modular Ceiling", (legend_x + 30, legend_y - 170), height=25, layer="E-TEXT")
        self.writer.add_text(f"Quantity: {self.res.total_fixtures_count} Nos.", (legend_x + 30, legend_y - 220), height=25, layer="E-TEXT")
        self.writer.add_text(f"Grid: {self.res.grid_columns} Cols x {self.res.grid_rows} Rows", (legend_x + 30, legend_y - 270), height=25, layer="E-TEXT")
        self.writer.add_text("Circuit: CKT-L01 (10A MCB, 3x1.5mm2)", (legend_x + 30, legend_y - 320), height=25, layer="E-TEXT")

        return self.writer.save(filepath)
