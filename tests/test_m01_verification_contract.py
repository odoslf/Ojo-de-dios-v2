"""M01 full verification contracts for external tooling and secure API config."""

import pytest

from app.contracts.evidence_contract import RESULT_MISSING_TOOL
from app.contracts.technique_contract import TechniqueExecutionContext
from app.core.errors import ContractError
from app.modules.m01_osint import techniques
from app.modules.m01_osint.techniques import (
    AmassPassiveActiveEnumTechnique,
    CensysPassiveIntelTechnique,
    ExiftoolMetadataExtractTechnique,
    HibpEmailLeakLookupTechnique,
    MasscanFastSweepTechnique,
    NaabuHttpxKatanaDiscoveryTechnique,
    NmapTcpUdpMassiveTechnique,
    SecuritytrailsPassiveIntelTechnique,
    ShodanPassiveIntelTechnique,
    SubfinderSubdomainEnumTechnique,
    TheharvesterEmailsTechnique,
)


def _context(parameters: dict[str, object]) -> TechniqueExecutionContext:
    return TechniqueExecutionContext(
        target_id="target-verify",
        run_id="run-verify",
        mode="controlled",
        parameters=parameters,
        confirmed=True,
    )


@pytest.mark.parametrize(
    ("technique_cls", "parameters", "expected_tools"),
    [
        (NmapTcpUdpMassiveTechnique, {"target": "127.0.0.1", "ports": "80", "protocol_mode": "tcp"}, ["nmap"]),
        (MasscanFastSweepTechnique, {"target": "127.0.0.1", "ports": "80", "rate_profile": "low"}, ["masscan"]),
        (NaabuHttpxKatanaDiscoveryTechnique, {"target": "example.com", "http_probe_enabled": True, "crawl_enabled": True}, ["naabu", "httpx", "katana"]),
        (SubfinderSubdomainEnumTechnique, {"domain": "example.com"}, ["subfinder"]),
        (AmassPassiveActiveEnumTechnique, {"domain": "example.com", "mode": "passive"}, ["amass"]),
        (TheharvesterEmailsTechnique, {"domain": "example.com", "source_profile": "search_engines"}, ["theHarvester"]),
    ],
)
def test_m01_external_cli_techniques_return_missing_tool_without_evidence(monkeypatch, technique_cls, parameters, expected_tools) -> None:
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: None)

    result = technique_cls().execute(_context(parameters))

    assert result.result_status == RESULT_MISSING_TOOL
    assert result.evidence == []
    assert result.raw_result["real_execution"] is False
    assert result.raw_result["missing_tools"] == expected_tools


def test_m01_exiftool_missing_tool_after_real_input_validation(monkeypatch, tmp_path) -> None:
    document = tmp_path / "sample.pdf"
    document.write_bytes(b"%PDF-1.4")
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: None)

    result = ExiftoolMetadataExtractTechnique().execute(_context({"input_files": [document.as_posix()]}))

    assert result.result_status == RESULT_MISSING_TOOL
    assert result.evidence == []
    assert result.raw_result["missing_tools"] == ["exiftool"]


@pytest.mark.parametrize(
    ("technique_cls", "parameters", "missing_secret"),
    [
        (ShodanPassiveIntelTechnique, {"query": "198.51.100.10", "target_type": "ip"}, "SHODAN_API_KEY"),
        (CensysPassiveIntelTechnique, {"query": "example.com", "target_type": "domain"}, "CENSYS_API_ID"),
        (SecuritytrailsPassiveIntelTechnique, {"domain": "example.com"}, "SECURITYTRAILS_API_KEY"),
        (HibpEmailLeakLookupTechnique, {"email": "alice@example.com"}, "HIBP_API_KEY"),
    ],
)
def test_m01_api_techniques_fail_honestly_without_secure_config(monkeypatch, technique_cls, parameters, missing_secret) -> None:
    for env_name in ("SHODAN_API_KEY", "CENSYS_API_ID", "CENSYS_API_SECRET", "SECURITYTRAILS_API_KEY", "HIBP_API_KEY"):
        monkeypatch.delenv(env_name, raising=False)
    monkeypatch.setenv("OJO_DISABLE_KEYRING", "1")

    with pytest.raises(ContractError) as error:
        technique_cls().execute(_context(parameters))

    message = str(error.value)
    assert missing_secret in message
    assert "Status: missing-tool" in message
