"""M04 web response baseline from operator-approved, already observed HTTP metadata.

No request is sent to a URL. This records supplied response metadata and derives
a deterministic header posture so later authorised workflows can work from
traceable evidence rather than free-form notes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from app.core.target_model import TargetRecord
from app.core.target_workspace import bind_target_module_workspace

M04_MODULE_ID = "m04_web_intrusion"
MAX_HEADERS = 100
MAX_HEADER_VALUE_LENGTH = 4096


@dataclass(frozen=True, slots=True)
class WebResponseObservation:
    """Non-sensitive metadata of an HTTP response already observed by an approved process."""

    url: str
    status_code: int
    headers: dict[str, str]
    source: str
    evidence_ref: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "url": self.url,
            "status_code": self.status_code,
            "headers": self.headers,
            "source": self.source,
            "evidence_ref": self.evidence_ref,
            "target_request_performed": False,
        }


def _clean_text(value: object, name: str, max_length: int = 512, required: bool = True) -> str | None:
    text = str(value or "").strip()
    if not text:
        if required:
            raise ValueError(f"{name} is required.")
        return None
    if len(text) > max_length or "\x00" in text:
        raise ValueError(f"{name} is invalid or too long.")
    return text


def web_response_observation_from_payload(payload: dict[str, Any]) -> WebResponseObservation:
    """Validate approved response metadata without accepting cookie values or body contents."""
    url = _clean_text(payload.get("url"), "url")
    parsed = urlparse(url or "")
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("url must be an absolute http or https URL.")
    try:
        status_code = int(payload.get("status_code"))
    except (TypeError, ValueError) as exc:
        raise ValueError("status_code must be an integer from 100 to 599.") from exc
    if not 100 <= status_code <= 599:
        raise ValueError("status_code must be an integer from 100 to 599.")
    raw_headers = payload.get("headers", {})
    if not isinstance(raw_headers, dict) or len(raw_headers) > MAX_HEADERS:
        raise ValueError("headers must be an object with at most 100 entries.")
    headers: dict[str, str] = {}
    for raw_name, raw_value in raw_headers.items():
        name = _clean_text(raw_name, "header name", max_length=128)
        if name is None or any(char in name for char in "\r\n:"):
            raise ValueError("header name is invalid.")
        value = _clean_text(raw_value, f"header {name}", max_length=MAX_HEADER_VALUE_LENGTH)
        if value is None or "\r" in value or "\n" in value:
            raise ValueError(f"header {name} is invalid.")
        if name.casefold() in {"authorization", "cookie", "set-cookie", "proxy-authorization"}:
            continue
        headers[name.casefold()] = value
    return WebResponseObservation(
        url=url or "",
        status_code=status_code,
        headers=headers,
        source=_clean_text(payload.get("source", "operator_observed"), "source") or "operator_observed",
        evidence_ref=_clean_text(payload.get("evidence_ref"), "evidence_ref", required=False),
    )


def derive_web_header_posture(observation: WebResponseObservation) -> dict[str, object]:
    """Derive explainable header posture; absence is not a vulnerability finding by itself."""
    headers = observation.headers
    https = urlparse(observation.url).scheme == "https"
    checks = {
        "content_security_policy": "content-security-policy" in headers,
        "content_type_nosniff": headers.get("x-content-type-options", "").casefold() == "nosniff",
        "frame_protection": "x-frame-options" in headers or "frame-ancestors" in headers.get("content-security-policy", "").casefold(),
        "referrer_policy": "referrer-policy" in headers,
        "permissions_policy": "permissions-policy" in headers,
        "strict_transport_security": "strict-transport-security" in headers if https else None,
    }
    missing = [name for name, present in checks.items() if present is False]
    return {
        "checks": checks,
        "missing_or_unobserved": missing,
        "interpretation": "Header posture is evidence for review; validate application behavior and scope before reporting a security issue.",
    }


def write_m04_web_baseline(target: TargetRecord, observation: WebResponseObservation, repo_root: Path | None = None) -> Path:
    """Persist one supplied HTTP baseline and its derived non-executing posture in M04."""
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M04_MODULE_ID, repo_root=root)
    path = binding.root_path / "evidence" / "web_response_baseline.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "schema_version": 1,
        "target_id": target.target_id,
        "module_id": M04_MODULE_ID,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "observation": observation.to_dict(),
        "header_posture": derive_web_header_posture(observation),
        "target_request_performed": False,
        "execution_started": False,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def read_m04_web_baseline(target: TargetRecord, repo_root: Path | None = None) -> dict[str, object] | None:
    """Read an existing M04 baseline without accessing the target."""
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M04_MODULE_ID, repo_root=root)
    path = binding.root_path / "evidence" / "web_response_baseline.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None
