"""Passive service fingerprint contract tests."""

import pytest

from app.core.service_fingerprint import build_service_fingerprint_report
from app.core.target_fingerprint import build_target_fingerprint
from app.core.target_model import TARGET_DOMAIN, TARGET_URL, TargetRecord


def _target(target_type: str, value: str, normalized_value: str, metadata: dict | None = None) -> TargetRecord:
    return TargetRecord(
        target_id="target-services-1",
        name="Services Target",
        target_type=target_type,
        value=value,
        normalized_value=normalized_value,
        mode="dry_run",
        metadata=metadata or {},
    )


def test_url_service_fingerprint_derives_http_endpoint_without_scan() -> None:
    target = _target(TARGET_URL, "https://Example.COM/login", "https://example.com/login")
    fingerprint = build_target_fingerprint(target.target_id, target.target_type, target.value)

    report = build_service_fingerprint_report(target, fingerprint)
    payload = report.to_dict()

    assert payload["execution_started"] is False
    assert payload["endpoint_count"] == 1
    assert payload["endpoints"][0]["host"] == "example.com"
    assert payload["endpoints"][0]["port"] == 443
    assert payload["endpoints"][0]["service_name"] == "https"
    assert payload["endpoints"][0]["source"] == "target_fingerprint"


def test_operator_metadata_services_are_validated_and_deduplicated() -> None:
    target = _target(
        TARGET_DOMAIN,
        "example.com",
        "example.com",
        {
            "services": [
                {"host": "Example.COM", "port": 8443, "transport": "tcp", "service_name": "https", "confidence": 0.8},
                {"host": "example.com", "port": 8443, "transport": "tcp", "service_name": "https", "confidence": 0.6},
                {"port": 53, "transport": "udp", "service_name": "dns", "product": "bind"},
            ]
        },
    )
    fingerprint = build_target_fingerprint(target.target_id, target.target_type, target.value)

    report = build_service_fingerprint_report(target, fingerprint)
    endpoints = {endpoint.endpoint_id: endpoint for endpoint in report.endpoints}

    assert report.endpoint_count == 2
    assert "tcp:example.com:8443:https" in endpoints
    assert "udp:example.com:53:dns" in endpoints
    assert endpoints["udp:example.com:53:dns"].properties["product"] == "bind"


def test_invalid_metadata_service_port_raises() -> None:
    target = _target(TARGET_DOMAIN, "example.com", "example.com", {"services": [{"port": 70000}]})
    fingerprint = build_target_fingerprint(target.target_id, target.target_type, target.value)

    with pytest.raises(ValueError, match="between 1 and 65535"):
        build_service_fingerprint_report(target, fingerprint)
