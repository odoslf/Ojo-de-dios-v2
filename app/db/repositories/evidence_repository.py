"""Repository for evidence metadata records."""

from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.contracts.evidence_contract import EvidenceRecord, validate_evidence_record
from app.db.models import Evidence, EvidenceFile, utc_now


def _bounded_limit(limit: int) -> int:
    return min(max(limit, 1), 500)


def _created_at_from_record(record: EvidenceRecord) -> datetime:
    if record.created_at is None:
        return utc_now()
    return datetime.fromisoformat(record.created_at)


class EvidenceRepository:
    """Persistence operations for evidence metadata."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_evidence(
        self,
        record: EvidenceRecord,
        content_hash: str,
        content_path: str,
    ) -> Evidence:
        """Validate and persist evidence metadata."""
        validate_evidence_record(record)
        model = Evidence(
            evidence_id=record.evidence_id,
            run_id=record.run_id,
            target_id=record.target_id,
            technique_id=record.technique_id,
            module_id=record.module_id,
            evidence_type=record.evidence_type,
            quality=record.quality,
            summary=record.summary,
            source=record.source,
            demo=record.demo,
            real_execution=record.real_execution,
            content_hash=content_hash,
            content_path=content_path,
            created_at=_created_at_from_record(record),
        )
        self.session.add(model)
        self.session.flush()
        return model

    def get_by_evidence_id(self, evidence_id: str) -> Evidence | None:
        """Return evidence metadata by public evidence id."""
        return self.session.query(Evidence).filter(Evidence.evidence_id == evidence_id).one_or_none()

    def list_by_run_id(self, run_id: str, limit: int = 100) -> list[Evidence]:
        """Return evidence for a run ordered newest first."""
        return (
            self.session.query(Evidence)
            .filter(Evidence.run_id == run_id)
            .order_by(desc(Evidence.created_at), desc(Evidence.id))
            .limit(_bounded_limit(limit))
            .all()
        )

    def list_by_target_id(self, target_id: str, limit: int = 100) -> list[Evidence]:
        """Return evidence for a target ordered newest first."""
        return (
            self.session.query(Evidence)
            .filter(Evidence.target_id == target_id)
            .order_by(desc(Evidence.created_at), desc(Evidence.id))
            .limit(_bounded_limit(limit))
            .all()
        )

    def list_by_target_and_module(self, target_id: str, module_id: str, limit: int = 100) -> list[Evidence]:
        """Return evidence for a target/module pair ordered newest first."""
        return (
            self.session.query(Evidence)
            .filter(Evidence.target_id == target_id)
            .filter(Evidence.module_id == module_id)
            .order_by(desc(Evidence.created_at), desc(Evidence.id))
            .limit(_bounded_limit(limit))
            .all()
        )

    def add_file(
        self,
        evidence_id: str,
        file_path: str,
        file_hash: str,
        file_type: str,
    ) -> EvidenceFile:
        """Persist file metadata associated with an evidence id."""
        if not evidence_id:
            raise ValueError("Evidence id cannot be empty.")
        model = EvidenceFile(
            evidence_id=evidence_id,
            file_path=file_path,
            file_hash=file_hash,
            file_type=file_type,
        )
        self.session.add(model)
        self.session.flush()
        return model

    def list_files(self, evidence_id: str) -> list[EvidenceFile]:
        """Return file metadata associated with an evidence id."""
        return (
            self.session.query(EvidenceFile)
            .filter(EvidenceFile.evidence_id == evidence_id)
            .order_by(desc(EvidenceFile.created_at), desc(EvidenceFile.id))
            .all()
        )
