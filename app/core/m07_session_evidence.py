"""M07 authorized-session evidence inventory without command or network execution."""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.target_model import TargetRecord
from app.core.target_workspace import bind_target_module_workspace

M07_MODULE_ID = "m07_post_exploitation"
VALID_SESSION_STATES = frozenset({"observed", "closed", "expired", "revoked"})
VALID_PRIVILEGE_LEVELS = frozenset({"unknown", "user", "administrator", "system"})


@dataclass(frozen=True, slots=True)
class SessionEvidence:
    """Metadata for an already-authorized session; no session secret is accepted or stored."""

    session_reference: str
    host_label: str
    platform: str
    privilege_level: str
    state: str
    source: str
    evidence_ref: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "session_reference": self.session_reference,
            "host_label": self.host_label,
            "platform": self.platform,
            "privilege_level": self.privilege_level,
            "state": self.state,
            "source": self.source,
            "evidence_ref": self.evidence_ref,
            "session_secret_persisted": False,
            "command_execution_performed": False,
            "network_activity_performed": False,
        }


def _text(value: object, name: str, required: bool = True) -> str | None:
    text = str(value or "").strip()
    if not text:
        if required:
            raise ValueError(f"{name} is required.")
        return None
    if len(text) > 512 or "\x00" in text or "\n" in text or "\r" in text:
        raise ValueError(f"{name} is invalid or too long.")
    return text


def session_evidence_from_payload(payload: dict[str, Any]) -> SessionEvidence:
    """Validate session metadata while rejecting any attempt to attach a session secret."""
    if any(key in payload for key in {"session_secret", "token", "password", "cookie", "authorization"}):
        raise ValueError("Session secrets and authentication material are not accepted in M07 evidence.")
    privilege_level = str(payload.get("privilege_level", "unknown")).strip()
    state = str(payload.get("state", "observed")).strip()
    if privilege_level not in VALID_PRIVILEGE_LEVELS:
        raise ValueError("privilege_level is invalid.")
    if state not in VALID_SESSION_STATES:
        raise ValueError("state is invalid.")
    return SessionEvidence(
        session_reference=_text(payload.get("session_reference"), "session_reference") or "",
        host_label=_text(payload.get("host_label"), "host_label") or "",
        platform=_text(payload.get("platform"), "platform") or "",
        privilege_level=privilege_level,
        state=state,
        source=_text(payload.get("source", "operator_observed"), "source") or "operator_observed",
        evidence_ref=_text(payload.get("evidence_ref"), "evidence_ref", required=False),
    )


def write_m07_session_evidence(target: TargetRecord, evidence: SessionEvidence, repo_root: Path | None = None) -> Path:
    """Persist one secret-free session observation in the target M07 workspace."""
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M07_MODULE_ID, repo_root=root)
    directory = binding.root_path / "evidence" / "sessions"
    directory.mkdir(parents=True, exist_ok=True)
    reference_hash = hashlib.sha256(evidence.session_reference.encode("utf-8")).hexdigest()[:12]
    receipt_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')}-{reference_hash}"
    path = directory / f"{receipt_id}.json"
    path.write_text(json.dumps({
        "schema_version": 1, "receipt_id": receipt_id, "target_id": target.target_id, "module_id": M07_MODULE_ID,
        "recorded_at": datetime.now(timezone.utc).isoformat(), "evidence": evidence.to_dict(),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def list_m07_session_evidence(target: TargetRecord, repo_root: Path | None = None, limit: int = 100) -> tuple[dict[str, object], ...]:
    """List M07 session metadata receipts without interacting with a session or host."""
    if limit < 1:
        raise ValueError("limit must be at least 1.")
    root = Path.cwd() if repo_root is None else repo_root
    directory = bind_target_module_workspace(target, M07_MODULE_ID, repo_root=root).root_path / "evidence" / "sessions"
    if not directory.is_dir():
        return ()
    entries: list[dict[str, object]] = []
    for path in sorted(directory.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict) and payload.get("target_id") == target.target_id and payload.get("module_id") == M07_MODULE_ID:
            payload["path"] = path.as_posix()
            entries.append(payload)
        if len(entries) >= limit:
            break
    return tuple(entries)
