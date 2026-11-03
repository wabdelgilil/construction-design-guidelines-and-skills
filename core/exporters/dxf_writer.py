"""
CAD DXF Exporter Core Utility using ezdxf.
Provides standardized engineering layers, drawing scales, dimensions, and detailing.
"""

from pathlib import Path
from typing import Optional, Tuple
import ezdxf
from ezdxf.enums import TextEntityAlignment


class DXFWriter:
    """Manages creation of standardized AutoCAD .dxf drawings."""

    # Standard Engineering Color Palette (AutoCAD ACI Colors)
    COLOR_RED = 1
    COLOR_YELLOW = 2
    COLOR_GREEN = 3
    COLOR_CYAN = 4
    COLOR_BLUE = 5
    COLOR_MAGENTA = 6
    COLOR_WHITE = 7
    COLOR_GRAY = 8

    def __init__(self, filename: str = "drawing.dxf"):
        self.doc = ezdxf.new("R2010", setup=True)
        self.msp = self.doc.modelspace()
        self.filename = filename
        self._setup_standard_layers()

    def _setup_standard_layers(self):
        """Initializes standard multi-disciplinary CAD layers (Structural, Electrical, Mechanical)."""
        layers = [
            # Structural
            ("S-CONC-BLINDING", self.COLOR_GRAY, "Continuous", 0.18),
            ("S-CONC-RC", self.COLOR_CYAN, "Continuous", 0.35),
            ("S-COLUMN", self.COLOR_WHITE, "Continuous", 0.50),
            ("S-REBAR-BOT", self.COLOR_RED, "Continuous", 0.35),
            ("S-REBAR-DOWEL", self.COLOR_YELLOW, "Continuous", 0.35),
            ("S-DIMS", self.COLOR_GREEN, "Continuous", 0.15),
            ("S-TEXT", self.COLOR_YELLOW, "Continuous", 0.20),
            ("S-HATCH", self.COLOR_GRAY, "Continuous", 0.13),
            ("S-TITLEBLOCK", self.COLOR_BLUE, "Continuous", 0.25),
            # Electrical
            ("E-POWR-PANL", self.COLOR_MAGENTA, "Continuous", 0.50),
            ("E-POWR-SCKT", self.COLOR_CYAN, "Continuous", 0.30),
            ("E-POWR-CIRC", self.COLOR_YELLOW, "Continuous", 0.25),
            ("E-LITE-FIXT", self.COLOR_YELLOW, "Continuous", 0.35),
            ("E-LITE-CIRC", self.COLOR_CYAN, "Continuous", 0.20),
            ("E-TEXT", self.COLOR_WHITE, "Continuous", 0.20),
            # Mechanical
            ("M-HVAC-DUCT", self.COLOR_BLUE, "Continuous", 0.35),
            ("M-HVAC-EQUP", self.COLOR_MAGENTA, "Continuous", 0.40),
            ("M-PLMB-PIPE", self.COLOR_GREEN, "Continuous", 0.30),
            ("M-TEXT", self.COLOR_WHITE, "Continuous", 0.20),
        ]
        for name, color, ltype, lineweight in layers:
            if name not in self.doc.layers:
                layer = self.doc.layers.add(name)
                layer.color = color
                layer.linetype = ltype
                layer.lineweight = int(lineweight * 100)

    def add_rectangle(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        layer: str = "S-CONC-RC",
    ):
        """Draws a closed rectangular polyline."""
        points = [
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
            (x, y),
        ]
        self.msp.add_lwpolyline(points, dxfattribs={"layer": layer})

    def add_line(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        layer: str = "S-REBAR-BOT",
    ):
        """Draws a line segment."""
        self.msp.add_line(start, end, dxfattribs={"layer": layer})

    def add_rebar_with_90deg_hooks(
        self,
        x_start: float,
        y: float,
        x_end: float,
        hook_height: float,
        layer: str = "S-REBAR-BOT",
    ):
        """Draws a horizontal rebar with vertical 90-degree end hooks."""
        points = [
            (x_start, y + hook_height),
            (x_start, y),
            (x_end, y),
            (x_end, y + hook_height),
        ]
        self.msp.add_lwpolyline(points, dxfattribs={"layer": layer})

    def add_text(
        self,
        text: str,
        pos: Tuple[float, float],
        height: float = 25.0,
        layer: str = "S-TEXT",
        align: TextEntityAlignment = TextEntityAlignment.LEFT,
    ):
        """Draws text with specified height and alignment."""
        txt = self.msp.add_text(text, dxfattribs={"layer": layer, "height": height})
        txt.set_placement(pos, align=align)

    def add_linear_dimension(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        text_pos: Tuple[float, float],
        layer: str = "S-DIMS",
    ):
        """Adds an aligned linear dimension."""
        self.msp.add_aligned_dim(
            p1=start,
            p2=end,
            distance=20.0,
            override={"dimtad": 1, "dimtxt": 25.0, "dimclrd": self.COLOR_GREEN},
            dxfattribs={"layer": layer},
        )

    def save(self, filepath: Optional[Path] = None) -> Path:
        """Saves the drawing to disk."""
        target = Path(filepath or self.filename).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        self.doc.saveas(str(target))
        return target
