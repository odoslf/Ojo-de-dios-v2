"""Runtime target planning integration tests."""

from app.api import routes_targets
from app.contracts.technique_contract import BaseTechnique, STATUS_READY_PASSIVE
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.runtime_registry import RuntimeRegistrySnapshot
from app.core.target_model import TARGET_DOMAIN, TARGET_MODE_DRY_RUN, TargetRecord
from app.core.technique_registry import create_empty_registry


class RuntimePlanningTechnique(BaseTechnique):
    technique_id = "runtime.osint.domain_metadata"
    module_id = "m01_osint"
    display_name = "Runtime OSINT Domain Metadata"
    description = "Collects passive domain metadata for runtime planning integration tests."
    tool_name = "python"
    recommended_version = "builtin"
    runtime = "python"
    worker = "python"
    permission_level = PERMISSION_PASSIVE
    required_inputs = ["target"]
    expected_evidence = ["domain_metadata"]
    implementation_status = STATUS_READY_PASSIVE
    requires_user_implementation = False


def test_runtime_router_uses_runtime_registry_snapshot(monkeypatch) -> None:
    registry = create_empty_registry()
    registry.register(RuntimePlanningTechnique)
    snapshot = RuntimeRegistrySnapshot(registry=registry)
    monkeypatch.setattr(routes_targets, "get_runtime_registry_snapshot", lambda: snapshot)

    router, returned_snapshot = routes_targets._runtime_router()
    plan = router.plan_target(
        TargetRecord(
            target_id="target-1",
            name="Example",
            target_type=TARGET_DOMAIN,
            value="example.com",
            normalized_value="example.com",
            mode=TARGET_MODE_DRY_RUN,
            allowed_modules=["m01_osint"],
        )
    )

    assert returned_snapshot is snapshot
    assert router.list_registered_technique_ids() == ["runtime.osint.domain_metadata"]
    assert plan.steps[0].technique_id == "runtime.osint.domain_metadata"
    assert plan.steps[0].can_run_now is True
