"""M01 OSINT techniques 1-47 concrete execution contracts."""

from app.contracts.evidence_contract import RESULT_MISSING_TOOL, RESULT_SUCCESS
from app.contracts.technique_contract import STATUS_READY_CONTROLLED, TechniqueExecutionContext
from app.core.errors import ContractError
from app.core.registry_loader import load_registry_from_package
from app.core.permission_levels import PERMISSION_ACTIVE_LOW, PERMISSION_PASSIVE
from app.modules.m01_osint.techniques import (
    AlienvaultOtxPassiveIntelTechnique,
    AmassPassiveActiveEnumTechnique,
    AquatoneScreenshotsTechnique,
    CensysPassiveIntelTechnique,
    CommandResult,
    DehashedLookupTechnique,
    ExiftoolMetadataExtractTechnique,
    FocaMetadataExtractTechnique,
    GhuntGoogleInfoTechnique,
    GoogleDorksAutoTechnique,
    GithubSocialOsintTechnique,
    GitleaksRepoLeaksTechnique,
    HibpEmailLeakLookupTechnique,
    HoleheEmailCheckTechnique,
    BloodhoundPyAdMapTechnique,
    CaptchaTextSolverAiTechnique,
    CaptchaVisualBypassTechnique,
    IntelxLookupTechnique,
    InternalArpNetbiosTechnique,
    InternalLdapEnumTechnique,
    InternalMssqlEnumTechnique,
    InternalRdpEnumTechnique,
    InternalSmbEnumTechnique,
    InternalVncEnumTechnique,
    IpGeolocationAsnBgpTechnique,
    LdapsearchAdMapTechnique,
    LinkedinSocialOsintTechnique,
    MaigretProfilesTechnique,
    MlLocalFingerprintingTechnique,
    MasscanFastSweepTechnique,
    NaabuHttpxKatanaDiscoveryTechnique,
    NmapTcpUdpMassiveTechnique,
    ProxyRotationSimTechnique,
    RecursiveAiDiscoveryTechnique,
    ReverseDnsTechnique,
    SecuritytrailsPassiveIntelTechnique,
    SherlockUsernameTechnique,
    ShodanPassiveIntelTechnique,
    SpiderfootAutomationTechnique,
    SubfinderSubdomainEnumTechnique,
    TheharvesterEmailsTechnique,
    TrufflehogRepoLeaksTechnique,
    TwitterSocialOsintTechnique,
    X4EngineIntegrationTechnique,
    X5IntelligentPlannerTechnique,
    WappalyzerFingerprintTechnique,
    WhatwebFingerprintTechnique,
    WhoisHistoryTechnique,
)
from app.modules.m01_osint import techniques


def _context(parameters: dict[str, object]) -> TechniqueExecutionContext:
    return TechniqueExecutionContext(
        target_id="target-1",
        run_id="run-1",
        mode="controlled",
        parameters=parameters,
        confirmed=True,
    )


def test_m01_techniques_1_to_47_register_as_real_ready_controlled_techniques() -> None:
    registry = load_registry_from_package("app.modules.m01_osint")

    assert registry.list_ids() == [
        "osint.alienvault_otx_passive_intel",
        "osint.amass_passive_active_enum",
        "osint.aquatone_screenshots",
        "osint.bloodhound_py_ad_map",
        "osint.censys_passive_intel",
        "osint.dehashed_lookup",
        "osint.exiftool_metadata_extract",
        "osint.foca_metadata_extract",
        "osint.ghunt_google_info",
        "osint.github_social_osint",
        "osint.gitleaks_repo_leaks",
        "osint.google_dorks_auto",
        "osint.hibp_email_leak_lookup",
        "osint.holehe_email_check",
        "osint.intelx_lookup",
        "osint.internal_arp_netbios",
        "osint.internal_ldap_enum",
        "osint.internal_mssql_enum",
        "osint.internal_rdp_enum",
        "osint.internal_smb_enum",
        "osint.internal_vnc_enum",
        "osint.ip_geolocation_asn_bgp",
        "osint.ldapsearch_ad_map",
        "osint.linkedin_social_osint",
        "osint.maigret_profiles",
        "osint.masscan_fast_sweep",
        "osint.ml_local_fingerprinting",
        "osint.naabu_httpx_katana_discovery",
        "osint.nmap_tcp_udp_massive",
        "osint.reverse_dns",
        "osint.securitytrails_passive_intel",
        "osint.sherlock_username",
        "osint.shodan_passive_intel",
        "osint.spiderfoot_automation",
        "osint.subfinder_subdomain_enum",
        "osint.theharvester_emails",
        "osint.trufflehog_repo_leaks",
        "osint.twitter_social_osint",
        "osint.wappalyzer_fingerprint",
        "osint.whatweb_fingerprint",
        "osint.whois_history",
        "scraping.captcha_text_solver_ai",
        "scraping.captcha_visual_bypass",
        "scraping.proxy_rotation_sim",
        "scraping.recursive_ai_discovery",
        "scraping.x4_engine_integration",
        "scraping.x5_intelligent_planner",
    ]
    for technique_cls in registry.list_all():
        technique = technique_cls()
        technique.validate_metadata()
        assert technique.module_id == "m01_osint"
        assert technique.permission_level in {PERMISSION_ACTIVE_LOW, PERMISSION_PASSIVE}
        assert technique.implementation_status == STATUS_READY_CONTROLLED
        assert technique.requires_user_implementation is False
        assert isinstance(technique.requires_network, bool)


def test_nmap_technique_executes_tool_output_parser_with_real_evidence(monkeypatch) -> None:
    xml = """<?xml version="1.0"?>
<nmaprun>
  <host>
    <address addr="127.0.0.1" addrtype="ipv4"/>
    <ports>
      <port protocol="tcp" portid="80">
        <state state="open"/>
        <service name="http" product="nginx" version="1.24"/>
      </port>
    </ports>
  </host>
</nmaprun>
"""
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: f"/usr/bin/{tool}" if tool == "nmap" else None)
    monkeypatch.setattr(
        techniques,
        "_run_command",
        lambda command, timeout_seconds, stdin=None: CommandResult(tuple(command), 0, xml, ""),
    )

    result = NmapTcpUdpMassiveTechnique().execute(
        _context({"target": "127.0.0.1", "ports": "80", "protocol_mode": "tcp", "max_duration_seconds": 10})
    )

    assert result.result_status == RESULT_SUCCESS
    assert result.evidence[0].real_execution is True
    assert result.evidence[0].content["open_ports"][0]["port"] == 80
    assert result.evidence[0].content["service_fingerprints"][0]["service_name"] == "http"
    assert result.evidence[0].content["command"][0] == "/usr/bin/nmap"
    assert "-sT" in result.evidence[0].content["command"]


def test_active_discovery_requires_operator_confirmation() -> None:
    context = TechniqueExecutionContext(
        target_id="target-1",
        run_id="run-1",
        mode="controlled",
        parameters={"target": "127.0.0.1", "ports": "80", "protocol_mode": "tcp"},
        confirmed=False,
    )

    try:
        NmapTcpUdpMassiveTechnique().execute(context)
    except ContractError as error:
        assert "explicit operator confirmation" in str(error)
    else:
        raise AssertionError("Expected active M01 discovery to require confirmation.")


def test_masscan_technique_reports_missing_tool_without_fake_success(monkeypatch) -> None:
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: None)

    result = MasscanFastSweepTechnique().execute(
        _context({"target": "127.0.0.1", "ports": "80", "rate_profile": "low", "max_duration_seconds": 10})
    )

    assert result.result_status == RESULT_MISSING_TOOL
    assert result.evidence == []
    assert result.raw_result["real_execution"] is False


def test_naabu_httpx_katana_pipeline_normalizes_web_discovery(monkeypatch) -> None:
    outputs = {
        "naabu": '{"host":"example.com","port":443}\n',
        "httpx": '{"url":"https://example.com","status_code":200,"title":"Example","webserver":"nginx","tech":["nginx"]}\n',
        "katana": '{"request":{"endpoint":"https://example.com/login"}}\n',
    }

    def fake_run(command: list[str], timeout_seconds: int, stdin: str | None = None) -> CommandResult:
        tool = command[0].rsplit("/", 1)[-1]
        return CommandResult(tuple(command), 0, outputs[tool], "")

    monkeypatch.setattr(techniques, "_tool_path", lambda tool: f"/usr/bin/{tool}")
    monkeypatch.setattr(techniques, "_run_command", fake_run)

    result = NaabuHttpxKatanaDiscoveryTechnique().execute(
        _context(
            {
                "target": "example.com",
                "port_profile": "web",
                "http_probe_enabled": True,
                "crawl_enabled": True,
                "crawl_depth": 1,
                "include_headers": True,
                "include_technologies": True,
                "max_duration_seconds": 10,
            }
        )
    )

    content = result.evidence[0].content
    assert result.result_status == RESULT_SUCCESS
    assert content["web_services"][0]["url"] == "https://example.com"
    assert content["crawled_urls"] == ["https://example.com/login"]
    assert content["technology_hints"] == ["nginx"]
    assert {"https://example.com", "https://example.com/login"} <= set(content["discovered_endpoints"])


def test_subfinder_technique_parses_json_and_text_subdomains(monkeypatch) -> None:
    stdout = '{"host":"api.example.com"}\nwww.example.com\nignored.net\n'
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: f"/usr/bin/{tool}" if tool == "subfinder" else None)
    monkeypatch.setattr(techniques, "_run_command", lambda command, timeout_seconds, stdin=None: CommandResult(tuple(command), 0, stdout, ""))

    result = SubfinderSubdomainEnumTechnique().execute(_context({"domain": "example.com", "recursive": True}))

    assert result.result_status == RESULT_SUCCESS
    assert result.evidence[0].content["subdomains"] == ["api.example.com", "www.example.com"]
    assert "-recursive" in result.evidence[0].content["command"]


def test_amass_active_mode_requires_confirmation_before_running() -> None:
    context = TechniqueExecutionContext(
        target_id="target-1",
        run_id="run-1",
        mode="controlled",
        parameters={"domain": "example.com", "mode": "active"},
        confirmed=False,
    )

    try:
        AmassPassiveActiveEnumTechnique().execute(context)
    except ContractError as error:
        assert "explicit operator confirmation" in str(error)
    else:
        raise AssertionError("Expected active Amass mode to require confirmation.")


def test_amass_passive_mode_parses_subdomains_ips_and_asns(monkeypatch) -> None:
    stdout = '{"name":"api.example.com","addresses":[{"ip":"192.0.2.10","asn":64500,"desc":"Example ASN","cidr":"192.0.2.0/24"}]}\n'
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: f"/usr/bin/{tool}" if tool == "amass" else None)
    monkeypatch.setattr(techniques, "_run_command", lambda command, timeout_seconds, stdin=None: CommandResult(tuple(command), 0, stdout, ""))

    result = AmassPassiveActiveEnumTechnique().execute(_context({"domain": "example.com", "mode": "passive"}))
    content = result.evidence[0].content

    assert content["subdomains"] == ["api.example.com"]
    assert content["ips"] == ["192.0.2.10"]
    assert content["asn_records"][0]["asn"] == 64500
    assert "-passive" in content["command"]


def test_aquatone_hashes_generated_screenshot_artifacts(monkeypatch, tmp_path) -> None:
    output_dir = tmp_path / "aquatone"
    output_dir.mkdir()
    (output_dir / "shot.png").write_bytes(b"png-bytes")
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: f"/usr/bin/{tool}" if tool == "aquatone" else None)
    monkeypatch.setattr(techniques, "_run_command", lambda command, timeout_seconds, stdin=None: CommandResult(tuple(command), 0, "", ""))

    result = AquatoneScreenshotsTechnique().execute(
        _context({"urls": ["https://example.com"], "output_directory": output_dir.as_posix(), "max_duration_seconds": 10})
    )

    assert result.result_status == RESULT_SUCCESS
    assert result.evidence[0].content["screenshots"][0]["path"].endswith("shot.png")
    assert len(result.evidence[0].content["screenshot_hashes"][0]) == 64


def test_shodan_normalizes_passive_api_response(monkeypatch) -> None:
    monkeypatch.setenv("SHODAN_API_KEY", "test-key")
    monkeypatch.setattr(
        techniques,
        "_http_get_json",
        lambda url, headers=None, params=None, timeout_seconds=20: {
            "status_code": 200,
            "url": url,
            "payload": {
                "ip_str": "198.51.100.10",
                "hostnames": ["www.example.com"],
                "org": "Example Org",
                "data": [{"port": 443, "transport": "tcp", "product": "nginx", "version": "1.24", "data": "banner"}],
            },
        },
    )

    result = ShodanPassiveIntelTechnique().execute(_context({"query": "198.51.100.10", "target_type": "ip", "include_banners": True}))

    assert result.evidence[0].content["passive_ports"][0]["port"] == 443
    assert result.evidence[0].content["passive_service_inventory"][0]["source_provider"] == "shodan"
    assert result.evidence[0].content["passive_service_inventory"][0]["service_name"] == "nginx"
    assert result.evidence[0].content["banners"][0]["data"] == "banner"


def test_censys_normalizes_passive_services(monkeypatch) -> None:
    class FakeResponse:
        status_code = 200
        url = "https://search.censys.io/api/v2/hosts/search?q=example.com"

        def json(self):
            return {"result": {"total": 1, "hits": [{"ip": "198.51.100.20", "services": [{"port": 443, "service_name": "HTTPS", "transport_protocol": "TCP"}]}]}}

    monkeypatch.setenv("CENSYS_API_ID", "id")
    monkeypatch.setenv("CENSYS_API_SECRET", "secret")
    monkeypatch.setattr("app.modules.m01_osint.techniques.requests.get", lambda *args, **kwargs: FakeResponse())

    result = CensysPassiveIntelTechnique().execute(_context({"query": "example.com", "target_type": "domain"}))

    assert result.evidence[0].content["passive_services"][0]["port"] == 443
    assert result.evidence[0].content["passive_service_inventory"][0]["source_provider"] == "censys"
    assert result.evidence[0].content["passive_service_inventory"][0]["service_name"] == "HTTPS"


def test_otx_normalizes_pulses_and_related_indicators(monkeypatch) -> None:
    monkeypatch.setenv("OTX_API_KEY", "test-key")
    monkeypatch.setattr(
        techniques,
        "_http_get_json",
        lambda url, headers=None, params=None, timeout_seconds=20: {
            "status_code": 200,
            "url": url,
            "payload": {"pulse_info": {"pulses": [{"id": "p1", "name": "Pulse"}]}, "related": {"domains": ["api.example.com"]}},
        },
    )

    result = AlienvaultOtxPassiveIntelTechnique().execute(_context({"indicator": "example.com", "indicator_type": "domain"}))

    assert result.evidence[0].content["pulses"] == [{"id": "p1", "name": "Pulse"}]
    assert result.evidence[0].content["related_indicators"] == [{"type": "domains", "indicator": "api.example.com"}]


def test_securitytrails_combines_selected_passive_sources(monkeypatch) -> None:
    monkeypatch.setenv("SECURITYTRAILS_API_KEY", "test-key")

    def fake_get_json(url, headers=None, params=None, timeout_seconds=20):
        if url.endswith("/subdomains"):
            payload = {"subdomains": ["www", "api"]}
        elif "/history/dns/a/" in url:
            payload = {"records": [{"first_seen": "2026-01-01", "last_seen": "2026-02-01", "values": [{"ip": "198.51.100.30"}]}]}
        else:
            payload = {"records": [{"registrar": "Example Registrar"}]}
        return {"status_code": 200, "url": url, "payload": payload}

    monkeypatch.setattr(techniques, "_http_get_json", fake_get_json)

    result = SecuritytrailsPassiveIntelTechnique().execute(_context({"domain": "example.com"}))
    content = result.evidence[0].content

    assert content["subdomains"] == ["api.example.com", "www.example.com"]
    assert content["dns_history"][0]["values"] == [{"ip": "198.51.100.30"}]
    assert content["whois_records"]["records"][0]["registrar"] == "Example Registrar"


def test_hibp_email_leak_lookup_normalizes_breaches_and_pastes(monkeypatch) -> None:
    class FakeResponse:
        status_code = 200
        url = "https://haveibeenpwned.com/api/v3/test"

        def __init__(self, payload):
            self._payload = payload

        def json(self):
            return self._payload

    def fake_get(url, **kwargs):
        if "/pasteaccount/" in url:
            return FakeResponse([{"Source": "Pastebin", "Id": "abc"}])
        return FakeResponse([{"Name": "ExampleBreach", "Domain": "example.com"}])

    monkeypatch.setenv("HIBP_API_KEY", "test-key")
    monkeypatch.setattr("app.modules.m01_osint.techniques.requests.get", fake_get)

    result = HibpEmailLeakLookupTechnique().execute(_context({"email": "alice@example.com", "include_pastes": True}))
    content = result.evidence[0].content

    assert content["breach_names"] == ["ExampleBreach"]
    assert content["paste_findings"] == [{"source": "Pastebin", "id": "abc", "title": None, "date": None}]
    assert content["exposure_summary"]["queried_email"] == "a***@example.com"


def test_dehashed_lookup_redacts_sensitive_exposure_records(monkeypatch) -> None:
    class FakeResponse:
        status_code = 200
        url = "https://api.dehashed.com/search?query=email%3Aalice%40example.com"

        def json(self):
            return {"entries": [{"email": "alice@example.com", "password": "secret", "database_name": "leak"}]}

    monkeypatch.setenv("DEHASHED_USERNAME", "alice")
    monkeypatch.setenv("DEHASHED_API_KEY", "test-key")
    monkeypatch.setattr("app.modules.m01_osint.techniques.requests.get", lambda *args, **kwargs: FakeResponse())

    result = DehashedLookupTechnique().execute(_context({"query": "email:alice@example.com", "redact_sensitive": True}))
    record = result.evidence[0].content["exposure_records"][0]

    assert record["email"] == "a***@example.com"
    assert "password" not in record
    assert record["has_password"] is True


def test_intelx_lookup_normalizes_passive_records(monkeypatch) -> None:
    class FakeResponse:
        status_code = 200
        url = "https://2.intelx.io/intelligent/search/result"

        def json(self):
            return {"records": [{"name": "doc.txt", "bucket": "public", "xref": "ref-1"}]}

    monkeypatch.setenv("INTELX_API_KEY", "test-key")
    monkeypatch.setattr("app.modules.m01_osint.techniques.requests.post", lambda *args, **kwargs: FakeResponse())

    result = IntelxLookupTechnique().execute(_context({"query": "example.com"}))
    content = result.evidence[0].content

    assert content["intel_records"][0]["name"] == "doc.txt"
    assert content["source_references"] == ["ref-1"]


def test_theharvester_emails_parses_json_report(monkeypatch) -> None:
    stdout = '{"emails":["a@example.com"],"hosts":["www.example.com"],"sources":["bing"]}'
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: "/usr/bin/theHarvester" if tool == "theHarvester" else None)
    monkeypatch.setattr(techniques, "_run_command", lambda command, timeout_seconds, stdin=None: CommandResult(tuple(command), 0, stdout, ""))

    result = TheharvesterEmailsTechnique().execute(_context({"domain": "example.com", "source_profile": "search_engines"}))
    content = result.evidence[0].content

    assert content["emails"] == ["a@example.com"]
    assert content["hosts"] == ["www.example.com"]
    assert content["source_references"] == ["bing"]


def test_profile_cli_tools_normalize_public_profile_lines(monkeypatch) -> None:
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: f"/usr/bin/{tool}")
    monkeypatch.setattr(
        techniques,
        "_run_command",
        lambda command, timeout_seconds, stdin=None: CommandResult(tuple(command), 0, "[+] Twitter: https://twitter.com/alice\n[-] Missing", ""),
    )

    sherlock_result = SherlockUsernameTechnique().execute(_context({"username": "alice"}))
    maigret_result = MaigretProfilesTechnique().execute(_context({"username": "alice"}))

    assert sherlock_result.evidence[0].content["profile_urls"] == ["https://twitter.com/alice"]
    assert maigret_result.evidence[0].content["social_profiles"][0]["site"] == "Twitter"


def test_holehe_email_check_parses_site_presence(monkeypatch) -> None:
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: "/usr/bin/holehe" if tool == "holehe" else None)
    monkeypatch.setattr(techniques, "_run_command", lambda command, timeout_seconds, stdin=None: CommandResult(tuple(command), 0, "[+] twitter\n[-] github", ""))

    result = HoleheEmailCheckTechnique().execute(_context({"email": "alice@example.com"}))

    assert result.evidence[0].content["site_matches"] == ["twitter"]


def test_exiftool_metadata_extract_summarizes_real_file_metadata(monkeypatch, tmp_path) -> None:
    document = tmp_path / "doc.pdf"
    document.write_bytes(b"%PDF-1.4")
    stdout = '[{"SourceFile":"%s","Author":"Alice","Software":"Word","GPSLatitude":"1.0"}]' % document.as_posix()
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: "/usr/bin/exiftool" if tool == "exiftool" else None)
    monkeypatch.setattr(techniques, "_run_command", lambda command, timeout_seconds, stdin=None: CommandResult(tuple(command), 0, stdout, ""))

    result = ExiftoolMetadataExtractTechnique().execute(_context({"input_files": [document.as_posix()]}))
    content = result.evidence[0].content

    assert content["metadata_findings"][0]["Author"] == "Alice"
    assert content["gps_metadata"][0]["GPSLatitude"] == "1.0"
    assert content["software_metadata"] == ["Word"]


def test_google_dorks_auto_uses_configured_search_provider(monkeypatch) -> None:
    monkeypatch.setenv("SERPAPI_API_KEY", "test-key")
    monkeypatch.setattr(
        techniques,
        "_http_get_json",
        lambda url, headers=None, params=None, timeout_seconds=20: {
            "url": url,
            "payload": {"organic_results": [{"title": "PDF", "link": "https://example.com/file.pdf", "snippet": "doc"}]},
        },
    )

    result = GoogleDorksAutoTechnique().execute(_context({"target": "example.com", "dork_profile": "documents"}))
    content = result.evidence[0].content

    assert content["exposed_documents"] == ["https://example.com/file.pdf"]
    assert content["source_urls"][0].startswith("https://serpapi.com/search.json")


def test_ip_geolocation_asn_bgp_normalizes_ripe_stat_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        techniques,
        "_http_get_json",
        lambda url, headers=None, params=None, timeout_seconds=20: {
            "url": url,
            "payload": {"data": {"resource": "AS64500", "asns": [{"asn": 64500}], "prefixes": [{"prefix": "198.51.100.0/24"}]}},
        },
    )

    result = IpGeolocationAsnBgpTechnique().execute(_context({"ip_or_asn": "AS64500", "lookup_type": "asn"}))
    content = result.evidence[0].content

    assert content["asn_records"] == [{"asn": 64500}]
    assert content["bgp_prefixes"] == [{"prefix": "198.51.100.0/24"}]


def test_whois_history_uses_rdap_without_history_key(monkeypatch) -> None:
    monkeypatch.setattr(
        techniques,
        "_http_get_json",
        lambda url, headers=None, params=None, timeout_seconds=20: {"url": url, "payload": {"entities": [{"roles": ["registrar"], "handle": "REG"}]}},
    )

    result = WhoisHistoryTechnique().execute(_context({"domain": "example.com", "include_history": False}))
    content = result.evidence[0].content

    assert content["registrar_history"] == [{"roles": ["registrar"], "handle": "REG"}]
    assert content["historical_ownership"] == []


def test_reverse_dns_uses_system_resolver_without_mutation(monkeypatch) -> None:
    monkeypatch.setattr(techniques.socket, "gethostbyaddr", lambda ip: ("ptr.example.com", ["alias.example.com"], [ip]))

    result = ReverseDnsTechnique().execute(_context({"ip_or_range": "198.51.100.1"}))
    content = result.evidence[0].content

    assert content["domains"] == ["alias.example.com", "ptr.example.com"]
    assert content["reverse_dns_records"][0]["status"] == "RESOLVED"


def test_linkedin_social_osint_normalizes_public_search_results(monkeypatch) -> None:
    monkeypatch.setenv("SERPAPI_API_KEY", "test-key")
    monkeypatch.setattr(
        techniques,
        "_http_get_json",
        lambda url, headers=None, params=None, timeout_seconds=20: {
            "url": url,
            "payload": {"organic_results": [{"title": "Alice Example", "link": "https://www.linkedin.com/in/alice", "snippet": "Engineer"}]},
        },
    )

    result = LinkedinSocialOsintTechnique().execute(_context({"query": "Alice Example", "query_type": "person"}))

    assert result.evidence[0].content["social_profiles"][0]["url"] == "https://www.linkedin.com/in/alice"
    assert result.evidence[0].content["relationship_hints"][0]["relationship"] == "public_search_match"


def test_twitter_social_osint_uses_bearer_api_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("TWITTER_BEARER_TOKEN", "token")
    monkeypatch.setattr(
        techniques,
        "_http_get_json",
        lambda url, headers=None, params=None, timeout_seconds=20: {
            "url": url,
            "payload": {"data": [{"id": "1", "author_id": "42", "text": "hello example.com", "created_at": "2026-01-01T00:00:00Z"}]},
        },
    )

    result = TwitterSocialOsintTechnique().execute(_context({"query": "example.com", "query_type": "domain"}))

    assert result.evidence[0].content["mentions"][0]["author_id"] == "42"
    assert result.evidence[0].content["relationship_hints"][0]["relationship"] == "tweet_match"


def test_github_social_osint_normalizes_user_and_repository_results(monkeypatch) -> None:
    def fake_get_json(url, headers=None, params=None, timeout_seconds=20):
        if url.endswith("/users"):
            payload = {"items": [{"login": "alice", "html_url": "https://github.com/alice", "type": "User"}]}
        else:
            payload = {"items": [{"full_name": "alice/project", "html_url": "https://github.com/alice/project", "language": "Python"}]}
        return {"url": url, "payload": payload}

    monkeypatch.setattr(techniques, "_http_get_json", fake_get_json)

    result = GithubSocialOsintTechnique().execute(_context({"query": "alice", "query_type": "username"}))
    content = result.evidence[0].content

    assert content["github_profiles"][0]["login"] == "alice"
    assert content["repositories"][0]["full_name"] == "alice/project"
    assert content["exposed_references"][0]["reference_type"] == "repository_search_match"


def test_repo_leak_scanners_redact_secret_material(monkeypatch, tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    stdout = '{"DetectorName":"API Key","Raw":"super-secret","SourceMetadata":{"Data":{"Filesystem":{"file":"app.py"}}},"Verified":true}\n'
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: f"/usr/bin/{tool}" if tool in {"trufflehog", "gitleaks"} else None)
    monkeypatch.setattr(techniques, "_run_command", lambda command, timeout_seconds, stdin=None: CommandResult(tuple(command), 0, stdout, ""))

    trufflehog = TrufflehogRepoLeaksTechnique().execute(_context({"local_path": repo.as_posix()}))
    gitleaks = GitleaksRepoLeaksTechnique().execute(_context({"local_path": repo.as_posix()}))

    assert trufflehog.evidence[0].content["secret_findings"][0]["secret"] == "[REDACTED]"
    assert len(gitleaks.evidence[0].content["secret_findings"][0]["secret_sha256"]) == 64


def test_whatweb_fingerprint_normalizes_plugin_matches(monkeypatch) -> None:
    stdout = '[{"target":"https://example.com","plugins":{"nginx":{"version":["1.24"]},"Title":{"string":["Example"]}}}]'
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: "/usr/bin/whatweb" if tool == "whatweb" else None)
    monkeypatch.setattr(techniques, "_run_command", lambda command, timeout_seconds, stdin=None: CommandResult(tuple(command), 0, stdout, ""))

    result = WhatwebFingerprintTechnique().execute(_context({"urls": ["https://example.com"], "aggression_profile": "passive"}))

    assert {item["product"] for item in result.evidence[0].content["technology_fingerprints"]} >= {"nginx", "Title"}


def test_wappalyzer_fingerprint_normalizes_api_payload(monkeypatch) -> None:
    monkeypatch.setenv("WAPPALYZER_API_KEY", "key")
    monkeypatch.setattr(
        techniques,
        "_http_get_json",
        lambda url, headers=None, params=None, timeout_seconds=20: {
            "url": url,
            "payload": [{"name": "React", "confidence": 100, "version": "18"}],
        },
    )

    result = WappalyzerFingerprintTechnique().execute(_context({"urls": ["https://example.com"]}))

    assert result.evidence[0].content["technology_fingerprints"][0]["product"] == "React"
    assert result.evidence[0].content["confidence_scores"]["React"] == 1.0


def test_ml_local_fingerprinting_predicts_products_and_versions() -> None:
    result = MlLocalFingerprintingTechnique().execute(
        _context({"banner_texts": ["HTTP/1.1 200 OK", "Server: nginx/1.24"], "headers": {"X-Powered-By": "Express"}, "confidence_threshold": 0.5})
    )
    content = result.evidence[0].content

    assert "nginx" in content["predicted_products"]
    assert {item["product"] for item in content["predicted_versions"]} == {"nginx"}
    assert content["confidence_scores"]["express"] >= 0.5


def _internal_context(parameters: dict[str, object]) -> TechniqueExecutionContext:
    params = {**parameters, "internal_scope_confirmed": True}
    return _context(params)


def test_internal_scope_is_required_for_active_low_internal_discovery() -> None:
    context = TechniqueExecutionContext(target_id="target-1", run_id="run-1", mode="controlled", parameters={"network_range": "10.0.0.0/24"}, confirmed=True)

    try:
        InternalArpNetbiosTechnique().execute(context)
    except ContractError as error:
        assert "internal_scope_confirmed" in str(error)
    else:
        raise AssertionError("Expected internal techniques to require explicit scope confirmation.")


def test_internal_arp_netbios_parses_nmap_xml_without_intrusive_actions(monkeypatch) -> None:
    xml = '<nmaprun><host><status state="up"/><address addr="10.0.0.5" addrtype="ipv4"/><address addr="AA:BB:CC:DD:EE:FF" addrtype="mac"/><hostnames><hostname name="WS01"/></hostnames></host></nmaprun>'
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: "/usr/bin/nmap" if tool == "nmap" else None)
    monkeypatch.setattr(techniques, "_run_command", lambda command, timeout_seconds, stdin=None: CommandResult(tuple(command), 0, xml, ""))

    result = InternalArpNetbiosTechnique().execute(_internal_context({"network_range": "10.0.0.0/24", "include_netbios": True}))
    content = result.evidence[0].content

    assert content["internal_hosts"] == [{"ip": "10.0.0.5", "source": "nmap_ping", "status": "up"}]
    assert content["netbios_names"] == ["WS01"]
    assert "-sn" in content["command"]


def test_internal_smb_and_mssql_enum_parse_read_only_cme_output(monkeypatch) -> None:
    stdout = "SMB 10.0.0.5 445 HOST [*] Windows 10\nSMB 10.0.0.5 445 HOST Share READ Docs\n"
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: "/usr/bin/cme" if tool == "cme" else None)
    monkeypatch.setattr(techniques, "_run_command", lambda command, timeout_seconds, stdin=None: CommandResult(tuple(command), 0, stdout, ""))

    smb = InternalSmbEnumTechnique().execute(_internal_context({"targets": ["10.0.0.5"], "enum_profile": "shares"}))
    mssql = InternalMssqlEnumTechnique().execute(_internal_context({"targets": ["10.0.0.5"]}))

    assert smb.evidence[0].content["smb_hosts"][0]["ip"] == "10.0.0.5"
    assert smb.evidence[0].content["smb_shares"][0]["access"] == "READ"
    assert mssql.evidence[0].content["mssql_instances"][0]["ip"] == "10.0.0.5"


def test_internal_ldap_and_ad_map_parse_ldif_profiles(monkeypatch) -> None:
    ldif = "dn: CN=Alice,DC=example,DC=local\nobjectClass: user\ncn: Alice\n\ndn: CN=Workstations,DC=example,DC=local\nobjectClass: group\ncn: Workstations\n"
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: "/usr/bin/ldapsearch" if tool == "ldapsearch" else None)
    monkeypatch.setattr(techniques, "_run_command", lambda command, timeout_seconds, stdin=None: CommandResult(tuple(command), 0, ldif, ""))

    ldap = InternalLdapEnumTechnique().execute(_internal_context({"ldap_server": "ldap://10.0.0.10", "base_dn": "DC=example,DC=local", "query_profile": "users"}))
    ad = LdapsearchAdMapTechnique().execute(_internal_context({"ldap_server": "ldap://10.0.0.10", "base_dn": "DC=example,DC=local", "collection_profile": "users"}))

    assert ldap.evidence[0].content["users"][0]["cn"] == "Alice"
    assert ad.evidence[0].content["ad_entries"] == ad.evidence[0].content["ldap_entries"]


def test_internal_rdp_and_vnc_nmap_scripts_normalize_security_info(monkeypatch) -> None:
    xml = '<nmaprun><host><address addr="10.0.0.5" addrtype="ipv4"/><ports><port protocol="tcp" portid="3389"><state state="open"/><service name="ms-wbt-server"/></port></ports><hostscript><script id="rdp-enum-encryption" output="CredSSP supported"/></hostscript></host></nmaprun>'
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: "/usr/bin/nmap" if tool == "nmap" else None)
    monkeypatch.setattr(techniques, "_run_command", lambda command, timeout_seconds, stdin=None: CommandResult(tuple(command), 0, xml, ""))

    rdp = InternalRdpEnumTechnique().execute(_internal_context({"targets": ["10.0.0.5"]}))
    vnc = InternalVncEnumTechnique().execute(_internal_context({"targets": ["10.0.0.5"]}))

    assert rdp.evidence[0].content["rdp_services"][0]["port"] == 3389
    assert vnc.evidence[0].content["security_info"]["script_outputs"][0]["output"] == "CredSSP supported"


def test_bloodhound_py_ad_map_summarizes_generated_graph_files(monkeypatch, tmp_path) -> None:
    out = tmp_path / "bloodhound"
    out.mkdir()
    (out / "users.json").write_text('{"data":[{"name":"ALICE"}]}', encoding="utf-8")
    (out / "groups.json").write_text('{"data":[{"name":"ADMINS"}]}', encoding="utf-8")
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: "/usr/bin/bloodhound-python" if tool == "bloodhound-python" else None)
    monkeypatch.setattr(techniques, "_run_command", lambda command, timeout_seconds, stdin=None: CommandResult(tuple(command), 0, "", ""))

    result = BloodhoundPyAdMapTechnique().execute(_internal_context({"domain": "example.local", "dc_host": "10.0.0.10", "output_directory": out.as_posix()}))
    content = result.evidence[0].content

    assert len(content["ad_graph_files"]) == 2
    assert content["users"] == [{"name": "ALICE"}]
    assert content["groups"] == [{"name": "ADMINS"}]


def test_x4_engine_integration_extracts_rows_from_html(monkeypatch) -> None:
    class FakeResponse:
        status_code = 200
        text = '<html><body><h1>Example title</h1><a href="https://example.com/item">Example item</a></body></html>'

    monkeypatch.setattr("app.modules.m01_osint.techniques.requests.get", lambda *args, **kwargs: FakeResponse())

    result = X4EngineIntegrationTechnique().execute(_context({"natural_language_query": "example item", "base_url": "https://example.com"}))
    content = result.evidence[0].content

    assert content["source_urls"] == ["https://example.com"]
    assert any(row.get("url") == "https://example.com/item" for row in content["extracted_rows"])


def test_x5_intelligent_planner_builds_steps_from_schema() -> None:
    result = X5IntelligentPlannerTechnique().execute(
        _context({"user_goal": "collect product names", "source_candidates": ["https://example.com/catalog"], "depth_limit": 2, "data_schema": {"name": "string"}})
    )
    content = result.evidence[0].content

    assert content["scraping_plan"]["schema_fields"] == ["name"]
    assert {step["step"] for step in content["planned_steps"]} >= {"fetch", "extract", "discover_links"}


def test_captcha_text_solver_requires_manual_review_for_candidates() -> None:
    result = CaptchaTextSolverAiTechnique().execute(_context({"challenge_text": "2 + 3?", "source_context": "unit test", "confidence_threshold": 0.9}))
    content = result.evidence[0].content

    assert content["answer_candidate"] == "5"
    assert content["manual_required_status"] == "REQUIRED"


def test_captcha_visual_ocr_hashes_screenshot_and_keeps_manual_review(monkeypatch, tmp_path) -> None:
    screenshot = tmp_path / "captcha.png"
    screenshot.write_bytes(b"image-bytes")
    monkeypatch.setattr(techniques, "_tool_path", lambda tool: "/usr/bin/tesseract" if tool == "tesseract" else None)
    monkeypatch.setattr(techniques, "_run_command", lambda command, timeout_seconds, stdin=None: CommandResult(tuple(command), 0, "ABCD", ""))

    result = CaptchaVisualBypassTechnique().execute(_context({"page_url": "https://example.com/login", "screenshot_path": screenshot.as_posix()}))
    content = result.evidence[0].content

    assert len(content["screenshot_hash"]) == 64
    assert content["ocr_output"] == "ABCD"
    assert content["manual_required_status"] == "REQUIRED"


def test_proxy_rotation_sim_generates_offline_events() -> None:
    result = ProxyRotationSimTechnique().execute(_context({"proxy_profile": "corp-proxies", "rotation_strategy": "failure_based", "connection_profile": "read-only", "max_failures": 2}))
    content = result.evidence[0].content

    assert len(content["rotation_events"]) == 2
    assert content["connection_status"]["opened_connections"] == 0
    assert content["connection_status"]["simulation_only"] is True


def test_recursive_ai_discovery_expands_supplied_seed_urls_without_fetching() -> None:
    result = RecursiveAiDiscoveryTechnique().execute(
        _context({"seed_results": {"rows": [{"url": "https://example.com/a"}, {"url": "https://example.com/b"}]}, "discovery_goal": "find related pages", "max_iterations": 2})
    )
    content = result.evidence[0].content

    assert content["discovered_sources"] == ["https://example.com/a", "https://example.com/b"]
    assert content["structured_results"][0]["goal"] == "find related pages"


def test_run_command_caches_subprocess_results_by_command_and_stdin(monkeypatch, tmp_path) -> None:
    calls = {"count": 0}

    class Completed:
        returncode = 0
        stdout = "first"
        stderr = ""

    def fake_run(*args, **kwargs):
        calls["count"] += 1
        return Completed()

    monkeypatch.setenv("OJO_M01_CACHE_DIR", tmp_path.as_posix())
    monkeypatch.delenv("OJO_M01_DISABLE_CACHE", raising=False)
    monkeypatch.setattr(techniques.subprocess, "run", fake_run)

    first = techniques._run_command(["/bin/tool", "example.com"], 10, stdin="a")
    second = techniques._run_command(["/bin/tool", "example.com"], 10, stdin="a")

    assert calls["count"] == 1
    assert first.cache_status == "miss"
    assert second.cache_status == "hit"
    assert second.stdout == "first"


def test_run_command_returns_honest_timeout_result(monkeypatch, tmp_path) -> None:
    def fake_run(*args, **kwargs):
        raise techniques.subprocess.TimeoutExpired(cmd=args[0], timeout=5, output="partial", stderr="late")

    monkeypatch.setenv("OJO_M01_CACHE_DIR", tmp_path.as_posix())
    monkeypatch.setattr(techniques.subprocess, "run", fake_run)

    result = techniques._run_command(["/bin/slow-tool"], 5)

    assert result.returncode == 124
    assert result.timed_out is True
    assert "timed out" in result.stderr
