"""M14 security-awareness campaign workspace and outcome normalization."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from app.core.target_model import TargetRecord
from app.core.target_workspace import bind_target_module_workspace

M14_MODULE_ID = "m14_phishing"
MAX_RECIPIENTS = 20_000
MAX_OUTCOMES = 20_000
MAX_TEXT_LENGTH = 8_000
VALID_CHANNELS = frozenset({"email", "sms", "chat"})
VALID_OUTCOME_EVENTS = frozenset({"delivered", "opened", "clicked", "reported", "training_completed"})
_CREDENTIAL_COLLECTION_PATTERNS = (
    re.compile(r"<input[^>]+type\s*=\s*['\"]?password", re.IGNORECASE),
    re.compile(r"\b(password|contrase(?:ñ|n)a|credential|credencial)\b", re.IGNORECASE),
)


def _text(value: object, name: str, *, max_length: int = MAX_TEXT_LENGTH, required: bool = True) -> str | None:
    text = str(value or "").strip()
    if not text:
        if required:
            raise ValueError(f"{name} is required.")
        return None
    if len(text) > max_length or any(character in text for character in "\x00\r\n"):
        raise ValueError(f"{name} is invalid or too long.")
    return text


def _recipient_hash(value: object) -> str:
    recipient = _text(value, "recipient", max_length=512)
    return hashlib.sha256((recipient or "").casefold().encode("utf-8")).hexdigest()


def _validate_training_url(value: object) -> str:
    url = _text(value, "training_url", max_length=2_048)
    parsed = urlparse(url or "")
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("training_url must be an absolute HTTPS URL.")
    return parsed._replace(fragment="").geturl()


def _validate_template(subject: str, body: str) -> None:
    content = f"{subject}\n{body}"
    if any(pattern.search(content) for pattern in _CREDENTIAL_COLLECTION_PATTERNS):
        raise ValueError("Campaign template must not request or collect credentials.")


@dataclass(frozen=True, slots=True)
class AwarenessCampaign:
    """Privacy-preserving campaign definition for a training exercise."""

    campaign_name: str
    channel: str
    subject: str
    body: str
    training_url: str
    recipient_hashes: tuple[str, ...]
    owner: str

    def to_dict(self) -> dict[str, object]:
        identity = f"{self.campaign_name}\n{self.channel}\n{self.training_url}\n{self.owner}"
        return {
            "campaign_id": hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16],
            "campaign_name": self.campaign_name,
            "channel": self.channel,
            "subject": self.subject,
            "body": self.body,
            "training_url": self.training_url,
            "recipient_hashes": list(self.recipient_hashes),
            "recipient_count": len(self.recipient_hashes),
            "owner": self.owner,
            "delivery_performed": False,
            "credential_collection_enabled": False,
        }


def awareness_campaign_from_payload(payload: dict[str, Any]) -> AwarenessCampaign:
    """Validate and normalize a campaign definition without storing recipient identities."""
    channel = (_text(payload.get("channel"), "channel", max_length=64) or "").casefold()
    if channel not in VALID_CHANNELS:
        raise ValueError("channel is invalid.")
    subject = _text(payload.get("subject", "Awareness training"), "subject", max_length=512) or ""
    body = _text(payload.get("body"), "body") or ""
    _validate_template(subject, body)
    raw_recipients = payload.get("recipients")
    if not isinstance(raw_recipients, list) or not raw_recipients or len(raw_recipients) > MAX_RECIPIENTS:
        raise ValueError(f"recipients must contain between 1 and {MAX_RECIPIENTS} entries.")
    recipient_hashes = tuple(sorted({_recipient_hash(recipient) for recipient in raw_recipients}))
    return AwarenessCampaign(
        campaign_name=_text(payload.get("campaign_name"), "campaign_name", max_length=512) or "",
        channel=channel,
        subject=subject,
        body=body,
        training_url=_validate_training_url(payload.get("training_url")),
        recipient_hashes=recipient_hashes,
        owner=_text(payload.get("owner", "local_operator"), "owner", max_length=512) or "local_operator",
    )


def _campaign_directory(target: TargetRecord, repo_root: Path | None) -> Path:
    root = Path.cwd() if repo_root is None else repo_root
    return bind_target_module_workspace(target, M14_MODULE_ID, repo_root=root).root_path / "evidence" / "awareness_campaigns"


def write_m14_awareness_campaign(target: TargetRecord, campaign: AwarenessCampaign, repo_root: Path | None = None) -> Path:
    """Persist an awareness campaign definition in the target M14 workspace."""
    directory = _campaign_directory(target, repo_root)
    directory.mkdir(parents=True, exist_ok=True)
    campaign_payload = campaign.to_dict()
    path = directory / f"{campaign_payload['campaign_id']}.json"
    path.write_text(json.dumps({
        "schema_version": 1,
        "target_id": target.target_id,
        "module_id": M14_MODULE_ID,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "campaign": campaign_payload,
        "outcome_summary": {"event_count": 0, "event_count_by_type": {}},
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def write_m14_awareness_outcomes(
    target: TargetRecord, campaign_id: str, outcomes: list[dict[str, Any]], repo_root: Path | None = None
) -> Path:
    """Attach imported awareness outcomes to an existing campaign using hashed recipients."""
    if not re.fullmatch(r"[0-9a-f]{16}", campaign_id):
        raise ValueError("campaign_id is invalid.")
    if not outcomes or len(outcomes) > MAX_OUTCOMES:
        raise ValueError(f"outcomes must contain between 1 and {MAX_OUTCOMES} entries.")
    path = _campaign_directory(target, repo_root) / f"{campaign_id}.json"
    if not path.is_file():
        raise ValueError("campaign does not exist.")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("campaign receipt is unreadable.") from exc
    campaign = payload.get("campaign") if isinstance(payload, dict) else None
    known_hashes = set(campaign.get("recipient_hashes", [])) if isinstance(campaign, dict) else set()
    normalized: list[dict[str, str]] = []
    for outcome in outcomes:
        if not isinstance(outcome, dict):
            raise ValueError("outcomes must contain objects.")
        event = (_text(outcome.get("event"), "event", max_length=64) or "").casefold()
        if event not in VALID_OUTCOME_EVENTS:
            raise ValueError("outcome event is invalid.")
        recipient_hash = _recipient_hash(outcome.get("recipient"))
        if recipient_hash not in known_hashes:
            raise ValueError("outcome recipient does not belong to this campaign.")
        normalized.append({
            "recipient_sha256": recipient_hash,
            "event": event,
            "observed_at": _text(outcome.get("observed_at"), "observed_at", max_length=128) or "",
        })
    unique = {(item["recipient_sha256"], item["event"], item["observed_at"]): item for item in normalized}
    existing = payload.get("outcomes", [])
    current = [item for item in existing if isinstance(item, dict)] if isinstance(existing, list) else []
    merged = {(str(item.get("recipient_sha256")), str(item.get("event")), str(item.get("observed_at"))): item for item in current}
    merged.update(unique)
    final_outcomes = list(merged.values())
    event_counts = Counter(str(item["event"]) for item in final_outcomes)
    payload["outcomes"] = final_outcomes
    payload["outcome_summary"] = {"event_count": len(final_outcomes), "event_count_by_type": dict(sorted(event_counts.items()))}
    payload["outcomes_recorded_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def read_m14_awareness_campaigns(target: TargetRecord, repo_root: Path | None = None) -> tuple[dict[str, object], ...]:
    """Read persisted M14 campaign receipts and imported outcome summaries."""
    directory = _campaign_directory(target, repo_root)
    if not directory.is_dir():
        return ()
    campaigns: list[dict[str, object]] = []
    for path in sorted(directory.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict) and payload.get("target_id") == target.target_id and payload.get("module_id") == M14_MODULE_ID:
            payload["path"] = path.as_posix()
            campaigns.append(payload)
    return tuple(campaigns)
