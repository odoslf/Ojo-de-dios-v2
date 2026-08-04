"""Technique workspace contract tests."""

from pathlib import Path

from app.core.technique_workspace import (
    ensure_all_technique_workspaces,
    ensure_module_technique_workspaces,
    ensure_technique_workspace,
    inspect_technique_workspace,
    list_technique_workspace_artifacts,
    read_technique_workspace_json_artifact,
    read_technique_workspace_manifest,
    require_module_technique,
    technique_workspace_for_module,
    write_technique_workspace_json_artifact,
)


def test_require_module_technique_reads_documented_technique() -> None:
    technique = require_module_technique("m07_post_exploitation", "post.c2.havoc_deploy")

    assert technique.technique_id == "post.c2.havoc_deploy"
    assert technique.metadata["worker"] == "C2Worker"


def test_ensure_technique_workspace_persists_non_executing_manifest(tmp_path: Path) -> None:
    workspace = ensure_technique_workspace(
        "m07_post_exploitation",
        "post.c2.havoc_deploy",
        repo_root=tmp_path,
    )
    expected = technique_workspace_for_module(
        "m07_post_exploitation",
        "post.c2.havoc_deploy",
        repo_root=tmp_path,
    )

    assert workspace.root_path == expected.root_path
    assert workspace.manifest_path.is_file()
    assert all(path.is_dir() for path in workspace.standard_dirs)
    manifest = read_technique_workspace_manifest(
        "m07_post_exploitation",
        "post.c2.havoc_deploy",
        repo_root=tmp_path,
    )
    state = inspect_technique_workspace(
        "m07_post_exploitation",
        "post.c2.havoc_deploy",
        repo_root=tmp_path,
    )
    assert manifest["source_technique_id"] == "post.c2.havoc_deploy"
    assert manifest["execution_implied"] is False
    assert manifest["technique_state"] == "catalog_only_not_executed"
    assert state["exists"] is True
    assert state["manifest_exists"] is True
    assert state["manifest"] == manifest


def test_ensure_module_technique_workspaces_creates_every_documented_workspace(tmp_path: Path) -> None:
    workspaces = ensure_module_technique_workspaces("m07_post_exploitation", repo_root=tmp_path)
    technique_ids = {workspace.technique_id for workspace in workspaces}

    assert "post.c2.havoc_deploy" in technique_ids
    assert len(workspaces) >= 1
    assert all(workspace.manifest_path.is_file() for workspace in workspaces)
    assert all(path.is_dir() for workspace in workspaces for path in workspace.standard_dirs)


def test_ensure_all_technique_workspaces_preserves_catalog_scope(tmp_path: Path) -> None:
    summary = ensure_all_technique_workspaces(include_reserved=False, repo_root=tmp_path)

    assert summary["include_reserved"] is False
    assert summary["workspace_count"] > 0
    assert summary["execution_implied"] is False
    module_counts = {module["module_id"]: module["workspace_count"] for module in summary["modules"]}
    assert module_counts["m07_post_exploitation"] >= 1
    assert "m17_hackrf_sdr" not in module_counts


def test_technique_workspace_json_artifacts_roundtrip(tmp_path: Path) -> None:
    ensure_technique_workspace("m07_post_exploitation", "post.c2.havoc_deploy", repo_root=tmp_path)

    artifact = write_technique_workspace_json_artifact(
        "m07_post_exploitation",
        "post.c2.havoc_deploy",
        artifact_name="operator-plan",
        artifact_type="input",
        payload={"scope": "lab", "execute": False},
        repo_root=tmp_path,
    )
    recovered, payload = read_technique_workspace_json_artifact(
        "m07_post_exploitation",
        "post.c2.havoc_deploy",
        artifact_name="operator-plan",
        artifact_type="input",
        repo_root=tmp_path,
    )
    artifacts = list_technique_workspace_artifacts(
        "m07_post_exploitation", "post.c2.havoc_deploy", repo_root=tmp_path
    )

    assert artifact.path.is_file()
    assert recovered.sha256 == artifact.sha256
    assert payload == {"scope": "lab", "execute": False}
    assert [item.artifact_name for item in artifacts] == ["operator-plan"]
