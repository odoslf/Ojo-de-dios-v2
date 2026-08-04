import json
from pathlib import Path

WORKED_MODULE_IDS = (
    "m01_osint",
    "m03_network_services",
    "m09_scraping_intelligence",
    "m12_orchestration",
    "m15_cloud",
    "m16_ops_quality",
    "m18_honeypots_deception",
)


def test_implemented_rounds_status_doc_tracks_worked_modules_without_overclaiming() -> None:
    content = Path("docs/IMPLEMENTED_ROUNDS_STATUS.md").read_text(encoding="utf-8")

    for module_id in WORKED_MODULE_IDS:
        assert module_id.split("_", 1)[0].upper() in content or module_id in content
    assert "does not launch services" in content
    assert "no model download" in content
    assert "Full `pytest -q` collection is blocked" in content


def test_worked_module_manifests_include_real_implementation_status_block() -> None:
    for module_id in WORKED_MODULE_IDS:
        manifest = json.loads(Path("app/modules").joinpath(module_id, "module_manifest.json").read_text(encoding="utf-8"))
        status = manifest["implementation_status"]

        assert status["source"] == "registry_and_contract_tests"
        assert status["ready_technique_count"] <= status["implemented_technique_count"]
        assert "scope_note" in status
        assert manifest["readiness"] in {"documented", "reserved_future_module"}
