# MÓDULO 2 — ANÁLISIS DE VULNERABILIDADES

## PARTE 1/2 — BASE + TÉCNICAS 1-10

### Regla absoluta

NO_DOCKER=true

Este módulo solo usa:

- binarios Windows;
- aplicaciones Windows;
- Python en Windows;
- WSL2 con paquetes instalados manualmente;
- APIs locales en localhost;
- IA local.

Runtimes prohibidos:

- docker
- docker_compose
- container_runtime

### Base del módulo

module_id: vulnerabilities
module_name: Análisis de Vulnerabilidades
panel: Vulnerabilidades
default_status: IMPLEMENTACION_USUARIO_REQUERIDA
default_demo: true
default_dry_run: true
default_user_logic: true

workers:

- VulnerabilityWorker
- WindowsWorker
- WSLWorker
- APIWorker
- PythonToolWorker
- WebScannerWorker
- AIWorker
- GVMWorker
- MetasploitRPCWorker
- OpsWorker

runtimes:

- windows_binary
- windows_app
- python_lib
- wsl2
- local_api
- local_ai
- manual_required

inputs_base:

- target_id
- target_type
- target_value
- service_fingerprints
- web_endpoints
- technology_fingerprints
- ports
- protocols
- headers
- certificates
- scope_profile
- execution_mode
- evidence_profile

outputs_base:

- vulnerability_findings
- cve_candidates
- misconfig_findings
- exposed_panels
- tls_findings
- exploit_references
- false_positive_status
- dynamic_cvss
- critical_preparation
- next_module_recommendations
- evidence_ids

evidence_comun:

- raw_output_path
- normalized_json
- finding_id
- affected_asset
- affected_service
- cve_id
- cwe_id
- severity
- confidence
- cvss_base
- cvss_contextual
- tool_version
- template_id
- plugin_id
- source
- validation_status
- false_positive_status
- exploit_available
- recommended_next_step
- started_at
- finished_at
- errors
- warnings

panel_base:

- target_selector
- asset_filter
- service_filter
- scan_profile
- severity_filter
- template_profile
- validation_profile
- rate_limit_profile
- output_profile
- evidence_profile
- execution_mode
- send_to_module_3
- notes_for_laia

execution_mode:

- demo
- dry_run
- controlled
- expert

### Versiones oficiales de este módulo

Nuclei: 3.8.0
Nuclei Templates: 10.4.4
Nmap: 7.99 + Npcap 1.88
OpenVAS/GVM: latest-release-lock en WSL2/Kali, sin Docker
OpenVAS/GVM baseline_usuario: openvas-scanner 23.26.1, gvmd 23.11.0, ospd-openvas 23.1.0
Nikto: 2.6.0
Nikto nota: parser_compatibility_review_required=true por cambios de formato JSON/XML
Wapiti: 3.3.0
ZAP: 2.17.0
Burp Suite Community: latest-release-lock
Burp baseline_usuario: 2026.5.1
testssl.sh: 3.2 latest-release-lock

### Anclajes reales por herramienta

#### NucleiAdapter

runtime: windows_binary
worker: WindowsWorker
connection_fields: targets, template_profile, severity_filter, tags, rate_limit_profile, output_format, evidence_profile
outputs: template_matches, cve_findings, misconfig_findings, exposed_panels, raw_output_path, normalized_json
hook_base: app/modules/vulnerabilities/adapters/nuclei_adapter.py::NucleiAdapter
notes: no_docker, json_or_sarif_output, versionlock_required

#### GVMAdapter

runtime: wsl2_local_api
worker: GVMWorker
connection_fields: gmp_profile, target_profile, scan_config_profile, credential_profile, schedule_profile, report_profile, evidence_profile
outputs: gvm_task_reference, report_reference, vulnerability_findings, plugin_results, raw_output_path, normalized_json
hook_base: app/modules/vulnerabilities/adapters/gvm_adapter.py::GVMAdapter
notes: no_docker, python_gvm_connection, latest_release_lock, package_version_resolved_in_wsl2

#### WebScannerAdapter

runtime: python_lib_or_wsl2
worker: WebScannerWorker
connection_fields: target_url, crawl_profile, auth_context, scan_profile, module_profile, output_format, evidence_profile
outputs: web_findings, request_response_summary, raw_output_path, normalized_json
hook_base: app/modules/vulnerabilities/adapters/web_scanner_adapter.py::WebScannerAdapter
notes: used_by_nikto_wapiti_zap_burp_launcher

#### TLSScannerAdapter

runtime: wsl2
worker: WSLWorker
connection_fields: host, port, tls_profile, output_format, evidence_profile
outputs: tls_findings, certificate_summary, protocol_summary, cipher_summary, raw_output_path, normalized_json
hook_base: app/modules/vulnerabilities/adapters/tls_scanner_adapter.py::TLSScannerAdapter
notes: used_by_testssl, no_docker

#### ExploitReferenceAdapter

runtime: wsl2_or_python_lib
worker: PythonToolWorker
connection_fields: product, version, cve_id, service_fingerprint, source_profile, evidence_profile
outputs: exploit_references, public_reference_summary, confidence, normalized_json
hook_base: app/modules/vulnerabilities/adapters/exploit_reference_adapter.py::ExploitReferenceAdapter
notes: used_by_searchsploit_metasploit_packetstorm, does_not_execute_exploit

#### InventoryAdapter

runtime: windows_binary_or_windows_agent
worker: WindowsWorker
connection_fields: host_profile, inventory_profile, query_pack, agent_profile, output_format, evidence_profile
outputs: software_inventory, vulnerable_software_candidates, agent_inventory, normalized_json
hook_base: app/modules/vulnerabilities/adapters/inventory_adapter.py::InventoryAdapter
notes: used_by_osquery_wazuh, passive_or_agent_based

#### AICveReasonerAdapter

runtime: local_ai
worker: AIWorker
connection_fields: service_fingerprints, banners, technology_fingerprints, cve_candidates, evidence_profile, scoring_profile
outputs: prioritized_cves, dynamic_cvss, false_positive_status, recommended_next_step, normalized_json
hook_base: app/modules/vulnerabilities/adapters/ai_cve_reasoner_adapter.py::AICveReasonerAdapter
notes: no_execution, no_fake_cves, evidence_required

### Técnicas 1-10

#### 1. vuln.nuclei_cve_detection

tool: Nuclei + Nuclei Templates
version: Nuclei 3.8.0 + Templates 10.4.4
runtime: windows_binary
worker: WindowsWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, template_profile, severity_filter, tags, rate_limit_profile, output_format, evidence_profile
inputs: targets:list_string, template_profile:cve|default|custom, severity_filter:list_enum, tags:list_string, rate_limit_profile:string, output_format:json|sarif|report
ai: template_profile, severity_filter, tags, rate_limit_profile
evidence: cve_findings, template_matches, raw_output_path, normalized_json, cve_candidates, attack_surface_updates
graph: CVENode, WeaknessNode, ServiceNode, FindingNode
hook: app/modules/vulnerabilities/nuclei_cve_detection.py::NucleiCveDetectionTechnique.execute
notes: no_docker, versionlock_required

#### 2. vuln.nuclei_misconfig_detection

tool: Nuclei
version: 3.8.0
runtime: windows_binary
worker: WindowsWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, template_profile, misconfig_categories, severity_filter, output_format, rate_limit_profile
inputs: targets:list_string, template_profile:misconfig|default|custom, misconfig_categories:list_string, severity_filter:list_enum, output_format:json|sarif|report, rate_limit_profile:string
ai: template_profile, misconfig_categories, severity_filter
evidence: misconfig_findings, template_matches, normalized_json, raw_output_path
graph: MisconfigNode, WeaknessNode, ServiceNode, FindingNode
hook: app/modules/vulnerabilities/nuclei_misconfig_detection.py::NucleiMisconfigDetectionTechnique.execute
notes: no_docker

#### 3. vuln.nuclei_panel_exposure

tool: Nuclei
version: 3.8.0
runtime: windows_binary
worker: WindowsWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, panel_categories, template_profile, output_format, rate_limit_profile, screenshot_reference
inputs: targets:list_string, panel_categories:list_string, template_profile:panel|exposure|custom, output_format:json|report, rate_limit_profile:string, screenshot_reference:string_optional
ai: panel_categories, template_profile
evidence: exposed_panels, exposed_paths, template_matches, normalized_json
graph: ExposedPanelNode, WebEndpointNode, FindingNode
hook: app/modules/vulnerabilities/nuclei_panel_exposure.py::NucleiPanelExposureTechnique.execute
notes: no_docker

#### 4. vuln.openvas_gvm_deep_scan

tool: OpenVAS/GVM + python-gvm
version: latest-release-lock
baseline_usuario: openvas-scanner 23.26.1 + gvmd 23.11.0 + ospd-openvas 23.1.0
runtime: wsl2_local_api
worker: GVMWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, gvm_profile, scan_config, credential_profile, port_list_profile, max_duration_seconds, output_format
inputs: targets:list_string, gvm_profile:string, scan_config:string, credential_profile:string_optional, port_list_profile:string, max_duration_seconds:int, output_format:xml|json|report
ai: scan_config, port_list_profile, max_duration_seconds
evidence: gvm_findings, cve_candidates, vt_references, raw_report_path, normalized_json
graph: CVENode, WeaknessNode, ServiceNode, FindingNode
hook: app/modules/vulnerabilities/openvas_gvm_deep_scan.py::OpenvasGvmDeepScanTechnique.execute
notes: no_docker, wsl2_only, python_gvm_connector, resolve_real_versions_in_versionlock=true

#### 5. vuln.nikto_web_scan

tool: Nikto
version: 2.6.0
runtime: wsl2
worker: WSLWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: urls, scan_profile, tuning_profile, output_format, max_duration_seconds
inputs: urls:list_string, scan_profile:standard|deep|custom, tuning_profile:string_optional, output_format:json|xml|report, max_duration_seconds:int
ai: scan_profile, tuning_profile, max_duration_seconds
evidence: web_findings, dangerous_files, outdated_versions, raw_output_path, normalized_json
graph: WebEndpointNode, WeaknessNode, FindingNode
hook: app/modules/vulnerabilities/nikto_web_scan.py::NiktoWebScanTechnique.execute
notes: no_docker, wsl2_runtime, parser_compatibility_review_required=true

#### 6. vuln.wapiti_web_scan

tool: Wapiti
version: 3.3.0
runtime: python_lib
worker: PythonToolWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: urls, scan_profile, module_profile, scope_profile, output_format, max_depth
inputs: urls:list_string, scan_profile:standard|deep|custom, module_profile:string, scope_profile:string, output_format:json|html|report, max_depth:int
ai: scan_profile, module_profile, scope_profile, max_depth
evidence: web_vuln_findings, injection_findings, raw_output_path, normalized_json, report_path
graph: WebEndpointNode, WeaknessNode, FindingNode
hook: app/modules/vulnerabilities/wapiti_web_scan.py::WapitiWebScanTechnique.execute
notes: no_docker

#### 7. vuln.zap_automated_scan

tool: ZAP
version: 2.17.0
runtime: windows_app_local_api
worker: APIWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: target_url, zap_api_profile, scan_profile, spider_enabled, ajax_spider_enabled, output_format, max_duration_seconds
inputs: target_url:string, zap_api_profile:string, scan_profile:baseline|standard|full|custom, spider_enabled:bool, ajax_spider_enabled:bool, output_format:json|html|report, max_duration_seconds:int
ai: scan_profile, spider_enabled, ajax_spider_enabled, max_duration_seconds
evidence: zap_alerts, spider_results, scan_report_path, normalized_json
graph: WebEndpointNode, WeaknessNode, FindingNode
hook: app/modules/vulnerabilities/zap_automated_scan.py::ZapAutomatedScanTechnique.execute
notes: no_docker, local_api=http://localhost:8080

#### 8. vuln.burp_manual_scan

tool: Burp Suite Community
version: latest-release-lock
baseline_usuario: 2026.5.1
runtime: windows_app
worker: WindowsWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: project_profile, target_url, proxy_profile, notes, evidence_import_path
inputs: project_profile:string, target_url:string, proxy_profile:string_optional, notes:string_optional, evidence_import_path:path_optional
ai: target_url, notes
evidence: manual_scan_notes, imported_findings, evidence_import_path, normalized_json
graph: WebEndpointNode, FindingNode
hook: app/modules/vulnerabilities/burp_manual_scan.py::BurpManualScanTechnique.execute
notes: community_no_rest_api, launch_or_import_only, resolve_real_version_in_versionlock=true

#### 9. vuln.nmap_vuln_nse

tool: Nmap + Npcap
version: Nmap 7.99 + Npcap 1.88
runtime: windows_binary
worker: WindowsWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, ports, nse_profile, output_format, max_duration_seconds
inputs: targets:list_string, ports:string, nse_profile:vuln|safe_vuln|custom, output_format:xml|json|text, max_duration_seconds:int
ai: ports, nse_profile, max_duration_seconds
evidence: nse_vuln_findings, service_fingerprints, raw_output_path, normalized_json
graph: ServiceNode, CVENode, WeaknessNode, FindingNode
hook: app/modules/vulnerabilities/nmap_vuln_nse.py::NmapVulnNseTechnique.execute
notes: no_docker

#### 10. vuln.testssl_tls_scan

tool: testssl.sh
version: 3.2 latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: targets, tls_profile, include_protocols, include_ciphers, output_format, max_duration_seconds
inputs: targets:list_string, tls_profile:standard|deep|compliance|custom, include_protocols:bool, include_ciphers:bool, output_format:json|html|report, max_duration_seconds:int
ai: tls_profile, include_protocols, include_ciphers
evidence: tls_findings, weak_ciphers, protocol_findings, certificate_findings, raw_output_path, normalized_json
graph: CertificateNode, TLSFindingNode, WeaknessNode, FindingNode
hook: app/modules/vulnerabilities/testssl_tls_scan.py::TestsslTlsScanTechnique.execute
notes: no_docker, wsl2_runtime

## PARTE 2/2 — TÉCNICAS 11-19 + ENLACES

#### 11. vuln.ai_cve_tagger

tool: Dolphin Mistral Nemo 12B local
version: Dolphin Mistral Nemo 12B baseline
runtime: local_ai
worker: AIWorker
perm: PASSIVE
status: READY_LOCAL_AI
docker: false
fields: service_fingerprints, banners, headers, technology_fingerprints, cve_source_profile, confidence_threshold
inputs: service_fingerprints:list_dict, banners:list_string, headers:dict_optional, technology_fingerprints:list_dict, cve_source_profile:string, confidence_threshold:float
ai: all_fields
evidence: cve_candidates, confidence_scores, reasoning_summary, source_references, normalized_json
graph: CVENode, ProductNode, VersionNode, WeaknessNode
hook: app/modules/vulnerabilities/ai_cve_tagger.py::AiCveTaggerTechnique.execute
notes: no_docker, json_schema_required, no_success_without_evidence

#### 12. vuln.exploitdb_cross_reference

tool: Searchsploit / Exploit-DB
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: product, version, cve_id, service_name, search_profile, output_format
inputs: product:string_optional, version:string_optional, cve_id:string_optional, service_name:string_optional, search_profile:exact|broad|custom, output_format:json|report
ai: product, version, cve_id, search_profile
evidence: exploit_references, exploit_metadata, raw_output_path, normalized_json
graph: CVENode, ExploitReferenceNode, WeaknessNode
hook: app/modules/vulnerabilities/exploitdb_cross_reference.py::ExploitdbCrossReferenceTechnique.execute
notes: no_docker, reference_only_no_execution

#### 13. vuln.metasploit_cross_reference

tool: Metasploit Framework + pymetasploit3
version: nightly/latest baseline
runtime: wsl2_local_rpc
worker: MetasploitRPCWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: cve_id, product, version, service_name, msfrpc_profile, search_profile, output_format
inputs: cve_id:string_optional, product:string_optional, version:string_optional, service_name:string_optional, msfrpc_profile:string, search_profile:exact|broad|custom, output_format:json|report
ai: cve_id, product, version, service_name, search_profile
evidence: metasploit_module_references, module_metadata, normalized_json
graph: CVENode, ExploitReferenceNode, TechniqueCandidateNode
hook: app/modules/vulnerabilities/metasploit_cross_reference.py::MetasploitCrossReferenceTechnique.execute
notes: no_docker, reference_only_in_module_2, execution_handoff_to_module_3

#### 14. vuln.packetstorm_cross_reference

tool: PacketStorm external index connector
version: latest
runtime: python_lib
worker: PythonToolWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: query, query_type, result_limit, source_profile, output_format
inputs: query:string, query_type:cve|product|version|keyword, result_limit:int, source_profile:string, output_format:json|report
ai: query_type, result_limit, source_profile
evidence: advisory_references, exploit_references, source_urls, normalized_json
graph: AdvisoryNode, ExploitReferenceNode, CVENode
hook: app/modules/vulnerabilities/packetstorm_cross_reference.py::PacketstormCrossReferenceTechnique.execute
notes: no_docker, reference_only

#### 15. vuln.dynamic_cvss_contextual

tool: internal_python_engine
version: internal
runtime: python_lib
worker: PythonToolWorker
perm: PASSIVE
status: READY_LOCAL_AI
docker: false
fields: finding_id, base_cvss, exposure_context, asset_criticality, exploit_available, evidence_quality
inputs: finding_id:string, base_cvss:float_optional, exposure_context:dict, asset_criticality:low|medium|high|critical, exploit_available:bool, evidence_quality:none|low|medium|high|critical
ai: exposure_context, asset_criticality, exploit_available
evidence: contextual_cvss, score_reasoning, normalized_json
graph: FindingNode, RiskScoreNode
hook: app/modules/vulnerabilities/dynamic_cvss_contextual.py::DynamicCvssContextualTechnique.execute
notes: no_docker, scoring_engine_related=true

#### 16. vuln.false_positive_soft_validation

tool: internal_python_engine + safe validators
version: internal
runtime: python_lib
worker: PythonToolWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: finding_id, target, validation_profile, safe_check_only, evidence_profile, timeout_seconds
inputs: finding_id:string, target:string, validation_profile:passive|soft|custom, safe_check_only:bool, evidence_profile:string, timeout_seconds:int
ai: validation_profile, safe_check_only, timeout_seconds
evidence: validation_result, false_positive_status, validation_evidence, normalized_json
graph: FindingNode, ValidationNode
hook: app/modules/vulnerabilities/false_positive_soft_validation.py::FalsePositiveSoftValidationTechnique.execute
notes: no_docker, no_exploit_execution_in_module_2

#### 17. vuln.critical_vuln_preparation

tool: internal_python_engine
version: internal
runtime: python_lib
worker: PythonToolWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: finding_id, cve_id, affected_service, exploit_references, required_inputs, handoff_module
inputs: finding_id:string, cve_id:string_optional, affected_service:dict, exploit_references:list_dict, required_inputs:dict, handoff_module:network_exploitation|web_intrusion|credentials_auth|manual
ai: required_inputs, handoff_module
evidence: preparation_summary, missing_inputs, recommended_module, normalized_json
graph: TechniqueCandidateNode, NextStepNode, CVENode
hook: app/modules/vulnerabilities/critical_vuln_preparation.py::CriticalVulnPreparationTechnique.execute
notes: no_docker, prepares_module_3_or_4, does_not_execute_exploit

#### 18. vuln.osquery_vulnerability_check

tool: Osquery
version: 5.15.0 latest-release-lock baseline
runtime: windows_binary
worker: WindowsWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: host_profile, query_pack, software_inventory_enabled, output_format, evidence_profile
inputs: host_profile:string, query_pack:string, software_inventory_enabled:bool, output_format:json|report, evidence_profile:string
ai: query_pack, software_inventory_enabled, output_format
evidence: software_inventory, vulnerable_software_candidates, raw_output_path, normalized_json
graph: HostNode, ProductNode, VersionNode, CVECandidateNode
hook: app/modules/vulnerabilities/osquery_vulnerability_check.py::OsqueryVulnerabilityCheckTechnique.execute
notes: no_docker, resolve_real_version_in_versionlock=true

#### 19. vuln.wazuh_agent_info

tool: Wazuh Agent
version: 4.14.5 latest-release-lock
baseline_usuario: 4.10.0
runtime: windows_agent
worker: WindowsWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: host_profile, wazuh_profile, include_inventory, include_vuln_data, output_format
inputs: host_profile:string, wazuh_profile:string, include_inventory:bool, include_vuln_data:bool, output_format:json|report
ai: include_inventory, include_vuln_data, output_format
evidence: agent_inventory, vulnerability_inventory, normalized_json
graph: HostNode, ProductNode, CVECandidateNode
hook: app/modules/vulnerabilities/wazuh_agent_info.py::WazuhAgentInfoTechnique.execute
notes: no_docker, optional=true, version_updated_from_user_baseline=true

## Integración final del Módulo 2 con LaIA

LaIA puede interpretar ServiceFingerprint, banners, tecnologías, CVEs candidatas, evidencias previas y contexto del objetivo.

LaIA debe priorizar hallazgos, rellenar fields, detectar missing_inputs, proponer validación no intrusiva, calcular criticidad contextual, explicar falsos positivos probables y recomendar handoff a Módulo 3, 4, 5, 15 o 16.

LaIA no puede inventar CVEs, marcar explotable sin evidence, ejecutar directamente, saltar X5, ignorar MISSING_TOOL ni marcar IMPLEMENTACION_USUARIO_REQUERIDA como funcional.

## Integración final del Módulo 2 con X5/OjoRouter

X5/OjoRouter debe validar technique_id, module_id, scope, permission_level, execution_mode, required_inputs y evidence_profile.

X5 debe seleccionar worker, crear job, guardar EvidenceStore, actualizar ScoringEngine, actualizar Attack Surface Graph, preparar handoff y pedir Hermes si falta wrapper, parser, normalizador o evidence_writer.

Estados permitidos:

- SUCCESS
- FAILED
- PARTIAL
- MANUAL_REQUIRED
- MISSING_TOOL
- MISSING_API_KEY
- MISSING_INPUT
- PERMISSION_DENIED
- OUT_OF_SCOPE
- IMPLEMENTACION_USUARIO_REQUERIDA

## Integración final del Módulo 2 con Hermes

Hermes puede crear en sandbox wrappers, parsers, normalizadores CVE, mappers CVE→técnica, schemas, panel_fields, evidence_writers, fixtures demo, documentación y propuestas de técnica nueva.

Hermes no puede tocar producción, autoaprobarse, ejecutar técnica real, inventar CVEs, marcar stub como funcional ni eliminar IMPLEMENTACION_USUARIO_REQUERIDA.

Flujo Hermes:

sandbox → tests estructurales → evidence → revisión Mistral → diff → aprobación usuario → promoción controlada → rollback disponible

## Integración final con EvidenceStore

Toda técnica del Módulo 2 debe guardar:

- run_id
- target_id
- technique_id
- module_id
- worker_id
- tool_name
- tool_version
- runtime
- affected_asset
- affected_service
- finding_id
- cve_id si existe
- cwe_id si existe
- severity
- confidence
- cvss_base
- cvss_contextual
- validation_status
- false_positive_status
- exploit_available
- evidence_quality
- raw_output_path
- normalized_json
- recommended_next_step
- started_at
- finished_at
- errors
- warnings

Reglas:

SUCCESS nunca es válido sin evidence útil.
Un CVE no se marca explotable sin evidence.
Los falsos positivos deben conservarse como candidates, no borrarse.
Módulo 2 no ejecuta explotación final.

## Integración final con Attack Surface Graph

El Módulo 2 debe actualizar el grafo con:

CVENode, CWENode, WeaknessNode, MisconfigNode, ExposedPanelNode, TLSFindingNode, ProductNode, VersionNode, ExploitReferenceNode, FalsePositiveNode, TechniqueCandidateNode, EvidenceNode, NextStepNode.

Relaciones mínimas:

SERVICE_HAS_CVE_CANDIDATE
PRODUCT_VERSION_MATCHES_CVE
FINDING_HAS_EVIDENCE
FINDING_HAS_CONFIDENCE
FINDING_MAPS_TO_TECHNIQUE
FINDING_REQUIRES_VALIDATION
FINDING_SUGGESTS_NEXT_MODULE
TECHNIQUE_FAILED_NEEDS_HERMES

## Índice completo del Módulo 2

El catálogo completo del Módulo 2 debe contener 19 técnicas:

1-3 Nuclei CVE, misconfig y panel exposure
4 OpenVAS/GVM deep scan
5-8 Nikto, Wapiti, ZAP y Burp
9-10 Nmap vuln NSE y testssl
11 AI CVE Tagger
12-14 ExploitDB, Metasploit y PacketStorm references
15-17 CVSS contextual, soft validation y critical preparation
18-19 Osquery y Wazuh

## Actualizaciones de índice

README.md:

- docs/techniques/02_VULNERABILITIES.md

AI_HANDOFF_OJO_DE_DIOS.md:

- El catálogo declarativo del Módulo 2 Vulnerabilidades está en docs/techniques/02_VULNERABILITIES.md y es fuente oficial para generar técnicas, paneles, workers y evidence del módulo.

MASTER_PLAN_OJO_DE_DIOS.md:

- Módulo 2 Vulnerabilidades: catálogo declarativo completo en docs/techniques/02_VULNERABILITIES.md. Este módulo no usa Docker; todo va por binarios Windows, Python, WSL2, API local o IA local. Contiene 19 técnicas y prepara handoff a explotación, web, credenciales, cloud y ops.

ROADMAP_RONDAS_OJO_DE_DIOS.md:

- Ronda 0-F2A — Vulnerabilidades catálogo parte 1/2.
- Ronda 0-F2B — Vulnerabilidades catálogo parte 2/2.
- Ronda 0-F2-CLOSE-1 — Vulnerabilidades adapters y conexiones.
- Ronda 0-F2-CLOSE-2 — Cierre final Vulnerabilidades.
