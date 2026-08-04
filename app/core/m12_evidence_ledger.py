"""M12 cross-module evidence ledger built from target workspace artifacts."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.module_catalog import list_modules
from app.core.target_model import TargetRecord
from app.core.target_workspace import bind_target_module_workspace, target_workspace_for_record

M12_MODULE_ID = "m12_orchestration"
MAX_LEDGER_ARTIFACTS = 2_000
_EXCLUDED_PARTS = {"tmp", "ai_reviews"}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stored_evidence_ledger_entry(item: dict[str, Any]) -> dict[str, object]:
    return {
        "record_type": "evidence_store_record",
        "module_id": str(item.get("module_id") or ""),
        "evidence_id": str(item.get("evidence_id") or ""),
        "run_id": str(item.get("run_id") or ""),
        "technique_id": str(item.get("technique_id") or ""),
        "evidence_type": str(item.get("evidence_type") or ""),
        "quality": str(item.get("quality") or ""),
        "summary": str(item.get("summary") or ""),
        "content_hash": str(item.get("content_hash") or ""),
        "content_path": str(item.get("content_path") or ""),
        "content_hash_verified": bool(item.get("content_hash_verified")),
        "content_read_status": str(item.get("content_read_status") or "not_checked"),
        "content_read_error": item.get("content_read_error"),
        "created_at": str(item.get("created_at") or ""),
    }


def build_m12_evidence_ledger(
    target: TargetRecord,
    repo_root: Path | None = None,
    stored_evidence: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
) -> dict[str, object]:
    """Index actual persisted artifacts from M01–M11 without interpreting or executing them."""
    root = Path.cwd() if repo_root is None else repo_root
    workspace = target_workspace_for_record(target, repo_root=root)
    artifacts: list[dict[str, object]] = []
    by_module: dict[str, int] = {}
    stored_evidence_count = 0
    unverified_stored_evidence_count = 0
    for item in stored_evidence or ():
        if len(artifacts) >= MAX_LEDGER_ARTIFACTS:
            break
        entry = _stored_evidence_ledger_entry(dict(item))
        module_id = str(entry["module_id"])
        if module_id == M12_MODULE_ID:
            continue
        artifacts.append(entry)
        by_module[module_id] = by_module.get(module_id, 0) + 1
        stored_evidence_count += 1
        if entry["content_read_status"] == "unverified":
            unverified_stored_evidence_count += 1
    for module in list_modules(include_reserved=False):
        if module.module_id == M12_MODULE_ID:
            continue
        module_root = workspace.root_path / "modules" / module.module_id
        if not module_root.is_dir():
            continue
        for path in sorted(module_root.rglob("*")):
            if not path.is_file() or any(part in _EXCLUDED_PARTS for part in path.relative_to(module_root).parts):
                continue
            artifacts.append({
                "record_type": "workspace_artifact",
                "module_id": module.module_id,
                "path": path.relative_to(workspace.root_path).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
                "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
            })
            by_module[module.module_id] = by_module.get(module.module_id, 0) + 1
            if len(artifacts) >= MAX_LEDGER_ARTIFACTS:
                break
        if len(artifacts) >= MAX_LEDGER_ARTIFACTS:
            break
    return {
        "schema_version": 1,
        "target_id": target.target_id,
        "module_id": M12_MODULE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": artifacts,
        "artifact_count": len(artifacts),
        "artifact_count_by_module": by_module,
        "stored_evidence_count": stored_evidence_count,
        "unverified_stored_evidence_count": unverified_stored_evidence_count,
        "truncated": len(artifacts) >= MAX_LEDGER_ARTIFACTS,
        "target_activity_performed": False,
        "ai_call_performed": False,
    }


def write_m12_evidence_ledger(
    target: TargetRecord,
    repo_root: Path | None = None,
    stored_evidence: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
) -> Path:
    """Persist current cross-module artifact ledger in the target M12 workspace."""
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M12_MODULE_ID, repo_root=root)
    path = binding.root_path / "outputs" / "evidence_ledger.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(build_m12_evidence_ledger(target, repo_root=root, stored_evidence=stored_evidence), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return path


def read_m12_evidence_ledger(target: TargetRecord, repo_root: Path | None = None) -> dict[str, object] | None:
    """Read a persisted ledger without scanning target systems or invoking AI."""
    root = Path.cwd() if repo_root is None else repo_root
    path = bind_target_module_workspace(target, M12_MODULE_ID, repo_root=root).root_path / "outputs" / "evidence_ledger.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None
