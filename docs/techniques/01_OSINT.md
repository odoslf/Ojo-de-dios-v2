# MÓDULO 1 — RECONOCIMIENTO E INTELIGENCIA OSINT

## PARTE 1/3 — BASE + TÉCNICAS 1-16

### Reglas del catálogo

Este documento es fuente oficial para crear después archivos, clases, paneles, schemas, workers y evidence del Módulo 1.

No contiene lógica funcional.
No contiene recetas de ejecución.
No contiene comandos operativos.
Solo define conexiones reales por técnica.

Cada técnica debe conservar:

- id exacto;
- herramienta;
- versión base;
- runtime;
- worker;
- permission_level;
- status;
- fields propios;
- ai_fillable;
- evidence esperada;
- salida al Attack Surface Graph;
- hook futuro donde el usuario conectará lógica privada.

Si falta herramienta: MISSING_TOOL.
Si falta API key: MISSING_API_KEY.
Si falta lógica privada: IMPLEMENTACION_USUARIO_REQUERIDA.
Si hay versión superior: upgrade_candidate_requires_review, sin cambiar baseline.

### Base del módulo

module_id: osint
module_name: Reconocimiento e Inteligencia OSINT
panel: OSINT
default_status: IMPLEMENTACION_USUARIO_REQUERIDA
default_demo: true
default_dry_run: true
default_user_logic: true

workers_permitidos:

- OSINTWorker
- WindowsWorker
- WSLWorker
- APIWorker
- PythonToolWorker
- BrowserAutomationWorker
- AIWorker
- X4ConnectorWorker
- X5PlannerWorker
- ScrapingWorker

runtimes_permitidos:

- windows
- wsl2
- api
- python_lib
- browser_automation
- local_ai
- x4_connector
- x5_planner
- scraping
- manual_required

evidence_comun:

- raw_output_path
- normalized_json
- source_urls
- observed_entities
- confidence
- tool_version
- runtime
- started_at
- finished_at
- errors
- warnings
- attack_surface_updates
- target_fingerprint_updates

panel_base:

- target_type
- target_value
- scope_profile
- source_profile
- api_profile
- rate_limit_profile
- proxy_profile
- output_profile
- evidence_profile
- execution_mode
- notes_for_laia

execution_mode:

- demo
- dry_run
- controlled
- expert

### Notas de versión

Nmap 7.99 + Npcap 1.88: mantener.
masscan 1.3.2: mantener.
Subfinder 2.14.0: mantener.
httpx 1.9.0: mantener.
Katana 1.6.x: mantener.
Amass latest-release-lock: mantener; resolver versión real en VersionLock.
Aquatone latest-release-lock / v1.7.0: mantener; archived_upstream=true; upgrade_candidate_requires_review=true.
SpiderFoot HX v4.0: mantener.
theHarvester 4.5.0: mantener; upgrade_candidate_requires_review=true.
Holehe 1.64: mantener.

### Técnicas 1-16

#### 1. osint.nmap_tcp_udp_massive

tool: Nmap + Npcap
version: Nmap 7.99 + Npcap 1.88
runtime: windows
worker: WindowsWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: target, ports, protocol_mode, scan_profile, timing_profile, output_format, max_duration_seconds, scope_profile
inputs: target:string, ports:string, protocol_mode:tcp|udp|both, scan_profile:quick|standard|deep|custom, timing_profile:low_noise|normal|fast|custom, output_format:json|xml|text, max_duration_seconds:int
ai: ports, protocol_mode, scan_profile, timing_profile
evidence: open_ports, service_fingerprints, raw_output_path, normalized_json, attack_surface_updates
graph: HostNode, PortNode, ServiceNode, ServiceFingerprint
hook: app/modules/osint/nmap_tcp_udp_massive.py::NmapTcpUdpMassiveTechnique.execute
notes: no_code_in_docs

#### 2. osint.masscan_fast_sweep

tool: masscan
version: 1.3.2
runtime: windows_or_wsl2
worker: WSLWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: target, ports, rate_profile, interface, output_format, max_duration_seconds, scope_profile
inputs: target:string, ports:string, rate_profile:low|normal|fast|custom, interface:string_optional, output_format:json|list|text, max_duration_seconds:int
ai: ports, rate_profile
evidence: open_ports, raw_output_path, normalized_json, attack_surface_updates
graph: HostNode, PortNode
hook: app/modules/osint/masscan_fast_sweep.py::MasscanFastSweepTechnique.execute

#### 3. osint.naabu_httpx_katana_discovery

tool: Naabu + httpx + Katana
version: Naabu 2.x + httpx 1.9.0 + Katana 1.6.x
runtime: windows
worker: WindowsWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: target, port_profile, http_probe_enabled, crawl_enabled, crawl_depth, include_headers, include_technologies, output_format
inputs: target:string, port_profile:top|web|custom, http_probe_enabled:bool, crawl_enabled:bool, crawl_depth:int, include_headers:bool, include_technologies:bool, output_format:json|report
ai: port_profile, crawl_depth, include_headers, include_technologies
evidence: web_services, http_headers, crawled_urls, discovered_endpoints, technology_hints, normalized_json, attack_surface_updates
graph: ServiceFingerprint, WebEndpointNode, TechnologyNode
hook: app/modules/osint/naabu_httpx_katana_discovery.py::NaabuHttpxKatanaDiscoveryTechnique.execute

#### 4. osint.subfinder_subdomain_enum

tool: Subfinder
version: 2.14.0
runtime: windows
worker: WindowsWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: domain, source_profile, recursive, include_resolved, output_format
inputs: domain:string, source_profile:default|configured_sources|custom, recursive:bool, include_resolved:bool, output_format:json|text|report
ai: source_profile, recursive, include_resolved
evidence: subdomains, source_urls, normalized_json, attack_surface_updates
graph: DomainNode, HostNode
hook: app/modules/osint/subfinder_subdomain_enum.py::SubfinderSubdomainEnumTechnique.execute
notes: requires_api_key_possible=true

#### 5. osint.amass_passive_active_enum

tool: Amass
version: latest-release-lock
runtime: windows
worker: WindowsWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: domain, mode, source_profile, include_asn, include_ips, max_duration_seconds, output_format
inputs: domain:string, mode:passive|active|both, source_profile:string, include_asn:bool, include_ips:bool, max_duration_seconds:int, output_format:json|graph|report
ai: mode, include_asn, include_ips
evidence: subdomains, ips, asn_records, graph_edges, normalized_json, attack_surface_updates
graph: DomainNode, HostNode, ASNNode, IPNode
hook: app/modules/osint/amass_passive_active_enum.py::AmassPassiveActiveEnumTechnique.execute
notes: resolve_version_in_versionlock=true

#### 6. osint.aquatone_screenshots

tool: Aquatone
version: latest-release-lock / v1.7.0 baseline
runtime: windows_or_wsl2
worker: WSLWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: targets_file, urls, screenshot_profile, output_directory, include_html_report
inputs: targets_file:path_optional, urls:list_string, screenshot_profile:standard|fast|full_page, output_directory:path, include_html_report:bool
ai: screenshot_profile, include_html_report
evidence: screenshots, html_report_path, screenshot_hashes, normalized_json
graph: ScreenshotEvidence, WebServiceVisualNode
hook: app/modules/osint/aquatone_screenshots.py::AquatoneScreenshotsTechnique.execute
notes: archived_upstream=true, upgrade_candidate_requires_review=true

#### 7. osint.shodan_passive_intel

tool: Shodan API
version: latest
runtime: api
worker: APIWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: query, target_type, api_profile, result_limit, include_banners
inputs: query:string, target_type:ip|domain|query, api_profile:string, result_limit:int, include_banners:bool
ai: query, result_limit, include_banners
evidence: passive_ports, banners, host_metadata, normalized_json, source_urls
graph: HostNode, PortNode, ServiceFingerprint
hook: app/modules/osint/shodan_passive_intel.py::ShodanPassiveIntelTechnique.execute
notes: requires_api_key=true

#### 8. osint.censys_passive_intel

tool: Censys API
version: latest
runtime: api
worker: APIWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: query, target_type, api_profile, result_limit, include_certificates
inputs: query:string, target_type:ip|domain|certificate|query, api_profile:string, result_limit:int, include_certificates:bool
ai: query, result_limit, include_certificates
evidence: certificates, passive_services, host_metadata, normalized_json
graph: CertificateNode, HostNode, ServiceFingerprint
hook: app/modules/osint/censys_passive_intel.py::CensysPassiveIntelTechnique.execute
notes: requires_api_key=true

#### 9. osint.alienvault_otx_passive_intel

tool: AlienVault OTX API
version: latest
runtime: api
worker: APIWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: indicator, indicator_type, api_profile, include_pulses, include_related
inputs: indicator:string, indicator_type:domain|ip|url|hash|email, api_profile:string, include_pulses:bool, include_related:bool
ai: indicator_type, include_pulses, include_related
evidence: iocs, related_indicators, pulses, normalized_json
graph: IOCNode, RelationshipEdge
hook: app/modules/osint/alienvault_otx_passive_intel.py::AlienvaultOtxPassiveIntelTechnique.execute
notes: requires_api_key=true

#### 10. osint.securitytrails_passive_intel

tool: SecurityTrails API
version: latest
runtime: api
worker: APIWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: domain, api_profile, include_dns_history, include_subdomains, include_whois
inputs: domain:string, api_profile:string, include_dns_history:bool, include_subdomains:bool, include_whois:bool
ai: include_dns_history, include_subdomains, include_whois
evidence: dns_history, subdomains, whois_records, normalized_json
graph: DomainNode, DNSRecordNode, HostNode
hook: app/modules/osint/securitytrails_passive_intel.py::SecuritytrailsPassiveIntelTechnique.execute
notes: requires_api_key=true

#### 11. osint.hibp_email_leak_lookup

tool: Have I Been Pwned API
version: latest
runtime: api
worker: APIWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: email, api_profile, include_pastes, include_breaches, redact_sensitive
inputs: email:string, api_profile:string, include_pastes:bool, include_breaches:bool, redact_sensitive:bool
ai: include_pastes, include_breaches, redact_sensitive
evidence: breach_names, paste_findings, exposure_summary, normalized_json
graph: IdentityExposureNode, CredentialRiskHint
hook: app/modules/osint/hibp_email_leak_lookup.py::HibpEmailLeakLookupTechnique.execute
notes: requires_api_key=true

#### 12. osint.dehashed_lookup

tool: Dehashed API
version: latest
runtime: api
worker: APIWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: query, query_type, api_profile, result_limit, redact_sensitive
inputs: query:string, query_type:email|domain|username|phone|hash, api_profile:string, result_limit:int, redact_sensitive:bool
ai: query_type, result_limit, redact_sensitive
evidence: exposure_records, redacted_summary, normalized_json
graph: IdentityExposureNode, CredentialRiskHint
hook: app/modules/osint/dehashed_lookup.py::DehashedLookupTechnique.execute
notes: requires_api_key=true

#### 13. osint.intelx_lookup

tool: IntelX API
version: latest
runtime: api
worker: APIWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: query, query_type, api_profile, result_limit, source_profile
inputs: query:string, query_type:email|domain|ip|phone|hash|keyword, api_profile:string, result_limit:int, source_profile:default|wide|custom
ai: query_type, result_limit, source_profile
evidence: intel_records, source_references, normalized_json
graph: OSINTRecordNode, IdentityExposureNode
hook: app/modules/osint/intelx_lookup.py::IntelxLookupTechnique.execute
notes: requires_api_key=true

#### 14. osint.spiderfoot_automation

tool: SpiderFoot / SpiderFoot HX
version: v4.0 latest-release-lock
runtime: python_lib_or_api
worker: PythonToolWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: target, target_type, scan_profile, modules_profile, api_profile, result_limit
inputs: target:string, target_type:domain|ip|email|username|company, scan_profile:quick|standard|deep|custom, modules_profile:string, api_profile:string_optional, result_limit:int
ai: target_type, scan_profile, modules_profile, result_limit
evidence: osint_graph, discovered_entities, relationship_edges, normalized_json, report_path
graph: OSINTGraph, RelationshipEdge, TargetFingerprintUpdate
hook: app/modules/osint/spiderfoot_automation.py::SpiderfootAutomationTechnique.execute

#### 15. osint.theharvester_emails

tool: theHarvester
version: 4.5.0
runtime: python_lib
worker: PythonToolWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: domain, source_profile, result_limit, include_hosts, include_emails
inputs: domain:string, source_profile:default|search_engines|apis|custom, result_limit:int, include_hosts:bool, include_emails:bool
ai: source_profile, result_limit, include_hosts, include_emails
evidence: emails, hosts, subdomains, source_references, normalized_json
graph: IdentityNode, HostNode, DomainNode
hook: app/modules/osint/theharvester_emails.py::TheharvesterEmailsTechnique.execute
notes: upgrade_candidate_requires_review=true

#### 16. osint.holehe_email_check

tool: Holehe
version: 1.64 latest-release-lock
runtime: python_lib
worker: PythonToolWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: email, site_profile, result_limit, timeout_seconds
inputs: email:string, site_profile:default|wide|custom, result_limit:int, timeout_seconds:int
ai: site_profile, result_limit, timeout_seconds
evidence: account_presence_findings, site_matches, normalized_json
graph: IdentityExposureNode
hook: app/modules/osint/holehe_email_check.py::HoleheEmailCheckTechnique.execute

## PARTE 2/3 — TÉCNICAS 17-33

#### 17. osint.sherlock_username

tool: Sherlock
version: 0.15 latest-release-lock
runtime: python_lib
worker: PythonToolWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: username, site_profile, include_nsfw, timeout_seconds, output_format
inputs: username:string, site_profile:default|wide|custom, include_nsfw:bool, timeout_seconds:int, output_format:json|text|report
ai: site_profile, timeout_seconds, output_format
evidence: social_profiles, profile_urls, normalized_json, report_path
graph: SocialProfileNode, IdentityNode
hook: app/modules/osint/sherlock_username.py::SherlockUsernameTechnique.execute
notes: upgrade_candidate_requires_review=true

#### 18. osint.maigret_profiles

tool: Maigret
version: 0.4 latest-release-lock
runtime: python_lib
worker: PythonToolWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: username, profile_depth, report_format, site_profile, timeout_seconds
inputs: username:string, profile_depth:quick|standard|deep, report_format:json|html|pdf, site_profile:default|wide|custom, timeout_seconds:int
ai: profile_depth, report_format, site_profile
evidence: social_profiles, profile_report_path, normalized_json
graph: SocialProfileNode, IdentityNode
hook: app/modules/osint/maigret_profiles.py::MaigretProfilesTechnique.execute

#### 19. osint.ghunt_google_info

tool: GHunt
version: 2.0 latest-release-lock
runtime: python_lib
worker: PythonToolWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: google_identifier, identifier_type, session_profile, include_public_profile, output_format
inputs: google_identifier:string, identifier_type:email|gaia_id|username, session_profile:string, include_public_profile:bool, output_format:json|report
ai: identifier_type, include_public_profile, output_format
evidence: google_profile_findings, public_identifiers, normalized_json, report_path
graph: IdentityNode, PublicProfileNode
hook: app/modules/osint/ghunt_google_info.py::GhuntGoogleInfoTechnique.execute
notes: requires_session_profile=true, upgrade_candidate_requires_review=true

#### 20. osint.foca_metadata_extract

tool: FOCA
version: latest-release-lock
runtime: windows
worker: WindowsWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: input_files, input_urls, metadata_profile, output_format, redact_sensitive
inputs: input_files:list_path, input_urls:list_string, metadata_profile:standard|deep, output_format:json|report, redact_sensitive:bool
ai: metadata_profile, output_format, redact_sensitive
evidence: metadata_findings, authors, software_versions, paths, normalized_json, report_path
graph: MetadataNode, IdentityNode, TechnologyNode
hook: app/modules/osint/foca_metadata_extract.py::FocaMetadataExtractTechnique.execute

#### 21. osint.exiftool_metadata_extract

tool: exiftool
version: 12.80 latest-release-lock
runtime: windows
worker: WindowsWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: input_files, recursive, metadata_profile, output_format, redact_sensitive
inputs: input_files:list_path, recursive:bool, metadata_profile:standard|all, output_format:json|csv|report, redact_sensitive:bool
ai: metadata_profile, output_format, redact_sensitive
evidence: metadata_findings, gps_metadata, device_metadata, software_metadata, normalized_json
graph: MetadataNode, LocationHintNode, TechnologyNode
hook: app/modules/osint/exiftool_metadata_extract.py::ExiftoolMetadataExtractTechnique.execute

#### 22. osint.google_dorks_auto

tool: custom_python_search_connector
version: internal
runtime: python_lib
worker: PythonToolWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: target, dork_profile, search_provider_profile, result_limit, proxy_profile, redact_sensitive
inputs: target:string, dork_profile:documents|backups|panels|configs|custom, search_provider_profile:string, result_limit:int, proxy_profile:string_optional, redact_sensitive:bool
ai: dork_profile, result_limit, redact_sensitive
evidence: search_results, exposed_documents, exposed_paths, source_urls, normalized_json
graph: OSINTRecordNode, ExposedResourceNode
hook: app/modules/osint/google_dorks_auto.py::GoogleDorksAutoTechnique.execute
notes: custom_connector_no_code_in_docs

#### 23. osint.ip_geolocation_asn_bgp

tool: bgp.he.net + custom scripts
version: internal
runtime: api
worker: APIWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: ip_or_asn, lookup_type, include_prefixes, include_peers, output_format
inputs: ip_or_asn:string, lookup_type:ip|asn|prefix, include_prefixes:bool, include_peers:bool, output_format:json|report
ai: lookup_type, include_prefixes, include_peers
evidence: asn_records, bgp_prefixes, geolocation, normalized_json
graph: ASNNode, IPRangeNode, LocationHintNode
hook: app/modules/osint/ip_geolocation_asn_bgp.py::IpGeolocationAsnBgpTechnique.execute

#### 24. osint.whois_history

tool: ViewDNS.info / WhoisXMLAPI
version: latest
runtime: api
worker: APIWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: domain, provider_profile, include_history, output_format
inputs: domain:string, provider_profile:string, include_history:bool, output_format:json|report
ai: provider_profile, include_history
evidence: whois_records, historical_ownership, registrar_history, normalized_json
graph: WhoisNode, DomainNode, OrganizationNode
hook: app/modules/osint/whois_history.py::WhoisHistoryTechnique.execute
notes: requires_api_key_optional=true

#### 25. osint.reverse_dns

tool: ViewDNS.info / custom scripts
version: latest
runtime: api
worker: APIWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: ip_or_range, provider_profile, result_limit, output_format
inputs: ip_or_range:string, provider_profile:string, result_limit:int, output_format:json|report
ai: provider_profile, result_limit
evidence: reverse_dns_records, domains, normalized_json
graph: DNSRecordNode, DomainNode, HostNode
hook: app/modules/osint/reverse_dns.py::ReverseDnsTechnique.execute
notes: requires_api_key_optional=true

#### 26. osint.linkedin_social_osint

tool: custom_playwright_connector
version: internal
runtime: browser_automation
worker: BrowserAutomationWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: query, query_type, session_profile, source_profile, result_limit, redact_sensitive
inputs: query:string, query_type:person|company|domain|email, session_profile:string_optional, source_profile:string, result_limit:int, redact_sensitive:bool
ai: query_type, result_limit, redact_sensitive
evidence: social_profiles, company_profiles, relationship_hints, normalized_json
graph: SocialProfileNode, OrganizationNode, IdentityNode
hook: app/modules/osint/linkedin_social_osint.py::LinkedinSocialOsintTechnique.execute
notes: browser_connector_no_code_in_docs

#### 27. osint.twitter_social_osint

tool: custom_playwright_connector
version: internal
runtime: browser_automation
worker: BrowserAutomationWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: query, query_type, session_profile, source_profile, result_limit, redact_sensitive
inputs: query:string, query_type:person|company|domain|email|keyword, session_profile:string_optional, source_profile:string, result_limit:int, redact_sensitive:bool
ai: query_type, result_limit, redact_sensitive
evidence: social_profiles, mentions, relationship_hints, normalized_json
graph: SocialProfileNode, MentionNode, IdentityNode
hook: app/modules/osint/twitter_social_osint.py::TwitterSocialOsintTechnique.execute
notes: browser_connector_no_code_in_docs

#### 28. osint.github_social_osint

tool: GitHub API / custom_playwright_connector
version: latest
runtime: api_or_browser_automation
worker: APIWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: query, query_type, api_profile, result_limit, include_repositories, include_users
inputs: query:string, query_type:username|organization|domain|email|keyword, api_profile:string_optional, result_limit:int, include_repositories:bool, include_users:bool
ai: query_type, result_limit, include_repositories, include_users
evidence: github_profiles, repositories, exposed_references, normalized_json
graph: RepositoryNode, IdentityNode, OrganizationNode
hook: app/modules/osint/github_social_osint.py::GithubSocialOsintTechnique.execute
notes: requires_api_key_optional=true

#### 29. osint.trufflehog_repo_leaks

tool: truffleHog
version: 3.69 latest-release-lock
runtime: windows
worker: WindowsWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: repository_url, local_path, scan_profile, redact_secrets, output_format
inputs: repository_url:string_optional, local_path:path_optional, scan_profile:standard|deep, redact_secrets:bool, output_format:json|report
ai: scan_profile, redact_secrets, output_format
evidence: secret_findings, redacted_findings, raw_output_path, normalized_json
graph: SecretExposureNode, RepositoryNode
hook: app/modules/osint/trufflehog_repo_leaks.py::TrufflehogRepoLeaksTechnique.execute
notes: upgrade_candidate_requires_review=true

#### 30. osint.gitleaks_repo_leaks

tool: Gitleaks
version: 8.18 latest-release-lock
runtime: windows
worker: WindowsWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: repository_url, local_path, config_profile, redact_secrets, output_format
inputs: repository_url:string_optional, local_path:path_optional, config_profile:string_optional, redact_secrets:bool, output_format:json|sarif|report
ai: redact_secrets, output_format
evidence: secret_findings, sarif_report, normalized_json, redacted_findings
graph: SecretExposureNode, RepositoryNode
hook: app/modules/osint/gitleaks_repo_leaks.py::GitleaksRepoLeaksTechnique.execute
notes: upgrade_candidate_requires_review=true

#### 31. osint.whatweb_fingerprint

tool: WhatWeb
version: 0.5.5 latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: urls, target, aggression_profile, output_format, include_plugins
inputs: urls:list_string, target:string_optional, aggression_profile:passive|standard|deep, output_format:json|text|report, include_plugins:bool
ai: aggression_profile, output_format, include_plugins
evidence: technology_fingerprints, plugin_matches, normalized_json
graph: TechnologyNode, ProductNode, ServiceFingerprint
hook: app/modules/osint/whatweb_fingerprint.py::WhatwebFingerprintTechnique.execute

#### 32. osint.wappalyzer_fingerprint

tool: Wappalyzer CLI/API
version: latest
runtime: api_or_node
worker: APIWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: urls, api_profile, include_confidence, output_format
inputs: urls:list_string, api_profile:string_optional, include_confidence:bool, output_format:json|report
ai: include_confidence, output_format
evidence: technology_fingerprints, confidence_scores, normalized_json
graph: TechnologyNode, ProductNode, ServiceFingerprint
hook: app/modules/osint/wappalyzer_fingerprint.py::WappalyzerFingerprintTechnique.execute
notes: requires_api_key_optional=true

#### 33. osint.ml_local_fingerprinting

tool: local_embeddings_model
version: all-MiniLM-L6-v2 baseline
runtime: local_ai
worker: AIWorker
perm: PASSIVE
status: READY_LOCAL_AI
fields: banner_texts, headers, model_profile, confidence_threshold, output_format
inputs: banner_texts:list_string, headers:dict_optional, model_profile:string, confidence_threshold:float, output_format:json|report
ai: model_profile, confidence_threshold
evidence: predicted_products, predicted_versions, confidence_scores, normalized_json
graph: ProductNode, VersionNode, ServiceFingerprint
hook: app/modules/osint/ml_local_fingerprinting.py::MlLocalFingerprintingTechnique.execute
notes: model_required=true, implementation_private_hook=true

## PARTE 3/3 — TÉCNICAS 34-47 + ENLACES

#### 34. osint.internal_arp_netbios

tool: nmap NSE + custom scripts
version: Nmap 7.99
runtime: windows_or_wsl2
worker: WindowsWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: network_range, interface, discovery_profile, include_netbios, output_format
inputs: network_range:string, interface:string_optional, discovery_profile:low_noise|standard|deep, include_netbios:bool, output_format:json|report
ai: discovery_profile, include_netbios
evidence: internal_hosts, netbios_names, mac_addresses, normalized_json, attack_surface_updates
graph: InternalHostNode, HostNode, ServiceFingerprint
hook: app/modules/osint/internal_arp_netbios.py::InternalArpNetbiosTechnique.execute
notes: requires_internal_scope=true

#### 35. osint.internal_smb_enum

tool: CrackMapExec
version: 6.x latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: targets, credential_profile, enum_profile, output_format
inputs: targets:list_string, credential_profile:string_optional, enum_profile:shares|hosts|users|standard, output_format:json|report
ai: enum_profile, output_format
evidence: smb_hosts, smb_shares, smb_metadata, normalized_json
graph: ServiceFingerprint, SMBNode, InternalHostNode
hook: app/modules/osint/internal_smb_enum.py::InternalSmbEnumTechnique.execute
notes: requires_internal_scope=true

#### 36. osint.internal_ldap_enum

tool: ldapsearch
version: system
runtime: wsl2
worker: WSLWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: ldap_server, base_dn, credential_profile, query_profile, output_format
inputs: ldap_server:string, base_dn:string_optional, credential_profile:string_optional, query_profile:base|users|groups|computers|custom, output_format:json|ldif|report
ai: query_profile, output_format
evidence: ldap_entries, users, groups, computers, normalized_json
graph: DirectoryNode, IdentityNode, InternalHostNode
hook: app/modules/osint/internal_ldap_enum.py::InternalLdapEnumTechnique.execute
notes: requires_internal_scope=true

#### 37. osint.internal_mssql_enum

tool: CrackMapExec
version: 6.x latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: targets, credential_profile, enum_profile, output_format
inputs: targets:list_string, credential_profile:string_optional, enum_profile:instances|databases|logins|standard, output_format:json|report
ai: enum_profile, output_format
evidence: mssql_instances, mssql_metadata, normalized_json
graph: ServiceFingerprint, DatabaseNode, InternalHostNode
hook: app/modules/osint/internal_mssql_enum.py::InternalMssqlEnumTechnique.execute
notes: requires_internal_scope=true

#### 38. osint.internal_rdp_enum

tool: nmap NSE
version: Nmap 7.99
runtime: windows_or_wsl2
worker: WindowsWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: targets, rdp_profile, output_format
inputs: targets:list_string, rdp_profile:standard|security_info, output_format:json|report
ai: rdp_profile, output_format
evidence: rdp_services, security_info, normalized_json
graph: ServiceFingerprint, RDPNode, InternalHostNode
hook: app/modules/osint/internal_rdp_enum.py::InternalRdpEnumTechnique.execute
notes: requires_internal_scope=true

#### 39. osint.internal_vnc_enum

tool: nmap NSE
version: Nmap 7.99
runtime: windows_or_wsl2
worker: WindowsWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: targets, vnc_profile, output_format
inputs: targets:list_string, vnc_profile:standard|security_info, output_format:json|report
ai: vnc_profile, output_format
evidence: vnc_services, security_info, normalized_json
graph: ServiceFingerprint, VNCNode, InternalHostNode
hook: app/modules/osint/internal_vnc_enum.py::InternalVncEnumTechnique.execute
notes: requires_internal_scope=true

#### 40. osint.bloodhound_py_ad_map

tool: BloodHound.py
version: latest-release-lock
runtime: python_lib_or_wsl2
worker: WSLWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: domain, dc_host, credential_profile, collection_profile, output_directory
inputs: domain:string, dc_host:string_optional, credential_profile:string_optional, collection_profile:default|session|acl|objectprops|custom, output_directory:path
ai: collection_profile
evidence: ad_graph_files, users, groups, computers, relationships, normalized_json
graph: DirectoryGraphNode, IdentityNode, RelationshipEdge
hook: app/modules/osint/bloodhound_py_ad_map.py::BloodhoundPyAdMapTechnique.execute
notes: requires_internal_scope=true

#### 41. osint.ldapsearch_ad_map

tool: ldapsearch
version: system
runtime: wsl2
worker: WSLWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: ldap_server, base_dn, credential_profile, collection_profile, output_format
inputs: ldap_server:string, base_dn:string_optional, credential_profile:string_optional, collection_profile:users|groups|computers|spns|custom, output_format:json|ldif|report
ai: collection_profile, output_format
evidence: ad_entries, users, groups, computers, normalized_json
graph: DirectoryNode, IdentityNode, InternalHostNode
hook: app/modules/osint/ldapsearch_ad_map.py::LdapsearchAdMapTechnique.execute
notes: requires_internal_scope=true

### Referencias cruzadas con Módulo 9 — Scraping Inteligente

Estas 6 entradas se reciben dentro del paquete OSINT porque alimentan inteligencia y búsqueda, pero su implementación principal futura debe vivir en:

docs/techniques/09_SCRAPING_INTELLIGENCE.md
app/modules/scraping_intelligence/

En OSINT quedan como cross_module_reference.

#### 42. scraping.x4_engine_integration

tool: X4 internal engine
version: internal
runtime: x4_connector
worker: X4ConnectorWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: natural_language_query, base_url, source_profile, selector_profile, export_format, preview_enabled
inputs: natural_language_query:string, base_url:string_optional, source_profile:string, selector_profile:string_optional, export_format:json|csv, preview_enabled:bool
ai: source_profile, selector_profile, export_format
evidence: extracted_rows, source_urls, normalized_json, export_path
graph: OSINTRecordNode, ScrapingResultNode
hook: app/modules/scraping_intelligence/x4_engine_integration.py::X4EngineIntegrationTechnique.execute
notes: cross_module_reference=module_09_scraping_intelligence

#### 43. scraping.x5_intelligent_planner

tool: X5 + Dolphin Mistral Nemo 12B
version: internal
runtime: x5_planner
worker: X5PlannerWorker
perm: PASSIVE
status: READY_LOCAL_AI
fields: user_goal, source_candidates, depth_limit, data_schema, output_format
inputs: user_goal:string, source_candidates:list_string, depth_limit:int, data_schema:dict, output_format:json|csv|report
ai: source_candidates, depth_limit, data_schema
evidence: scraping_plan, source_priorities, planned_steps, normalized_json
graph: PlanningNode, ScrapingPlanNode
hook: app/modules/scraping_intelligence/x5_intelligent_planner.py::X5IntelligentPlannerTechnique.execute
notes: cross_module_reference=module_09_scraping_intelligence

#### 44. scraping.captcha_text_solver_ai

tool: Dolphin Mistral Nemo 12B
version: local_model
runtime: local_ai
worker: AIWorker
perm: PASSIVE
status: READY_LOCAL_AI
fields: challenge_text, source_context, confidence_threshold, manual_review_enabled
inputs: challenge_text:string, source_context:string, confidence_threshold:float, manual_review_enabled:bool
ai: challenge_text, source_context
evidence: challenge_summary, solver_confidence, answer_candidate, manual_required_status
graph: ChallengeNode
hook: app/modules/scraping_intelligence/captcha_text_solver_ai.py::CaptchaTextSolverAiTechnique.execute
notes: cross_module_reference=module_09_scraping_intelligence, no_fake_success=true

#### 45. scraping.captcha_visual_bypass

tool: Playwright + Tesseract OCR
version: latest-release-lock
runtime: browser_automation
worker: BrowserAutomationWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: page_url, screenshot_path, ocr_profile, browser_profile, manual_review_enabled
inputs: page_url:string, screenshot_path:path_optional, ocr_profile:string, browser_profile:string, manual_review_enabled:bool
ai: ocr_profile, manual_review_enabled
evidence: screenshot_hash, ocr_output, confidence, manual_required_status
graph: ChallengeNode, BrowserEvidenceNode
hook: app/modules/scraping_intelligence/captcha_visual_bypass.py::CaptchaVisualBypassTechnique.execute
notes: cross_module_reference=module_09_scraping_intelligence

#### 46. scraping.proxy_rotation_sim

tool: proxies SOCKS5 + double SIM profile
version: internal
runtime: network_profile
worker: ScrapingWorker
perm: ACTIVE_LOW
status: IMPLEMENTACION_USUARIO_REQUERIDA
fields: proxy_profile, rotation_strategy, cooldown_seconds, max_failures, connection_profile
inputs: proxy_profile:string, rotation_strategy:manual|timed|failure_based|custom, cooldown_seconds:int, max_failures:int, connection_profile:string
ai: rotation_strategy, cooldown_seconds, max_failures
evidence: proxy_usage_log, rotation_events, connection_status, normalized_json
graph: NetworkProfileNode
hook: app/modules/scraping_intelligence/proxy_rotation_sim.py::ProxyRotationSimTechnique.execute
notes: cross_module_reference=module_09_scraping_intelligence

#### 47. scraping.recursive_ai_discovery

tool: Dolphin Mistral Nemo 12B + X4
version: internal
runtime: local_ai_x4
worker: ScrapingWorker
perm: PASSIVE
status: READY_LOCAL_AI
fields: seed_results, discovery_goal, max_iterations, source_rules, stop_conditions
inputs: seed_results:dict, discovery_goal:string, max_iterations:int, source_rules:dict, stop_conditions:list_string
ai: discovery_goal, source_rules, stop_conditions
evidence: discovered_sources, iteration_log, structured_results, normalized_json
graph: ScrapingResultNode, OSINTRecordNode
hook: app/modules/scraping_intelligence/recursive_ai_discovery.py::RecursiveAiDiscoveryTechnique.execute
notes: cross_module_reference=module_09_scraping_intelligence

## Integración final del Módulo 1 con LaIA

LaIA debe actuar como analista de reconocimiento y enriquecimiento.

LaIA puede:

- interpretar objetivo inicial: dominio, IP, rango, email, persona, empresa, repositorio, documento o activo web;
- elegir técnicas OSINT candidatas;
- rellenar fields;
- detectar missing_inputs;
- proponer source_profile, api_profile, rate_limit_profile y proxy_profile;
- priorizar fuentes según objetivo;
- resumir hallazgos;
- detectar entidades observadas;
- proponer actualización del TargetFingerprint;
- proponer actualización del Attack Surface Graph;
- recomendar siguiente módulo.

LaIA no puede:

- inventar resultados;
- marcar una entidad como verificada sin evidence;
- inventar claves API;
- saltar scope_profile;
- ejecutar directamente;
- saltar X5/OjoRouter;
- marcar IMPLEMENTACION_USUARIO_REQUERIDA como funcional;
- crear scraping funcional desde documentación.

## Integración final del Módulo 1 con X5/OjoRouter

X5/OjoRouter debe:

- validar technique_id;
- validar module_id;
- validar scope_profile;
- validar permission_level;
- validar execution_mode;
- validar required_inputs;
- seleccionar worker;
- crear job;
- guardar EvidenceStore;
- actualizar TargetFingerprint;
- actualizar Attack Surface Graph;
- actualizar ScoringEngine;
- devolver result_status;
- proponer fallback;
- pedir Hermes si falta wrapper, parser, normalizador, panel field o evidence_writer.

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

## Integración final del Módulo 1 con Hermes

Hermes puede crear en sandbox:

- wrapper de herramienta OSINT;
- parser de salida;
- normalizador de entidades;
- normalizador de subdominios;
- normalizador de leaks;
- schema;
- panel_fields;
- evidence_writer;
- fixture demo;
- documentación;
- propuesta de técnica nueva.

Hermes no puede:

- tocar producción directamente;
- autoaprobarse;
- ejecutar técnica real;
- marcar stub como funcional;
- eliminar IMPLEMENTACION_USUARIO_REQUERIDA;
- inventar resultados OSINT;
- mostrar secretos sin redacción.

Flujo Hermes obligatorio:

sandbox → tests estructurales → evidence → revisión Mistral → diff → aprobación usuario → promoción controlada → rollback disponible

## Integración final con EvidenceStore

Toda técnica del Módulo 1 debe guardar:

- run_id
- target_id
- technique_id
- module_id
- worker_id
- tool_name
- tool_version
- runtime
- started_at
- finished_at
- result_status
- evidence_quality
- raw_output_path
- normalized_json
- source_urls
- observed_entities
- confidence
- errors
- warnings
- attack_surface_updates
- target_fingerprint_updates
- next_recommended_techniques

Reglas:

SUCCESS nunca es válido sin evidence útil.
Las API keys nunca se guardan en evidence.
Los secretos detectados deben redactarse por defecto.
Los resultados no verificados deben marcarse como candidates.
Las técnicas scraping.x4/x5 siguen siendo IMPLEMENTACION_USUARIO_REQUERIDA si falta lógica privada.

## Integración final con Attack Surface Graph

El Módulo 1 debe actualizar el grafo con:

DomainNode, HostNode, IPNode, ASNNode, PortNode, ServiceNode, ServiceFingerprint, WebEndpointNode, TechnologyNode, EmailNode, PersonNode, OrganizationNode, SocialProfileNode, RepositoryNode, LeakNode, SecretExposureNode, DocumentNode, MetadataNode, DNSRecordNode, SubdomainNode, EvidenceNode, NextStepNode.

Relaciones mínimas:

TARGET_HAS_DOMAIN
DOMAIN_RESOLVES_TO_IP
DOMAIN_HAS_SUBDOMAIN
HOST_EXPOSES_PORT
PORT_RUNS_SERVICE
SERVICE_HAS_FINGERPRINT
WEB_ENDPOINT_USES_TECHNOLOGY
EMAIL_APPEARS_IN_LEAK
REPOSITORY_CONTAINS_SECRET_CANDIDATE
DOCUMENT_CONTAINS_METADATA
EVIDENCE_SUPPORTS_ENTITY
ENTITY_SUGGESTS_NEXT_STEP
TECHNIQUE_FAILED_NEEDS_HERMES

## Índice completo del Módulo 1

El catálogo completo del Módulo 1 debe contener 47 técnicas:

1-3 Descubrimiento de superficie externa
4-6 Subdominios y activos web
7-10 Inteligencia pasiva por APIs
11-25 OSINT sobre personas, organizaciones, metadatos, geolocalización, WHOIS y DNS
26-30 Redes sociales y fugas en repositorios
31-33 Fingerprinting de tecnologías
34-41 Inteligencia de red interna
42-47 Scraping inteligente X4 + X5 + IA

## Actualizaciones de índice

README.md:

Debe contener una sola referencia a:

- docs/techniques/01_OSINT.md

AI_HANDOFF_OJO_DE_DIOS.md:

Debe contener una sola referencia a:

- El catálogo declarativo del Módulo 1 OSINT está en docs/techniques/01_OSINT.md y es fuente oficial para generar técnicas, paneles, workers y evidence del módulo.

MASTER_PLAN_OJO_DE_DIOS.md:

Debe contener una sola referencia a:

- Módulo 1 OSINT: catálogo declarativo completo en docs/techniques/01_OSINT.md. Contiene 47 técnicas, integración X4/X5 para scraping inteligente, workers Windows/WSL2/API/Python/Browser/IA y salida hacia EvidenceStore, TargetFingerprint y Attack Surface Graph.

ROADMAP_RONDAS_OJO_DE_DIOS.md:

Debe contener una sola referencia a:

- Ronda 0-F1 — OSINT catálogo declarativo completo.
- Ronda 0-F1-CLOSE — Cierre final OSINT con LaIA, X5, Hermes, EvidenceStore y Attack Surface Graph.
