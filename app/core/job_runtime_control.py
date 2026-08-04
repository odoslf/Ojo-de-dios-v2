"""File-backed cooperative job stop requests for the local in-process runner."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

_JOB_STOP_DIR = Path("storage/runtime/job_stops")
_ALLOWED_ID_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")


@dataclass(frozen=True, slots=True)
class JobStopRequest:
    """Persisted cooperative stop request for one local job."""

    job_id: str
    target_id: str
    reason: str
    requested_at: str
    path: Path

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe stop request payload."""
        return {
            "job_id": self.job_id,
            "target_id": self.target_id,
            "reason": self.reason,
            "requested_at": self.requested_at,
            "path": self.path.as_posix(),
        }


def _safe_identifier(value: str, name: str) -> str:
    normalized = str(value or "").strip()
    if not normalized or len(normalized) > 128 or any(character not in _ALLOWED_ID_CHARS for character in normalized):
        raise ValueError(f"{name} is invalid.")
    return normalized


def _stop_dir(repo_root: Path | None = None) -> Path:
    root = Path.cwd() if repo_root is None else repo_root
    return root / _JOB_STOP_DIR


def stop_request_path(job_id: str, repo_root: Path | None = None) -> Path:
    """Return the deterministic stop-request path for a job id."""
    return _stop_dir(repo_root) / f"{_safe_identifier(job_id, 'job_id')}.json"


def write_job_stop_request(
    job_id: str,
    target_id: str,
    reason: str = "operator_requested_stop",
    repo_root: Path | None = None,
) -> JobStopRequest:
    """Persist a cooperative stop request consumed by JobRunner between techniques."""
    safe_job_id = _safe_identifier(job_id, "job_id")
    safe_target_id = _safe_identifier(target_id, "target_id")
    safe_reason = str(reason or "operator_requested_stop").strip()[:512]
    path = stop_request_path(safe_job_id, repo_root=repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    requested_at = datetime.now(timezone.utc).isoformat()
    payload = {
        "job_id": safe_job_id,
        "target_id": safe_target_id,
        "reason": safe_reason,
        "requested_at": requested_at,
        "cooperative": True,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return JobStopRequest(
        job_id=safe_job_id,
        target_id=safe_target_id,
        reason=safe_reason,
        requested_at=requested_at,
        path=path,
    )


def read_job_stop_request(job_id: str, repo_root: Path | None = None) -> JobStopRequest | None:
    """Read a persisted stop request if one exists and is valid."""
    path = stop_request_path(job_id, repo_root=repo_root)
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    stored_job_id = str(payload.get("job_id") or "")
    if stored_job_id != _safe_identifier(job_id, "job_id"):
        return None
    try:
        return JobStopRequest(
            job_id=stored_job_id,
            target_id=_safe_identifier(str(payload.get("target_id") or ""), "target_id"),
            reason=str(payload.get("reason") or "operator_requested_stop"),
            requested_at=str(payload.get("requested_at") or ""),
            path=path,
        )
    except ValueError:
        return None


def is_job_stop_requested(job_id: str, repo_root: Path | None = None) -> bool:
    """Return True when a cooperative stop request has been persisted for this job."""
    return read_job_stop_request(job_id, repo_root=repo_root) is not None
