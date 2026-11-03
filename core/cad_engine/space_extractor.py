"""
Universal Architectural Space & Geometry Extractor.
Parses architectural CAD drawings (DXF), extracts room polygons, calculates net floor areas,
and matches room label texts using Point-in-Polygon ray-casting.
Serves Architectural (Planning), Structural (Tributary loads), Mechanical (CFM), and Electrical (Lighting).
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import ezdxf
from ezdxf.math import Vec2


def point_in_polygon(x: float, y: float, poly_points: List[Tuple[float, float]]) -> bool:
    """Ray-casting algorithm to test if (x, y) is inside a 2D polygon."""
    n = len(poly_points)
    if n < 3:
        return False
    inside = False
    p1x, p1y = poly_points[0]
    for i in range(1, n + 1):
        p2x, p2y = poly_points[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def polygon_area(points: List[Tuple[float, float]]) -> float:
    """Calculates polygon area using the Shoelace formula."""
    n = len(points)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    return abs(area) / 2.0


def polygon_centroid(points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Calculates polygon geometric centroid."""
    n = len(points)
    if n < 3:
        return (0.0, 0.0)
    cx = sum(p[0] for p in points) / n
    cy = sum(p[1] for p in points) / n
    return (round(cx, 2), round(cy, 2))


@dataclass
class ExtractedSpace:
    space_id: str
    room_name: str
    area_m2: float
    center_point: Tuple[float, float]
    bounding_box: Dict[str, float]
    boundary_points: List[Tuple[float, float]] = field(default_factory=list)
    suggested_live_load_kn_m2: float = 2.0
    suggested_target_lux: float = 150.0
    suggested_cooling_load_tons: float = 1.0


class SpaceExtractor:
    """Extracts architectural room spaces from DXF floor plans."""

    def __init__(self, dxf_path: Path, drawing_units: str = "mm"):
        self.dxf_path = Path(dxf_path).resolve()
        if not self.dxf_path.is_file():
            raise FileNotFoundError(f"CAD file not found: {self.dxf_path}")

        self.doc = ezdxf.readfile(str(self.dxf_path))
        self.msp = self.doc.modelspace()
        # Scale factor to convert drawing coordinates to meters
        self.to_meters = 0.001 if drawing_units.lower() == "mm" else 1.0

    def extract_spaces(
        self,
        min_area_m2: float = 1.0,
        max_area_m2: float = 2000.0,
    ) -> List[ExtractedSpace]:
        """Discovers rooms by analyzing closed polylines and text labels."""
        # 1. Collect closed polylines
        candidates = []
        for entity in self.msp:
            if entity.dxftype() in ("LWPOLYLINE", "POLYLINE") and entity.is_closed:
                pts = [(p[0] * self.to_meters, p[1] * self.to_meters) for p in entity.get_points()]
                area = polygon_area(pts)
                if min_area_m2 <= area <= max_area_m2:
                    centroid = polygon_centroid(pts)
                    xs = [p[0] for p in pts]
                    ys = [p[1] for p in pts]
                    bbox = {
                        "min_x": min(xs),
                        "max_x": max(xs),
                        "min_y": min(ys),
                        "max_y": max(ys),
                    }
                    candidates.append({
                        "points": pts,
                        "area_m2": round(area, 2),
                        "centroid": centroid,
                        "bbox": bbox,
                        "texts": [],
                    })

        # 2. Collect room label texts
        text_entities = []
        for entity in self.msp:
            if entity.dxftype() in ("TEXT", "MTEXT"):
                text_val = (
                    entity.dxf.text if entity.dxftype() == "TEXT" else entity.text
                ).strip()
                if text_val and not text_val.replace(".", "", 1).isdigit():
                    pos = entity.dxf.insert
                    x_m = pos[0] * self.to_meters
                    y_m = pos[1] * self.to_meters
                    text_entities.append((x_m, y_m, text_val))

        # 3. Match texts inside candidate polygons using Point-in-Polygon
        for poly in candidates:
            pts = poly["points"]
            for tx, ty, text_val in text_entities:
                if point_in_polygon(tx, ty, pts):
                    poly["texts"].append(text_val)

        # 4. Formulate ExtractedSpace deliverables
        extracted: List[ExtractedSpace] = []
        for idx, poly in enumerate(candidates, start=1):
            room_name = (
                " / ".join(poly["texts"]) if poly["texts"] else f"Unassigned_Room_{idx}"
            )
            area = poly["area_m2"]

            # Heuristic assignment based on room name keywords
            name_lower = room_name.lower()
            if any(k in name_lower for k in ["kitchen", "مطبخ"]):
                live_load = 2.0
                lux = 300.0
                cooling_ton = round(area / 10.0, 1)
            elif any(k in name_lower for k in ["bed", "نوم"]):
                live_load = 2.0
                lux = 100.0
                cooling_ton = round(area / 14.0, 1)
            elif any(k in name_lower for k in ["living", "majlis", "معيشة", "مجلس"]):
                live_load = 2.0
                lux = 200.0
                cooling_ton = round(area / 12.0, 1)
            elif any(k in name_lower for k in ["office", "مكتب", "class", "فصل"]):
                live_load = 3.0
                lux = 400.0
                cooling_ton = round(area / 12.0, 1)
            elif any(k in name_lower for k in ["bath", "حمام", "toilet", "دورة"]):
                live_load = 2.0
                lux = 150.0
                cooling_ton = 0.5
            elif any(k in name_lower for k in ["corridor", "stair", "ممر", "درج"]):
                live_load = 4.0
                lux = 100.0
                cooling_ton = round(area / 16.0, 1)
            else:
                live_load = 2.0
                lux = 150.0
                cooling_ton = round(area / 12.0, 1)

            space = ExtractedSpace(
                space_id=f"RM-{idx:02d}",
                room_name=room_name,
                area_m2=area,
                center_point=poly["centroid"],
                bounding_box=poly["bbox"],
                boundary_points=poly["points"],
                suggested_live_load_kn_m2=live_load,
                suggested_target_lux=lux,
                suggested_cooling_load_tons=max(cooling_ton, 0.5),
            )
            extracted.append(space)

        return extracted
