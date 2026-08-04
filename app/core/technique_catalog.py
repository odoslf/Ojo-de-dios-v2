"""Documentation-backed technique catalog extraction.

The technique catalog is intentionally read-only and documentation-backed. It
parses the official ``docs/techniques`` markdown files linked by the module
catalog and exposes declared technique identifiers plus simple metadata without
executing tools or implying implementation readiness.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.module_catalog import ModuleCatalogEntry, get_module_by_id, list_modules

TECHNIQUE_CATALOG_SCHEMA_VERSION = 1
_TECHNIQUE_HEADING_RE = re.compile(r"^#{3,6}\s+(?:\d+[.)]\s+)?(?P<tech>[a-z][a-z0-9_]*(?:[.-][a-z0-9_]+)+)\s*$")
_TECHNIQUE_BULLET_RE = re.compile(r"^-\s+`(?P<tech>[a-z][a-z0-9_]*(?:[.-][a-z0-9_]+)+)`(?P<title>.*)$")
_METADATA_RE = re.compile(r"^(?P<key>[a-zA-Z_][a-zA-Z0-9_ -]{1,48}):\s*(?P<value>.+)$")
_LIST_HEADER_RE = re.compile(r"^(?P<key>[a-zA-Z_][a-zA-Z0-9_ -]{1,48}):\s*$")
_LIST_ITEM_RE = re.compile(r"^-\s+(?P<value>[^`].+)$")


@dataclass(frozen=True, slots=True)
class ModuleTechnique:
    """One documentation-declared technique entry."""

    technique_id: str
    module_id: str
    catalog_module_id: str
    title: str
    doc_path: str
    line_number: int
    source: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "technique_id": self.technique_id,
            "module_id": self.module_id,
            "catalog_module_id": self.catalog_module_id,
            "title": self.title,
            "doc_path": self.doc_path,
            "line_number": self.line_number,
            "source": self.source,
            "metadata": self.metadata,
            "execution_implied": False,
        }


def _repo_path(repo_root: Path | None = None) -> Path:
    return (Path.cwd() if repo_root is None else Path(repo_root)).resolve()


def _read_doc_lines(module: ModuleCatalogEntry, repo_root: Path | None = None) -> tuple[Path, list[str]]:
    if module.doc_path is None:
        return _repo_path(repo_root), []
    root = _repo_path(repo_root)
    path = (root / module.doc_path).resolve()
    if root != path and root not in path.parents:
        raise ValueError(f"Technique document escapes repository root: {module.doc_path}.")
    if not path.is_file():
        return path, []
    return path, path.read_text(encoding="utf-8").splitlines()


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace(" ", "_").replace("-", "_")


def _parse_inline_value(value: str) -> Any:
    raw = value.strip().strip("`")
    if "," in raw:
        parts = [part.strip().strip("`") for part in raw.split(",") if part.strip()]
        if len(parts) > 1:
            return parts
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    return raw


def _collect_base_metadata(lines: list[str]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    active_list_key: str | None = None
    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("### ") and "base" not in line.lower() and metadata:
            break
        list_header = _LIST_HEADER_RE.match(line)
        if list_header:
            active_list_key = _normalize_key(list_header.group("key"))
            metadata.setdefault(active_list_key, [])
            continue
        if active_list_key:
            item = _LIST_ITEM_RE.match(line)
            if item:
                current = metadata.setdefault(active_list_key, [])
                if isinstance(current, list):
                    current.append(item.group("value").strip().strip("`"))
                continue
            if line and not line.startswith("-"):
                active_list_key = None
        field = _METADATA_RE.match(line)
        if field:
            metadata[_normalize_key(field.group("key"))] = _parse_inline_value(field.group("value"))
    return metadata


def _collect_technique_metadata(lines: list[str], start_index: int) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for raw_line in lines[start_index + 1 :]:
        line = raw_line.strip()
        if line.startswith("###") or _TECHNIQUE_BULLET_RE.match(line):
            break
        field = _METADATA_RE.match(line)
        if field:
            metadata[_normalize_key(field.group("key"))] = _parse_inline_value(field.group("value"))
    return metadata


def _extract_techniques(module: ModuleCatalogEntry, doc_path: Path, lines: list[str]) -> tuple[ModuleTechnique, ...]:
    base_metadata = _collect_base_metadata(lines)
    declared_module_id = str(base_metadata.get("module_id") or module.slug)
    techniques: list[ModuleTechnique] = []
    seen: set[str] = set()
    for index, raw_line in enumerate(lines):
        line = raw_line.strip()
        heading = _TECHNIQUE_HEADING_RE.match(line)
        bullet = _TECHNIQUE_BULLET_RE.match(line)
        match = heading or bullet
        if not match:
            continue
        technique_id = match.group("tech").strip()
        if technique_id in seen:
            continue
        seen.add(technique_id)
        title = technique_id
        if bullet:
            suffix = bullet.group("title").strip(" :-–—")
            title = suffix or technique_id
        metadata = _collect_technique_metadata(lines, index) if heading else {}
        techniques.append(
            ModuleTechnique(
                technique_id=technique_id,
                module_id=declared_module_id,
                catalog_module_id=module.module_id,
                title=title,
                doc_path=module.doc_path or doc_path.as_posix(),
                line_number=index + 1,
                source="docs/techniques",
                metadata=metadata,
            )
        )
    return tuple(techniques)


def list_module_techniques(module_id: str, repo_root: Path | None = None) -> tuple[ModuleTechnique, ...]:
    """Return documentation-declared techniques for one catalog module."""
    module = get_module_by_id(module_id)
    if module is None:
        raise KeyError(module_id)
    doc_path, lines = _read_doc_lines(module, repo_root=repo_root)
    if not lines:
        return ()
    return _extract_techniques(module, doc_path, lines)


def summarize_module_techniques(include_reserved: bool = False, repo_root: Path | None = None) -> dict[str, Any]:
    """Return aggregate technique counts for catalog modules."""
    modules = list_modules(include_reserved=include_reserved)
    module_counts: dict[str, int] = {}
    total = 0
    for module in modules:
        count = len(list_module_techniques(module.module_id, repo_root=repo_root)) if module.doc_path else 0
        module_counts[module.module_id] = count
        total += count
    return {
        "schema_version": TECHNIQUE_CATALOG_SCHEMA_VERSION,
        "include_reserved": include_reserved,
        "module_counts": module_counts,
        "total_techniques": total,
        "execution_implied": False,
    }
