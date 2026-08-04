"""Contract tests for target repository persistence."""

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session

from app.core.target_fingerprint import build_target_fingerprint
from app.core.target_model import TARGET_DOMAIN, TargetRequest
from app.db import models
from app.db.base import Base
from app.db.repositories.targets_repository import TargetsRepository
from app.db.session import init_db


def test_targets_repository_persists_targets_and_fingerprints() -> None:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    init_db(engine)
    assert "jobs" in Base.metadata.tables
    assert "evidence" in Base.metadata.tables

    with Session(engine) as session:
        repository = TargetsRepository(session)
        target = repository.create_target(TargetRequest(name="Example", target_type=TARGET_DOMAIN, value="Example.COM"))
        assert target.target_id
        assert target.normalized_value == "example.com"

        retrieved = repository.get_by_target_id(target.target_id)
        assert retrieved is not None
        assert retrieved.name == "Example"

        fingerprint = build_target_fingerprint(target.target_id, target.target_type, target.value)
        stored_fingerprint = repository.create_fingerprint(fingerprint)
        assert stored_fingerprint.normalized_value == "example.com"

        latest_fingerprint = repository.get_latest_fingerprint(target.target_id)
        assert latest_fingerprint is not None
        assert latest_fingerprint.id == stored_fingerprint.id

        second = repository.create_target(TargetRequest(name="Second", target_type=TARGET_DOMAIN, value="second.example"))
        listed = repository.list_targets(limit=1)
        assert len(listed) == 1
        assert listed[0].target_id == second.target_id

    assert hasattr(models, "Job")
    assert hasattr(models, "Evidence")
