"""Evidence repository contract tests."""

from sqlalchemy import create_engine, inspect

from app.contracts.evidence_contract import EVIDENCE_QUALITY_LOW, EvidenceRecord
from app.db.repositories.evidence_repository import EvidenceRepository
from app.db.session import create_session_factory, init_db


def _session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'evidence.db'}", connect_args={"check_same_thread": False})
    init_db(engine)
    session_factory = create_session_factory(engine)
    return engine, session_factory()


def _record(evidence_id: str = "ev-1") -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=evidence_id,
        run_id="run-1",
        target_id="target-1",
        technique_id="test.tech",
        module_id="test",
        evidence_type="json",
        quality=EVIDENCE_QUALITY_LOW,
        summary="Test evidence",
        content={"hello": "world"},
        source="test",
        demo=False,
        real_execution=True,
        created_at="2026-05-30T00:00:00+00:00",
    )


def test_evidence_repository_persists_metadata_and_files(tmp_path) -> None:
    engine, session = _session(tmp_path)
    inspector = inspect(engine)
    assert "evidence" in inspector.get_table_names()
    assert "evidence_files" in inspector.get_table_names()

    repository = EvidenceRepository(session)
    model = repository.create_evidence(_record(), "abc123", "storage/evidence/ev-1.json")
    session.commit()

    assert model.evidence_id == "ev-1"
    assert repository.get_by_evidence_id("ev-1").content_hash == "abc123"
    assert [item.evidence_id for item in repository.list_by_run_id("run-1")] == ["ev-1"]
    assert [item.evidence_id for item in repository.list_by_target_id("target-1")] == ["ev-1"]

    file_model = repository.add_file("ev-1", "storage/evidence/file.txt", "filehash", "text")
    session.commit()

    assert file_model.evidence_id == "ev-1"
    files = repository.list_files("ev-1")
    assert len(files) == 1
    assert files[0].file_hash == "filehash"
