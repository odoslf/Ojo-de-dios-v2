"""M16 readiness contract tests."""

import json
from pathlib import Path

from app.modules.m16_ops_quality.status import (
    MISTRAL_OFFICIAL_MODEL,
    STATUS_DISABLED,
    STATUS_FAILED,
    STATUS_KNOWLEDGE_MISSING,
    STATUS_KNOWLEDGE_STALE,
    STATUS_MODEL_MISSING,
    STATUS_PARTIAL,
    STATUS_READY_CONTROLLED,
    STATUS_READY_LOCAL_AI,
    build_m16_readiness_report,
    check_angel_hermes_runtime_status,
    check_ai_environment,
    check_evidence_quality,
    check_export_preparation,
    check_knowledge_base,
    check_runtime_cleanup_plan,
    check_version_lock_readiness,
    derive_overall_status,
    write_runtime_status,
)


def test_m16_report_uses_real_repository_checks_without_fake_ready() -> None:
    report = build_m16_readiness_report(env={"AI_ENABLED": "0"})
    statuses = {component.name: component.status for component in report.components}

    assert report.module_id == "m16_ops_quality"
    assert statuses["module_manifest_integrity"] == STATUS_READY_CONTROLLED
    assert statuses["runtime_storage"] == STATUS_READY_CONTROLLED
    assert statuses["module_workspace_root"] == STATUS_READY_CONTROLLED
    assert statuses["ai_prompts"] == STATUS_READY_CONTROLLED
    assert statuses["knowledge_base"] == STATUS_KNOWLEDGE_MISSING
    assert statuses["ai_environment"] == STATUS_DISABLED
    assert statuses["toolhealth_python_runtime"] == STATUS_READY_CONTROLLED
    assert report.status == STATUS_PARTIAL


def test_ai_environment_does_not_evaluate_mistral_or_angel_when_global_ai_is_disabled() -> None:
    status = check_ai_environment(
        {
            "AI_ENABLED": "0",
            "MISTRAL_ENABLED": "1",
            "ANGEL_ENABLED": "1",
            "DEEPSEEK_API_KEY": "super-secret",
        }
    )

    assert status.status == STATUS_DISABLED
    assert status.required is False
    assert status.details["mistral_evaluated"] is False
    assert status.details["angel_evaluated"] is False
    assert status.details["deepseek_api_key"] == "set"
    assert "super-secret" not in json.dumps(status.to_dict())


def test_ai_environment_requires_official_mistral_model_when_mistral_is_enabled() -> None:
    wrong_model = check_ai_environment(
        {
            "AI_ENABLED": "1",
            "MISTRAL_ENABLED": "1",
            "MISTRAL_MODEL": "mistral:latest",
        }
    )
    official_model = check_ai_environment(
        {
            "AI_ENABLED": "1",
            "MISTRAL_ENABLED": "1",
            "MISTRAL_MODEL": MISTRAL_OFFICIAL_MODEL,
        }
    )

    assert wrong_model.status == STATUS_MODEL_MISSING
    assert official_model.status == STATUS_READY_CONTROLLED


def test_knowledge_base_missing_is_partial_not_failed(tmp_path: Path) -> None:
    knowledge_dir = tmp_path / "storage" / "knowledge"
    knowledge_dir.mkdir(parents=True)
    (knowledge_dir / ".gitkeep").write_text("", encoding="utf-8")

    status = check_knowledge_base(tmp_path)

    assert status.status == STATUS_KNOWLEDGE_MISSING
    assert status.required is False


def test_knowledge_base_requires_auditable_status_manifest(tmp_path: Path) -> None:
    knowledge_dir = tmp_path / "storage" / "knowledge"
    knowledge_dir.mkdir(parents=True)
    (knowledge_dir / "chunks.jsonl").write_text("{}\n", encoding="utf-8")

    status = check_knowledge_base(tmp_path)

    assert status.status == STATUS_KNOWLEDGE_STALE
    assert status.required is False


def test_knowledge_base_ready_with_docs_only_manifest(tmp_path: Path) -> None:
    knowledge_dir = tmp_path / "storage" / "knowledge"
    knowledge_dir.mkdir(parents=True)
    (knowledge_dir / "chunks.jsonl").write_text("{}\n", encoding="utf-8")
    (knowledge_dir / "source_manifest.json").write_text('{"sources":[]}\n', encoding="utf-8")
    (knowledge_dir / "knowledge_status.json").write_text(
        json.dumps(
            {
                "status": "READY_DOCS_ONLY",
                "requested_mode": "docs-only",
                "semantic_index_status": "SKIPPED",
                "source_count": 2,
                "chunk_count": 3,
            }
        ),
        encoding="utf-8",
    )

    status = check_knowledge_base(tmp_path)

    assert status.status == STATUS_READY_LOCAL_AI
    assert status.required is False
    assert status.details["knowledge_status"] == "READY_DOCS_ONLY"
    assert status.details["semantic_index_status"] == "SKIPPED"


def test_overall_status_is_partial_for_missing_optional_knowledge() -> None:
    report = build_m16_readiness_report(env={"AI_ENABLED": "0"})

    assert derive_overall_status(report.components) == STATUS_PARTIAL


def test_runtime_status_writer_persists_json_without_secrets(tmp_path: Path) -> None:
    report = build_m16_readiness_report(
        env={
            "AI_ENABLED": "0",
            "DEEPSEEK_API_KEY": "super-secret",
        }
    )
    status_path = write_runtime_status(report, tmp_path)
    payload = status_path.read_text(encoding="utf-8")
    loaded = json.loads(payload)

    assert status_path.name == "m16_readiness_status.json"
    assert loaded["module_id"] == "m16_ops_quality"
    assert "super-secret" not in payload


def test_evidence_quality_detects_contract_violations_and_secret_exposure(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "storage" / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "bad.json").write_text(
        json.dumps(
            {
                "evidence_id": "ev-1",
                "run_id": "run-1",
                "target_id": "target-1",
                "technique_id": "tech-1",
                "module_id": "m16_ops_quality",
                "evidence_type": "json",
                "quality": "invalid",
                "summary": "bad",
                "source": "test",
                "demo": True,
                "real_execution": True,
                "created_at": "2026-07-22T00:00:00+00:00",
                "content": {"api_key": "sk-example-secret-value"},
            }
        ),
        encoding="utf-8",
    )

    status = check_evidence_quality(tmp_path)

    assert status.status == "FAILED"
    reasons = {failure["reason"] for failure in status.details["failures"]}
    assert "invalid_quality" in reasons
    assert "demo_marked_real_execution" in reasons
    assert "potential_secret_exposure" in reasons


def test_evidence_quality_accepts_valid_stored_payload(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "storage" / "evidence"
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "good.json").write_text(
        json.dumps(
            {
                "evidence_id": "ev-1",
                "run_id": "run-1",
                "target_id": "target-1",
                "technique_id": "tech-1",
                "module_id": "m16_ops_quality",
                "evidence_type": "json",
                "quality": "high",
                "summary": "valid",
                "source": "test",
                "demo": False,
                "real_execution": True,
                "created_at": "2026-07-22T00:00:00+00:00",
                "content": {"finding_count": 1},
            }
        ),
        encoding="utf-8",
    )

    status = check_evidence_quality(tmp_path)

    assert status.status == STATUS_READY_CONTROLLED
    assert status.details["audited_files"] == 1


def test_runtime_cleanup_plan_lists_candidates_without_deleting(tmp_path: Path) -> None:
    runtime_dir = tmp_path / "storage" / "runtime"
    runtime_dir.mkdir(parents=True)
    temporary = runtime_dir / "tmp_probe.tmp"
    status_json = runtime_dir / "m16_readiness_status.json"
    temporary.write_text("temporary", encoding="utf-8")
    status_json.write_text("{}", encoding="utf-8")

    status = check_runtime_cleanup_plan(tmp_path)

    assert status.status == STATUS_READY_CONTROLLED
    assert status.details["candidate_count"] == 1
    assert status.details["deletes_performed"] == 0
    assert temporary.exists()
    assert status_json.exists()


def test_export_preparation_requires_export_contract_files(tmp_path: Path) -> None:
    status = check_export_preparation(tmp_path)

    assert status.status == STATUS_PARTIAL
    assert "scripts/export_project_zip.py" in status.details["missing"]


def test_version_lock_readiness_locks_python_without_network_resolution() -> None:
    status = check_version_lock_readiness()

    assert status.status in {STATUS_READY_CONTROLLED, STATUS_PARTIAL}
    assert status.details["locked"][0]["tool_id"] == "python.runtime"
    assert status.details["locked"][0]["status"] == "LOCKED"


def test_angel_hermes_runtime_status_redacts_secret_failures(tmp_path: Path) -> None:
    runtime_dir = tmp_path / "storage" / "runtime"
    runtime_dir.mkdir(parents=True)
    (runtime_dir / "angel_hermes_status.json").write_text(
        json.dumps(
            {
                "status": "READY_CONTROLLED",
                "provider": "deepseek",
                "api_key": "sk-example-secret-value",
            }
        ),
        encoding="utf-8",
    )

    status = check_angel_hermes_runtime_status(tmp_path)

    assert status.status == "FAILED"
    assert "sk-example-secret-value" not in json.dumps(status.to_dict())


def test_guided_clean_runtime_deletes_only_planned_temporary_artifacts(tmp_path: Path) -> None:
    runtime_dir = tmp_path / "storage" / "runtime"
    runtime_dir.mkdir(parents=True)
    temporary = runtime_dir / "tmp_probe.tmp"
    preserved = runtime_dir / "m16_readiness_status.json"
    temporary.write_text("temporary", encoding="utf-8")
    preserved.write_text("{}", encoding="utf-8")

    from app.modules.m16_ops_quality.status import clean_m16_runtime

    result = clean_m16_runtime(tmp_path)

    assert result.status == STATUS_READY_CONTROLLED
    assert result.mutation_performed is True
    assert result.details["planned_count"] == 1
    assert result.details["deleted_count"] == 1
    assert not temporary.exists()
    assert preserved.exists()


def test_guided_recheck_export_and_version_lock_actions_are_auditable(tmp_path: Path) -> None:
    runtime_dir = tmp_path / "storage" / "runtime"
    runtime_dir.mkdir(parents=True)
    (tmp_path / "storage" / "workspaces").mkdir(parents=True)
    (tmp_path / "docs" / "ai_prompts").mkdir(parents=True)
    (tmp_path / "docs" / "ai_prompts" / "laia_mistral_system_prompt.md").write_text("laia", encoding="utf-8")
    (tmp_path / "docs" / "ai_prompts" / "angel_hermes_system_prompt.md").write_text("hermes", encoding="utf-8")

    from app.modules.m16_ops_quality.status import run_m16_operational_action

    recheck = run_m16_operational_action("force_recheck", repo_root=tmp_path, env={"AI_ENABLED": "0"})
    export = run_m16_operational_action("export_readiness", repo_root=tmp_path, env={"AI_ENABLED": "0"})
    lock = run_m16_operational_action("version_lock", repo_root=tmp_path)

    export_path = tmp_path / "storage" / "runtime" / "m16_readiness_export.json"
    lock_path = tmp_path / "storage" / "runtime" / "m16_version_lock_snapshot.json"
    export_payload = json.loads(export_path.read_text(encoding="utf-8"))
    lock_payload = json.loads(lock_path.read_text(encoding="utf-8"))

    assert recheck.action == "force_recheck"
    assert recheck.mutation_performed is False
    assert recheck.details["component_count"] >= 1
    assert export.status == STATUS_READY_CONTROLLED
    assert export.mutation_performed is True
    assert export_payload["schema_version"] == "m16.readiness_export.v1"
    assert lock.mutation_performed is True
    assert lock_payload["external_resolution_performed"] is False
    assert lock_payload["version_lock_readiness"]["details"]["locked"][0]["tool_id"] == "python.runtime"


def test_guided_export_rejects_output_outside_runtime(tmp_path: Path) -> None:
    from app.modules.m16_ops_quality.status import run_m16_operational_action

    result = run_m16_operational_action(
        "export_readiness",
        parameters={"output_path": "outside.json"},
        repo_root=tmp_path,
        env={"AI_ENABLED": "0"},
    )

    assert result.status == STATUS_FAILED
    assert result.mutation_performed is False
    assert "storage/runtime" in result.message
    assert not (tmp_path / "outside.json").exists()


def test_readiness_history_records_degraded_alerts_without_secrets(tmp_path: Path) -> None:
    from app.modules.m16_ops_quality.status import (
        append_m16_readiness_history,
        build_m16_readiness_alerts,
        read_m16_readiness_history,
    )

    report = build_m16_readiness_report(
        repo_root=Path.cwd(),
        env={"AI_ENABLED": "1", "MISTRAL_ENABLED": "1", "MISTRAL_MODEL": "wrong", "DEEPSEEK_API_KEY": "super-secret"},
    )
    alerts = build_m16_readiness_alerts(report)
    result = append_m16_readiness_history(report, tmp_path)
    history = read_m16_readiness_history(tmp_path)
    serialized = json.dumps(history)

    assert alerts
    assert result["alert_count"] == len(alerts)
    assert history["history_count"] == 1
    assert history["alert_count"] >= 1
    assert any(alert["component"] == "ai_environment" for alert in history["alerts"])
    assert "super-secret" not in serialized


def test_write_runtime_status_appends_history_and_alert_files(tmp_path: Path) -> None:
    from app.modules.m16_ops_quality.status import read_m16_readiness_history

    report = build_m16_readiness_report(env={"AI_ENABLED": "0"})
    write_runtime_status(report, tmp_path)
    view = read_m16_readiness_history(tmp_path)

    assert (tmp_path / "m16_readiness_history.jsonl").is_file()
    assert view["history_count"] == 1
    assert view["alert_count"] >= 1
    assert view["history"][0]["schema_version"] == "m16.readiness_history.v1"
