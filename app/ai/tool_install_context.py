"""AI-safe context packs for module tool installation planning and receipts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.tool_install_plan import build_module_tool_install_plan
from app.core.tool_install_receipts import list_tool_install_receipts
from app.core.tool_install_workspace import read_prepared_module_tool_install_plan

TOOL_INSTALL_CONTEXT_SCHEMA_VERSION = 1
MAX_CONTEXT_STEPS = 80
MAX_CONTEXT_RECEIPTS = 40
MAX_TEXT_FIELD_CHARS = 500


@dataclass(frozen=True, slots=True)
class ToolInstallContextPack:
    """Bounded JSON-safe context for LaIA/Mistral install-plan review."""

    module_id: str
    plan_prepared: bool
    plan: dict[str, Any]
    receipts: tuple[dict[str, Any], ...]
    checksum: str
    schema_version: int = TOOL_INSTALL_CONTEXT_SCHEMA_VERSION
    mode: str = "install_metadata_only_no_execution"
    external_ai_call_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "mode": self.mode,
            "module_id": self.module_id,
            "plan_prepared": self.plan_prepared,
            "plan": self.plan,
            "receipts": list(self.receipts),
            "checksum": self.checksum,
            "external_ai_call_performed": self.external_ai_call_performed,
        }


def _bounded_text(value: object) -> str:
    text = "" if value is None else str(value)
    return text if len(text) <= MAX_TEXT_FIELD_CHARS else text[:MAX_TEXT_FIELD_CHARS] + "…"


def _compact_step(step: dict[str, Any]) -> dict[str, Any]:
    return {
        "module_id": step.get("module_id"),
        "tool_id": step.get("tool_id"),
        "display_name": step.get("display_name"),
        "status": step.get("status"),
        "manager": step.get("manager"),
        "package_name": step.get("package_name"),
        "requires_sudo": step.get("requires_sudo"),
        "execution_performed": step.get("execution_performed"),
        "reason": _bounded_text(step.get("reason")),
    }


def _compact_plan(plan: dict[str, Any]) -> dict[str, Any]:
    steps = plan.get("steps", [])
    if not isinstance(steps, list):
        steps = []
    return {
        "module_id": plan.get("module_id"),
        "count": plan.get("count", 0),
        "ready_count": plan.get("ready_count", 0),
        "needs_metadata_count": plan.get("needs_metadata_count", 0),
        "execution_performed": plan.get("execution_performed", False),
        "truncated": len(steps) > MAX_CONTEXT_STEPS,
        "steps": [_compact_step(step) for step in steps[:MAX_CONTEXT_STEPS] if isinstance(step, dict)],
    }


def _compact_receipt(receipt_payload: dict[str, Any]) -> dict[str, Any]:
    receipt = receipt_payload.get("receipt", {})
    if not isinstance(receipt, dict):
        receipt = {}
    return {
        "receipt_id": receipt_payload.get("receipt_id"),
        "tool_id": receipt_payload.get("tool_id"),
        "sha256": receipt_payload.get("sha256"),
        "status": receipt.get("status"),
        "return_code": receipt.get("return_code"),
        "execution_performed": receipt.get("execution_performed"),
        "message": _bounded_text(receipt.get("message")),
        "stdout_excerpt": _bounded_text(receipt.get("stdout")),
        "stderr_excerpt": _bounded_text(receipt.get("stderr")),
    }


def _checksum(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_tool_install_context_pack(
    module_id: str,
    repo_root: Path | None = None,
) -> ToolInstallContextPack:
    """Build an AI-safe install context pack without calling an LLM or executing tools."""
    plan_prepared = True
    try:
        persisted, _ = read_prepared_module_tool_install_plan(module_id, repo_root=repo_root)
        plan_dict = persisted.plan.to_dict()
    except FileNotFoundError:
        plan_prepared = False
        plan_dict = build_module_tool_install_plan(module_id).to_dict()

    compact_plan = _compact_plan(plan_dict)
    receipt_dicts = [receipt.to_dict() for receipt in list_tool_install_receipts(module_id, repo_root=repo_root)]
    compact_receipts = tuple(_compact_receipt(receipt) for receipt in receipt_dicts[:MAX_CONTEXT_RECEIPTS])
    checksum_payload = {
        "schema_version": TOOL_INSTALL_CONTEXT_SCHEMA_VERSION,
        "module_id": module_id,
        "plan_prepared": plan_prepared,
        "plan": compact_plan,
        "receipts": list(compact_receipts),
        "receipt_truncated": len(receipt_dicts) > MAX_CONTEXT_RECEIPTS,
    }
    return ToolInstallContextPack(
        module_id=module_id,
        plan_prepared=plan_prepared,
        plan=compact_plan,
        receipts=compact_receipts,
        checksum=_checksum(checksum_payload),
    )
