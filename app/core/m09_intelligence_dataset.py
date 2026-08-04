"""M09 normalized intelligence dataset from already collected, authorized records."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from app.core.target_model import TargetRecord
from app.core.target_workspace import bind_target_module_workspace

M09_MODULE_ID = "m09_scraping_intelligence"
MAX_RECORDS = 5_000
MAX_TEXT_LENGTH = 20_000


def normalize_intelligence_record(payload: dict[str, Any]) -> dict[str, object]:
    """Normalize one externally collected record without fetching its URL or retaining raw HTML."""
    url = str(payload.get("url", "")).strip()
    source = str(payload.get("source", "operator_import")).strip()
    title = str(payload.get("title", "")).strip()
    text = str(payload.get("text", "")).strip()
    observed_at = str(payload.get("observed_at", "")).strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("url must be an absolute http or https URL.")
    if not source or len(source) > 512 or not observed_at or len(observed_at) > 128:
        raise ValueError("source and observed_at are required and bounded.")
    if len(title) > 2_000 or len(text) > MAX_TEXT_LENGTH:
        raise ValueError("title or text exceeds the M09 intake limit.")
    canonical_url = parsed._replace(fragment="").geturl()
    content_hash = hashlib.sha256(f"{canonical_url}\n{title}\n{text}".encode("utf-8")).hexdigest()
    return {
        "record_id": content_hash[:16],
        "url": canonical_url,
        "host": parsed.hostname,
        "title": title,
        "text": text,
        "source": source,
        "observed_at": observed_at,
        "content_sha256": content_hash,
        "target_request_performed": False,
    }


def write_m09_intelligence_dataset(target: TargetRecord, records: list[dict[str, object]], repo_root: Path | None = None) -> Path:
    """Persist a deduplicated normalized M09 dataset; no connector or scraper is run."""
    if not records or len(records) > MAX_RECORDS:
        raise ValueError(f"record count must be between 1 and {MAX_RECORDS}.")
    unique: dict[str, dict[str, object]] = {}
    for record in records:
        record_id = record.get("record_id")
        if not isinstance(record_id, str):
            raise ValueError("records must be normalized M09 records.")
        unique.setdefault(record_id, record)
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M09_MODULE_ID, repo_root=root)
    path = binding.root_path / "outputs" / "normalized_records.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "schema_version": 1,
        "target_id": target.target_id,
        "module_id": M09_MODULE_ID,
        "normalized_at": datetime.now(timezone.utc).isoformat(),
        "records": list(unique.values()),
        "input_record_count": len(records),
        "deduplicated_record_count": len(unique),
        "connector_execution_performed": False,
        "target_activity_performed": False,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def read_m09_intelligence_dataset(target: TargetRecord, repo_root: Path | None = None) -> dict[str, object] | None:
    """Read persisted M09 normalized records without requesting any source URL."""
    root = Path.cwd() if repo_root is None else repo_root
    path = bind_target_module_workspace(target, M09_MODULE_ID, repo_root=root).root_path / "outputs" / "normalized_records.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None
