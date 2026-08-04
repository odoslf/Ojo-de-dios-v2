"""Tool-run context packs for local AI-assisted operator review."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from app.core.tool_run_summary import summarize_tool_run_workspace
from app.core.workspace_artifacts import read_tool_run_json_artifact

TOOL_RUN_CONTEXT_SCHEMA_VERSION = 1
TOOL_RUN_CONTEXT_PACK_TYPE = "tool_run_context_pack"
TOOL_RUN_CONTEXT_PURPOSE = "local_ai_assisted_tool_run_review"
SECRET_KEY_PARTS = ("api_key", "apikey", "secret", "token", "password", "credential")


@dataclass(frozen=True, slots=True)
class ToolRunContextPack:
    """Bounded JSON context for one prepared tool-run workspace."""

    schema_version: int
    pack_type: str
    purpose: str
    module_id: str
    tool_id: str
    run_id: str
    summary: dict[str, Any]
    artifact_payloads: tuple[dict[str, Any], ...]
    checksum: str
    external_ai_call_performed: bool = False

    def to_dict(self, include_checksum: bool = True) -> dict[str, Any]:
        payload = {
            "schema_version": self.schema_version,
            "pack_type": self.pack_type,
            "purpose": self.purpose,
            "module_id": self.module_id,
            "tool_id": self.tool_id,
            "run_id": self.run_id,
            "summary": self.summary,
            "artifact_payloads": list(self.artifact_payloads),
            "artifact_payload_count": len(self.artifact_payloads),
            "external_ai_call_performed": self.external_ai_call_performed,
        }
        if include_checksum:
            payload["checksum"] = self.checksum
        return payload


def _payload_checksum(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _redact_for_ai(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            normalized_key = str(key).lower().replace("-", "_")
            if any(secret_part in normalized_key for secret_part in SECRET_KEY_PARTS):
                redacted[str(key)] = "***REDACTED***"
            else:
                redacted[str(key)] = _redact_for_ai(item)
        return redacted
    if isinstance(value, list):
        return [_redact_for_ai(item) for item in value]
    return value


def build_tool_run_context_pack(
    module_id: str,
    tool_id: str,
    run_id: str,
    max_artifacts: int = 10,
    max_payload_bytes: int = 64_000,
) -> ToolRunContextPack:
    """Build bounded, redacted JSON context for one existing prepared tool run."""
    summary = summarize_tool_run_workspace(module_id, tool_id, run_id)
    artifact_payloads: list[dict[str, Any]] = []
    consumed_bytes = 0
    for artifact in summary.artifacts[:max_artifacts]:
        if consumed_bytes + artifact.byte_count > max_payload_bytes:
            break
        _, payload = read_tool_run_json_artifact(
            summary.module_id,
            summary.tool_id,
            summary.run_id,
            artifact.artifact_name,
            artifact.artifact_type,
        )
        artifact_payloads.append(
            {
                "artifact": artifact.to_dict(),
                "payload": _redact_for_ai(payload),
            }
        )
        consumed_bytes += artifact.byte_count
    summary_payload = summary.to_dict()
    context_payload = {
        "schema_version": TOOL_RUN_CONTEXT_SCHEMA_VERSION,
        "pack_type": TOOL_RUN_CONTEXT_PACK_TYPE,
        "purpose": TOOL_RUN_CONTEXT_PURPOSE,
        "module_id": summary.module_id,
        "tool_id": summary.tool_id,
        "run_id": summary.run_id,
        "summary": summary_payload,
        "artifact_payloads": artifact_payloads,
        "artifact_payload_count": len(artifact_payloads),
        "external_ai_call_performed": False,
    }
    return ToolRunContextPack(
        schema_version=TOOL_RUN_CONTEXT_SCHEMA_VERSION,
        pack_type=TOOL_RUN_CONTEXT_PACK_TYPE,
        purpose=TOOL_RUN_CONTEXT_PURPOSE,
        module_id=summary.module_id,
        tool_id=summary.tool_id,
        run_id=summary.run_id,
        summary=summary_payload,
        artifact_payloads=tuple(artifact_payloads),
        checksum=_payload_checksum(context_payload),
    )
