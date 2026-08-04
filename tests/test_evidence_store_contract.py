"""Evidence store contract tests."""

import hashlib
import json
from pathlib import Path

from sqlalchemy import create_engine

from app.contracts.evidence_contract import EVIDENCE_QUALITY_LOW, EvidenceRecord
from app.core.evidence_store import EvidenceStore
from app.db.session import create_session_factory, init_db


def _session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'evidence.db'}", connect_args={"check_same_thread": False})
    init_db(engine)
    session_factory = create_session_factory(engine)
    return session_factory()


def _record() -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id="ev-1",
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
    )


def test_evidence_store_writes_json_hash_and_metadata(tmp_path) -> None:
    store = EvidenceStore(_session(tmp_path), base_path=tmp_path / "evidence")

    stored = store.store_record(_record())

    content_path = Path(stored.content_path)
    assert content_path.exists()
    assert stored.content_hash

    loaded = store.get_record("ev-1")
    assert loaded is not None
    assert loaded.evidence_id == "ev-1"
    assert loaded.content_hash == stored.content_hash

    run_items = store.list_run("run-1")
    assert [item.evidence_id for item in run_items] == ["ev-1"]

    payload = json.loads(content_path.read_text(encoding="utf-8"))
    assert payload["evidence_id"] == "ev-1"
    assert payload["content"] == {"hello": "world"}

    stable_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    assert stable_hash == stored.content_hash


def test_evidence_store_redacts_sensitive_content_before_persisting(tmp_path) -> None:
    store = EvidenceStore(_session(tmp_path), base_path=tmp_path / "evidence")
    record = _record()
    record.evidence_id = "ev-secret"
    record.summary = "operator note token=abcdef123456"
    record.source = "Bearer abcdef123456"
    record.content = {
        "api_key": "super-secret",
        "nested": {"message": "password=hunter2", "safe": "ok"},
    }

    stored = store.store_record(record)
    raw_payload = Path(stored.content_path).read_text(encoding="utf-8")
    payload = json.loads(raw_payload)

    assert "super-secret" not in raw_payload
    assert "hunter2" not in raw_payload
    assert "abcdef123456" not in raw_payload
    assert payload["content"]["api_key"] == "<redacted>"
    assert payload["content"]["nested"]["safe"] == "ok"
    assert payload["summary"] == "operator note token=<redacted>"
    assert payload["source"] == "Bearer <redacted>"
    assert stored.summary == "operator note token=<redacted>"
    assert stored.source == "Bearer <redacted>"
    assert store.get_record("ev-secret").summary == "operator note token=<redacted>"
    assert store.read_content_result("ev-secret").verified is True
