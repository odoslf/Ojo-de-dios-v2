"""Centralized secret redaction helpers for logs, evidence metadata and API receipts."""

from __future__ import annotations

import json
import re
from typing import Any

SECRET_KEY_RE = re.compile(r"(api[_-]?key|token|secret|password|passwd|authorization|credential)", re.IGNORECASE)
SECRET_ASSIGNMENT_RE = re.compile(r"(?i)(\b(?:api[_-]?key|token|secret|password|passwd|authorization|credential|bearer)\b\s*[:=]\s*)([^\s,'\"}]{4,})")
BEARER_RE = re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{8,}")
OPENAI_KEY_RE = re.compile(r"sk-[A-Za-z0-9_\-]{8,}")

REDACTED = "<redacted>"


def redact_text(value: str) -> str:
    """Redact obvious inline secret material from free text."""
    redacted = SECRET_ASSIGNMENT_RE.sub(lambda match: f"{match.group(1)}{REDACTED}", value)
    redacted = BEARER_RE.sub(f"Bearer {REDACTED}", redacted)
    redacted = OPENAI_KEY_RE.sub(REDACTED, redacted)
    return redacted


def redact_value(value: Any) -> Any:
    """Recursively redact secret-looking keys and string values."""
    if isinstance(value, dict):
        safe: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            safe[key_text] = REDACTED if SECRET_KEY_RE.search(key_text) else redact_value(item)
        return safe
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, tuple):
        return [redact_value(item) for item in value]
    if isinstance(value, str):
        return redact_text(value)
    return value


def redact_json_text(value: str | None) -> str | None:
    """Redact a JSON string when possible, otherwise redact as free text."""
    if value is None:
        return None
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        return redact_text(value)
    return json.dumps(redact_value(decoded), ensure_ascii=False, sort_keys=True)
