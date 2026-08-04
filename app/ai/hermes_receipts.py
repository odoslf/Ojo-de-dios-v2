"""Audit receipt persistence for gated Hermes/DeepSeek assistance calls."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.ai.hermes_assist import HermesAssistRequest, HermesAssistResponse
from app.core.workspace import normalize_run_id

HERMES_RECEIPTS_DIR = Path("storage/runtime/hermes_assist_receipts")
_SECRET_KEY_PATTERN = r"api[_-]?key|token|secret|password|passwd|authorization|credential"
_SECRET_KEY_RE = re.compile(rf"(?i)({_SECRET_KEY_PATTERN})")
_SECRET_TEXT_PATTERNS = (
    re.compile(rf"(?i)((?:{_SECRET_KEY_PATTERN})\s*[:=]\s*)[^\s,;}}]+"),
    re.compile(
        rf"(?i)((?:\\?['\"])?(?:{_SECRET_KEY_PATTERN})(?:\\?['\"])?\s*:\s*"
        r"""(?:\?['"])?)[^\'",;}]+"""
    ),
)


@dataclass(frozen=True, slots=True)
class HermesAssistReceipt:
    """One persisted, redacted Hermes assistance audit receipt."""

    receipt_id: str
    path: Path
    sha256: str
    byte_count: int
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "path": self.path.as_posix(),
            "sha256": self.sha256,
            "byte_count": self.byte_count,
            "payload": self.payload,
        }


def _redact_text(value: str) -> str:
    redacted = value
    for pattern in _SECRET_TEXT_PATTERNS:
        redacted = pattern.sub(lambda match: f"{match.group(1)}<redacted>", redacted)
    return redacted


def redact_hermes_payload(value: Any) -> Any:
    """Recursively redact secret-looking keys and inline secret assignments."""
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            safe_key = str(key)
            redacted[safe_key] = "<redacted>" if _SECRET_KEY_RE.search(safe_key) else redact_hermes_payload(item)
        return redacted
    if isinstance(value, list):
        return [redact_hermes_payload(item) for item in value]
    if isinstance(value, tuple):
        return [redact_hermes_payload(item) for item in value]
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return _redact_text(value)
        if isinstance(decoded, dict | list):
            return json.dumps(redact_hermes_payload(decoded), ensure_ascii=False, sort_keys=True)
        return _redact_text(value)
    return value


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _receipt_root(repo_root: Path | None = None) -> Path:
    root = Path(repo_root) if repo_root is not None else Path(".")
    return root / HERMES_RECEIPTS_DIR


def _receipt_path(receipt_id: str, repo_root: Path | None = None) -> Path:
    return _receipt_root(repo_root=repo_root) / f"{normalize_run_id(receipt_id)}.json"


def _receipt_id(request: HermesAssistRequest, created_at: str) -> str:
    digest_source = json.dumps(
        {
            "created_at": created_at,
            "model": request.model,
            "purpose": request.purpose,
            "question": redact_hermes_payload(request.question),
            "context": redact_hermes_payload(request.context),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    digest = hashlib.sha256(digest_source.encode("utf-8")).hexdigest()[:16]
    return normalize_run_id(f"hermes-{request.model}-{created_at.replace(':', '-')}-{digest}")


def _receipt_from_path(path: Path) -> HermesAssistReceipt:
    content = path.read_bytes()
    payload = json.loads(content.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Hermes receipt file must contain a JSON object.")
    return HermesAssistReceipt(
        receipt_id=path.stem,
        path=path,
        sha256=hashlib.sha256(content).hexdigest(),
        byte_count=len(content),
        payload=payload,
    )


def write_hermes_assist_receipt(
    request: HermesAssistRequest,
    response: HermesAssistResponse,
    receipt_id: str | None = None,
    repo_root: Path | None = None,
) -> HermesAssistReceipt:
    """Persist a redacted audit receipt for one approved Hermes assist response."""
    created_at = datetime.now(UTC).isoformat()
    safe_receipt_id = normalize_run_id(receipt_id) if receipt_id else _receipt_id(request, created_at)
    path = _receipt_path(safe_receipt_id, repo_root=repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "receipt_id": safe_receipt_id,
        "created_at": created_at,
        "mode": response.mode,
        "external_ai_call_performed": response.external_ai_call_performed,
        "request": {
            "purpose": request.purpose,
            "model": request.model,
            "allow_pro_model": request.allow_pro_model,
            "max_tokens": request.max_tokens,
            "reasoning_effort": request.reasoning_effort,
            "question": redact_hermes_payload(request.question),
            "context": redact_hermes_payload(request.context),
        },
        "response": {
            "model": response.model,
            "content": redact_hermes_payload(response.content),
            "raw": redact_hermes_payload(response.raw),
        },
    }
    path.write_bytes(_json_bytes(payload))
    return _receipt_from_path(path)


def read_hermes_assist_receipt(receipt_id: str, repo_root: Path | None = None) -> HermesAssistReceipt:
    """Read one persisted Hermes assist receipt by id."""
    return _receipt_from_path(_receipt_path(receipt_id, repo_root=repo_root))


def list_hermes_assist_receipts(repo_root: Path | None = None) -> tuple[HermesAssistReceipt, ...]:
    """List persisted Hermes assist receipts in stable path order."""
    root = _receipt_root(repo_root=repo_root)
    if not root.is_dir():
        return ()
    return tuple(_receipt_from_path(path) for path in sorted(root.glob("*.json")))


def summarize_hermes_assist_receipts(repo_root: Path | None = None) -> dict[str, Any]:
    """Return aggregate audit metadata for persisted Hermes assist receipts."""
    receipts = list_hermes_assist_receipts(repo_root=repo_root)
    models: dict[str, int] = {}
    purposes: dict[str, int] = {}
    external_ai_call_count = 0
    latest_created_at: str | None = None
    total_byte_count = 0
    for receipt in receipts:
        payload = receipt.payload
        request = payload.get("request", {}) if isinstance(payload.get("request"), dict) else {}
        response = payload.get("response", {}) if isinstance(payload.get("response"), dict) else {}
        model = str(request.get("model") or response.get("model") or "unknown")
        purpose = str(request.get("purpose") or "unknown")
        models[model] = models.get(model, 0) + 1
        purposes[purpose] = purposes.get(purpose, 0) + 1
        if payload.get("external_ai_call_performed") is True:
            external_ai_call_count += 1
        created_at = payload.get("created_at")
        if isinstance(created_at, str) and (latest_created_at is None or created_at > latest_created_at):
            latest_created_at = created_at
        total_byte_count += receipt.byte_count
    return {
        "count": len(receipts),
        "external_ai_call_count": external_ai_call_count,
        "models": dict(sorted(models.items())),
        "purposes": dict(sorted(purposes.items())),
        "latest_created_at": latest_created_at,
        "total_byte_count": total_byte_count,
    }


HERMES_RECEIPT_CONTEXT_MAX_CHARS = 12_000


def build_hermes_receipt_context_pack(receipt_id: str, repo_root: Path | None = None) -> dict[str, Any]:
    """Build a bounded, redacted context pack for local review of one Hermes receipt."""
    receipt = read_hermes_assist_receipt(receipt_id, repo_root=repo_root)
    payload = receipt.payload
    encoded_payload = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    checksum = hashlib.sha256(encoded_payload.encode("utf-8")).hexdigest()
    bounded_payload = payload
    truncated = False
    if len(encoded_payload) > HERMES_RECEIPT_CONTEXT_MAX_CHARS:
        bounded_payload = {
            "truncated_payload_json": encoded_payload[:HERMES_RECEIPT_CONTEXT_MAX_CHARS] + "…",
            "original_char_count": len(encoded_payload),
        }
        truncated = True
    return {
        "mode": "hermes_receipt_context_no_external_call",
        "receipt_id": receipt.receipt_id,
        "receipt_path": receipt.path.as_posix(),
        "sha256": receipt.sha256,
        "payload_checksum": checksum,
        "byte_count": receipt.byte_count,
        "external_ai_call_performed": False,
        "source_external_ai_call_performed": payload.get("external_ai_call_performed") is True,
        "truncated": truncated,
        "max_chars": HERMES_RECEIPT_CONTEXT_MAX_CHARS,
        "payload": bounded_payload,
    }


def build_hermes_receipt_prompt_envelope(receipt_id: str, repo_root: Path | None = None) -> dict[str, Any]:
    """Build a local prompt envelope for reviewing a Hermes receipt context pack."""
    context_pack = build_hermes_receipt_context_pack(receipt_id, repo_root=repo_root)
    return {
        "mode": "hermes_receipt_prompt_envelope_no_external_call",
        "external_ai_call_performed": False,
        "system_prompt": (
            "You are LaIA reviewing an audited Hermes Agent DeepSeek receipt. "
            "Use only the provided redacted receipt context. Do not execute tools, do not infer secrets, "
            "and mark any missing implementation as IMPLEMENTACION_USUARIO_REQUERIDA."
        ),
        "user_context": context_pack,
        "response_schema": {
            "type": "object",
            "required": ["summary", "risks", "follow_up_actions", "execution_implied"],
            "properties": {
                "summary": {"type": "string"},
                "risks": {"type": "array", "items": {"type": "string"}},
                "follow_up_actions": {"type": "array", "items": {"type": "string"}},
                "execution_implied": {"type": "boolean", "const": False},
            },
        },
    }


def render_hermes_receipt_chatml_prompt(receipt_id: str, repo_root: Path | None = None) -> dict[str, Any]:
    """Render a Hermes receipt prompt envelope as ChatML for local Dolphin Mistral Nemo."""
    envelope = build_hermes_receipt_prompt_envelope(receipt_id, repo_root=repo_root)
    user_payload = {
        "context": envelope["user_context"],
        "response_schema": envelope["response_schema"],
    }
    user_json = json.dumps(user_payload, ensure_ascii=False, sort_keys=True)
    prompt = (
        f"<|im_start|>system\n{envelope['system_prompt']}<|im_end|>\n"
        f"<|im_start|>user\n{user_json}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )
    return {
        "mode": "hermes_receipt_chatml_prompt_no_external_call",
        "external_ai_call_performed": False,
        "prompt_template": "chatml",
        "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "prompt_char_count": len(prompt),
        "receipt_id": envelope["user_context"]["receipt_id"],
    }


HERMES_LAIA_REVIEWS_DIR = Path("storage/runtime/hermes_assist_receipts/laia_reviews")


def _laia_review_path(review_id: str, repo_root: Path | None = None) -> Path:
    root = Path(repo_root) if repo_root is not None else Path(".")
    return root / HERMES_LAIA_REVIEWS_DIR / f"{normalize_run_id(review_id)}.json"


def write_laia_receipt_review(
    source_receipt_id: str,
    model: str,
    prompt_sha256: str,
    content: str,
    review_id: str | None = None,
    repo_root: Path | None = None,
) -> HermesAssistReceipt:
    """Persist a redacted local LaIA review for one Hermes assist receipt."""
    created_at = datetime.now(UTC).isoformat()
    if review_id is None:
        digest_source = f"{source_receipt_id}:{model}:{prompt_sha256}:{created_at}"
        digest = hashlib.sha256(digest_source.encode("utf-8")).hexdigest()[:16]
        review_id = f"laia-{source_receipt_id}-{digest}"
    safe_review_id = normalize_run_id(review_id)
    path = _laia_review_path(safe_review_id, repo_root=repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "review_id": safe_review_id,
        "source_receipt_id": normalize_run_id(source_receipt_id),
        "created_at": created_at,
        "mode": "laia_mistral_hermes_receipt_review",
        "external_ai_call_performed": False,
        "local_ai_call_performed": True,
        "model": model,
        "prompt_sha256": prompt_sha256,
        "content": redact_hermes_payload(content),
    }
    path.write_bytes(_json_bytes(payload))
    return _receipt_from_path(path)


def read_laia_receipt_review(review_id: str, repo_root: Path | None = None) -> HermesAssistReceipt:
    """Read one persisted local LaIA review receipt by id."""
    return _receipt_from_path(_laia_review_path(review_id, repo_root=repo_root))


def list_laia_receipt_reviews(
    source_receipt_id: str | None = None,
    repo_root: Path | None = None,
) -> tuple[HermesAssistReceipt, ...]:
    """List persisted local LaIA review receipts, optionally scoped to one Hermes receipt."""
    root = (Path(repo_root) if repo_root is not None else Path(".")) / HERMES_LAIA_REVIEWS_DIR
    if not root.is_dir():
        return ()
    reviews = tuple(_receipt_from_path(path) for path in sorted(root.glob("*.json")))
    if source_receipt_id is None:
        return reviews
    safe_source = normalize_run_id(source_receipt_id)
    return tuple(
        review
        for review in reviews
        if str(review.payload.get("source_receipt_id", "")) == safe_source
    )


def summarize_laia_receipt_reviews(
    source_receipt_id: str | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Return aggregate audit metadata for persisted local LaIA review receipts."""
    reviews = list_laia_receipt_reviews(source_receipt_id=source_receipt_id, repo_root=repo_root)
    models: dict[str, int] = {}
    source_receipts: dict[str, int] = {}
    local_ai_call_count = 0
    latest_created_at: str | None = None
    total_byte_count = 0
    for review in reviews:
        payload = review.payload
        model = str(payload.get("model") or "unknown")
        source_id = str(payload.get("source_receipt_id") or "unknown")
        models[model] = models.get(model, 0) + 1
        source_receipts[source_id] = source_receipts.get(source_id, 0) + 1
        if payload.get("local_ai_call_performed") is True:
            local_ai_call_count += 1
        created_at = payload.get("created_at")
        if isinstance(created_at, str) and (latest_created_at is None or created_at > latest_created_at):
            latest_created_at = created_at
        total_byte_count += review.byte_count
    return {
        "count": len(reviews),
        "local_ai_call_count": local_ai_call_count,
        "models": dict(sorted(models.items())),
        "source_receipts": dict(sorted(source_receipts.items())),
        "source_receipt_id": normalize_run_id(source_receipt_id) if source_receipt_id is not None else None,
        "latest_created_at": latest_created_at,
        "total_byte_count": total_byte_count,
    }


LAIA_RECEIPT_REVIEW_CONTEXT_MAX_CHARS = 8_000


def build_laia_receipt_review_context_pack(review_id: str, repo_root: Path | None = None) -> dict[str, Any]:
    """Build a bounded, redacted context pack for one local LaIA review receipt."""
    review = read_laia_receipt_review(review_id, repo_root=repo_root)
    payload = review.payload
    encoded_payload = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    checksum = hashlib.sha256(encoded_payload.encode("utf-8")).hexdigest()
    bounded_payload = payload
    truncated = False
    if len(encoded_payload) > LAIA_RECEIPT_REVIEW_CONTEXT_MAX_CHARS:
        bounded_payload = {
            "truncated_payload_json": encoded_payload[:LAIA_RECEIPT_REVIEW_CONTEXT_MAX_CHARS] + "…",
            "original_char_count": len(encoded_payload),
        }
        truncated = True
    return {
        "mode": "laia_receipt_review_context_no_ai_call",
        "review_id": review.receipt_id,
        "source_receipt_id": str(payload.get("source_receipt_id") or ""),
        "review_path": review.path.as_posix(),
        "sha256": review.sha256,
        "payload_checksum": checksum,
        "byte_count": review.byte_count,
        "external_ai_call_performed": False,
        "local_ai_call_performed": False,
        "source_local_ai_call_performed": payload.get("local_ai_call_performed") is True,
        "truncated": truncated,
        "max_chars": LAIA_RECEIPT_REVIEW_CONTEXT_MAX_CHARS,
        "payload": bounded_payload,
    }


def build_laia_receipt_review_prompt_envelope(review_id: str, repo_root: Path | None = None) -> dict[str, Any]:
    """Build a local prompt envelope for auditing one persisted LaIA review receipt."""
    context_pack = build_laia_receipt_review_context_pack(review_id, repo_root=repo_root)
    return {
        "mode": "laia_receipt_review_prompt_envelope_no_ai_call",
        "external_ai_call_performed": False,
        "local_ai_call_performed": False,
        "system_prompt": (
            "You are LaIA performing a second-pass audit of a previously persisted local LaIA/Mistral "
            "review receipt. Use only the provided redacted review context. Do not execute tools, "
            "do not infer secrets, and report whether the original local review stayed within policy."
        ),
        "user_context": context_pack,
        "response_schema": {
            "type": "object",
            "required": [
                "summary",
                "policy_observations",
                "source_review_issues",
                "follow_up_actions",
                "execution_implied",
            ],
            "properties": {
                "summary": {"type": "string"},
                "policy_observations": {"type": "array", "items": {"type": "string"}},
                "source_review_issues": {"type": "array", "items": {"type": "string"}},
                "follow_up_actions": {"type": "array", "items": {"type": "string"}},
                "execution_implied": {"type": "boolean", "const": False},
            },
        },
    }


def render_laia_receipt_review_chatml_prompt(review_id: str, repo_root: Path | None = None) -> dict[str, Any]:
    """Render a LaIA review receipt prompt envelope as ChatML for local Dolphin Mistral Nemo."""
    envelope = build_laia_receipt_review_prompt_envelope(review_id, repo_root=repo_root)
    user_payload = {
        "context": envelope["user_context"],
        "response_schema": envelope["response_schema"],
    }
    user_json = json.dumps(user_payload, ensure_ascii=False, sort_keys=True)
    prompt = (
        f"<|im_start|>system\n{envelope['system_prompt']}<|im_end|>\n"
        f"<|im_start|>user\n{user_json}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )
    return {
        "mode": "laia_receipt_review_chatml_prompt_no_ai_call",
        "external_ai_call_performed": False,
        "local_ai_call_performed": False,
        "prompt_template": "chatml",
        "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "prompt_char_count": len(prompt),
        "review_id": envelope["user_context"]["review_id"],
        "source_receipt_id": envelope["user_context"]["source_receipt_id"],
    }


HERMES_LAIA_REVIEW_AUDITS_DIR = Path("storage/runtime/hermes_assist_receipts/laia_review_audits")


def _laia_review_audit_path(audit_id: str, repo_root: Path | None = None) -> Path:
    root = Path(repo_root) if repo_root is not None else Path(".")
    return root / HERMES_LAIA_REVIEW_AUDITS_DIR / f"{normalize_run_id(audit_id)}.json"


def write_laia_review_receipt_audit(
    source_review_id: str,
    source_receipt_id: str,
    model: str,
    prompt_sha256: str,
    content: str,
    audit_id: str | None = None,
    repo_root: Path | None = None,
) -> HermesAssistReceipt:
    """Persist a redacted second-pass local LaIA audit for one LaIA review receipt."""
    created_at = datetime.now(UTC).isoformat()
    safe_source_review_id = normalize_run_id(source_review_id)
    safe_source_receipt_id = normalize_run_id(source_receipt_id)
    if audit_id is None:
        digest_source = f"{safe_source_review_id}:{safe_source_receipt_id}:{model}:{prompt_sha256}:{created_at}"
        digest = hashlib.sha256(digest_source.encode("utf-8")).hexdigest()[:16]
        audit_id = f"laia-audit-{safe_source_review_id}-{digest}"
    safe_audit_id = normalize_run_id(audit_id)
    path = _laia_review_audit_path(safe_audit_id, repo_root=repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "audit_id": safe_audit_id,
        "source_review_id": safe_source_review_id,
        "source_receipt_id": safe_source_receipt_id,
        "created_at": created_at,
        "mode": "laia_mistral_review_receipt_audit",
        "external_ai_call_performed": False,
        "local_ai_call_performed": True,
        "model": model,
        "prompt_sha256": prompt_sha256,
        "content": redact_hermes_payload(content),
    }
    path.write_bytes(_json_bytes(payload))
    return _receipt_from_path(path)
