"""Minimal evidence store with database metadata and JSON content storage."""

import hashlib
import json
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.contracts.evidence_contract import EvidenceRecord, validate_evidence_record
from app.core.errors import ContractError
from app.core.secret_redaction import redact_text, redact_value
from app.db.models import Evidence
from app.db.repositories.evidence_repository import EvidenceRepository


@dataclass
class StoredEvidence:
    """Stored evidence metadata returned by EvidenceStore."""

    evidence_id: str
    run_id: str
    target_id: str
    technique_id: str
    module_id: str
    evidence_type: str
    quality: str
    summary: str
    source: str
    content_hash: str
    content_path: str
    demo: bool
    real_execution: bool
    created_at: str


@dataclass(frozen=True)
class StoredEvidenceContent:
    """Verified content read result for one evidence payload."""

    evidence_id: str
    content: dict[str, Any] | None
    verified: bool
    failure_reason: str | None = None


class EvidenceStore:
    """Store validated evidence records and their JSON content payloads."""

    def __init__(
        self,
        session: Any,
        base_path: str | Path = "storage/evidence",
    ) -> None:
        self.session = session
        self.base_path = Path(base_path)
        self.repository = EvidenceRepository(session)

    def store_record(self, record: EvidenceRecord) -> StoredEvidence:
        """Validate, write, hash, and persist an evidence record."""
        validate_evidence_record(record)
        if record.created_at is None:
            record.created_at = datetime.now(UTC).isoformat()
        safe_record = replace(
            record,
            summary=redact_text(record.summary),
            source=redact_text(record.source),
            content=redact_value(record.content),
        )
        payload = self._build_content_payload(safe_record)
        content_hash = self._hash_payload(payload)
        content_path = self._write_payload(safe_record.evidence_id, payload)
        model = self.repository.create_evidence(safe_record, content_hash, str(content_path))
        commit = getattr(self.session, "commit", None)
        if callable(commit):
            commit()
        refresh = getattr(self.session, "refresh", None)
        if callable(refresh):
            refresh(model)
        return self._model_to_stored(model)

    def get_record(self, evidence_id: str) -> StoredEvidence | None:
        """Return stored evidence metadata by evidence id."""
        model = self.repository.get_by_evidence_id(evidence_id)
        if model is None:
            return None
        return self._model_to_stored(model)

    def list_run(self, run_id: str, limit: int = 100) -> list[StoredEvidence]:
        """Return stored evidence metadata for a run."""
        return [self._model_to_stored(model) for model in self.repository.list_by_run_id(run_id, limit)]

    def list_target(self, target_id: str, limit: int = 100) -> list[StoredEvidence]:
        """Return stored evidence metadata for a target."""
        return [self._model_to_stored(model) for model in self.repository.list_by_target_id(target_id, limit)]

    def list_target_module(self, target_id: str, module_id: str, limit: int = 100) -> list[StoredEvidence]:
        """Return stored evidence metadata for one target/module pair."""
        return [
            self._model_to_stored(model)
            for model in self.repository.list_by_target_and_module(target_id, module_id, limit)
        ]

    def read_content(self, evidence_id: str) -> dict[str, Any] | None:
        """Return a stored JSON payload only when path custody and hash both verify."""
        return self.read_content_result(evidence_id).content

    def read_content_result(self, evidence_id: str) -> StoredEvidenceContent:
        """Return verified content plus an explicit reason when verification fails."""
        stored = self.get_record(evidence_id)
        if stored is None:
            return StoredEvidenceContent(evidence_id=evidence_id, content=None, verified=False, failure_reason="not_found")
        path = self._resolve_content_path(stored.content_path)
        if path is None:
            return StoredEvidenceContent(
                evidence_id=evidence_id,
                content=None,
                verified=False,
                failure_reason="content_path_outside_evidence_store",
            )
        if not path.is_file():
            return StoredEvidenceContent(
                evidence_id=evidence_id,
                content=None,
                verified=False,
                failure_reason="content_file_missing",
            )
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return StoredEvidenceContent(
                evidence_id=evidence_id,
                content=None,
                verified=False,
                failure_reason="content_json_unreadable",
            )
        if not isinstance(payload, dict):
            return StoredEvidenceContent(
                evidence_id=evidence_id,
                content=None,
                verified=False,
                failure_reason="content_json_not_object",
            )
        if self._hash_payload(payload) != stored.content_hash:
            return StoredEvidenceContent(
                evidence_id=evidence_id,
                content=None,
                verified=False,
                failure_reason="content_hash_mismatch",
            )
        return StoredEvidenceContent(evidence_id=evidence_id, content=payload, verified=True)

    def _resolve_content_path(self, content_path: str) -> Path | None:
        raw_path = Path(content_path)
        base_path = self.base_path if self.base_path.is_absolute() else Path.cwd() / self.base_path
        resolved_base = base_path.resolve()
        resolved_path = raw_path.resolve() if raw_path.is_absolute() else (Path.cwd() / raw_path).resolve()
        if resolved_path != resolved_base and resolved_base not in resolved_path.parents:
            return None
        return resolved_path

    def _build_content_payload(self, record: EvidenceRecord) -> dict[str, Any]:
        return {
            "evidence_id": record.evidence_id,
            "run_id": record.run_id,
            "target_id": record.target_id,
            "technique_id": record.technique_id,
            "module_id": record.module_id,
            "evidence_type": record.evidence_type,
            "quality": record.quality,
            "summary": record.summary,
            "content": record.content,
            "source": record.source,
            "demo": record.demo,
            "real_execution": record.real_execution,
            "created_at": record.created_at,
        }

    def _hash_payload(self, payload: dict[str, Any]) -> str:
        serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()

    def _content_file_path(self, evidence_id: str) -> Path:
        """Return the content path for a single evidence id without allowing path traversal."""
        if not evidence_id or evidence_id != evidence_id.strip():
            raise ContractError("Evidence id must be a non-empty file-safe identifier.")
        if evidence_id in {".", ".."} or "/" in evidence_id or "\\" in evidence_id:
            raise ContractError("Evidence id cannot contain path separators.")
        return self.base_path / f"{evidence_id}.json"

    def _write_payload(self, evidence_id: str, payload: dict[str, Any]) -> Path:
        content_path = self._content_file_path(evidence_id)
        resolved_base = (self.base_path if self.base_path.is_absolute() else Path.cwd() / self.base_path).resolve()
        resolved_content = content_path.resolve()
        if resolved_content != resolved_base and resolved_base not in resolved_content.parents:
            raise ContractError("Evidence content path escaped the evidence store.")
        self.base_path.mkdir(parents=True, exist_ok=True)
        temporary_path = content_path.with_suffix(content_path.suffix + ".tmp")
        temporary_path.write_text(
            json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary_path.replace(content_path)
        return content_path

    def _model_to_stored(self, model: Evidence) -> StoredEvidence:
        return StoredEvidence(
            evidence_id=model.evidence_id,
            run_id=model.run_id,
            target_id=model.target_id,
            technique_id=model.technique_id,
            module_id=model.module_id,
            evidence_type=model.evidence_type,
            quality=model.quality,
            summary=model.summary,
            source=model.source,
            content_hash=model.content_hash,
            content_path=model.content_path,
            demo=model.demo,
            real_execution=model.real_execution,
            created_at=model.created_at.isoformat(),
        )
