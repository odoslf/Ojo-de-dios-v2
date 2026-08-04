"""Concrete passive M03 network-service fingerprinting and mapping techniques.

M03 is documented as an exploitation module, but this file intentionally exposes
only read-only techniques for Ronda 10: importing existing service fingerprints,
parsing operator-supplied scan artifacts, and deriving local banner fingerprints.
No technique in this file performs exploitation, authentication, payload delivery,
or service mutation.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from app.contracts.evidence_contract import EVIDENCE_QUALITY_HIGH, EvidenceRecord, RESULT_SUCCESS
from app.contracts.technique_contract import BaseTechnique, STATUS_READY_CONTROLLED, TechniqueExecutionContext, TechniqueExecutionResult
from app.core.errors import ContractError
from app.core.technique_evidence_utils import stable_evidence_id, utc_now_iso
from app.core.permission_levels import PERMISSION_PASSIVE

M03_MODULE_ID = "m03_network_services"


def _evidence(context: TechniqueExecutionContext, technique_id: str, suffix: str, summary: str, content: dict[str, Any]) -> EvidenceRecord:
    now = utc_now_iso()
    return EvidenceRecord(
        evidence_id=stable_evidence_id(context.run_id, technique_id, suffix),
        run_id=context.run_id,
        target_id=context.target_id,
        module_id=M03_MODULE_ID,
        technique_id=technique_id,
        evidence_type=suffix,
        summary=summary,
        content=content,
        created_at=now,
        quality=EVIDENCE_QUALITY_HIGH,
        source="m03-passive-fingerprint",
        demo=False,
        real_execution=True,
    )


def _string_list(parameters: dict[str, Any], name: str) -> list[str]:
    value = parameters.get(name, [])
    if isinstance(value, str):
        return [line.strip() for line in value.splitlines() if line.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    raise ContractError(f"{name} must be a list of strings or newline-separated string.")


def _fingerprints_from_parameter(parameters: dict[str, Any]) -> list[dict[str, Any]]:
    value = parameters.get("service_fingerprints")
    if not isinstance(value, list) or not value:
        raise ContractError("service_fingerprints must be a non-empty list of objects.")
    fingerprints: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ContractError("service_fingerprints entries must be objects.")
        port = item.get("port")
        if port is None:
            raise ContractError("service_fingerprints entries must include port.")
        fingerprints.append(
            {
                "host": str(item.get("host") or item.get("ip") or item.get("target") or "unknown"),
                "port": int(port),
                "transport": str(item.get("transport") or item.get("protocol") or "tcp").lower(),
                "service_name": str(item.get("service_name") or item.get("service") or "unknown"),
                "product": item.get("product"),
                "version": item.get("version"),
                "source": item.get("source", "operator_supplied"),
            }
        )
    return fingerprints


def _service_map(fingerprints: list[dict[str, Any]]) -> dict[str, Any]:
    by_host: dict[str, list[dict[str, Any]]] = {}
    affected_services: list[dict[str, Any]] = []
    graph_updates: list[dict[str, Any]] = []
    for fp in fingerprints:
        host = str(fp["host"])
        by_host.setdefault(host, []).append(fp)
        affected_services.append({"host": host, "port": fp["port"], "transport": fp["transport"], "service_name": fp["service_name"], "product": fp.get("product"), "version": fp.get("version")})
        graph_updates.append({"type": "ServiceFingerprint", "host": host, "port": fp["port"], "transport": fp["transport"], "service_name": fp["service_name"], "product": fp.get("product"), "version": fp.get("version")})
    return {"service_map": by_host, "affected_services": affected_services, "attack_surface_updates": graph_updates, "service_count": len(fingerprints)}


def _parse_nmap_xml(xml_text: str) -> list[dict[str, Any]]:
    if not xml_text.strip():
        raise ContractError("nmap XML content is empty.")
    root = ET.fromstring(xml_text)
    fingerprints: list[dict[str, Any]] = []
    for host_node in root.findall("host"):
        host = "unknown"
        address = host_node.find("address")
        if address is not None and address.attrib.get("addr"):
            host = str(address.attrib["addr"])
        for port_node in host_node.findall("./ports/port"):
            state = port_node.find("state")
            if state is not None and state.attrib.get("state") not in {"open", "open|filtered"}:
                continue
            service = port_node.find("service")
            fingerprints.append(
                {
                    "host": host,
                    "port": int(port_node.attrib["portid"]),
                    "transport": port_node.attrib.get("protocol", "tcp"),
                    "service_name": service.attrib.get("name", "unknown") if service is not None else "unknown",
                    "product": service.attrib.get("product") if service is not None else None,
                    "version": service.attrib.get("version") if service is not None else None,
                    "source": "nmap_xml_import",
                }
            )
    return fingerprints


def _nmap_xml_from_parameters(parameters: dict[str, Any]) -> str:
    if str(parameters.get("nmap_xml_content", "")).strip():
        return str(parameters["nmap_xml_content"])
    path_text = str(parameters.get("nmap_xml_path", "")).strip()
    if not path_text:
        raise ContractError("nmap_xml_content or nmap_xml_path is required.")
    path = Path(path_text)
    if not path.is_file():
        raise ContractError("nmap_xml_path must point to an existing file.")
    return path.read_text(encoding="utf-8")


def _fingerprint_banners(banners: list[str]) -> list[dict[str, Any]]:
    signatures = {
        "openssh": [r"openssh[_/-]?([0-9][^\s]*)?", "ssh-2.0"],
        "nginx": [r"nginx/([0-9][^\s]*)?"],
        "apache": [r"apache(?:/| httpd )([0-9][^\s]*)?"],
        "microsoft-iis": [r"microsoft-iis/([0-9][^\s]*)?"],
        "postfix": [r"postfix"],
        "mysql": [r"mysql"],
        "postgresql": [r"postgresql"],
    }
    results: list[dict[str, Any]] = []
    for index, banner in enumerate(banners):
        lower = banner.lower()
        for product, patterns in signatures.items():
            for pattern in patterns:
                match = re.search(pattern, lower)
                if match:
                    version = match.group(1).strip("/ _-") if match.lastindex and match.group(1) else None
                    results.append({"banner_index": index, "product": product, "version": version, "confidence": 0.9, "source": "banner_signature"})
                    break
    return results


class PassiveServiceFingerprintMapperTechnique(BaseTechnique):
    """Map upstream service fingerprints into M03 affected-service records."""

    technique_id = "netexploit.passive.service_fingerprint_mapper"
    module_id = M03_MODULE_ID
    display_name = "Passive service fingerprint mapper"
    description = "Transform supplied service_fingerprints into M03 service-map evidence without touching services."
    tool_name = "internal_mapper"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "NetworkExploitWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["service_fingerprints"]
    optional_inputs = ["attack_surface_graph_id", "finding_id", "evidence_profile"]
    expected_evidence = ["service_map", "service_fingerprints", "affected_services", "normalized_json"]
    input_schema = {"service_fingerprints": {"type": "array"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "service_fingerprints", "label": "Service fingerprints", "type": "textarea"}]
    success_markers = ["service_map", "affected_services"]
    failure_markers = ["missing_service_fingerprints"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"service_map": "dict", "service_fingerprints": "list", "affected_services": "list"}
    version_lock_id = "m03_network_services/passive-service-mapper"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        fingerprints = _fingerprints_from_parameter(context.parameters)
        mapped = _service_map(fingerprints)
        normalized = {"service_fingerprints": fingerprints, **mapped, "next_recommended_techniques": []}
        evidence = _evidence(context, self.technique_id, "passive_service_map", "Passive service fingerprint mapping completed.", normalized)
        return TechniqueExecutionResult(self.technique_id, M03_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class NmapXmlFingerprintImportTechnique(BaseTechnique):
    """Import operator-supplied nmap XML and map open services passively."""

    technique_id = "netexploit.passive.nmap_xml_fingerprint_import"
    module_id = M03_MODULE_ID
    display_name = "Nmap XML fingerprint import"
    description = "Parse existing nmap XML artifacts into service-fingerprint evidence without running nmap."
    tool_name = "nmap_xml_import"
    recommended_version = "Nmap 7.99 XML schema"
    runtime = "python_lib"
    worker = "EvidenceWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = []
    optional_inputs = ["nmap_xml_path", "nmap_xml_content", "evidence_profile"]
    expected_evidence = ["service_fingerprints", "service_map", "affected_services", "normalized_json"]
    input_schema = {"nmap_xml_path": {"type": "string"}, "nmap_xml_content": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "nmap_xml_path", "label": "Nmap XML path", "type": "text"}]
    success_markers = ["service_fingerprints", "service_map"]
    failure_markers = ["invalid_nmap_xml"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"service_fingerprints": "list", "service_map": "dict", "affected_services": "list"}
    version_lock_id = "m03_network_services/nmap-xml-import"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        fingerprints = _parse_nmap_xml(_nmap_xml_from_parameters(context.parameters))
        mapped = _service_map(fingerprints)
        normalized = {"service_fingerprints": fingerprints, **mapped, "raw_output_path": context.parameters.get("nmap_xml_path")}
        evidence = _evidence(context, self.technique_id, "nmap_xml_service_map", "Nmap XML service fingerprint import completed.", normalized)
        return TechniqueExecutionResult(self.technique_id, M03_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class PassiveBannerFingerprintTechnique(BaseTechnique):
    """Derive product/version hints from existing service banners only."""

    technique_id = "netexploit.passive.banner_fingerprint"
    module_id = M03_MODULE_ID
    display_name = "Passive banner fingerprint"
    description = "Classify operator-supplied service banners into product/version hints without connecting to targets."
    tool_name = "internal_banner_signature_catalog"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["banners"]
    optional_inputs = ["confidence_threshold", "evidence_profile"]
    expected_evidence = ["banner_fingerprints", "predicted_products", "predicted_versions", "normalized_json"]
    input_schema = {"banners": {"type": "array"}}
    ai_fillable_inputs = ["confidence_threshold"]
    panel_fields = [{"name": "banners", "label": "Service banners", "type": "textarea"}]
    success_markers = ["banner_fingerprints", "predicted_products"]
    failure_markers = ["missing_banners"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"banner_fingerprints": "list", "predicted_products": "list", "predicted_versions": "list"}
    version_lock_id = "m03_network_services/passive-banner-fingerprint"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        banners = _string_list(context.parameters, "banners")
        if not banners:
            raise ContractError("banners must include at least one banner.")
        threshold = float(context.parameters.get("confidence_threshold", 0.5))
        fingerprints = [item for item in _fingerprint_banners(banners) if float(item["confidence"]) >= threshold]
        products = sorted({str(item["product"]) for item in fingerprints})
        versions = [{"product": item["product"], "version": item["version"]} for item in fingerprints if item.get("version")]
        normalized = {"banner_fingerprints": fingerprints, "predicted_products": products, "predicted_versions": versions}
        evidence = _evidence(context, self.technique_id, "passive_banner_fingerprint", "Passive banner fingerprinting completed.", normalized)
        return TechniqueExecutionResult(self.technique_id, M03_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


def _dict_list(parameters: dict[str, Any], name: str) -> list[dict[str, Any]]:
    value = parameters.get(name, [])
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as error:
            raise ContractError(f"{name} must be JSON array text when supplied as a string.") from error
        value = parsed
    if not isinstance(value, list) or not value:
        raise ContractError(f"{name} must be a non-empty list of objects.")
    rows: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ContractError(f"{name} entries must be objects.")
        rows.append(item)
    return rows


def _service_identity(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "host": str(row.get("host") or row.get("ip") or row.get("target") or "unknown"),
        "port": int(row.get("port") or 0),
        "transport": str(row.get("transport") or row.get("protocol") or "tcp").lower(),
    }


def _tech_result(context: TechniqueExecutionContext, technique_id: str, suffix: str, summary: str, content: dict[str, Any]) -> TechniqueExecutionResult:
    evidence = _evidence(context, technique_id, suffix, summary, content)
    return TechniqueExecutionResult(technique_id, M03_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class PassiveTlsCertificateInventoryTechnique(BaseTechnique):
    """Normalize operator-supplied TLS certificate observations."""

    technique_id = "netexploit.passive.tls_certificate_inventory"
    module_id = M03_MODULE_ID
    display_name = "Passive TLS certificate inventory"
    description = "Build certificate/SAN/issuer inventory from existing TLS observations without connecting to hosts."
    tool_name = "internal_tls_certificate_parser"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "EvidenceWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["certificates"]
    optional_inputs = ["evidence_profile"]
    expected_evidence = ["certificate_inventory", "subject_names", "issuer_summary", "normalized_json"]
    input_schema = {"certificates": {"type": "array"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "certificates", "label": "Certificates", "type": "textarea"}]
    success_markers = ["certificate_inventory"]
    failure_markers = ["missing_certificates"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"certificate_inventory": "list", "subject_names": "list", "issuer_summary": "dict"}
    version_lock_id = "m03_network_services/passive-tls-certificate-inventory"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        rows = _dict_list(context.parameters, "certificates")
        inventory = []
        issuers: dict[str, int] = {}
        names: set[str] = set()
        for row in rows:
            san = [str(item).lower() for item in row.get("san", row.get("subject_alt_names", [])) if str(item).strip()] if isinstance(row.get("san", row.get("subject_alt_names", [])), list) else []
            common_name = str(row.get("common_name") or row.get("subject_cn") or "").lower()
            issuer = str(row.get("issuer") or row.get("issuer_cn") or "unknown")
            if common_name:
                names.add(common_name)
            names.update(san)
            issuers[issuer] = issuers.get(issuer, 0) + 1
            inventory.append(_service_identity(row) | {"common_name": common_name, "subject_alt_names": san, "issuer": issuer, "not_after": row.get("not_after"), "fingerprint_sha256": row.get("fingerprint_sha256")})
        return _tech_result(context, self.technique_id, "tls_certificate_inventory", "Passive TLS certificate inventory completed.", {"certificate_inventory": inventory, "subject_names": sorted(names), "issuer_summary": issuers})


class PassiveHttpHeaderFingerprintTechnique(BaseTechnique):
    technique_id = "netexploit.passive.http_header_fingerprint"
    module_id = M03_MODULE_ID
    display_name = "Passive HTTP header fingerprint"
    description = "Fingerprint products from supplied HTTP response headers without web requests."
    tool_name = "internal_http_header_parser"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "EvidenceWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["http_observations"]
    optional_inputs = ["evidence_profile"]
    expected_evidence = ["header_fingerprints", "technology_hints", "normalized_json"]
    input_schema = {"http_observations": {"type": "array"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "http_observations", "label": "HTTP observations", "type": "textarea"}]
    success_markers = ["header_fingerprints"]
    failure_markers = ["missing_http_observations"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"header_fingerprints": "list", "technology_hints": "list"}
    version_lock_id = "m03_network_services/passive-http-header-fingerprint"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        rows = _dict_list(context.parameters, "http_observations")
        fingerprints = []
        for row in rows:
            headers = row.get("headers", {})
            if not isinstance(headers, dict):
                headers = {}
            lowered = {str(k).lower(): str(v) for k, v in headers.items()}
            products = []
            server = lowered.get("server", "")
            powered = lowered.get("x-powered-by", "")
            for token in (server, powered):
                products.extend(item.strip() for item in re.split(r"[,;]", token) if item.strip())
            fingerprints.append(_service_identity(row) | {"url": row.get("url"), "status_code": row.get("status_code"), "products": products})
        hints = sorted({product for item in fingerprints for product in item["products"]})
        return _tech_result(context, self.technique_id, "http_header_fingerprint", "Passive HTTP header fingerprinting completed.", {"header_fingerprints": fingerprints, "technology_hints": hints})


class PassivePortRoleClassifierTechnique(BaseTechnique):
    technique_id = "netexploit.passive.port_role_classifier"
    module_id = M03_MODULE_ID
    display_name = "Passive port role classifier"
    description = "Classify common service roles from existing port observations only."
    tool_name = "internal_port_role_catalog"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "EvidenceWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["service_fingerprints"]
    optional_inputs = ["evidence_profile"]
    expected_evidence = ["role_assignments", "role_summary", "normalized_json"]
    input_schema = {"service_fingerprints": {"type": "array"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "service_fingerprints", "label": "Service fingerprints", "type": "textarea"}]
    success_markers = ["role_assignments"]
    failure_markers = ["missing_service_fingerprints"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"role_assignments": "list", "role_summary": "dict"}
    version_lock_id = "m03_network_services/passive-port-role-classifier"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        role_by_port = {22: "remote_admin", 80: "web", 443: "web", 25: "mail", 53: "dns", 445: "file_sharing", 3389: "remote_desktop", 5432: "database", 3306: "database"}
        assignments = []
        summary: dict[str, int] = {}
        for row in _dict_list(context.parameters, "service_fingerprints"):
            ident = _service_identity(row)
            role = role_by_port.get(ident["port"], str(row.get("service_name") or "unknown"))
            assignments.append(ident | {"service_name": row.get("service_name"), "role": role})
            summary[role] = summary.get(role, 0) + 1
        return _tech_result(context, self.technique_id, "port_role_classification", "Passive port role classification completed.", {"role_assignments": assignments, "role_summary": summary})


class PassiveMailSecurityInventoryTechnique(BaseTechnique):
    technique_id = "netexploit.passive.mail_security_inventory"
    module_id = M03_MODULE_ID
    display_name = "Passive mail security inventory"
    description = "Summarize supplied MX/SPF/DMARC observations without DNS queries."
    tool_name = "internal_mail_record_parser"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "EvidenceWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["mail_records"]
    optional_inputs = ["evidence_profile"]
    expected_evidence = ["mail_domains", "mail_security_summary", "normalized_json"]
    input_schema = {"mail_records": {"type": "array"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "mail_records", "label": "Mail records", "type": "textarea"}]
    success_markers = ["mail_security_summary"]
    failure_markers = ["missing_mail_records"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"mail_domains": "list", "mail_security_summary": "dict"}
    version_lock_id = "m03_network_services/passive-mail-security-inventory"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        domains = []
        missing = {"spf": [], "dmarc": [], "mx": []}
        for row in _dict_list(context.parameters, "mail_records"):
            domain = str(row.get("domain") or "unknown").lower()
            domains.append(domain)
            if not row.get("spf"):
                missing["spf"].append(domain)
            if not row.get("dmarc"):
                missing["dmarc"].append(domain)
            if not row.get("mx"):
                missing["mx"].append(domain)
        return _tech_result(context, self.technique_id, "mail_security_inventory", "Passive mail security inventory completed.", {"mail_domains": sorted(set(domains)), "mail_security_summary": {"missing": missing}})


class PassiveDnsServiceRecordMapperTechnique(BaseTechnique):
    technique_id = "netexploit.passive.dns_service_record_mapper"
    module_id = M03_MODULE_ID
    display_name = "Passive DNS service record mapper"
    description = "Map supplied SRV/TXT/A records into service hints without resolver traffic."
    tool_name = "internal_dns_record_mapper"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "EvidenceWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["dns_records"]
    optional_inputs = ["evidence_profile"]
    expected_evidence = ["dns_service_hints", "normalized_json"]
    input_schema = {"dns_records": {"type": "array"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "dns_records", "label": "DNS records", "type": "textarea"}]
    success_markers = ["dns_service_hints"]
    failure_markers = ["missing_dns_records"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"dns_service_hints": "list"}
    version_lock_id = "m03_network_services/passive-dns-service-record-mapper"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        hints = []
        for row in _dict_list(context.parameters, "dns_records"):
            rtype = str(row.get("type") or "").upper()
            name = str(row.get("name") or row.get("domain") or "").lower()
            value = str(row.get("value") or row.get("target") or "")
            if rtype == "SRV":
                parts = name.split(".")
                hints.append({"record_type": rtype, "name": name, "service": parts[0].lstrip("_") if parts else "unknown", "target": value})
            elif rtype in {"A", "AAAA", "CNAME", "TXT"}:
                hints.append({"record_type": rtype, "name": name, "target": value})
        return _tech_result(context, self.technique_id, "dns_service_record_map", "Passive DNS service record mapping completed.", {"dns_service_hints": hints})


class PassiveSshBannerClassifierTechnique(BaseTechnique):
    technique_id = "netexploit.passive.ssh_banner_classifier"
    module_id = M03_MODULE_ID
    display_name = "Passive SSH banner classifier"
    description = "Classify SSH implementations from supplied banners only."
    tool_name = "internal_ssh_banner_parser"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "EvidenceWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["banners"]
    optional_inputs = ["evidence_profile"]
    expected_evidence = ["ssh_fingerprints", "normalized_json"]
    input_schema = {"banners": {"type": "array"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "banners", "label": "SSH banners", "type": "textarea"}]
    success_markers = ["ssh_fingerprints"]
    failure_markers = ["missing_banners"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"ssh_fingerprints": "list"}
    version_lock_id = "m03_network_services/passive-ssh-banner-classifier"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        fingerprints = []
        for index, banner in enumerate(_string_list(context.parameters, "banners")):
            match = re.search(r"SSH-2\.0-([^\s]+)", banner, re.IGNORECASE)
            if match:
                product_version = match.group(1)
                product, _, version = product_version.replace("_", "-").partition("-")
                fingerprints.append({"banner_index": index, "product": product, "version": version or None, "confidence": 0.95})
        return _tech_result(context, self.technique_id, "ssh_banner_classification", "Passive SSH banner classification completed.", {"ssh_fingerprints": fingerprints})


class PassiveDatabaseServiceClassifierTechnique(PassivePortRoleClassifierTechnique):
    technique_id = "netexploit.passive.database_service_classifier"
    display_name = "Passive database service classifier"
    description = "Classify database services from supplied service observations only."
    required_inputs = ["service_fingerprints"]
    expected_evidence = ["database_services", "normalized_json"]
    success_markers = ["database_services"]
    evidence_schema = {"database_services": "list"}
    version_lock_id = "m03_network_services/passive-database-service-classifier"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        db_ports = {1433: "mssql", 1521: "oracle", 3306: "mysql", 5432: "postgresql", 6379: "redis", 27017: "mongodb"}
        services = []
        for row in _dict_list(context.parameters, "service_fingerprints"):
            ident = _service_identity(row)
            name = str(row.get("service_name") or "").lower()
            db = db_ports.get(ident["port"]) or next((candidate for candidate in db_ports.values() if candidate in name), None)
            if db:
                services.append(ident | {"database": db, "service_name": row.get("service_name"), "product": row.get("product"), "version": row.get("version")})
        return _tech_result(context, self.technique_id, "database_service_classification", "Passive database service classification completed.", {"database_services": services})


class PassiveRemoteAdminClassifierTechnique(PassivePortRoleClassifierTechnique):
    technique_id = "netexploit.passive.remote_admin_classifier"
    display_name = "Passive remote-admin classifier"
    description = "Classify remote administration services from supplied observations only."
    expected_evidence = ["remote_admin_services", "normalized_json"]
    success_markers = ["remote_admin_services"]
    evidence_schema = {"remote_admin_services": "list"}
    version_lock_id = "m03_network_services/passive-remote-admin-classifier"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        admin_ports = {22: "ssh", 3389: "rdp", 5900: "vnc", 5985: "winrm", 5986: "winrm_tls"}
        services = []
        for row in _dict_list(context.parameters, "service_fingerprints"):
            ident = _service_identity(row)
            if ident["port"] in admin_ports:
                services.append(ident | {"remote_admin_type": admin_ports[ident["port"]], "service_name": row.get("service_name")})
        return _tech_result(context, self.technique_id, "remote_admin_classification", "Passive remote-admin classification completed.", {"remote_admin_services": services})


class PassiveServiceOwnerMapperTechnique(BaseTechnique):
    technique_id = "netexploit.passive.service_owner_mapper"
    module_id = M03_MODULE_ID
    display_name = "Passive service owner mapper"
    description = "Join supplied service fingerprints with owner/team metadata without network access."
    tool_name = "internal_owner_mapper"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "EvidenceWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["service_fingerprints", "owner_records"]
    optional_inputs = ["evidence_profile"]
    expected_evidence = ["service_owners", "unowned_services", "normalized_json"]
    input_schema = {"service_fingerprints": {"type": "array"}, "owner_records": {"type": "array"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "service_fingerprints", "label": "Service fingerprints", "type": "textarea"}]
    success_markers = ["service_owners"]
    failure_markers = ["missing_owner_records"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"service_owners": "list", "unowned_services": "list"}
    version_lock_id = "m03_network_services/passive-service-owner-mapper"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        owners = {str(row.get("host") or row.get("ip") or "").lower(): row for row in _dict_list(context.parameters, "owner_records")}
        mapped = []
        unowned = []
        for row in _dict_list(context.parameters, "service_fingerprints"):
            ident = _service_identity(row)
            owner = owners.get(ident["host"].lower())
            if owner:
                mapped.append(ident | {"owner": owner.get("owner"), "team": owner.get("team")})
            else:
                unowned.append(ident)
        return _tech_result(context, self.technique_id, "service_owner_map", "Passive service owner mapping completed.", {"service_owners": mapped, "unowned_services": unowned})


class PassiveExposureTaggerTechnique(PassivePortRoleClassifierTechnique):
    technique_id = "netexploit.passive.exposure_tagger"
    display_name = "Passive exposure tagger"
    description = "Tag exposure categories from supplied service observations; it does not probe services."
    expected_evidence = ["exposure_tags", "normalized_json"]
    success_markers = ["exposure_tags"]
    evidence_schema = {"exposure_tags": "list"}
    version_lock_id = "m03_network_services/passive-exposure-tagger"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        tags = []
        internet_sensitive = {22, 3389, 445, 1433, 3306, 5432, 6379, 27017}
        for row in _dict_list(context.parameters, "service_fingerprints"):
            ident = _service_identity(row)
            tag = "internet_sensitive" if ident["port"] in internet_sensitive else "standard_service"
            tags.append(ident | {"tag": tag, "reason": "port_catalog"})
        return _tech_result(context, self.technique_id, "service_exposure_tags", "Passive exposure tagging completed.", {"exposure_tags": tags})


class PassiveAssetRelationshipMapperTechnique(BaseTechnique):
    technique_id = "netexploit.passive.asset_relationship_mapper"
    module_id = M03_MODULE_ID
    display_name = "Passive asset relationship mapper"
    description = "Build host/service/name relationship edges from supplied observations only."
    tool_name = "internal_relationship_mapper"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "EvidenceWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["service_fingerprints"]
    optional_inputs = ["dns_records", "certificates", "evidence_profile"]
    expected_evidence = ["relationship_edges", "normalized_json"]
    input_schema = {"service_fingerprints": {"type": "array"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "service_fingerprints", "label": "Service fingerprints", "type": "textarea"}]
    success_markers = ["relationship_edges"]
    failure_markers = ["missing_service_fingerprints"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"relationship_edges": "list"}
    version_lock_id = "m03_network_services/passive-asset-relationship-mapper"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        edges = []
        for row in _dict_list(context.parameters, "service_fingerprints"):
            ident = _service_identity(row)
            edges.append({"from": ident["host"], "to": f"{ident['host']}:{ident['port']}/{ident['transport']}", "relationship": "exposes_service"})
        for row in _dict_list({"dns_records": context.parameters.get("dns_records", []) or [{"skip": True}]}, "dns_records"):
            if row.get("skip"):
                continue
            edges.append({"from": row.get("name"), "to": row.get("value") or row.get("target"), "relationship": "resolves_to"})
        return _tech_result(context, self.technique_id, "asset_relationship_map", "Passive asset relationship mapping completed.", {"relationship_edges": edges})


class PassiveTechnologyStackMapperTechnique(PassiveHttpHeaderFingerprintTechnique):
    technique_id = "netexploit.passive.technology_stack_mapper"
    display_name = "Passive technology stack mapper"
    description = "Aggregate supplied header/banner/certificate observations into technology stacks."
    expected_evidence = ["technology_stacks", "normalized_json"]
    success_markers = ["technology_stacks"]
    evidence_schema = {"technology_stacks": "list"}
    version_lock_id = "m03_network_services/passive-technology-stack-mapper"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        stacks: dict[str, set[str]] = {}
        for row in _dict_list(context.parameters, "http_observations"):
            ident = _service_identity(row)
            key = f"{ident['host']}:{ident['port']}/{ident['transport']}"
            headers = row.get("headers", {}) if isinstance(row.get("headers", {}), dict) else {}
            stacks.setdefault(key, set()).update(str(value) for value in headers.values() if str(value).strip())
        normalized = {"technology_stacks": [{"service": key, "technologies": sorted(values)} for key, values in sorted(stacks.items())]}
        return _tech_result(context, self.technique_id, "technology_stack_map", "Passive technology stack mapping completed.", normalized)


class PassiveServiceLifecycleMapperTechnique(PassiveServiceOwnerMapperTechnique):
    technique_id = "netexploit.passive.service_lifecycle_mapper"
    display_name = "Passive service lifecycle mapper"
    description = "Join supplied services with lifecycle metadata such as environment and criticality."
    required_inputs = ["service_fingerprints", "lifecycle_records"]
    expected_evidence = ["service_lifecycle", "normalized_json"]
    success_markers = ["service_lifecycle"]
    evidence_schema = {"service_lifecycle": "list"}
    version_lock_id = "m03_network_services/passive-service-lifecycle-mapper"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        lifecycle = {str(row.get("host") or row.get("ip") or "").lower(): row for row in _dict_list(context.parameters, "lifecycle_records")}
        rows = []
        for service in _dict_list(context.parameters, "service_fingerprints"):
            ident = _service_identity(service)
            meta = lifecycle.get(ident["host"].lower(), {})
            rows.append(ident | {"environment": meta.get("environment", "unknown"), "criticality": meta.get("criticality", "unknown")})
        return _tech_result(context, self.technique_id, "service_lifecycle_map", "Passive service lifecycle mapping completed.", {"service_lifecycle": rows})


class PassiveProtocolFamilyClassifierTechnique(PassivePortRoleClassifierTechnique):
    technique_id = "netexploit.passive.protocol_family_classifier"
    display_name = "Passive protocol family classifier"
    description = "Classify protocol families from supplied service observations only."
    expected_evidence = ["protocol_families", "normalized_json"]
    success_markers = ["protocol_families"]
    evidence_schema = {"protocol_families": "list"}
    version_lock_id = "m03_network_services/passive-protocol-family-classifier"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        family_by_service = {"http": "web", "https": "web", "ssh": "remote_admin", "smtp": "mail", "domain": "dns", "dns": "dns", "mysql": "database", "postgresql": "database"}
        families = []
        for row in _dict_list(context.parameters, "service_fingerprints"):
            ident = _service_identity(row)
            service = str(row.get("service_name") or "").lower()
            families.append(ident | {"service_name": service, "protocol_family": family_by_service.get(service, "other")})
        return _tech_result(context, self.technique_id, "protocol_family_classification", "Passive protocol family classification completed.", {"protocol_families": families})


class PassiveHostnameRoleMapperTechnique(BaseTechnique):
    technique_id = "netexploit.passive.hostname_role_mapper"
    module_id = M03_MODULE_ID
    display_name = "Passive hostname role mapper"
    description = "Infer hostname roles from supplied names without DNS or network activity."
    tool_name = "internal_hostname_role_rules"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "EvidenceWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["hostnames"]
    optional_inputs = ["evidence_profile"]
    expected_evidence = ["hostname_roles", "normalized_json"]
    input_schema = {"hostnames": {"type": "array"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "hostnames", "label": "Hostnames", "type": "textarea"}]
    success_markers = ["hostname_roles"]
    failure_markers = ["missing_hostnames"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"hostname_roles": "list"}
    version_lock_id = "m03_network_services/passive-hostname-role-mapper"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        roles = []
        rules = {"api": "api", "db": "database", "sql": "database", "mail": "mail", "mx": "mail", "vpn": "remote_access", "dev": "development", "prod": "production"}
        for hostname in _string_list(context.parameters, "hostnames"):
            lower = hostname.lower()
            role = next((value for token, value in rules.items() if token in lower), "unknown")
            roles.append({"hostname": lower, "role": role})
        return _tech_result(context, self.technique_id, "hostname_role_map", "Passive hostname role mapping completed.", {"hostname_roles": roles})


def _nmap_json_from_parameters(parameters: dict[str, Any]) -> Any:
    if str(parameters.get("nmap_json_content", "")).strip():
        try:
            return json.loads(str(parameters["nmap_json_content"]))
        except json.JSONDecodeError as error:
            raise ContractError("nmap_json_content must be valid JSON.") from error
    path_text = str(parameters.get("nmap_json_path", "")).strip()
    if not path_text:
        raise ContractError("nmap_json_content or nmap_json_path is required.")
    path = Path(path_text)
    if not path.is_file():
        raise ContractError("nmap_json_path must point to an existing file.")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ContractError("nmap_json_path must contain valid JSON.") from error


def _parse_nmap_json(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        hosts = payload.get("hosts") or payload.get("host") or payload.get("scan") or []
        if isinstance(hosts, dict):
            hosts = [hosts]
    elif isinstance(payload, list):
        hosts = payload
    else:
        raise ContractError("Nmap JSON payload must be an object or array.")
    if not isinstance(hosts, list):
        raise ContractError("Nmap JSON hosts must be a list.")
    fingerprints: list[dict[str, Any]] = []
    for host_entry in hosts:
        if not isinstance(host_entry, dict):
            continue
        addresses = host_entry.get("addresses") or host_entry.get("address") or host_entry.get("ip") or host_entry.get("host") or "unknown"
        if isinstance(addresses, list):
            host = str(addresses[0]) if addresses else "unknown"
        elif isinstance(addresses, dict):
            host = str(addresses.get("addr") or addresses.get("ipv4") or addresses.get("ip") or "unknown")
        else:
            host = str(addresses)
        ports = host_entry.get("ports") or host_entry.get("port") or []
        if isinstance(ports, dict):
            ports = [ports]
        if not isinstance(ports, list):
            continue
        for port_entry in ports:
            if not isinstance(port_entry, dict):
                continue
            state = str(port_entry.get("state") or port_entry.get("status") or "open").lower()
            if state not in {"open", "open|filtered"}:
                continue
            service = port_entry.get("service", {}) if isinstance(port_entry.get("service", {}), dict) else {}
            fingerprints.append(
                {
                    "host": host,
                    "port": int(port_entry.get("port") or port_entry.get("portid")),
                    "transport": str(port_entry.get("protocol") or port_entry.get("transport") or "tcp").lower(),
                    "service_name": str(service.get("name") or port_entry.get("service_name") or port_entry.get("service") or "unknown"),
                    "product": service.get("product") or port_entry.get("product"),
                    "version": service.get("version") or port_entry.get("version"),
                    "source": "nmap_json_import",
                }
            )
    return fingerprints


class NmapJsonFingerprintImportTechnique(BaseTechnique):
    """Import operator-supplied nmap JSON-like artifacts and map services passively."""

    technique_id = "netexploit.passive.nmap_json_fingerprint_import"
    module_id = M03_MODULE_ID
    display_name = "Nmap JSON fingerprint import"
    description = "Parse existing Nmap JSON/converter artifacts into service-fingerprint evidence without running Nmap."
    tool_name = "nmap_json_import"
    recommended_version = "operator_supplied_json"
    runtime = "python_lib"
    worker = "EvidenceWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs: list[str] = []
    optional_inputs = ["nmap_json_path", "nmap_json_content", "evidence_profile"]
    expected_evidence = ["service_fingerprints", "service_map", "affected_services", "normalized_json"]
    input_schema = {"nmap_json_path": {"type": "string"}, "nmap_json_content": {"type": "string"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "nmap_json_path", "label": "Nmap JSON path", "type": "text"}]
    success_markers = ["service_fingerprints", "service_map"]
    failure_markers = ["invalid_nmap_json"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"service_fingerprints": "list", "service_map": "dict", "affected_services": "list"}
    version_lock_id = "m03_network_services/nmap-json-import"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        fingerprints = _parse_nmap_json(_nmap_json_from_parameters(context.parameters))
        mapped = _service_map(fingerprints)
        normalized = {"service_fingerprints": fingerprints, **mapped, "raw_output_path": context.parameters.get("nmap_json_path")}
        return _tech_result(context, self.technique_id, "nmap_json_service_map", "Nmap JSON service fingerprint import completed.", normalized)


def _cve_matches_service(service: dict[str, Any], cve: dict[str, Any]) -> bool:
    service_name = str(service.get("service_name") or "").lower()
    product = str(service.get("product") or "").lower()
    version = str(service.get("version") or "").lower()
    cve_products = [str(item).lower() for item in cve.get("products", [])] if isinstance(cve.get("products", []), list) else []
    cve_services = [str(item).lower() for item in cve.get("service_names", [])] if isinstance(cve.get("service_names", []), list) else []
    cve_versions = [str(item).lower() for item in cve.get("versions", [])] if isinstance(cve.get("versions", []), list) else []
    product_match = any(candidate and candidate in product for candidate in cve_products) or any(candidate and candidate in service_name for candidate in cve_services)
    version_match = not cve_versions or any(candidate and version.startswith(candidate) for candidate in cve_versions if candidate)
    return product_match and version_match


class PassiveCveCorrelationReportTechnique(BaseTechnique):
    """Correlate supplied services with a supplied CVE catalog in report-only mode."""

    technique_id = "netexploit.passive.cve_correlation_report"
    module_id = M03_MODULE_ID
    display_name = "Passive CVE correlation report"
    description = "List possible CVE correlations from supplied service data and catalog entries; never exploits or validates vulnerability presence."
    tool_name = "internal_cve_report_correlator"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "EvidenceWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["service_fingerprints", "cve_catalog"]
    optional_inputs = ["minimum_cvss", "evidence_profile"]
    expected_evidence = ["cve_correlations", "report_only", "normalized_json"]
    input_schema = {"service_fingerprints": {"type": "array"}, "cve_catalog": {"type": "array"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "service_fingerprints", "label": "Service fingerprints", "type": "textarea"}]
    success_markers = ["cve_correlations"]
    failure_markers = ["missing_service_fingerprints", "missing_cve_catalog"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"cve_correlations": "list", "report_only": "boolean"}
    version_lock_id = "m03_network_services/passive-cve-correlation-report"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        services = _dict_list(context.parameters, "service_fingerprints")
        cves = _dict_list(context.parameters, "cve_catalog")
        minimum_cvss = float(context.parameters.get("minimum_cvss", 0.0))
        correlations = []
        for service in services:
            ident = _service_identity(service)
            for cve in cves:
                score = float(cve.get("cvss", cve.get("score", 0.0)) or 0.0)
                if score < minimum_cvss or not _cve_matches_service(service, cve):
                    continue
                correlations.append(
                    ident
                    | {
                        "service_name": service.get("service_name"),
                        "product": service.get("product"),
                        "version": service.get("version"),
                        "cve_id": cve.get("cve_id") or cve.get("id"),
                        "cvss": score,
                        "summary": cve.get("summary"),
                        "confidence": "possible_version_match",
                        "validated_vulnerability": False,
                    }
                )
        normalized = {"cve_correlations": correlations, "report_only": True, "exploitation_attempted": False, "validation_attempted": False}
        return _tech_result(context, self.technique_id, "cve_correlation_report", "Passive CVE correlation report completed in report-only mode.", normalized)


def _safe_output_path(parameters: dict[str, Any], name: str = "output_path") -> Path:
    raw_path = str(parameters.get(name, "")).strip()
    if not raw_path:
        raise ContractError(f"{name} is required.")
    path = Path(raw_path)
    if path.exists() and path.is_dir():
        raise ContractError(f"{name} must be a file path, not a directory.")
    if path.suffix.lower() != ".json":
        raise ContractError(f"{name} must end with .json.")
    return path


def _graph_from_services_and_edges(services: list[dict[str, Any]], extra_edges: list[dict[str, Any]]) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    for service in services:
        ident = _service_identity(service)
        host_id = f"host:{ident['host']}"
        service_id = f"service:{ident['host']}:{ident['port']}/{ident['transport']}"
        nodes.setdefault(host_id, {"id": host_id, "type": "host", "label": ident["host"]})
        nodes[service_id] = {
            "id": service_id,
            "type": "service",
            "label": f"{service.get('service_name') or 'unknown'} {ident['port']}/{ident['transport']}",
            "host": ident["host"],
            "port": ident["port"],
            "transport": ident["transport"],
            "service_name": service.get("service_name"),
            "product": service.get("product"),
            "version": service.get("version"),
        }
        edges.append({"from": host_id, "to": service_id, "relationship": "exposes_service"})
    for edge in extra_edges:
        source = str(edge.get("from") or edge.get("source") or "").strip()
        target = str(edge.get("to") or edge.get("target") or "").strip()
        if not source or not target:
            continue
        source_id = source if ":" in source else f"asset:{source}"
        target_id = target if ":" in target else f"asset:{target}"
        nodes.setdefault(source_id, {"id": source_id, "type": "asset", "label": source})
        nodes.setdefault(target_id, {"id": target_id, "type": "asset", "label": target})
        edges.append({"from": source_id, "to": target_id, "relationship": str(edge.get("relationship") or "related_to")})
    return {"nodes": sorted(nodes.values(), key=lambda item: item["id"]), "edges": edges, "node_count": len(nodes), "edge_count": len(edges)}


class PassiveNetworkGraphExportTechnique(BaseTechnique):
    """Export supplied passive network map data to a JSON graph artifact."""

    technique_id = "netexploit.passive.network_graph_export"
    module_id = M03_MODULE_ID
    display_name = "Passive network graph export"
    description = "Export supplied M03 passive service/relationship data to a JSON graph file without probing any target."
    tool_name = "internal_json_graph_exporter"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "EvidenceWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["service_fingerprints", "output_path"]
    optional_inputs = ["relationship_edges", "workspace_id", "evidence_profile"]
    expected_evidence = ["graph_json", "export_path", "node_count", "edge_count"]
    input_schema = {"service_fingerprints": {"type": "array"}, "relationship_edges": {"type": "array"}, "output_path": {"type": "string"}}
    ai_fillable_inputs: list[str] = []
    panel_fields = [{"name": "output_path", "label": "Output JSON path", "type": "text"}]
    success_markers = ["export_path", "graph_json"]
    failure_markers = ["missing_service_fingerprints", "invalid_output_path"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"graph_json": "dict", "export_path": "string", "node_count": "integer", "edge_count": "integer"}
    version_lock_id = "m03_network_services/passive-network-graph-export"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        services = _dict_list(context.parameters, "service_fingerprints")
        raw_edges = context.parameters.get("relationship_edges", [])
        edges = _dict_list({"relationship_edges": raw_edges or [{"skip": True}]}, "relationship_edges")
        edges = [edge for edge in edges if not edge.get("skip")]
        output_path = _safe_output_path(context.parameters)
        graph = _graph_from_services_and_edges(services, edges)
        payload = {"schema_version": "m03.network_graph.v1", "module_id": M03_MODULE_ID, "graph": graph}
        output_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
        temporary_path.write_text(json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary_path.replace(output_path)
        normalized = {"graph_json": payload, "export_path": output_path.as_posix(), "node_count": graph["node_count"], "edge_count": graph["edge_count"]}
        return _tech_result(context, self.technique_id, "network_graph_export", "Passive network graph JSON export completed.", normalized)
