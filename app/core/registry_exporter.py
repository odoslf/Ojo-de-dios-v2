"""Technique registry export helpers."""

import json
from pathlib import Path
from typing import Any

from app.core.technique_registry import TechniqueRegistry


def registry_metadata_to_json_text(registry: TechniqueRegistry) -> str:
    """Return registry metadata as stable JSON text."""
    return json.dumps(
        registry.to_metadata_list(),
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )


def _yaml_scalar(value: Any) -> str:
    if isinstance(value, str):
        return value if value else '""'
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def registry_metadata_to_yaml_text(registry: TechniqueRegistry) -> str:
    """Return registry metadata as simple stable YAML text without PyYAML."""
    lines: list[str] = []
    for item in registry.to_metadata_list():
        first = True
        for key, value in item.items():
            prefix = "-" if first else " "
            first = False
            if isinstance(value, list):
                if not value:
                    lines.append(f"{prefix} {key}: []")
                else:
                    lines.append(f"{prefix} {key}:")
                    for entry in value:
                        lines.append(f"  - {_yaml_scalar(entry)}")
            else:
                lines.append(f"{prefix} {key}: {_yaml_scalar(value)}")
    return "\n".join(lines) + ("\n" if lines else "")


def export_registry_json(registry: TechniqueRegistry, output_path: str | Path) -> Path:
    """Write registry metadata JSON to a UTF-8 file and return its path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(registry_metadata_to_json_text(registry), encoding="utf-8")
    return path


def export_registry_yaml(registry: TechniqueRegistry, output_path: str | Path) -> Path:
    """Write registry metadata YAML to a UTF-8 file and return its path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(registry_metadata_to_yaml_text(registry), encoding="utf-8")
    return path
