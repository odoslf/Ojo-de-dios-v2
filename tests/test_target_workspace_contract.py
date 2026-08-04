"""Target-bound workspace contract tests."""

from pathlib import Path

import pytest

from app.core.target_model import TARGET_DOMAIN, TargetRecord
from app.core.target_workspace import (
    TARGET_MODULE_BINDING_MANIFEST_FILENAME,
    TARGET_WORKSPACE_MANIFEST_FILENAME,
    bind_target_module_workspace,
    catalog_module_ids_from_allowed_modules,
    collect_target_workspace_state,
    ensure_target_workspace,
    load_target_workspace_manifest,
    validate_target_workspace_id,
)


def _target_record() -> TargetRecord:
    return TargetRecord(
        target_id="target-001",
        name="Example",
        target_type=TARGET_DOMAIN,
        value="Example.COM",
        normalized_value="example.com",
        mode="dry_run",
        allowed_modules=["m01_osint", "external.technique.module"],
        limits={"max_runtime_seconds": 60},
    )


def test_ensure_target_workspace_creates_target_area_and_manifest(tmp_path: Path) -> None:
    target = _target_record()
    workspace = ensure_target_workspace(target, repo_root=tmp_path)

    assert workspace.root_path == tmp_path / "storage" / "targets" / "target-001"
    assert workspace.manifest_path.name == TARGET_WORKSPACE_MANIFEST_FILENAME
    assert workspace.manifest_path.is_file()
    assert all(path.is_dir() for path in workspace.standard_dirs)

    manifest = load_target_workspace_manifest(target, repo_root=tmp_path)
    assert manifest["target_id"] == "target-001"
    assert manifest["normalized_value"] == "example.com"
    assert manifest["allowed_modules"] == ["m01_osint", "external.technique.module"]
    assert manifest["execution_implied"] is False


def test_bind_target_module_workspace_links_target_and_catalog_module(tmp_path: Path) -> None:
    target = _target_record()
    binding = bind_target_module_workspace(target, "m01_osint", repo_root=tmp_path)

    assert binding.root_path == tmp_path / "storage" / "targets" / "target-001" / "modules" / "m01_osint"
    assert binding.manifest_path.name == TARGET_MODULE_BINDING_MANIFEST_FILENAME
    assert binding.manifest_path.is_file()
    assert binding.module_workspace_path == tmp_path / "storage" / "workspaces" / "m01_osint"
    assert binding.module_workspace_path.is_dir()
    assert all(path.is_dir() for path in binding.standard_dirs)

    state = collect_target_workspace_state(target, repo_root=tmp_path)
    assert state.workspace_exists is True
    assert state.manifest_exists is True
    assert state.bound_modules == ("m01_osint",)
    assert state.bound_module_count == 1


def test_catalog_module_ids_from_allowed_modules_filters_non_catalog_ids() -> None:
    assert catalog_module_ids_from_allowed_modules(["m01_osint", "osint", "m01_osint", "m16_ops_quality"]) == (
        "m01_osint",
        "m16_ops_quality",
    )


def test_target_workspace_rejects_unsafe_target_ids() -> None:
    with pytest.raises(ValueError, match="not safe"):
        validate_target_workspace_id("../evil")
