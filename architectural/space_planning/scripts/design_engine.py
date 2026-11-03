"""
Deterministic Architectural Space Planning & Room Matrix Compliance Engine.
Audits room dimensions, areas, heights, and glazing ratios against building typology codes.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RoomDefinition:
    tag: str
    name: str
    space_type: str
    length_m: float
    width_m: float
    height_m: float = 3.0
    glazing_area_m2: float = 2.0


@dataclass
class RoomComplianceReport:
    tag: str
    name: str
    space_type: str
    length_m: float
    width_m: float
    height_m: float
    area_m2: float
    glazing_ratio: float
    min_area_required_m2: float
    min_width_required_m: float
    min_height_required_m: float
    area_pass: bool
    width_pass: bool
    height_pass: bool
    glazing_pass: bool
    overall_status: str


@dataclass
class ProjectSpaceAuditResult:
    project_name: str
    building_typology: str
    code_used: str
    total_gross_area_m2: float
    total_habitable_area_m2: float
    rooms_audited: List[RoomComplianceReport]
    all_rooms_pass: bool
    mep_recommendations: List[str] = field(default_factory=list)


class SpacePlanningEngine:
    """Evaluates architectural spaces against code minimums."""

    def __init__(self, typology: str = "residential", code: str = "SBC"):
        self.typology = typology
        self.code = code

    def audit_spaces(
        self,
        project_name: str,
        rooms: List[RoomDefinition],
        code_rules: Dict[str, Dict[str, float]],
    ) -> ProjectSpaceAuditResult:
        reports = []
        total_gross = 0.0
        total_habitable = 0.0
        all_pass = True

        for r in rooms:
            area = round(r.length_m * r.width_m, 2)
            total_gross += area

            narrowest_dim = min(r.length_m, r.width_m)
            glazing_ratio = round(r.glazing_area_m2 / max(area, 0.1), 3)

            # Get code requirements for this space type
            req = code_rules.get(r.space_type, {})
            min_area = req.get("min_area_m2", 9.0)
            min_width = req.get("min_width_m", 2.4)
            min_height = req.get("min_height_m", 2.8)
            min_glazing = req.get("min_glazing_ratio", 0.08)

            area_pass = area >= min_area
            width_pass = narrowest_dim >= min_width
            height_pass = r.height_m >= min_height
            glazing_pass = glazing_ratio >= min_glazing if min_glazing > 0 else True

            is_ok = area_pass and width_pass and height_pass and glazing_pass
            if not is_ok:
                all_pass = False

            if "bedroom" in r.space_type or "living" in r.space_type or "office" in r.space_type:
                total_habitable += area

            reports.append(
                RoomComplianceReport(
                    tag=r.tag,
                    name=r.name,
                    space_type=r.space_type,
                    length_m=r.length_m,
                    width_m=r.width_m,
                    height_m=r.height_m,
                    area_m2=area,
                    glazing_ratio=glazing_ratio,
                    min_area_required_m2=min_area,
                    min_width_required_m=min_width,
                    min_height_required_m=min_height,
                    area_pass=area_pass,
                    width_pass=width_pass,
                    height_pass=height_pass,
                    glazing_pass=glazing_pass,
                    overall_status="COMPLIANT" if is_ok else "NON-COMPLIANT",
                )
            )

        mep_recs = [
            f"Electrical Lighting Feed: Total {len(rooms)} spaces require minimum 1 lighting branch circuit per 60m² gross area.",
            f"HVAC Thermal Sizing: Total gross area {total_gross:.1f} m² requires approx. {round(total_gross / 18.0, 1)} TR total diversified cooling capacity.",
            "Plumbing Wet Areas: Verify sanitary drainage slopes and pipe sleeve coordinates for all bathrooms and kitchens.",
        ]

        return ProjectSpaceAuditResult(
            project_name=project_name,
            building_typology=self.typology,
            code_used=self.code,
            total_gross_area_m2=round(total_gross, 2),
            total_habitable_area_m2=round(total_habitable, 2),
            rooms_audited=reports,
            all_rooms_pass=all_pass,
            mep_recommendations=mep_recs,
        )
