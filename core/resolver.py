"""
Hierarchical Context & Code Resolver Engine.

Provides deterministic context resolution along the engineering tree:
Root (project_root.json) -> Discipline Parent (rules.json) -> Sub-branch (rules.json) -> Leaf (rules.json).
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class TreeResolver:
    """Resolves inherited rules and code-specific parameters along the tree path."""

    def __init__(self, workspace_root: Optional[Path] = None):
        if workspace_root is None:
            # Assume workspace root is the parent of 'core' directory
            self.workspace_root = Path(__file__).resolve().parent.parent
        else:
            self.workspace_root = Path(workspace_root).resolve()

        self.root_config_path = self.workspace_root / "project_root.json"
        self._root_config = self._load_json(self.root_config_path)

    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Safely load and parse a JSON file."""
        if not file_path.is_file():
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to parse JSON file {file_path}: {e}")

    @property
    def default_code(self) -> str:
        """Returns the active code declared in project_root.json."""
        return self._root_config.get("active_code", "SBC")

    def get_project_root_config(self) -> Dict[str, Any]:
        """Returns the full project_root.json dictionary."""
        return dict(self._root_config)

    def resolve_context(
        self, relative_path: str, code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Traverse from the workspace root down the specified relative_path.
        At each step, if 'rules.json' is found, extracts parameters matching
        the specified code (or root active_code) and merges them down.

        Example:
            resolve_context("structural/foundations/isolated_footing", code="SBC")
        """
        active_code = code or self.default_code
        resolved: Dict[str, Any] = {
            "active_code": active_code,
            "unit_system": self._root_config.get("unit_system", "SI"),
            "project_metadata": self._root_config.get("project_metadata", {}),
            "hierarchy_path": [],
            "rules": {},
        }

        # Normalize relative path into directory segments
        clean_path = Path(relative_path).as_posix().strip("/")
        segments = clean_path.split("/") if clean_path else []

        current_dir = self.workspace_root

        for seg in segments:
            current_dir = current_dir / seg
            resolved["hierarchy_path"].append(seg)
            rules_file = current_dir / "rules.json"

            if rules_file.is_file():
                rules_data = self._load_json(rules_file)
                # Check if rules are partitioned by code
                if "codes" in rules_data and active_code in rules_data["codes"]:
                    code_rules = rules_data["codes"][active_code]
                    resolved["rules"].update(code_rules)
                elif active_code in rules_data:
                    # Alternative flat mapping: { "SBC": {...}, "ECP": {...} }
                    resolved["rules"].update(rules_data[active_code])
                else:
                    # General parameters without code partitioning
                    filtered = {
                        k: v for k, v in rules_data.items() if k not in ("codes", "discipline", "level")
                    }
                    resolved["rules"].update(filtered)

        return resolved


# Convenience module-level instance
resolver = TreeResolver()
