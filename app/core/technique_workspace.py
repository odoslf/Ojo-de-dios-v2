"""Filesystem workspaces for documentation-backed module techniques."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.core.module_catalog import list_modules, require_module_by_id
from app.core.technique_catalog import ModuleTechnique, list_module_techniques
from app.core.workspace import normalize_tool_id, workspace_for_module

TECHNIQUE_WORKSPACE_SCHEMA_VERSION = 1
TECHNIQUE_WORKSPACE_MANIFEST_FILENAME = "technique_workspace_manifest.json"
TECHNIQUE_WORKSPACE_DIRS = ("inputs", "outputs", "evidence", "reports", "tmp")


@dataclass(frozen=True, slots=True)
class TechniqueWorkspace:
    """Concrete workspace paths for one documentation-backed technique."""

    module_id: str
    technique_id: str
    root_path: Path
    manifest_path: Path
    standard_dirs: tuple[Path, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "module_id": self.module_id,
            "technique_id": self.technique_id,
            "root_path": self.root_path.as_posix(),
            "manifest_path": self.manifest_path.as_posix(),
            "standard_dirs": [path.as_posix() for path in self.standard_dirs],
        }


def require_module_technique(module_id: str, technique_id: str) -> ModuleTechnique:
    """Return one documentation-backed technique or raise KeyError."""
    normalized = normalize_tool_id(technique_id)
    for technique in list_module_techniques(module_id):
        if normalize_tool_id(technique.technique_id) == normalized:
            return technique
    raise KeyError(f"Technique not found for module {module_id}: {technique_id}")


def technique_workspace_for_module(
    module_id: str,
    technique_id: str,
    repo_root: Path | None = None,
) -> TechniqueWorkspace:
    """Return technique workspace paths without creating directories."""
    module = require_module_by_id(module_id)
    technique = require_module_technique(module_id, technique_id)
    normalized_technique_id = normalize_tool_id(technique.technique_id)
    module_workspace = workspace_for_module(module, repo_root=repo_root)
    root_path = module_workspace.root_path / "techniques" / normalized_technique_id
    return TechniqueWorkspace(
        module_id=module.module_id,
        technique_id=normalized_technique_id,
        root_path=root_path,
        manifest_path=root_path / TECHNIQUE_WORKSPACE_MANIFEST_FILENAME,
        standard_dirs=tuple(root_path / dirname for dirname in TECHNIQUE_WORKSPACE_DIRS),
    )


def build_technique_workspace_manifest(module_id: str, technique_id: str) -> dict[str, object]:
    """Build a structural manifest for one documentation-backed technique workspace."""
    module = require_module_by_id(module_id)
    technique = require_module_technique(module_id, technique_id)
    normalized_technique_id = normalize_tool_id(technique.technique_id)
    return {
        "schema_version": TECHNIQUE_WORKSPACE_SCHEMA_VERSION,
        "module_number": module.module_number,
        "module_id": module.module_id,
        "technique_id": normalized_technique_id,
        "source_technique_id": technique.technique_id,
        "doc_path": technique.doc_path,
        "doc_line_number": technique.line_number,
        "workspace_path": f"{module.workspace_path}/techniques/{normalized_technique_id}",
        "standard_dirs": list(TECHNIQUE_WORKSPACE_DIRS),
        "approval_required": True,
        "execution_implied": False,
        "technique_state": "catalog_only_not_executed",
        "user_data_boundary": "module_technique_workspace",
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
    }


def ensure_technique_workspace(
    module_id: str,
    technique_id: str,
    repo_root: Path | None = None,
) -> TechniqueWorkspace:
    """Create and persist a technique workspace manifest without executing the technique."""
    workspace = technique_workspace_for_module(module_id, technique_id, repo_root=repo_root)
    workspace.root_path.mkdir(parents=True, exist_ok=True)
    for directory in workspace.standard_dirs:
        directory.mkdir(parents=True, exist_ok=True)
    manifest = build_technique_workspace_manifest(module_id, technique_id)
    workspace.manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return workspace


def ensure_module_technique_workspaces(
    module_id: str,
    repo_root: Path | None = None,
) -> tuple[TechniqueWorkspace, ...]:
    """Create workspaces for every documented technique in one module."""
    require_module_by_id(module_id)
    workspaces: list[TechniqueWorkspace] = []
    for technique in list_module_techniques(module_id):
        workspaces.append(
            ensure_technique_workspace(
                module_id=module_id,
                technique_id=technique.technique_id,
                repo_root=repo_root,
            )
        )
    return tuple(workspaces)


def ensure_all_technique_workspaces(
    include_reserved: bool = False,
    repo_root: Path | None = None,
) -> dict[str, object]:
    """Create workspaces for every documented technique in catalog order."""
    module_summaries: list[dict[str, object]] = []
    total = 0
    for module in list_modules(include_reserved=include_reserved):
        workspaces = ensure_module_technique_workspaces(module.module_id, repo_root=repo_root) if module.doc_path else ()
        total += len(workspaces)
        module_summaries.append(
            {
                "module_id": module.module_id,
                "reserved": module.reserved,
                "workspace_count": len(workspaces),
                "workspaces": [workspace.to_dict() for workspace in workspaces],
            }
        )
    return {
        "include_reserved": include_reserved,
        "module_count": len(module_summaries),
        "workspace_count": total,
        "modules": module_summaries,
        "execution_implied": False,
    }


def read_technique_workspace_manifest(
    module_id: str,
    technique_id: str,
    repo_root: Path | None = None,
) -> dict[str, object]:
    """Read one persisted technique workspace manifest."""
    workspace = technique_workspace_for_module(module_id, technique_id, repo_root=repo_root)
    return json.loads(workspace.manifest_path.read_text(encoding="utf-8"))


def inspect_technique_workspace(
    module_id: str,
    technique_id: str,
    repo_root: Path | None = None,
) -> dict[str, object]:
    """Inspect technique workspace filesystem state without creating or executing anything."""
    workspace = technique_workspace_for_module(module_id, technique_id, repo_root=repo_root)
    manifest: dict[str, object] | None = None
    if workspace.manifest_path.is_file():
        manifest = read_technique_workspace_manifest(module_id, technique_id, repo_root=repo_root)
    return {
        "workspace": workspace.to_dict(),
        "exists": workspace.root_path.is_dir(),
        "manifest_exists": workspace.manifest_path.is_file(),
        "standard_dirs": [
            {"path": path.as_posix(), "exists": path.is_dir()}
            for path in workspace.standard_dirs
        ],
        "manifest": manifest,
        "execution_implied": False,
    }

_TECHNIQUE_ARTIFACT_DIR_BY_TYPE: dict[str, str] = {
    "input": "inputs",
    "output": "outputs",
    "evidence": "evidence",
    "report": "reports",
}


@dataclass(frozen=True, slots=True)
class TechniqueWorkspaceArtifact:
    """Metadata for a JSON artifact stored in a technique workspace."""

    module_id: str
    technique_id: str
    artifact_name: str
    artifact_type: str
    path: Path
    sha256: str
    byte_count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "module_id": self.module_id,
            "technique_id": self.technique_id,
            "artifact_name": self.artifact_name,
            "artifact_type": self.artifact_type,
            "path": self.path.as_posix(),
            "sha256": self.sha256,
            "byte_count": self.byte_count,
        }


def _technique_artifact_path(workspace: TechniqueWorkspace, artifact_type: str, artifact_name: str) -> Path:
    if artifact_type not in _TECHNIQUE_ARTIFACT_DIR_BY_TYPE:
        raise ValueError(f"Unsupported technique artifact type: {artifact_type}.")
    safe_name = normalize_tool_id(artifact_name)
    return workspace.root_path / _TECHNIQUE_ARTIFACT_DIR_BY_TYPE[artifact_type] / f"{safe_name}.json"


def _technique_artifact_from_path(
    workspace: TechniqueWorkspace,
    artifact_type: str,
    path: Path,
) -> TechniqueWorkspaceArtifact:
    return TechniqueWorkspaceArtifact(
        module_id=workspace.module_id,
        technique_id=workspace.technique_id,
        artifact_name=path.stem,
        artifact_type=artifact_type,
        path=path,
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        byte_count=len(path.read_bytes()),
    )


def write_technique_workspace_json_artifact(
    module_id: str,
    technique_id: str,
    artifact_name: str,
    artifact_type: str,
    payload: dict[str, object],
    repo_root: Path | None = None,
) -> TechniqueWorkspaceArtifact:
    """Write a JSON artifact into an existing technique workspace."""
    read_technique_workspace_manifest(module_id, technique_id, repo_root=repo_root)
    workspace = technique_workspace_for_module(module_id, technique_id, repo_root=repo_root)
    path = _technique_artifact_path(workspace, artifact_type, artifact_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return _technique_artifact_from_path(workspace, artifact_type, path)


def read_technique_workspace_json_artifact(
    module_id: str,
    technique_id: str,
    artifact_name: str,
    artifact_type: str,
    repo_root: Path | None = None,
) -> tuple[TechniqueWorkspaceArtifact, dict[str, object]]:
    """Read a JSON artifact from an existing technique workspace."""
    read_technique_workspace_manifest(module_id, technique_id, repo_root=repo_root)
    workspace = technique_workspace_for_module(module_id, technique_id, repo_root=repo_root)
    path = _technique_artifact_path(workspace, artifact_type, artifact_name)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Technique artifact {path} must contain a JSON object.")
    return _technique_artifact_from_path(workspace, artifact_type, path), payload


def list_technique_workspace_artifacts(
    module_id: str,
    technique_id: str,
    repo_root: Path | None = None,
) -> tuple[TechniqueWorkspaceArtifact, ...]:
    """List JSON artifacts present in an existing technique workspace."""
    read_technique_workspace_manifest(module_id, technique_id, repo_root=repo_root)
    workspace = technique_workspace_for_module(module_id, technique_id, repo_root=repo_root)
    artifacts: list[TechniqueWorkspaceArtifact] = []
    for artifact_type, dirname in _TECHNIQUE_ARTIFACT_DIR_BY_TYPE.items():
        directory = workspace.root_path / dirname
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            artifacts.append(_technique_artifact_from_path(workspace, artifact_type, path))
    return tuple(artifacts)
