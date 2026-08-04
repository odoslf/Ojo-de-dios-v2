"""Controlled in-process job runner for registered techniques."""

from app.contracts.evidence_contract import (
    RESULT_FAILED,
    RESULT_MANUAL_REQUIRED,
    RESULT_MISSING_TOOL,
    RESULT_PARTIAL,
    RESULT_SKIPPED,
    RESULT_SUCCESS,
)
from app.contracts.job_contract import (
    JOB_MODE_DEMO,
    JOB_MODE_DRY_RUN,
    JOB_STATUS_FAILED,
    JOB_STATUS_MANUAL_REQUIRED,
    JOB_STATUS_PARTIAL,
    JOB_STATUS_STOPPED,
    JOB_STATUS_SUCCESS,
    JobRequest,
    JobResult,
    validate_job_request,
)
from app.contracts.technique_contract import TechniqueExecutionContext
from app.core.errors import ContractError
from app.core.job_runtime_control import is_job_stop_requested
from app.core.kill_switch import KillSwitchController, get_global_kill_switch
from app.core.technique_registry import TechniqueRegistry
from app.workers.android_worker import AndroidWorker
from app.workers.base_worker import BaseWorker, WorkerResult
from app.workers.cloud_worker import CloudWorker
from app.workers.demo_worker import DemoWorker
from app.workers.docker_worker import DockerWorker
from app.workers.hackrf_worker import HackRFWorker
from app.workers.hardware_worker import HardwareWorker
from app.workers.hermes_lab_worker import HermesLabWorker
from app.workers.ops_worker import OpsWorker
from app.workers.phishing_worker import PhishingWorker
from app.workers.scraping_worker import ScrapingWorker
from app.workers.windows_worker import WindowsWorker
from app.workers.wsl_worker import WSLWorker


class JobRunner:
    """Resolve a registered technique and run it through an available worker."""

    def __init__(
        self,
        registry: TechniqueRegistry,
        workers: list[BaseWorker] | None = None,
        kill_switch: KillSwitchController | None = None,
        evidence_store: object | None = None,
    ) -> None:
        self.registry = registry
        self.workers = workers if workers is not None else self._default_workers()
        self.kill_switch = kill_switch if kill_switch is not None else get_global_kill_switch()
        self.evidence_store = evidence_store

    def get_worker(self, worker_name: str) -> BaseWorker | None:
        """Return a worker that can handle the requested worker name."""
        for worker in self.workers:
            if worker.can_handle(worker_name):
                return worker
        return None

    def run_job(self, request: JobRequest) -> JobResult:
        """Run every selected technique in order and aggregate their real worker outcomes."""
        validate_job_request(request)
        try:
            self.kill_switch.ensure_can_start_job()
        except ContractError:
            return JobResult(
                job_id=request.job_id,
                status=JOB_STATUS_STOPPED,
                result_status=RESULT_FAILED,
                summary="Kill switch active: job was not started.",
                error="Kill switch active: new jobs are blocked.",
            )

        if not request.selected_techniques:
            return JobResult(
                job_id=request.job_id,
                status=JOB_STATUS_FAILED,
                result_status=RESULT_FAILED,
                summary="No techniques selected.",
                error="No techniques selected.",
            )

        worker_results: list[tuple[str, WorkerResult]] = []
        for technique_id in request.selected_techniques:
            if is_job_stop_requested(request.job_id):
                return self._aggregate_results(
                    request.job_id,
                    worker_results,
                    stopped=True,
                    stop_reason="Operator stop requested before next technique.",
                )
            try:
                self.kill_switch.ensure_can_start_job()
            except ContractError:
                return self._aggregate_results(
                    request.job_id,
                    worker_results,
                    stopped=True,
                    stop_reason="Kill switch active: new jobs are blocked.",
                )
            try:
                technique_cls = self.registry.require(technique_id)
                technique = technique_cls()
            except ContractError as error:
                worker_results.append(
                    (
                        technique_id,
                        WorkerResult(
                            worker_name="registry",
                            status="failed",
                            result_status=RESULT_FAILED,
                            summary="Technique could not be resolved.",
                            error=str(error),
                        ),
                    )
                )
                continue
            worker_name = "demo" if request.mode == JOB_MODE_DEMO else technique.worker
            worker = self.get_worker(worker_name)
            if worker is None:
                worker_results.append(
                    (
                        technique_id,
                        WorkerResult(
                            worker_name=worker_name,
                            status="failed",
                            result_status=RESULT_FAILED,
                            summary="Worker not available.",
                            error=f"Worker not available: {worker_name}",
                        ),
                    )
                )
                continue
            parameters = request.permissions_snapshot.get("parameters", {})
            context = TechniqueExecutionContext(
                target_id=request.target_id,
                run_id=request.job_id,
                mode=request.mode,
                parameters=parameters,
                confirmed=bool(request.permissions_snapshot.get("confirmed", False)),
                demo=request.mode == JOB_MODE_DEMO,
                dry_run=request.mode == JOB_MODE_DRY_RUN,
            )
            worker_result = worker.run_technique(technique, context)
            worker_results.append((technique_id, self._persist_worker_evidence(worker_result)))
            if is_job_stop_requested(request.job_id):
                return self._aggregate_results(
                    request.job_id,
                    worker_results,
                    stopped=True,
                    stop_reason="Operator stop requested after completed technique.",
                )
        return self._aggregate_results(request.job_id, worker_results)

    def _persist_worker_evidence(self, result: WorkerResult) -> WorkerResult:
        """Persist worker evidence when a concrete EvidenceStore is attached to this runner."""
        if self.evidence_store is None or not result.evidence:
            return result
        store_record = getattr(self.evidence_store, "store_record", None)
        if not callable(store_record):
            return WorkerResult(
                worker_name=result.worker_name,
                status="failed",
                result_status=RESULT_FAILED,
                summary="Evidence persistence failed.",
                error="Attached evidence_store does not expose store_record(record).",
                raw_result={"evidence_persistence": "store_record_missing"},
            )
        try:
            for record in result.evidence:
                store_record(record)
        except Exception as error:
            return WorkerResult(
                worker_name=result.worker_name,
                status="failed",
                result_status=RESULT_FAILED,
                summary="Evidence persistence failed.",
                error=str(error),
                raw_result={"evidence_persistence": "failed"},
            )
        return result

    def _aggregate_results(
        self,
        job_id: str,
        results: list[tuple[str, WorkerResult]],
        stopped: bool = False,
        stop_reason: str = "Kill switch active: new jobs are blocked.",
    ) -> JobResult:
        """Build one honest job result without dropping outcomes from selected techniques."""
        if stopped:
            summary = (
                "Kill switch active: remaining selected techniques were not started."
                if stop_reason.startswith("Kill switch")
                else "Job stopped cooperatively; remaining selected techniques were not started."
            )
            if results:
                summary = f"{summary} Completed before stop: {len(results)}."
            return JobResult(
                job_id=job_id,
                status=JOB_STATUS_STOPPED,
                result_status=RESULT_FAILED,
                evidence_ids=[evidence.evidence_id for _, item in results for evidence in item.evidence],
                summary=summary,
                error=stop_reason,
            )
        if not results:
            return JobResult(job_id=job_id, status=JOB_STATUS_FAILED, result_status=RESULT_FAILED, summary="No technique results.")

        failures = [item for _, item in results if item.status == "failed"]
        manual = [item for _, item in results if item.status == "manual_required"]
        successes = [item for _, item in results if item.status not in {"failed", "manual_required"}]
        evidence_ids = [evidence.evidence_id for _, item in results for evidence in item.evidence]
        summary = " | ".join(f"{technique_id}: {item.summary}" for technique_id, item in results)
        errors = [f"{technique_id}: {item.error}" for technique_id, item in results if item.error]
        if failures:
            status = JOB_STATUS_PARTIAL if successes or manual else JOB_STATUS_FAILED
            return JobResult(job_id, status, RESULT_FAILED, evidence_ids, summary, "; ".join(errors) or None)
        if manual:
            status = JOB_STATUS_PARTIAL if successes else JOB_STATUS_MANUAL_REQUIRED
            return JobResult(job_id, status, RESULT_MANUAL_REQUIRED, evidence_ids, summary, "; ".join(errors) or None)

        result_statuses = [item.result_status for _, item in results]
        unique_result_statuses = set(result_statuses)
        if unique_result_statuses == {RESULT_SUCCESS}:
            return JobResult(job_id, JOB_STATUS_SUCCESS, RESULT_SUCCESS, evidence_ids, summary)
        if unique_result_statuses == {RESULT_SKIPPED}:
            return JobResult(job_id, JOB_STATUS_SUCCESS, RESULT_SKIPPED, evidence_ids, summary)
        if unique_result_statuses == {RESULT_MISSING_TOOL}:
            return JobResult(job_id, JOB_STATUS_PARTIAL, RESULT_MISSING_TOOL, evidence_ids, summary, "; ".join(errors) or None)
        if RESULT_PARTIAL in unique_result_statuses or RESULT_MISSING_TOOL in unique_result_statuses or len(unique_result_statuses) > 1:
            return JobResult(job_id, JOB_STATUS_PARTIAL, RESULT_PARTIAL, evidence_ids, summary, "; ".join(errors) or None)
        return JobResult(job_id, JOB_STATUS_SUCCESS, result_statuses[0], evidence_ids, summary)

    def _default_workers(self) -> list[BaseWorker]:
        """Create the default in-process worker set."""
        return [
            DemoWorker(),
            WindowsWorker(),
            WSLWorker(),
            DockerWorker(),
            HardwareWorker(),
            HackRFWorker(),
            AndroidWorker(),
            PhishingWorker(),
            CloudWorker(),
            ScrapingWorker(),
            OpsWorker(),
            HermesLabWorker(),
        ]
