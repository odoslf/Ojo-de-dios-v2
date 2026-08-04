"""Module workspace filesystem contract tests."""

from pathlib import Path

import pytest

from app.core.module_catalog import TOTAL_MODULE_SLOTS
from app.core.workspace import (
    STANDARD_WORKSPACE_DIRS,
    WORKSPACE_MANIFEST_FILENAME,
    ensure_all_module_workspaces,
    ensure_module_workspace,
    load_workspace_manifest,
    validate_workspace_manifest,
    workspace_for_module,
)
from app.core.module_catalog import require_module_by_id


def test_ensure_module_workspace_creates_standard_directories_and_manifest(tmp_path: Path) -> None:
    workspace = ensure_module_workspace("m01_osint", repo_root=tmp_path)

    assert workspace.root_path == tmp_path / "storage" / "workspaces" / "m01_osint"
    assert workspace.manifest_path.name == WORKSPACE_MANIFEST_FILENAME
    assert workspace.manifest_path.is_file()
    assert [path.name for path in workspace.standard_dirs] == list(STANDARD_WORKSPACE_DIRS)
    assert all(path.is_dir() for path in workspace.standard_dirs)

    manifest = load_workspace_manifest("m01_osint", repo_root=tmp_path)
    assert manifest["module_id"] == "m01_osint"
    assert manifest["reserved"] is False
    assert manifest["execution_implied"] is False
    assert manifest["standard_dirs"] == list(STANDARD_WORKSPACE_DIRS)


def test_reserved_workspace_stays_reserved_and_non_executable(tmp_path: Path) -> None:
    ensure_module_workspace("m17_hackrf_sdr", repo_root=tmp_path)
    manifest = load_workspace_manifest("m17_hackrf_sdr", repo_root=tmp_path)

    assert manifest["official"] is False
    assert manifest["reserved"] is True
    assert manifest["requires_user_definition"] is True
    assert manifest["execution_implied"] is False


def test_workspace_manifest_validation_detects_drift(tmp_path: Path) -> None:
    workspace = ensure_module_workspace("m02_vulnerabilities", repo_root=tmp_path)
    validate_workspace_manifest("m02_vulnerabilities", repo_root=tmp_path)
    workspace.manifest_path.write_text('{"module_id": "m02_vulnerabilities"}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="Workspace manifest mismatch"):
        validate_workspace_manifest("m02_vulnerabilities", repo_root=tmp_path)


def test_all_module_workspaces_are_created_in_catalog_order(tmp_path: Path) -> None:
    workspaces = ensure_all_module_workspaces(repo_root=tmp_path)

    assert len(workspaces) == TOTAL_MODULE_SLOTS
    assert workspaces[0].module_id == "m01_osint"
    assert workspaces[-1].module_id == "m20_future_expansion"
    assert all(workspace.manifest_path.is_file() for workspace in workspaces)


def test_workspace_path_resolution_stays_inside_repo(tmp_path: Path) -> None:
    module = require_module_by_id("m16_ops_quality")
    workspace = workspace_for_module(module, repo_root=tmp_path)

    assert tmp_path.resolve() in workspace.root_path.resolve().parents


def test_tool_workspace_creates_isolated_tool_area_and_manifest(tmp_path: Path) -> None:
    from app.core.workspace import (
        TOOL_WORKSPACE_DIRS,
        TOOL_WORKSPACE_MANIFEST_FILENAME,
        ensure_tool_workspace,
        load_tool_workspace_manifest,
        validate_tool_workspace_manifest,
    )

    workspace = ensure_tool_workspace("m01_osint", "Nmap", repo_root=tmp_path)

    assert workspace.tool_id == "nmap"
    assert workspace.root_path == tmp_path / "storage" / "workspaces" / "m01_osint" / "tools" / "nmap"
    assert workspace.manifest_path.name == TOOL_WORKSPACE_MANIFEST_FILENAME
    assert [path.name for path in workspace.standard_dirs] == list(TOOL_WORKSPACE_DIRS)
    assert all(path.is_dir() for path in workspace.standard_dirs)
    validate_tool_workspace_manifest("m01_osint", "nmap", repo_root=tmp_path)

    manifest = load_tool_workspace_manifest("m01_osint", "nmap", repo_root=tmp_path)
    assert manifest["module_id"] == "m01_osint"
    assert manifest["tool_id"] == "nmap"
    assert manifest["approval_required"] is True
    assert manifest["execution_implied"] is False
    assert manifest["tool_run_state"] == "not_executed"


def test_tool_workspace_normalizes_common_tool_names_and_rejects_path_traversal(tmp_path: Path) -> None:
    from app.core.workspace import normalize_tool_id, tool_workspace_for_module

    assert normalize_tool_id("Have I Been Pwned") == "have-i-been-pwned"
    assert normalize_tool_id("BloodHound.py") == "bloodhound.py"
    assert normalize_tool_id("CrackMapExec / NetExec")

    with pytest.raises(ValueError, match="path traversal"):
        tool_workspace_for_module("m01_osint", "../evil", repo_root=tmp_path)
    with pytest.raises(ValueError, match="path traversal"):
        tool_workspace_for_module("m01_osint", "folder/evil", repo_root=tmp_path)


def test_tool_workspace_manifest_validation_detects_drift(tmp_path: Path) -> None:
    from app.core.workspace import ensure_tool_workspace, validate_tool_workspace_manifest

    workspace = ensure_tool_workspace("m02_vulnerabilities", "Nuclei", repo_root=tmp_path)
    workspace.manifest_path.write_text('{"module_id": "m02_vulnerabilities"}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="Tool workspace manifest mismatch"):
        validate_tool_workspace_manifest("m02_vulnerabilities", "nuclei", repo_root=tmp_path)


def test_start_tool_run_workspace_creates_prepared_run_area(tmp_path: Path) -> None:
    from app.core.workspace import (
        load_tool_run_manifest,
        start_tool_run_workspace,
        validate_tool_run_manifest,
    )

    run_workspace = start_tool_run_workspace("m01_osint", "Nmap", run_id="first-pass", repo_root=tmp_path)

    assert run_workspace.module_id == "m01_osint"
    assert run_workspace.tool_id == "nmap"
    assert run_workspace.run_id == "first-pass"
    assert run_workspace.input_path.is_dir()
    assert run_workspace.output_path.is_dir()
    assert run_workspace.log_path.is_dir()
    assert run_workspace.evidence_path.is_dir()
    assert run_workspace.tmp_path.is_dir()
    validate_tool_run_manifest("m01_osint", "nmap", "first-pass", repo_root=tmp_path)

    manifest = load_tool_run_manifest("m01_osint", "nmap", "first-pass", repo_root=tmp_path)
    assert manifest["workspace_path"] == "storage/workspaces/m01_osint/tools/nmap/tool_runs/first-pass"
    assert manifest["status"] == "prepared"
    assert manifest["execution_requested"] is False
    assert manifest["execution_implied"] is False


def test_start_tool_run_workspace_generates_unique_run_ids(tmp_path: Path) -> None:
    from app.core.workspace import start_tool_run_workspace

    first = start_tool_run_workspace("m02_vulnerabilities", "Nuclei", repo_root=tmp_path)
    second = start_tool_run_workspace("m02_vulnerabilities", "Nuclei", repo_root=tmp_path)

    assert first.run_id.startswith("run-")
    assert second.run_id.startswith("run-")
    assert first.run_id != second.run_id
    assert first.manifest_path.is_file()
    assert second.manifest_path.is_file()


def test_tool_run_manifest_validation_detects_drift(tmp_path: Path) -> None:
    from app.core.workspace import start_tool_run_workspace, validate_tool_run_manifest

    run_workspace = start_tool_run_workspace("m03_network_services", "Hydra", run_id="hydra-prep", repo_root=tmp_path)
    run_workspace.manifest_path.write_text('{"module_id": "m03_network_services"}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="Tool run manifest mismatch"):
        validate_tool_run_manifest("m03_network_services", "hydra", "hydra-prep", repo_root=tmp_path)
