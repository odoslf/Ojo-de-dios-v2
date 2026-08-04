"""Summaries for prepared tool-run workspaces."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.workspace import load_tool_run_manifest, normalize_run_id, normalize_tool_id
from app.core.workspace_artifacts import ArtifactType, WorkspaceArtifact, list_tool_run_artifacts


@dataclass(frozen=True, slots=True)
class ToolRunSummary:
    """Current manifest and artifact summary for one prepared tool run."""

    module_id: str
    tool_id: str
    run_id: str
    manifest: dict[str, object]
    artifacts: tuple[WorkspaceArtifact, ...]

    @property
    def status(self) -> str | None:
        status = self.manifest.get("status")
        return str(status) if status is not None else None

    @property
    def artifact_count(self) -> int:
        return len(self.artifacts)

    @property
    def total_artifact_bytes(self) -> int:
        return sum(artifact.byte_count for artifact in self.artifacts)

    @property
    def artifact_counts_by_type(self) -> dict[ArtifactType, int]:
        counts: dict[ArtifactType, int] = {"input": 0, "output": 0, "evidence": 0, "log": 0}
        for artifact in self.artifacts:
            counts[artifact.artifact_type] += 1
        return counts

    def to_dict(self) -> dict[str, object]:
        return {
            "module_id": self.module_id,
            "tool_id": self.tool_id,
            "run_id": self.run_id,
            "status": self.status,
            "manifest": self.manifest,
            "artifact_count": self.artifact_count,
            "artifact_counts_by_type": self.artifact_counts_by_type,
            "total_artifact_bytes": self.total_artifact_bytes,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
        }


def summarize_tool_run_workspace(
    module_id: str,
    tool_id: str,
    run_id: str,
    repo_root: Path | None = None,
) -> ToolRunSummary:
    """Return manifest and artifact summary for an existing prepared tool-run workspace."""
    manifest = load_tool_run_manifest(module_id, tool_id, run_id, repo_root=repo_root)
    normalized_tool_id = normalize_tool_id(tool_id)
    normalized_run_id = normalize_run_id(run_id)
    artifacts = list_tool_run_artifacts(module_id, normalized_tool_id, normalized_run_id, repo_root=repo_root)
    return ToolRunSummary(
        module_id=str(manifest["module_id"]),
        tool_id=normalized_tool_id,
        run_id=normalized_run_id,
        manifest=manifest,
        artifacts=artifacts,
    )
