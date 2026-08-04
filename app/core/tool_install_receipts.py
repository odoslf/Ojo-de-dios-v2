"""Persistence helpers for guarded tool installation execution receipts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.tool_install_runner import ToolInstallExecutionReceipt
from app.core.tool_install_workspace import INSTALL_PLAN_DIRNAME
from app.core.workspace import normalize_run_id, normalize_tool_id, workspace_for_module
from app.core.module_catalog import require_module_by_id

INSTALL_RECEIPTS_DIRNAME = "receipts"


@dataclass(frozen=True, slots=True)
class PersistedToolInstallReceipt:
    """Filesystem metadata for a persisted install execution receipt."""

    module_id: str
    receipt_id: str
    tool_id: str
    path: Path
    sha256: str
    byte_count: int
    receipt: ToolInstallExecutionReceipt

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "receipt_id": self.receipt_id,
            "tool_id": self.tool_id,
            "path": self.path.as_posix(),
            "sha256": self.sha256,
            "byte_count": self.byte_count,
            "receipt": self.receipt.to_dict(),
        }


def _receipts_root(module_id: str, repo_root: Path | None = None) -> Path:
    module = require_module_by_id(module_id)
    workspace = workspace_for_module(module, repo_root=repo_root)
    return workspace.root_path / INSTALL_PLAN_DIRNAME / INSTALL_RECEIPTS_DIRNAME


def _receipt_path(module_id: str, receipt_id: str, repo_root: Path | None = None) -> Path:
    safe_receipt_id = normalize_run_id(receipt_id)
    return _receipts_root(module_id, repo_root=repo_root) / f"{safe_receipt_id}.json"


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _receipt_id(receipt: ToolInstallExecutionReceipt) -> str:
    started = normalize_run_id(receipt.started_at.replace(":", "-").replace("+", "-"))
    return normalize_run_id(f"{receipt.tool_id}-{receipt.status.lower()}-{started}")


def _persisted_from_path(module_id: str, path: Path) -> PersistedToolInstallReceipt:
    content = path.read_bytes()
    payload = json.loads(content.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Install receipt file must contain a JSON object.")
    receipt_payload = payload.get("receipt")
    if not isinstance(receipt_payload, dict):
        raise ValueError("Install receipt payload is missing.")
    receipt = ToolInstallExecutionReceipt(
        module_id=str(receipt_payload["module_id"]),
        tool_id=str(receipt_payload["tool_id"]),
        display_name=str(receipt_payload["display_name"]),
        status=str(receipt_payload["status"]),
        command_argv=tuple(str(item) for item in receipt_payload.get("command_argv", [])),
        started_at=str(receipt_payload["started_at"]),
        finished_at=str(receipt_payload["finished_at"]),
        return_code=receipt_payload.get("return_code"),
        stdout=str(receipt_payload.get("stdout", "")),
        stderr=str(receipt_payload.get("stderr", "")),
        message=str(receipt_payload.get("message", "")),
        execution_performed=bool(receipt_payload.get("execution_performed", False)),
        duration_seconds=float(receipt_payload.get("duration_seconds", 0.0)),
        metadata=dict(receipt_payload.get("metadata", {})),
    )
    return PersistedToolInstallReceipt(
        module_id=module_id,
        receipt_id=path.stem,
        tool_id=normalize_tool_id(receipt.tool_id),
        path=path,
        sha256=hashlib.sha256(content).hexdigest(),
        byte_count=len(content),
        receipt=receipt,
    )


def write_tool_install_receipt(
    receipt: ToolInstallExecutionReceipt,
    receipt_id: str | None = None,
    repo_root: Path | None = None,
) -> PersistedToolInstallReceipt:
    """Persist a guarded install receipt into the module install workspace."""
    safe_receipt_id = normalize_run_id(receipt_id) if receipt_id else _receipt_id(receipt)
    path = _receipt_path(receipt.module_id, safe_receipt_id, repo_root=repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "receipt_id": safe_receipt_id,
        "module_id": receipt.module_id,
        "tool_id": normalize_tool_id(receipt.tool_id),
        "receipt": receipt.to_dict(),
    }
    content = _json_bytes(payload)
    path.write_bytes(content)
    return _persisted_from_path(receipt.module_id, path)


def read_tool_install_receipt(
    module_id: str,
    receipt_id: str,
    repo_root: Path | None = None,
) -> PersistedToolInstallReceipt:
    """Read one persisted guarded install receipt."""
    path = _receipt_path(module_id, receipt_id, repo_root=repo_root)
    return _persisted_from_path(module_id, path)


def list_tool_install_receipts(
    module_id: str,
    repo_root: Path | None = None,
) -> tuple[PersistedToolInstallReceipt, ...]:
    """List persisted guarded install receipts for one module."""
    root = _receipts_root(module_id, repo_root=repo_root)
    if not root.is_dir():
        return ()
    return tuple(_persisted_from_path(module_id, path) for path in sorted(root.glob("*.json")))
