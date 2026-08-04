"""Artifact writers and readers for prepared tool-run workspaces."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from app.core.workspace import load_tool_run_manifest, normalize_tool_id, tool_run_workspace_for_module

ArtifactType = Literal["input", "output", "evidence", "log"]
_ARTIFACT_DIR_BY_TYPE: dict[ArtifactType, str] = {
    "input": "inputs",
    "output": "outputs",
    "evidence": "evidence",
    "log": "logs",
}


@dataclass(frozen=True, slots=True)
class WorkspaceArtifact:
    """Metadata for a file written into a tool-run workspace."""

    module_id: str
    tool_id: str
    run_id: str
    artifact_name: str
    artifact_type: ArtifactType
    content_type: str
    path: Path
    sha256: str
    byte_count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "module_id": self.module_id,
            "tool_id": self.tool_id,
            "run_id": self.run_id,
            "artifact_name": self.artifact_name,
            "artifact_type": self.artifact_type,
            "content_type": self.content_type,
            "path": self.path.as_posix(),
            "sha256": self.sha256,
            "byte_count": self.byte_count,
        }


def _json_bytes(payload: dict[str, Any]) -> bytes:
    """Serialize an artifact as deterministic UTF-8 JSON bytes."""
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _artifact_root(run_workspace: object, artifact_type: ArtifactType) -> Path:
    directory_name = _ARTIFACT_DIR_BY_TYPE[artifact_type]
    return Path(getattr(run_workspace, f"{directory_name[:-1]}_path")) if artifact_type != "evidence" else Path(getattr(run_workspace, "evidence_path"))


def _artifact_path(run_workspace: object, artifact_type: ArtifactType, artifact_name: str) -> Path:
    safe_name = normalize_tool_id(artifact_name)
    return _artifact_root(run_workspace, artifact_type) / f"{safe_name}.json"


def _artifact_from_file(
    module_id: str,
    tool_id: str,
    run_id: str,
    artifact_type: ArtifactType,
    path: Path,
) -> WorkspaceArtifact:
    content = path.read_bytes()
    return WorkspaceArtifact(
        module_id=module_id,
        tool_id=tool_id,
        run_id=run_id,
        artifact_name=path.stem,
        artifact_type=artifact_type,
        content_type="application/json" if path.suffix == ".json" else "application/octet-stream",
        path=path,
        sha256=hashlib.sha256(content).hexdigest(),
        byte_count=len(content),
    )


def read_tool_run_json_artifact(
    module_id: str,
    tool_id: str,
    run_id: str,
    artifact_name: str,
    artifact_type: ArtifactType,
    repo_root: Path | None = None,
) -> tuple[WorkspaceArtifact, dict[str, Any]]:
    """Read a structured JSON artifact from an existing prepared tool run."""
    load_tool_run_manifest(module_id, tool_id, run_id, repo_root=repo_root)
    run_workspace = tool_run_workspace_for_module(module_id, tool_id, run_id, repo_root=repo_root)
    artifact_path = _artifact_path(run_workspace, artifact_type, artifact_name)
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Artifact {artifact_path} must contain a JSON object.")
    return (
        _artifact_from_file(
            run_workspace.module_id,
            run_workspace.tool_id,
            run_workspace.run_id,
            artifact_type,
            artifact_path,
        ),
        payload,
    )


def write_tool_run_json_artifact(
    module_id: str,
    tool_id: str,
    run_id: str,
    artifact_name: str,
    payload: dict[str, Any],
    artifact_type: ArtifactType,
    repo_root: Path | None = None,
) -> WorkspaceArtifact:
    """Write a structured JSON artifact into an existing prepared tool run."""
    load_tool_run_manifest(module_id, tool_id, run_id, repo_root=repo_root)
    run_workspace = tool_run_workspace_for_module(module_id, tool_id, run_id, repo_root=repo_root)
    artifact_path = _artifact_path(run_workspace, artifact_type, artifact_name)
    content = _json_bytes(payload)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_bytes(content)
    return WorkspaceArtifact(
        module_id=run_workspace.module_id,
        tool_id=run_workspace.tool_id,
        run_id=run_workspace.run_id,
        artifact_name=artifact_path.stem,
        artifact_type=artifact_type,
        content_type="application/json",
        path=artifact_path,
        sha256=hashlib.sha256(content).hexdigest(),
        byte_count=len(content),
    )


def write_tool_run_input_artifact(
    module_id: str,
    tool_id: str,
    run_id: str,
    artifact_name: str,
    payload: dict[str, Any],
    repo_root: Path | None = None,
) -> WorkspaceArtifact:
    """Write a structured JSON input artifact into an existing prepared tool run."""
    return write_tool_run_json_artifact(
        module_id, tool_id, run_id, artifact_name, payload, "input", repo_root=repo_root
    )


def write_tool_run_output_artifact(
    module_id: str,
    tool_id: str,
    run_id: str,
    artifact_name: str,
    payload: dict[str, Any],
    repo_root: Path | None = None,
) -> WorkspaceArtifact:
    """Write a structured JSON output artifact into an existing prepared tool run."""
    return write_tool_run_json_artifact(
        module_id, tool_id, run_id, artifact_name, payload, "output", repo_root=repo_root
    )


def write_tool_run_evidence_artifact(
    module_id: str,
    tool_id: str,
    run_id: str,
    artifact_name: str,
    payload: dict[str, Any],
    repo_root: Path | None = None,
) -> WorkspaceArtifact:
    """Write a structured JSON evidence artifact into an existing prepared tool run."""
    return write_tool_run_json_artifact(
        module_id, tool_id, run_id, artifact_name, payload, "evidence", repo_root=repo_root
    )


def list_tool_run_artifacts(
    module_id: str,
    tool_id: str,
    run_id: str,
    repo_root: Path | None = None,
) -> tuple[WorkspaceArtifact, ...]:
    """List JSON artifacts currently present in a prepared tool-run workspace."""
    load_tool_run_manifest(module_id, tool_id, run_id, repo_root=repo_root)
    run_workspace = tool_run_workspace_for_module(module_id, tool_id, run_id, repo_root=repo_root)
    artifacts: list[WorkspaceArtifact] = []
    for artifact_type in _ARTIFACT_DIR_BY_TYPE:
        artifact_dir = _artifact_root(run_workspace, artifact_type)
        if not artifact_dir.is_dir():
            continue
        for path in sorted(artifact_dir.glob("*.json")):
            artifacts.append(
                _artifact_from_file(
                    run_workspace.module_id,
                    run_workspace.tool_id,
                    run_workspace.run_id,
                    artifact_type,
                    path,
                )
            )
    return tuple(artifacts)
