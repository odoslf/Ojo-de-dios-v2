"""Common target-module run result envelope for persisted module artifacts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class TargetModuleRunResult:
    """Standard result envelope shared by target-scoped module write flows."""

    target_id: str
    module_id: str
    run_type: str
    status: str
    artifact_path: Path
    report_path: Path | None = None
    finding_count: int = 0
    execution_scope: str = "target_module_workspace_artifact"
    artifact_sha256: str | None = None
    recorded_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    summary: dict[str, object] = field(default_factory=dict)
    flags: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        """Return the result in the same shape expected by target-module APIs."""
        return {
            "target_id": self.target_id,
            "module_id": self.module_id,
            "run_type": self.run_type,
            "status": self.status,
            "artifact_path": self.artifact_path.as_posix(),
            "report_path": self.report_path.as_posix() if self.report_path else None,
            "finding_count": self.finding_count,
            "execution_scope": self.execution_scope,
            "artifact_sha256": self.artifact_sha256,
            "recorded_at": self.recorded_at,
            "summary": self.summary,
            "flags": self.flags,
        }


def _hash_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_summary(path: Path, payload: dict[str, Any] | None = None) -> dict[str, object]:
    source = payload
    if source is None and path.is_file():
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            parsed = None
        if isinstance(parsed, dict):
            source = parsed
    if not isinstance(source, dict):
        return {}
    summary: dict[str, object] = {}
    for key in (
        "schema_version",
        "input_service_count",
        "service_count",
        "input_observation_count",
        "deduplicated_device_count",
        "input_asset_count",
        "deduplicated_asset_count",
        "receipt_id",
        "campaign_id",
    ):
        if key in source:
            summary[key] = source[key]
    nested_summary = source.get("summary")
    if isinstance(nested_summary, dict):
        summary["summary"] = nested_summary
    return summary


def build_target_module_run_result(
    *,
    target_id: str,
    module_id: str,
    run_type: str,
    artifact_path: Path | str,
    status: str = "artifact_persisted",
    report_path: Path | str | None = None,
    finding_count: int = 0,
    execution_scope: str = "target_module_workspace_artifact",
    payload: dict[str, Any] | None = None,
    flags: dict[str, object] | None = None,
) -> TargetModuleRunResult:
    """Build a deterministic result envelope from a real artifact path."""
    artifact = Path(artifact_path)
    return TargetModuleRunResult(
        target_id=target_id,
        module_id=module_id,
        run_type=run_type,
        status=status,
        artifact_path=artifact,
        report_path=Path(report_path) if report_path else None,
        finding_count=max(int(finding_count), 0),
        execution_scope=execution_scope,
        artifact_sha256=_hash_file(artifact),
        summary=_json_summary(artifact, payload=payload),
        flags=dict(flags or {}),
    )
