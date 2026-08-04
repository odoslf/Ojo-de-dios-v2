"""M01 context packs and prompt envelopes for local LaIA/Mistral review."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from app.core.target_model import TargetRecord
from app.core.target_osint import list_target_passive_dns_history
from app.core.target_workspace import bind_target_module_workspace

M01_CONTEXT_PACK_TYPE = "m01_target_passive_osint_context_pack"
M01_PROMPT_MODE = "m01_laia_mistral_review_prompt_no_ai_call"
M01_MODULE_ID = "m01_osint"


@dataclass(frozen=True, slots=True)
class M01TargetContextPack:
    """Bounded target-specific context for M01 local AI review."""

    target_id: str
    target_name: str
    target_type: str
    normalized_value: str
    mode: str
    generated_at: str
    history: tuple[dict[str, object], ...]
    safety: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "pack_type": M01_CONTEXT_PACK_TYPE,
            "target": {
                "target_id": self.target_id,
                "name": self.target_name,
                "target_type": self.target_type,
                "normalized_value": self.normalized_value,
                "mode": self.mode,
            },
            "generated_at": self.generated_at,
            "history": list(self.history),
            "history_count": len(self.history),
            "safety": self.safety,
        }


def build_m01_target_context_pack(
    target: TargetRecord, repo_root: Path | None = None, history_limit: int = 5
) -> M01TargetContextPack:
    """Build a local M01 context pack from persisted target evidence."""
    history = tuple(entry.to_dict() for entry in list_target_passive_dns_history(target, repo_root=repo_root, limit=history_limit))
    return M01TargetContextPack(
        target_id=target.target_id,
        target_name=target.name,
        target_type=target.target_type,
        normalized_value=target.normalized_value or target.value,
        mode=target.mode,
        generated_at=datetime.now(timezone.utc).isoformat(),
        history=history,
        safety={
            "uses_persisted_workspace_only": True,
            "external_ai_call_performed": False,
            "local_ai_call_performed": False,
            "target_web_request_performed": False,
            "port_scan_performed": False,
            "subdomain_bruteforce_performed": False,
            "allowed_ai_role": "local_laia_mistral_operator_review",
        },
    )


def build_m01_target_prompt_envelope(target: TargetRecord, repo_root: Path | None = None) -> dict[str, object]:
    """Build a no-call prompt envelope for local Mistral review of M01 evidence."""
    context_pack = build_m01_target_context_pack(target, repo_root=repo_root)
    return {
        "mode": M01_PROMPT_MODE,
        "system": (
            "Eres LaIA/Mistral local dentro de Ojo de Dios. Revisa solo evidencia M01 ya persistida. "
            "No inventes datos, no propongas escaneos activos sin scope explicito y devuelve JSON compacto."
        ),
        "developer_rules": [
            "Usa solo el context_pack incluido.",
            "Si no hay historial M01, responde que falta ejecutar M01 DNS pasivo.",
            "Separa hallazgos confirmados de recomendaciones de siguiente paso.",
            "No pidas credenciales ni secretos.",
        ],
        "expected_json_schema": {
            "summary": "string",
            "confirmed_findings": "array",
            "recommended_next_steps": "array",
            "needs_more_m01_evidence": "boolean",
            "safety_notes": "array",
        },
        "context_pack": context_pack.to_dict(),
        "external_ai_call_performed": False,
        "local_ai_call_performed": False,
    }


def render_m01_target_chatml_prompt(target: TargetRecord, repo_root: Path | None = None) -> dict[str, object]:
    """Render the M01 prompt envelope as ChatML text for local Mistral/Ollama."""
    envelope = build_m01_target_prompt_envelope(target, repo_root=repo_root)
    prompt = (
        "<|system|>\n"
        f"{envelope['system']}\n"
        "<|user|>\n"
        f"{json.dumps(envelope, ensure_ascii=False, indent=2)}\n"
        "<|assistant|>\n"
    )
    return {
        "target_id": target.target_id,
        "mode": "m01_laia_mistral_review_chatml",
        "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "external_ai_call_performed": False,
        "local_ai_call_performed": False,
    }

@dataclass(frozen=True, slots=True)
class M01TargetAIReview:
    """Persisted local LaIA/Mistral review receipt for M01 target evidence."""

    review_id: str
    target_id: str
    model: str
    prompt_sha256: str
    content: str
    created_at: str
    path: Path
    parsed_content: dict[str, object] | None
    parse_status: str
    parse_error: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "review_id": self.review_id,
            "target_id": self.target_id,
            "module_id": M01_MODULE_ID,
            "mode": "m01_laia_mistral_local_review",
            "model": self.model,
            "prompt_sha256": self.prompt_sha256,
            "content": self.content,
            "parsed_content": self.parsed_content,
            "parse_status": self.parse_status,
            "parse_error": self.parse_error,
            "created_at": self.created_at,
            "path": self.path.as_posix(),
            "external_ai_call_performed": False,
            "local_ai_call_performed": True,
        }


def _extract_first_json_object(text: str) -> tuple[dict[str, object] | None, str | None]:
    stripped = text.strip()
    candidates = [stripped]
    candidates.extend(match.group(1).strip() for match in re.finditer(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE))
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace > first_brace:
        candidates.append(text[first_brace : last_brace + 1])
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = str(exc)
            continue
        if isinstance(payload, dict):
            return payload, None
    return None, locals().get("last_error", "No JSON object found in local review content.")


def _string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def normalize_m01_review_payload(payload: dict[str, object]) -> dict[str, object]:
    """Normalize a local Mistral M01 review into the expected operator schema."""
    return {
        "summary": str(payload.get("summary", "")).strip(),
        "confirmed_findings": _string_list(payload.get("confirmed_findings", [])),
        "recommended_next_steps": _string_list(payload.get("recommended_next_steps", [])),
        "needs_more_m01_evidence": bool(payload.get("needs_more_m01_evidence", False)),
        "safety_notes": _string_list(payload.get("safety_notes", [])),
    }


def _review_from_path(path: Path) -> M01TargetAIReview | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    content = str(payload.get("content", ""))
    maybe_json, parse_error = _extract_first_json_object(content)
    parsed_content = normalize_m01_review_payload(maybe_json) if maybe_json is not None else None
    parse_status = "parsed" if parsed_content is not None else "raw_text"
    return M01TargetAIReview(
        review_id=str(payload.get("review_id") or path.stem),
        target_id=str(payload.get("target_id", "")),
        model=str(payload.get("model", "")),
        prompt_sha256=str(payload.get("prompt_sha256", "")),
        content=content,
        created_at=str(payload.get("created_at", "")),
        path=path,
        parsed_content=parsed_content,
        parse_status=parse_status,
        parse_error=parse_error,
    )


def list_m01_target_ai_reviews(
    target: TargetRecord, repo_root: Path | None = None, limit: int = 10
) -> tuple[M01TargetAIReview, ...]:
    """List persisted local Mistral reviews for a target M01 workspace."""
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M01_MODULE_ID, repo_root=root)
    reviews_dir = binding.root_path / "ai_reviews" / "laia_mistral"
    if not reviews_dir.exists():
        return ()
    reviews: list[M01TargetAIReview] = []
    for path in sorted(reviews_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        review = _review_from_path(path)
        if review is not None:
            reviews.append(review)
        if len(reviews) >= limit:
            break
    return tuple(reviews)


def write_m01_target_ai_review(
    target: TargetRecord, model: str, prompt_sha256: str, content: str, repo_root: Path | None = None
) -> Path:
    """Persist one local Mistral review receipt under the target M01 workspace."""
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M01_MODULE_ID, repo_root=root)
    reviews_dir = binding.root_path / "ai_reviews" / "laia_mistral"
    reviews_dir.mkdir(parents=True, exist_ok=True)
    created_at = datetime.now(timezone.utc).isoformat()
    review_id = hashlib.sha256(f"{target.target_id}:{model}:{prompt_sha256}:{created_at}".encode("utf-8")).hexdigest()[:16]
    path = reviews_dir / f"{review_id}.json"
    payload = {
        "review_id": review_id,
        "target_id": target.target_id,
        "module_id": M01_MODULE_ID,
        "mode": "m01_laia_mistral_local_review",
        "model": model,
        "prompt_sha256": prompt_sha256,
        "content": content,
        "created_at": created_at,
        "external_ai_call_performed": False,
        "local_ai_call_performed": True,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
