"""Minimal AI context builder."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AIContext:
    """Small context object supplied to local AI prompts."""

    target_id: str | None = None
    target_type: str | None = None
    target_value: str | None = None
    available_techniques: list[dict[str, Any]] = field(default_factory=list)
    evidence_summaries: list[dict[str, Any]] = field(default_factory=list)
    mode: str = "dry_run"


def build_basic_context(
    target_id: str | None = None,
    target_type: str | None = None,
    target_value: str | None = None,
    available_techniques: list[dict[str, Any]] | None = None,
    evidence_summaries: list[dict[str, Any]] | None = None,
    mode: str = "dry_run",
) -> AIContext:
    """Build a minimal context without external lookups."""
    return AIContext(
        target_id=target_id,
        target_type=target_type,
        target_value=target_value,
        available_techniques=list(available_techniques or []),
        evidence_summaries=list(evidence_summaries or []),
        mode=mode,
    )


def context_to_dict(context: AIContext) -> dict[str, Any]:
    """Convert an AIContext into a plain dictionary."""
    return {
        "target_id": context.target_id,
        "target_type": context.target_type,
        "target_value": context.target_value,
        "available_techniques": context.available_techniques,
        "evidence_summaries": context.evidence_summaries,
        "mode": context.mode,
    }
