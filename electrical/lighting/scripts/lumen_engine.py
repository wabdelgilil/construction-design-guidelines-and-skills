"""
Lumen Method Lighting Design Engine.
Computes room-by-room required lumens, fixture count, and grid layout (Rows x Columns).
Zero mental math, zero hallucination.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class LightingFixture:
    model_name: str
    lumens_per_fixture: float = 3600.0  # e.g., 600x600 LED panel 36W @ 100 lm/W
    power_watts: float = 36.0
    cct_kelvin: int = 4000
    cri: int = 80


@dataclass
class LightingDesignResult:
    room_name: str
    room_length_m: float
    room_width_m: float
    room_area_m2: float
    target_lux: float
    achieved_lux: float
    fixture_model: str
    total_fixtures_count: int
    grid_columns: int  # along length
    grid_rows: int     # along width
    spacing_x_m: float
    spacing_y_m: float
    wall_offset_x_m: float
    wall_offset_y_m: float
    total_power_watts: float
    lighting_power_density_w_per_m2: float
    fixture_coordinates: List[Tuple[float, float]] = field(default_factory=list)
    compliance_status: str = "COMPLIANT"
    summary: Dict[str, Any] = field(default_factory=dict)


class LumenEngine:
    """Calculates room lighting requirements and generates fixture coordinate grid."""

    @classmethod
    def design_room_lighting(
        cls,
        room_name: str,
        length_m: float,
        width_m: float,
        target_lux: float = 300.0,
        ceiling_height_m: float = 3.0,
        workplane_height_m: float = 0.80,
        maintenance_factor: float = 0.80,
        coefficient_of_utilization: float = 0.65,
        fixture: Optional[LightingFixture] = None,
    ) -> LightingDesignResult:
        if fixture is None:
            fixture = LightingFixture(model_name="600x600 LED Panel 36W", lumens_per_fixture=3600.0, power_watts=36.0)

        area = round(length_m * width_m, 2)
        total_lumens_required = (target_lux * area) / (coefficient_of_utilization * maintenance_factor)

        # Minimum number of fixtures
        raw_count = total_lumens_required / fixture.lumens_per_fixture
        initial_n = max(math.ceil(raw_count), 1)

        # Calculate grid layout matching room aspect ratio
        aspect_ratio = length_m / max(width_m, 0.1)

        # Estimate rows and columns
        n_rows = max(round(math.sqrt(initial_n / aspect_ratio)), 1)
        n_cols = max(math.ceil(initial_n / n_rows), 1)
        total_fixtures = n_rows * n_cols

        # Spacing
        spacing_x = round(length_m / n_cols, 2)
        spacing_y = round(width_m / n_rows, 2)
        wall_offset_x = round(spacing_x / 2.0, 2)
        wall_offset_y = round(spacing_y / 2.0, 2)

        # Actual achieved illuminance
        actual_lumens = total_fixtures * fixture.lumens_per_fixture
        achieved_lux = round((actual_lumens * coefficient_of_utilization * maintenance_factor) / area, 1)

        # Power density (W/m2)
        total_power = total_fixtures * fixture.power_watts
        lpd = round(total_power / area, 2)

        # Generate exact fixture coordinates
        coordinates = []
        for c in range(n_cols):
            x = wall_offset_x + (c * spacing_x)
            for r in range(n_rows):
                y = wall_offset_y + (r * spacing_y)
                coordinates.append((round(x, 2), round(y, 2)))

        is_compliant = achieved_lux >= (target_lux * 0.95)

        return LightingDesignResult(
            room_name=room_name,
            room_length_m=length_m,
            room_width_m=width_m,
            room_area_m2=area,
            target_lux=target_lux,
            achieved_lux=achieved_lux,
            fixture_model=fixture.model_name,
            total_fixtures_count=total_fixtures,
            grid_columns=n_cols,
            grid_rows=n_rows,
            spacing_x_m=spacing_x,
            spacing_y_m=spacing_y,
            wall_offset_x_m=wall_offset_x,
            wall_offset_y_m=wall_offset_y,
            total_power_watts=total_power,
            lighting_power_density_w_per_m2=lpd,
            fixture_coordinates=coordinates,
            compliance_status="COMPLIANT" if is_compliant else "UNDER_LIT",
            summary={
                "fixtures_grid": f"{n_cols} x {n_rows} ({total_fixtures} Fixtures)",
                "achieved_vs_target": f"{achieved_lux} Lux / {target_lux} Lux Target",
                "lighting_power_density": f"{lpd} W/m2",
            },
        )
