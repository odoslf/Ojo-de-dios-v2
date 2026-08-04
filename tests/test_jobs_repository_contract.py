"""Persisted jobs repository and target start route contract tests."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes_targets import TargetJobStartRequest, start_target
from app.contracts.job_contract import JOB_STATUS_SUCCESS, JobResult
from app.contracts.evidence_contract import RESULT_SKIPPED
from app.core.target_model import TARGET_DOMAIN, TargetRequest
from app.db.repositories.jobs_repository import JobsRepository
from app.db.repositories.targets_repository import TargetsRepository
from app.db.session import init_db


def _session_factory():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    init_db(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def test_jobs_repository_persists_and_completes_job() -> None:
    session_factory = _session_factory()
    with session_factory() as session:
        repository = JobsRepository(session)
        job = repository.create_queued_job(
            target_id="target-1",
            created_by="tester",
            mode="dry_run",
            selected_techniques=["test.technique"],
        )
        request = repository.to_job_request(job, permissions_snapshot={"confirmed": True})
        completed = repository.complete_job(
            job,
            JobResult(
                job_id=job.job_id,
                status=JOB_STATUS_SUCCESS,
                result_status=RESULT_SKIPPED,
                summary="Dry run completed.",
            ),
        )

        assert request.selected_techniques == ["test.technique"]
        assert request.permissions_snapshot == {"confirmed": True}
        assert completed.status == JOB_STATUS_SUCCESS
        assert completed.finished_at is not None
        assert repository.get_by_job_id(job.job_id) is not None
        assert repository.list_for_target("target-1")[0].job_id == job.job_id


def test_start_target_persists_job_when_runtime_techniques_are_available() -> None:
    session_factory = _session_factory()
    with session_factory() as session:
        targets = TargetsRepository(session)
        target = targets.create_target(TargetRequest(name="Example", target_type=TARGET_DOMAIN, value="example.com"))

        response = start_target(target.target_id, TargetJobStartRequest(), session=session)
        jobs = JobsRepository(session).list_for_target(target.target_id)

        assert response["execution_started"] is True
        assert response["plan"]["runnable_step_count"] > 0
        assert response["job"]["target_id"] == target.target_id
        assert response["runtime_registry"]["technique_count"] > 0
        assert len(jobs) == 1
        assert jobs[0].job_id == response["job"]["job_id"]
