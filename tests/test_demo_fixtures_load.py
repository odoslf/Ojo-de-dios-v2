"""Demo fixture store loading tests."""

import pytest

from app.core.errors import ContractError
from app.core.fixtures import DemoFixtureStore

EXPECTED_FIXTURES = {
    "android_apk_analysis_basic.json",
    "cloud_scan_basic.json",
    "credentials_hashes_basic.json",
    "hackrf_signal_basic.json",
    "hermes_proposal_basic.json",
    "mitm_pcap_summary_basic.json",
    "osint_domain_basic.json",
    "scraping_results_basic.json",
    "vuln_scan_basic.json",
    "web_findings_basic.json",
}


def test_list_fixture_names_contains_expected_json_files() -> None:
    fixture_names = set(DemoFixtureStore().list_fixture_names())

    assert EXPECTED_FIXTURES.issubset(fixture_names)


def test_load_fixture_with_json_suffix_returns_dict_payload() -> None:
    fixture = DemoFixtureStore().load("osint_domain_basic.json")

    assert isinstance(fixture.payload, dict)


def test_load_fixture_without_json_suffix_returns_payload() -> None:
    fixture = DemoFixtureStore().load("osint_domain_basic")

    assert fixture.fixture_name == "osint_domain_basic.json"


def test_loaded_fixture_payload_marks_demo_true() -> None:
    fixture = DemoFixtureStore().load("osint_domain_basic.json")

    assert fixture.payload["demo"] is True


def test_loaded_fixture_payload_marks_real_execution_false() -> None:
    fixture = DemoFixtureStore().load("osint_domain_basic.json")

    assert fixture.payload["real_execution"] is False


def test_exists_missing_fixture_returns_false() -> None:
    assert DemoFixtureStore().exists("missing.json") is False


def test_load_rejects_parent_traversal_fixture_name() -> None:
    with pytest.raises(ContractError):
        DemoFixtureStore().load("../bad.json")


def test_load_rejects_nested_fixture_name() -> None:
    with pytest.raises(ContractError):
        DemoFixtureStore().load("bad/name.json")
