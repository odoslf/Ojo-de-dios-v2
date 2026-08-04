"""Contract tests for target fingerprint generation."""

import pytest

from app.core.errors import ContractError
from app.core.target_fingerprint import build_target_fingerprint, normalize_target_value
from app.core.target_model import (
    TARGET_DOMAIN,
    TARGET_EMAIL,
    TARGET_IP,
    TARGET_RANGE,
    TARGET_SCRAPING_QUERY,
    TARGET_URL,
)


def test_domain_normalization_removes_scheme_path_and_port() -> None:
    assert normalize_target_value(TARGET_DOMAIN, "HTTPS://Example.COM/path") == "example.com"
    assert normalize_target_value(TARGET_DOMAIN, "example.com:443") == "example.com"


def test_ip_normalization_and_validation() -> None:
    assert normalize_target_value(TARGET_IP, "127.0.0.1") == "127.0.0.1"
    with pytest.raises(ContractError):
        normalize_target_value(TARGET_IP, "999.999.999.999")


def test_range_normalization_and_validation() -> None:
    assert normalize_target_value(TARGET_RANGE, "192.168.1.1/24") == "192.168.1.0/24"


def test_url_normalization_requires_http_scheme_and_host() -> None:
    assert normalize_target_value(TARGET_URL, "HTTPS://Example.COM/a?x=1#b") == "https://example.com/a"
    with pytest.raises(ContractError):
        normalize_target_value(TARGET_URL, "example.com/a")


def test_email_normalization_and_validation() -> None:
    normalized = normalize_target_value(TARGET_EMAIL, "User@Example.COM")
    assert normalized == "user@example.com"
    fingerprint = build_target_fingerprint("target-1", TARGET_EMAIL, "User@Example.COM")
    assert fingerprint.fingerprint["domain"] == "example.com"
    with pytest.raises(ContractError):
        normalize_target_value(TARGET_EMAIL, "not-email")


def test_scraping_query_preserves_text_case() -> None:
    assert normalize_target_value(TARGET_SCRAPING_QUERY, "  ACME Exposed Buckets  ") == "ACME Exposed Buckets"


def test_build_target_fingerprint_returns_expected_tags() -> None:
    assert build_target_fingerprint("target-1", TARGET_DOMAIN, "example.com").tags == ["domain"]
    assert build_target_fingerprint("target-1", TARGET_IP, "127.0.0.1").tags == ["ip"]
    assert build_target_fingerprint("target-1", TARGET_RANGE, "192.168.1.1/24").tags == ["range"]
    assert build_target_fingerprint("target-1", TARGET_URL, "https://example.com/a").tags == ["url", "web"]
    assert build_target_fingerprint("target-1", TARGET_SCRAPING_QUERY, "Query").tags == ["scraping"]
