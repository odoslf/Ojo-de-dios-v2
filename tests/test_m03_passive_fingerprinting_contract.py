"""M03 passive fingerprinting and mapping contracts."""

import json

from app.contracts.evidence_contract import RESULT_SUCCESS
from app.contracts.technique_contract import STATUS_READY_CONTROLLED, TechniqueExecutionContext
from app.core.errors import ContractError
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.registry_loader import load_registry_from_package
from app.modules.m03_network_services.techniques import (
    NmapJsonFingerprintImportTechnique,
    NmapXmlFingerprintImportTechnique,
    PassiveNetworkGraphExportTechnique,
    PassiveCveCorrelationReportTechnique,
    PassiveAssetRelationshipMapperTechnique,
    PassiveBannerFingerprintTechnique,
    PassiveDatabaseServiceClassifierTechnique,
    PassiveDnsServiceRecordMapperTechnique,
    PassiveExposureTaggerTechnique,
    PassiveHostnameRoleMapperTechnique,
    PassiveHttpHeaderFingerprintTechnique,
    PassiveMailSecurityInventoryTechnique,
    PassivePortRoleClassifierTechnique,
    PassiveProtocolFamilyClassifierTechnique,
    PassiveRemoteAdminClassifierTechnique,
    PassiveServiceFingerprintMapperTechnique,
    PassiveServiceLifecycleMapperTechnique,
    PassiveServiceOwnerMapperTechnique,
    PassiveSshBannerClassifierTechnique,
    PassiveTechnologyStackMapperTechnique,
    PassiveTlsCertificateInventoryTechnique,
)


def _context(parameters: dict[str, object]) -> TechniqueExecutionContext:
    return TechniqueExecutionContext(target_id="target-3", run_id="run-3", mode="controlled", parameters=parameters, confirmed=True)


def test_m03_registers_only_passive_ready_fingerprinting_techniques() -> None:
    registry = load_registry_from_package("app.modules.m03_network_services")

    assert registry.list_ids() == [
        "netexploit.passive.asset_relationship_mapper",
        "netexploit.passive.banner_fingerprint",
        "netexploit.passive.cve_correlation_report",
        "netexploit.passive.database_service_classifier",
        "netexploit.passive.dns_service_record_mapper",
        "netexploit.passive.exposure_tagger",
        "netexploit.passive.hostname_role_mapper",
        "netexploit.passive.http_header_fingerprint",
        "netexploit.passive.mail_security_inventory",
        "netexploit.passive.network_graph_export",
        "netexploit.passive.nmap_json_fingerprint_import",
        "netexploit.passive.nmap_xml_fingerprint_import",
        "netexploit.passive.port_role_classifier",
        "netexploit.passive.protocol_family_classifier",
        "netexploit.passive.remote_admin_classifier",
        "netexploit.passive.service_fingerprint_mapper",
        "netexploit.passive.service_lifecycle_mapper",
        "netexploit.passive.service_owner_mapper",
        "netexploit.passive.ssh_banner_classifier",
        "netexploit.passive.technology_stack_mapper",
        "netexploit.passive.tls_certificate_inventory",
    ]
    for technique_cls in registry.list_all():
        technique = technique_cls()
        technique.validate_metadata()
        assert technique.module_id == "m03_network_services"
        assert technique.permission_level == PERMISSION_PASSIVE
        assert technique.implementation_status == STATUS_READY_CONTROLLED
        assert technique.requires_user_implementation is False
        assert technique.requires_network is False


def test_passive_service_fingerprint_mapper_builds_service_map_without_network() -> None:
    result = PassiveServiceFingerprintMapperTechnique().execute(
        _context(
            {
                "service_fingerprints": [
                    {"host": "10.0.0.5", "port": 22, "transport": "tcp", "service_name": "ssh", "product": "OpenSSH", "version": "9.6"},
                    {"host": "10.0.0.5", "port": 443, "service_name": "https", "product": "nginx"},
                ]
            }
        )
    )
    content = result.evidence[0].content

    assert result.result_status == RESULT_SUCCESS
    assert content["service_count"] == 2
    assert {"host", "port", "service_name", "source", "transport"} <= set(content["service_map"]["10.0.0.5"][0])
    assert content["attack_surface_updates"][0]["type"] == "ServiceFingerprint"


def test_nmap_xml_fingerprint_import_parses_existing_artifact(tmp_path) -> None:
    xml_path = tmp_path / "nmap.xml"
    xml_path.write_text(
        '<nmaprun><host><address addr="10.0.0.8" addrtype="ipv4"/><ports><port protocol="tcp" portid="80"><state state="open"/><service name="http" product="Apache" version="2.4"/></port><port protocol="tcp" portid="25"><state state="closed"/><service name="smtp"/></port></ports></host></nmaprun>',
        encoding="utf-8",
    )

    result = NmapXmlFingerprintImportTechnique().execute(_context({"nmap_xml_path": xml_path.as_posix()}))
    content = result.evidence[0].content

    assert result.result_status == RESULT_SUCCESS
    assert content["service_fingerprints"] == [
        {"host": "10.0.0.8", "port": 80, "transport": "tcp", "service_name": "http", "product": "Apache", "version": "2.4", "source": "nmap_xml_import"}
    ]
    assert content["raw_output_path"] == xml_path.as_posix()


def test_passive_banner_fingerprint_extracts_products_versions() -> None:
    result = PassiveBannerFingerprintTechnique().execute(_context({"banners": ["SSH-2.0-OpenSSH_9.6", "Server: nginx/1.24.0"]}))
    content = result.evidence[0].content

    assert result.result_status == RESULT_SUCCESS
    assert content["predicted_products"] == ["nginx", "openssh"]
    assert {item["product"] for item in content["predicted_versions"]} == {"nginx", "openssh"}


def test_m03_passive_mapper_rejects_missing_fingerprints() -> None:
    try:
        PassiveServiceFingerprintMapperTechnique().execute(_context({"service_fingerprints": []}))
    except ContractError as error:
        assert "service_fingerprints" in str(error)
    else:
        raise AssertionError("Expected missing service fingerprints to fail loudly.")


def test_m03_next_passive_batch_maps_artifacts_without_network() -> None:
    service_fingerprints = [
        {"host": "10.0.0.10", "port": 22, "service_name": "ssh", "product": "OpenSSH", "version": "9.6"},
        {"host": "10.0.0.20", "port": 5432, "service_name": "postgresql", "product": "PostgreSQL", "version": "16"},
        {"host": "10.0.0.30", "port": 443, "service_name": "https"},
    ]
    http_observations = [{"host": "10.0.0.30", "port": 443, "headers": {"Server": "nginx/1.24", "X-Powered-By": "Express"}, "status_code": 200}]

    assert PassivePortRoleClassifierTechnique().execute(_context({"service_fingerprints": service_fingerprints})).evidence[0].content["role_summary"]["remote_admin"] == 1
    assert PassiveDatabaseServiceClassifierTechnique().execute(_context({"service_fingerprints": service_fingerprints})).evidence[0].content["database_services"][0]["database"] == "postgresql"
    assert PassiveRemoteAdminClassifierTechnique().execute(_context({"service_fingerprints": service_fingerprints})).evidence[0].content["remote_admin_services"][0]["remote_admin_type"] == "ssh"
    assert PassiveExposureTaggerTechnique().execute(_context({"service_fingerprints": service_fingerprints})).evidence[0].content["exposure_tags"][0]["tag"] == "internet_sensitive"
    assert PassiveProtocolFamilyClassifierTechnique().execute(_context({"service_fingerprints": service_fingerprints})).evidence[0].content["protocol_families"][2]["protocol_family"] == "web"
    assert PassiveHttpHeaderFingerprintTechnique().execute(_context({"http_observations": http_observations})).evidence[0].content["technology_hints"] == ["Express", "nginx/1.24"]
    assert PassiveTechnologyStackMapperTechnique().execute(_context({"http_observations": http_observations})).evidence[0].content["technology_stacks"][0]["technologies"] == ["Express", "nginx/1.24"]


def test_m03_next_passive_batch_maps_names_ownership_and_certificates() -> None:
    service_fingerprints = [{"host": "10.0.0.10", "port": 443, "service_name": "https"}]

    tls = PassiveTlsCertificateInventoryTechnique().execute(_context({"certificates": [{"host": "10.0.0.10", "port": 443, "common_name": "www.example.com", "san": ["api.example.com"], "issuer": "Example CA"}]})).evidence[0].content
    assert tls["subject_names"] == ["api.example.com", "www.example.com"]
    assert tls["issuer_summary"] == {"Example CA": 1}

    dns = PassiveDnsServiceRecordMapperTechnique().execute(_context({"dns_records": [{"type": "SRV", "name": "_sip._tcp.example.com", "target": "sip.example.com"}]})).evidence[0].content
    assert dns["dns_service_hints"][0]["service"] == "sip"

    mail = PassiveMailSecurityInventoryTechnique().execute(_context({"mail_records": [{"domain": "example.com", "mx": ["mx.example.com"], "spf": "v=spf1 -all", "dmarc": "v=DMARC1"}, {"domain": "missing.example"}]})).evidence[0].content
    assert mail["mail_security_summary"]["missing"]["mx"] == ["missing.example"]

    assert PassiveSshBannerClassifierTechnique().execute(_context({"banners": ["SSH-2.0-OpenSSH_9.6"]})).evidence[0].content["ssh_fingerprints"][0]["product"] == "OpenSSH"
    assert PassiveHostnameRoleMapperTechnique().execute(_context({"hostnames": ["prod-db-01.example.com"]})).evidence[0].content["hostname_roles"][0]["role"] == "database"
    assert PassiveServiceOwnerMapperTechnique().execute(_context({"service_fingerprints": service_fingerprints, "owner_records": [{"host": "10.0.0.10", "owner": "SecOps", "team": "Blue"}]})).evidence[0].content["service_owners"][0]["team"] == "Blue"
    assert PassiveServiceLifecycleMapperTechnique().execute(_context({"service_fingerprints": service_fingerprints, "lifecycle_records": [{"host": "10.0.0.10", "environment": "prod", "criticality": "high"}]})).evidence[0].content["service_lifecycle"][0]["criticality"] == "high"
    assert PassiveAssetRelationshipMapperTechnique().execute(_context({"service_fingerprints": service_fingerprints, "dns_records": [{"name": "www.example.com", "value": "10.0.0.10"}]})).evidence[0].content["relationship_edges"][0]["relationship"] == "exposes_service"


def test_nmap_json_fingerprint_import_parses_existing_json_artifact(tmp_path) -> None:
    json_path = tmp_path / "nmap.json"
    json_path.write_text(
        '{"hosts":[{"addresses":["10.0.0.9"],"ports":[{"port":443,"protocol":"tcp","state":"open","service":{"name":"https","product":"nginx","version":"1.24"}},{"port":23,"state":"closed","service":{"name":"telnet"}}]}]}',
        encoding="utf-8",
    )

    result = NmapJsonFingerprintImportTechnique().execute(_context({"nmap_json_path": json_path.as_posix()}))
    content = result.evidence[0].content

    assert content["service_fingerprints"] == [
        {"host": "10.0.0.9", "port": 443, "transport": "tcp", "service_name": "https", "product": "nginx", "version": "1.24", "source": "nmap_json_import"}
    ]
    assert content["service_count"] == 1
    assert content["raw_output_path"] == json_path.as_posix()


def test_passive_cve_correlation_is_report_only_and_never_validates_or_exploits() -> None:
    result = PassiveCveCorrelationReportTechnique().execute(
        _context(
            {
                "service_fingerprints": [{"host": "10.0.0.9", "port": 443, "service_name": "https", "product": "nginx", "version": "1.24.0"}],
                "cve_catalog": [{"cve_id": "CVE-2026-0001", "products": ["nginx"], "versions": ["1.24"], "cvss": 7.5, "summary": "Example report-only match"}],
                "minimum_cvss": 7.0,
            }
        )
    )
    content = result.evidence[0].content

    assert content["report_only"] is True
    assert content["exploitation_attempted"] is False
    assert content["validation_attempted"] is False
    assert content["cve_correlations"][0]["cve_id"] == "CVE-2026-0001"
    assert content["cve_correlations"][0]["validated_vulnerability"] is False


def test_passive_network_graph_export_writes_json_artifact(tmp_path) -> None:
    output_path = tmp_path / "m03_graph.json"
    result = PassiveNetworkGraphExportTechnique().execute(
        _context(
            {
                "output_path": output_path.as_posix(),
                "service_fingerprints": [
                    {"host": "10.0.0.10", "port": 443, "transport": "tcp", "service_name": "https", "product": "nginx", "version": "1.24"}
                ],
                "relationship_edges": [{"from": "www.example.com", "to": "10.0.0.10", "relationship": "resolves_to"}],
            }
        )
    )

    exported = json.loads(output_path.read_text(encoding="utf-8"))
    content = result.evidence[0].content

    assert result.result_status == RESULT_SUCCESS
    assert content["export_path"] == output_path.as_posix()
    assert exported["schema_version"] == "m03.network_graph.v1"
    assert exported["graph"]["node_count"] == 4
    assert {edge["relationship"] for edge in exported["graph"]["edges"]} == {"exposes_service", "resolves_to"}


def test_passive_network_graph_export_rejects_non_json_output(tmp_path) -> None:
    try:
        PassiveNetworkGraphExportTechnique().execute(
            _context({"output_path": (tmp_path / "graph.txt").as_posix(), "service_fingerprints": [{"host": "10.0.0.10", "port": 443}]})
        )
    except ContractError as error:
        assert "must end with .json" in str(error)
    else:
        raise AssertionError("Expected non-JSON graph export path to fail loudly.")
