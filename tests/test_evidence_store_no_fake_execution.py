"""Evidence store execution-truth contract tests."""

import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine

from app.contracts.evidence_contract import EVIDENCE_QUALITY_LOW, EvidenceRecord
from app.core.evidence_store import EvidenceStore
from app.core.errors import ContractError
from app.db.session import create_session_factory, init_db


def _store(tmp_path) -> EvidenceStore:
    engine = create_engine(f"sqlite:///{tmp_path / 'evidence.db'}", connect_args={"check_same_thread": False})
    init_db(engine)
    session_factory = create_session_factory(engine)
    return EvidenceStore(session_factory(), base_path=tmp_path / "evidence")


def _record(**overrides) -> EvidenceRecord:
    values = {
        "evidence_id": "ev-1",
        "run_id": "run-1",
        "target_id": "target-1",
        "technique_id": "test.tech",
        "module_id": "test",
        "evidence_type": "json",
        "quality": EVIDENCE_QUALITY_LOW,
        "summary": "Test evidence",
        "content": {"hello": "world"},
        "source": "test",
        "demo": False,
        "real_execution": True,
    }
    values.update(overrides)
    return EvidenceRecord(**values)


def test_demo_evidence_cannot_be_marked_as_real_execution(tmp_path) -> None:
    store = _store(tmp_path)

    with pytest.raises(ContractError):
        store.store_record(_record(demo=True, real_execution=True))


def test_demo_evidence_is_stored_as_not_real_execution(tmp_path) -> None:
    store = _store(tmp_path)

    stored = store.store_record(_record(demo=True, real_execution=False))

    payload = json.loads(Path(stored.content_path).read_text(encoding="utf-8"))
    assert payload["demo"] is True
    assert payload["real_execution"] is False


def test_invalid_quality_fails_before_store(tmp_path) -> None:
    store = _store(tmp_path)

    with pytest.raises(ContractError):
        store.store_record(_record(quality="invalid"))


def test_empty_evidence_id_fails_before_store(tmp_path) -> None:
    store = _store(tmp_path)

    with pytest.raises(ContractError):
        store.store_record(_record(evidence_id=""))
