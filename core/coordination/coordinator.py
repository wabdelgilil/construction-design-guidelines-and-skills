"""
Cross-Discipline Interface & Coordination Coordinator.
Prevents knowledge loss, missed electrical feeds, forgotten pipe sleeves,
and MEP/Structural clashes across engineering disciplines.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class DisciplineCoordinator:
    """Queries and manages cross-discipline interfaces and requirements."""

    def __init__(self, registry_path: Optional[Path] = None):
        if registry_path is None:
            self.registry_path = Path(__file__).resolve().parent / "interface_registry.json"
        else:
            self.registry_path = Path(registry_path).resolve()

        self._registry = self._load_json(self.registry_path)

    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        if not file_path.is_file():
            return {"interfaces": []}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load coordination registry {file_path}: {e}")

    def query_interfaces(
        self, target_discipline: str, keywords: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all cross-discipline requirements that target_discipline must provide.
        Optionally filters by keyword matching.
        """
        results = []
        target_norm = target_discipline.lower().strip()
        search_keys = [k.lower().strip() for k in keywords] if keywords else []

        for item in self._registry.get("interfaces", []):
            item_target = item.get("target_discipline", "").lower()
            if target_norm in item_target or item_target in target_norm:
                if not search_keys:
                    results.append(item)
                else:
                    item_keys = [k.lower() for k in item.get("target_keywords", [])]
                    item_title = item.get("title", "").lower()
                    item_desc = item.get("requirement_for_target", "").lower()
                    # Check match
                    matched = any(
                        sk in item_keys or sk in item_title or sk in item_desc
                        for sk in search_keys
                    )
                    if matched:
                        results.append(item)

        return results

    def generate_coordination_checklist(
        self, target_discipline: str, keywords: Optional[List[str]] = None
    ) -> str:
        """Generates a formatted Markdown checklist of cross-discipline dependencies."""
        interfaces = self.query_interfaces(target_discipline, keywords)
        if not interfaces:
            return "✅ No pending cross-discipline interface constraints found."

        lines = [
            "### ⚠️ Cross-Discipline Coordination Checklist",
            f"*The following requirements from other disciplines must be accommodated in **{target_discipline}**:*",
            "",
        ]

        for item in interfaces:
            ref_id = item.get("id", "INT")
            src = item.get("source_discipline", "")
            title = item.get("title", "")
            req = item.get("requirement_for_target", "")
            code = item.get("code_reference", "")

            lines.append(f"- [ ] **[{ref_id}] {title}** *(Source: `{src}` | Code: `{code}`)*")
            lines.append(f"  - **Requirement**: {req}")

        return "\n".join(lines)


# Singleton module instance
coordinator = DisciplineCoordinator()
