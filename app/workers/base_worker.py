"""Base worker primitives for controlled internal job execution."""

from dataclasses import dataclass, field
from typing import Any

from app.contracts.evidence_contract import (
    EvidenceRecord,
    RESULT_FAILED,
    RESULT_MANUAL_REQUIRED,
    RESULT_SKIPPED,
    RESULT_SUCCESS,
)
from app.contracts.manual_required import ManualImplementationRequired
from app.contracts.technique_contract import (
    BaseTechnique,
    TechniqueExecutionContext,
    TechniqueExecutionResult,
)
from app.core.errors import ContractError


@dataclass
class WorkerResult:
    """Controlled result returned by a worker after handling a technique."""

    worker_name: str
    status: str
    result_status: str
    summary: str
    evidence: list[EvidenceRecord] = field(default_factory=list)
    raw_result: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class BaseWorker:
    """Base worker that only delegates to in-process technique contracts."""

    worker_name: str = "base"

    def can_handle(self, worker_name: str) -> bool:
        """Return whether this worker handles the requested worker name."""
        return worker_name == self.worker_name

    def run_technique(
        self,
        technique: BaseTechnique,
        context: TechniqueExecutionContext,
    ) -> WorkerResult:
        """Run a technique through the controlled worker contract."""
        if context.demo is True:
            return WorkerResult(
                worker_name=self.worker_name,
                status="success",
                result_status=RESULT_SKIPPED,
                summary="Demo mode: no real execution performed.",
                raw_result={"demo": True, "real_execution": False},
            )

        if context.dry_run is True:
            technique.validate_metadata()
            return WorkerResult(
                worker_name=self.worker_name,
                status="success",
                result_status=RESULT_SKIPPED,
                summary="Dry run: technique metadata validated, no execution performed.",
                raw_result={"dry_run": True, "real_execution": False},
            )

        try:
            result = technique.execute(context)
        except ManualImplementationRequired as error:
            return WorkerResult(
                worker_name=self.worker_name,
                status="manual_required",
                result_status=RESULT_MANUAL_REQUIRED,
                summary=str(error),
                error=str(error),
            )
        except ContractError:
            raise
        except Exception as error:
            return WorkerResult(
                worker_name=self.worker_name,
                status="failed",
                result_status=RESULT_FAILED,
                summary="Technique execution failed.",
                error=str(error),
            )

        return self._from_execution_result(result)

    def _from_execution_result(self, result: TechniqueExecutionResult) -> WorkerResult:
        """Convert a technique execution result into a worker result."""
        return WorkerResult(
            worker_name=self.worker_name,
            status="success" if result.result_status == RESULT_SUCCESS else "finished",
            result_status=result.result_status,
            summary=result.summary,
            evidence=result.evidence,
            raw_result=result.raw_result,
            error=result.error,
        )
