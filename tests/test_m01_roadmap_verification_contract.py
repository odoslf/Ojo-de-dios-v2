"""M01 OSINT roadmap verification contracts."""

import re
from pathlib import Path

from app.contracts.technique_contract import STATUS_READY_CONTROLLED
from app.core.registry_loader import load_registry_from_package


def test_m01_registry_matches_documented_roadmap_techniques_1_to_47() -> None:
    docs = Path("docs/techniques/01_OSINT.md").read_text(encoding="utf-8")
    documented_ids = re.findall(r"^####\s+(?:[1-9]|[1-3][0-9]|4[0-7])\.\s+([^\s]+)$", docs, flags=re.MULTILINE)
    registry = load_registry_from_package("app.modules.m01_osint")

    assert len(documented_ids) == 47
    assert registry.list_ids() == sorted(documented_ids)


def test_m01_registry_marks_each_documented_technique_as_real_ready_controlled() -> None:
    registry = load_registry_from_package("app.modules.m01_osint")

    for technique_cls in registry.list_all():
        technique = technique_cls()
        technique.validate_metadata()
        assert technique.module_id == "m01_osint"
        assert technique.implementation_status == STATUS_READY_CONTROLLED
        assert technique.requires_user_implementation is False
        assert technique.demo_behavior.get("real_execution") is False
        assert technique.expected_evidence
