"""Workspace artifact behavior tests."""

import json
from pathlib import Path

from app.core.workspace import start_tool_run_workspace
from app.core.workspace_artifacts import read_tool_run_json_artifact, write_tool_run_input_artifact


def test_write_tool_run_input_artifact_persists_json_with_hash(tmp_path: Path) -> None:
    start_tool_run_workspace("m01_osint", "Nmap", run_id="fill-input", repo_root=tmp_path)

    artifact = write_tool_run_input_artifact(
        "m01_osint",
        "nmap",
        "fill-input",
        "target-domain",
        {"target": "example.test", "mode": "dry_run"},
        repo_root=tmp_path,
    )

    assert artifact.artifact_name == "target-domain"
    assert artifact.content_type == "application/json"
    assert artifact.byte_count > 0
    assert len(artifact.sha256) == 64
    assert artifact.path.is_file()
    assert json.loads(artifact.path.read_text(encoding="utf-8"))["target"] == "example.test"
    artifact_metadata, payload = read_tool_run_json_artifact(
        "m01_osint",
        "nmap",
        "fill-input",
        "target-domain",
        "input",
        repo_root=tmp_path,
    )
    assert payload == {"target": "example.test", "mode": "dry_run"}
    assert artifact_metadata.sha256 == artifact.sha256


def test_write_and_list_tool_run_output_and_evidence_artifacts(tmp_path: Path) -> None:
    from app.core.workspace_artifacts import (
        list_tool_run_artifacts,
        write_tool_run_evidence_artifact,
        write_tool_run_output_artifact,
    )

    start_tool_run_workspace("m02_vulnerabilities", "Nuclei", run_id="artifact-list", repo_root=tmp_path)
    output = write_tool_run_output_artifact(
        "m02_vulnerabilities",
        "nuclei",
        "artifact-list",
        "raw-findings",
        {"findings": []},
        repo_root=tmp_path,
    )
    evidence = write_tool_run_evidence_artifact(
        "m02_vulnerabilities",
        "nuclei",
        "artifact-list",
        "normalized-evidence",
        {"evidence": []},
        repo_root=tmp_path,
    )

    artifacts = list_tool_run_artifacts("m02_vulnerabilities", "nuclei", "artifact-list", repo_root=tmp_path)
    artifact_types = {artifact.artifact_type for artifact in artifacts}
    assert output.path.is_file()
    assert evidence.path.is_file()
    assert {"output", "evidence"}.issubset(artifact_types)
    assert len(artifacts) == 2
