"""Filesystem-backed module manifest registry.

This registry validates that the physical module workspace skeleton matches the
product-level module catalog. It does not register executable techniques and it
does not imply that a module can run tools.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.core.module_catalog import ModuleCatalogEntry, list_modules, require_module_by_id

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULES_ROOT = REPO_ROOT / "app" / "modules"
MANIFEST_FILENAME = "module_manifest.json"
MANIFEST_SCHEMA_VERSION = 1


class ModuleManifestError(ValueError):
    """Raised when a physical module manifest contradicts the catalog."""


def manifest_path_for(module: ModuleCatalogEntry) -> Path:
    """Return the absolute manifest path for a catalog module."""
    return REPO_ROOT / module.manifest_path


def workspace_path_for(module: ModuleCatalogEntry) -> Path:
    """Return the absolute workspace path declared for a catalog module."""
    return REPO_ROOT / module.workspace_path


def load_module_manifest(module_id: str) -> dict[str, Any]:
    """Load one module manifest by catalog module id."""
    module = require_module_by_id(module_id)
    manifest_path = manifest_path_for(module)
    if not manifest_path.exists():
        raise ModuleManifestError(f"Missing module manifest: {manifest_path}.")
    try:
        loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ModuleManifestError(f"Invalid JSON in module manifest: {manifest_path}.") from error
    if not isinstance(loaded, dict):
        raise ModuleManifestError(f"Module manifest must be a JSON object: {manifest_path}.")
    return loaded


def validate_module_manifest(module: ModuleCatalogEntry, manifest: dict[str, Any]) -> None:
    """Validate one physical manifest against its authoritative catalog entry."""
    expected_values: dict[str, Any] = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "module_number": module.module_number,
        "module_id": module.module_id,
        "slug": module.slug,
        "display_name": module.display_name,
        "lifecycle": module.lifecycle,
        "readiness": module.readiness,
        "official": module.official,
        "reserved": module.reserved,
        "requires_user_definition": module.requires_user_definition,
        "doc_path": module.doc_path,
        "workspace_path": module.workspace_path,
    }
    for field_name, expected_value in expected_values.items():
        if manifest.get(field_name) != expected_value:
            raise ModuleManifestError(
                f"Manifest mismatch for {module.module_id}.{field_name}: "
                f"expected {expected_value!r}, got {manifest.get(field_name)!r}."
            )
    notes = manifest.get("notes")
    if not isinstance(notes, list):
        raise ModuleManifestError(f"Manifest notes must be a list for {module.module_id}.")
    if notes != list(module.notes):
        raise ModuleManifestError(f"Manifest notes mismatch for {module.module_id}.")


def validate_all_module_manifests() -> tuple[str, ...]:
    """Validate every physical module manifest and return module ids in order."""
    validated_module_ids: list[str] = []
    for module in list_modules(include_reserved=True):
        manifest = load_module_manifest(module.module_id)
        validate_module_manifest(module, manifest)
        validated_module_ids.append(module.module_id)
    return tuple(validated_module_ids)


def load_all_module_manifests() -> tuple[dict[str, Any], ...]:
    """Load and validate all physical module manifests in catalog order."""
    manifests: list[dict[str, Any]] = []
    for module in list_modules(include_reserved=True):
        manifest = load_module_manifest(module.module_id)
        validate_module_manifest(module, manifest)
        manifests.append(manifest)
    return tuple(manifests)
