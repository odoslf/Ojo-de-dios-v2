from app.core.module_dashboard_status import build_dashboard_implementation_summary, build_module_implementation_status


def test_dashboard_status_uses_real_registered_techniques_for_worked_modules() -> None:
    summary = build_dashboard_implementation_summary()
    by_id = {item.module_id: item for item in summary["statuses"]}

    assert summary["execution_implied"] is False
    assert by_id["m01_osint"].implemented_technique_count == 47
    assert by_id["m03_network_services"].ready_technique_count == 21
    assert by_id["m09_scraping_intelligence"].local_ai_technique_count == 2
    assert by_id["m18_honeypots_deception"].ready_technique_count == 4
    assert by_id["m12_orchestration"].implemented_technique_count >= 1
    assert by_id["m15_cloud"].readiness_status == "READY_IMPLEMENTED"
    assert by_id["m18_honeypots_deception"].readiness_status == "READY_IMPLEMENTED"
    assert by_id["m16_ops_quality"].readiness_status == "READY_READINESS_CHECKS"


def test_module_detail_status_reports_manifest_only_when_no_registry_classes() -> None:
    status = build_module_implementation_status("m02_vulnerabilities")

    assert status.implemented_technique_count == 0
    assert status.ready_technique_count == 0
    assert status.readiness_status == "MANIFEST_ONLY"
    assert status.has_real_logic is False
