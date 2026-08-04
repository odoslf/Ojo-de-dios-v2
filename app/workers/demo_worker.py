"""Demo worker for non-real demo execution."""

from app.contracts.evidence_contract import (
    EVIDENCE_QUALITY_LOW,
    EvidenceRecord,
    RESULT_FAILED,
    RESULT_SKIPPED,
)
from app.contracts.technique_contract import BaseTechnique, TechniqueExecutionContext
from app.core.demo_mode import ensure_demo_allowed
from app.core.errors import ContractError
from app.core.fixtures import DemoFixtureStore
from app.workers.base_worker import BaseWorker, WorkerResult


class DemoWorker(BaseWorker):
    """Worker selected for demo mode."""

    worker_name = "demo"

    def run_technique(
        self,
        technique: BaseTechnique,
        context: TechniqueExecutionContext,
    ) -> WorkerResult:
        """Return non-real demo results, optionally backed by local fixtures."""
        if context.demo is not True:
            return WorkerResult(
                worker_name=self.worker_name,
                status="failed",
                result_status=RESULT_FAILED,
                summary="DemoWorker requires demo context.",
                error="DemoWorker requires demo context.",
            )

        try:
            ensure_demo_allowed(technique.can_run_in_demo)
        except ContractError as error:
            return WorkerResult(
                worker_name=self.worker_name,
                status="failed",
                result_status=RESULT_FAILED,
                summary=str(error),
                error=str(error),
                raw_result={"demo": True, "real_execution": False},
            )

        fixture_name = technique.demo_behavior.get("fixture")
        if not fixture_name:
            return WorkerResult(
                worker_name=self.worker_name,
                status="success",
                result_status=RESULT_SKIPPED,
                summary="Demo mode: no fixture configured, no real execution performed.",
                raw_result={"demo": True, "real_execution": False},
            )

        try:
            fixture = DemoFixtureStore().load(fixture_name)
        except FileNotFoundError as error:
            return WorkerResult(
                worker_name=self.worker_name,
                status="failed",
                result_status=RESULT_FAILED,
                summary="Demo fixture not found.",
                error=str(error),
                raw_result={"demo": True, "real_execution": False, "fixture": fixture_name},
            )

        summary = f"Demo fixture loaded: {fixture_name}"
        record = EvidenceRecord(
            evidence_id=f"demo-{context.run_id}-{technique.technique_id}",
            run_id=context.run_id,
            target_id=context.target_id,
            technique_id=technique.technique_id,
            module_id=technique.module_id,
            evidence_type="demo_fixture",
            quality=EVIDENCE_QUALITY_LOW,
            summary=summary,
            content=fixture.payload,
            source="fixture",
            demo=True,
            real_execution=False,
        )
        return WorkerResult(
            worker_name=self.worker_name,
            status="success",
            result_status=RESULT_SKIPPED,
            summary=summary,
            evidence=[record],
            raw_result={"demo": True, "real_execution": False, "fixture": fixture_name},
        )
