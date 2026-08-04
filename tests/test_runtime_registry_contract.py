"""Runtime registry provider contract tests."""

from app.core.runtime_registry import build_runtime_registry_snapshot


def test_runtime_registry_discovers_configured_package_without_creating_placeholders() -> None:
    snapshot = build_runtime_registry_snapshot("app.modules")
    payload = snapshot.to_status_payload()

    assert payload["ready"] is True
    assert payload["placeholder_techniques_created"] is False
    assert payload["execution_implied"] is False
    assert payload["technique_count"] == len(payload["technique_ids"])
    assert payload["packages"] == [
        {
            "package_name": "app.modules",
            "imported": True,
            "discovered_technique_count": payload["technique_count"],
            "error": None,
        }
    ]


def test_runtime_registry_reports_missing_package_as_degraded_status() -> None:
    snapshot = build_runtime_registry_snapshot("missing_ojo_de_dios_package")
    payload = snapshot.to_status_payload()

    assert payload["ready"] is False
    assert payload["technique_count"] == 0
    assert payload["packages"][0]["package_name"] == "missing_ojo_de_dios_package"
    assert payload["packages"][0]["imported"] is False
    assert payload["packages"][0]["error"]
