# MÓDULO 6 — RED Y MAN-IN-THE-MIDDLE

## PARTE 1/4 — BASE + RED LOCAL

### Regla absoluta

NO_DOCKER=true

Este módulo solo usa:

- Python 3.12 en Windows;
- binarios Windows cuando existan;
- librerías Python en Windows;
- WSL2 Kali con paquetes instalados manualmente;
- APIs locales;
- captura PCAP;
- IA local;
- lógica privada del usuario en hooks marcados.

Runtimes prohibidos:

- docker
- docker_compose
- container_runtime

### Objetivo del módulo

El Módulo 6 cubre operaciones de red, interceptación, captura, túneles, infraestructura y pruebas de resiliencia de red dentro de laboratorio o scope autorizado.

Este catálogo NO contiene lógica funcional ni comandos.

Cada técnica define:

- id exacto;
- herramienta;
- versión;
- runtime;
- worker;
- permisos;
- fields de panel;
- input_schema;
- campos rellenables por LaIA;
- evidence esperada;
- nodos del Attack Surface Graph;
- hook exacto futuro donde el usuario conectará su lógica privada.

### Base del módulo

module_id: mitm_network
module_name: Red y Man-in-the-Middle
panel: Red / MITM
default_status: IMPLEMENTACION_USUARIO_REQUERIDA
default_demo: true
default_dry_run: true
default_user_logic: true
docker_allowed: false

workers:

- MITMWorker
- NetworkWorker
- WindowsWorker
- WSLWorker
- PythonToolWorker
- PacketWorker
- ProxyToolWorker
- CaptureWorker
- TunnelWorker
- AIWorker
- EvidenceWorker

runtimes:

- windows_python
- windows_binary
- wsl2
- python_lib
- local_api
- packet_capture
- proxy_local
- tunnel_runtime
- local_ai
- manual_required

### Entradas desde otros módulos

inputs_base:

- target_id
- network_profile
- interface_profile
- gateway_profile
- victim_profile
- dns_profile
- service_fingerprints
- attack_surface_graph_id
- scope_profile
- permission_profile
- execution_mode
- confirmation_profile
- evidence_profile
- kill_switch_profile

### Salidas del módulo

outputs_base:

- network_position_summary
- traffic_capture_reference
- pcap_reference
- credential_artifact_reference
- hash_artifact_reference
- token_artifact_reference
- session_artifact_reference
- tunnel_artifact_reference
- device_state_change_summary
- evidence_ids
- next_module_recommendations

### Evidence común

evidence_comun:

- run_id
- target_id
- technique_id
- module_id
- worker_id
- tool_name
- tool_version
- runtime
- interface_used
- network_segment
- started_at
- finished_at
- result_status
- evidence_quality
- raw_output_path
- normalized_json
- pcap_reference
- packet_summary
- affected_hosts
- affected_services
- captured_artifacts
- restoration_status
- rollback_notes
- kill_switch_status
- errors
- warnings
- next_recommended_techniques

Regla:

SUCCESS nunca es válido sin evidence útil.

### Panel base

panel_base:

- target_selector
- network_selector
- interface_selector
- gateway_selector
- victim_selector
- dns_profile
- traffic_profile
- capture_profile
- proxy_profile
- tunnel_profile
- confirmation_required
- timeout_seconds
- evidence_profile
- kill_switch_profile
- notes_for_laia

execution_mode:

- demo
- dry_run
- controlled
- expert

### Permisos usados

permission_levels:

- PASSIVE
- ACTIVE_LOW
- ACTIVE_SENSITIVE
- CREDENTIALS
- NETWORK_CONTROL
- TUNNEL
- DOS_CONTROLLED
- LAB_ONLY

### Anclajes reales por herramienta

#### Bettercap connector

tool_adapter: BettercapAdapter
runtime: wsl2
worker: WSLWorker
connection_fields:

- interface_profile
- gateway_profile
- victim_profile
- bettercap_session_profile
- caplet_profile
- proxy_profile
- dns_profile
- event_stream_profile
- evidence_profile
- restoration_profile

outputs:

- bettercap_event_log
- host_discovery_summary
- spoof_state_summary
- proxy_event_summary
- dns_event_summary
- raw_output_path
- normalized_json

hook_base: app/modules/mitm_network/adapters/bettercap_adapter.py::BettercapAdapter

#### Scapy connector

tool_adapter: ScapyPacketAdapter
runtime: windows_python
worker: PacketWorker
connection_fields:

- interface_profile
- packet_profile
- victim_profile
- gateway_profile
- dns_profile
- route_profile
- timing_profile
- evidence_profile
- restoration_profile

outputs:

- packet_generation_summary
- packet_capture_summary
- pcap_reference
- raw_output_path
- normalized_json

hook_base: app/modules/mitm_network/adapters/scapy_packet_adapter.py::ScapyPacketAdapter

#### mitm6 connector

tool_adapter: Mitm6Adapter
runtime: wsl2
worker: WSLWorker
connection_fields:

- interface_profile
- domain_profile
- victim_profile
- ipv6_profile
- dns_profile
- relay_context_profile
- event_stream_profile
- evidence_profile
- restoration_profile

outputs:

- ipv6_advertisement_summary
- dns_takeover_summary
- affected_hosts
- raw_output_path
- normalized_json

hook_base: app/modules/mitm_network/adapters/mitm6_adapter.py::Mitm6Adapter

### Versiones oficiales de esta parte

Bettercap: 2.41.4
Bettercap baseline_usuario: 2.34

mitm6: 0.3.0
mitm6 baseline_usuario: 0.3

Scapy: 2.7.0
Scapy baseline_usuario: 2.5.0

Python: 3.12
Mistral: Dolphin Mistral Nemo 12B

### Submódulo 6.1 — Envenenamiento de red local

submodule_id: mitm_network.local_poisoning
submodule_name: ARP, DHCP, DNS, DHCPv6, ICMP redirect
primary_worker: MITMWorker
secondary_workers:

- WSLWorker
- PacketWorker
- PythonToolWorker
- AIWorker

Regla del submódulo:

Este submódulo solo documenta conexiones, fields, evidence y hooks.

No se documentan paquetes concretos.
No se documentan comandos.
No se documentan scripts.
No se documentan recetas de redirección.
Toda lógica queda como IMPLEMENTACION_USUARIO_REQUERIDA.

### Técnicas 1-6

#### 1. mitm.local.arp_spoof

tool: Bettercap
version: 2.41.4
baseline_usuario: 2.34
runtime: wsl2
worker: WSLWorker
perm: NETWORK_CONTROL
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: interface_profile, gateway_profile, victim_profile, arp_profile, traffic_direction_profile, restoration_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: interface_profile:string, gateway_profile:string, victim_profile:string, arp_profile:string, traffic_direction_profile:string, restoration_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: interface_profile, gateway_profile, victim_profile, traffic_direction_profile, timeout_seconds
evidence: spoof_state_summary, affected_hosts, packet_summary, pcap_reference, restoration_status, raw_output_path, normalized_json
graph: NetworkSegmentNode, HostNode, GatewayNode, MITMPositionNode, EvidenceNode
hook: app/modules/mitm_network/local_arp_spoof.py::LocalArpSpoofTechnique.execute
adapter: BettercapAdapter
notes: no_arp_steps_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, restoration_required=true

#### 2. mitm.local.arp_spoof_evasion

tool: Scapy
version: 2.7.0
baseline_usuario: 2.5.0
runtime: windows_python
worker: PacketWorker
perm: NETWORK_CONTROL
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: interface_profile, gateway_profile, victim_profile, packet_profile, timing_profile, evasion_profile, restoration_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: interface_profile:string, gateway_profile:string, victim_profile:string, packet_profile:string, timing_profile:string, evasion_profile:string, restoration_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: packet_profile, timing_profile, evasion_profile, timeout_seconds
evidence: packet_generation_summary, spoof_state_summary, affected_hosts, pcap_reference, restoration_status, raw_output_path, normalized_json
graph: NetworkSegmentNode, HostNode, PacketProfileNode, MITMPositionNode, EvidenceNode
hook: app/modules/mitm_network/local_arp_spoof_evasion.py::LocalArpSpoofEvasionTechnique.execute
adapter: ScapyPacketAdapter
notes: no_malformed_packets_in_docs, no_packet_code_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, restoration_required=true

#### 3. mitm.local.dns_spoof

tool: Bettercap
version: 2.41.4
baseline_usuario: 2.34
runtime: wsl2
worker: WSLWorker
perm: NETWORK_CONTROL
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: interface_profile, victim_profile, dns_profile, dns_map_profile, upstream_dns_profile, restoration_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: interface_profile:string, victim_profile:string, dns_profile:string, dns_map_profile:string, upstream_dns_profile:string, restoration_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: dns_profile, dns_map_profile, upstream_dns_profile, timeout_seconds
evidence: dns_event_summary, affected_domains, affected_hosts, pcap_reference, restoration_status, raw_output_path, normalized_json
graph: DNSNode, DomainNode, HostNode, MITMPositionNode, EvidenceNode
hook: app/modules/mitm_network/local_dns_spoof.py::LocalDnsSpoofTechnique.execute
adapter: BettercapAdapter
notes: no_dns_records_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, restoration_required=true

#### 4. mitm.local.dhcpv6_spoof

tool: mitm6
version: 0.3.0
baseline_usuario: 0.3
runtime: wsl2
worker: WSLWorker
perm: NETWORK_CONTROL
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: interface_profile, domain_profile, victim_profile, ipv6_profile, dns_profile, relay_context_profile, restoration_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: interface_profile:string, domain_profile:string, victim_profile:string, ipv6_profile:string, dns_profile:string, relay_context_profile:string, restoration_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: domain_profile, victim_profile, ipv6_profile, dns_profile, relay_context_profile
evidence: ipv6_advertisement_summary, dns_takeover_summary, affected_hosts, relay_context_summary, pcap_reference, restoration_status, raw_output_path, normalized_json
graph: IPv6Node, DNSNode, HostNode, RelayCandidateNode, MITMPositionNode
hook: app/modules/mitm_network/local_dhcpv6_spoof.py::LocalDhcpv6SpoofTechnique.execute
adapter: Mitm6Adapter
notes: no_relay_steps_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, restoration_required=true

#### 5. mitm.local.dhcp_starvation

tool: Scapy
version: 2.7.0
baseline_usuario: 2.5.0
runtime: windows_python
worker: PacketWorker
perm: NETWORK_CONTROL
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: interface_profile, dhcp_profile, packet_profile, rate_limit_profile, lab_limit_profile, restoration_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: interface_profile:string, dhcp_profile:string, packet_profile:string, rate_limit_profile:string, lab_limit_profile:string, restoration_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: dhcp_profile, rate_limit_profile, lab_limit_profile, timeout_seconds
evidence: dhcp_effect_summary, packet_generation_summary, affected_hosts, pcap_reference, restoration_status, raw_output_path, normalized_json
graph: DHCPNode, NetworkSegmentNode, HostNode, NetworkEffectNode, EvidenceNode
hook: app/modules/mitm_network/local_dhcp_starvation.py::LocalDhcpStarvationTechnique.execute
adapter: ScapyPacketAdapter
notes: no_starvation_logic_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, restoration_required=true, lab_only=true

#### 6. mitm.local.icmp_redirect

tool: Scapy
version: 2.7.0
baseline_usuario: 2.5.0
runtime: windows_python
worker: PacketWorker
perm: NETWORK_CONTROL
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: interface_profile, victim_profile, gateway_profile, route_profile, packet_profile, restoration_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: interface_profile:string, victim_profile:string, gateway_profile:string, route_profile:string, packet_profile:string, restoration_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: victim_profile, gateway_profile, route_profile, packet_profile
evidence: route_effect_summary, packet_generation_summary, affected_hosts, pcap_reference, restoration_status, raw_output_path, normalized_json
graph: ICMPNode, RouteNode, HostNode, NetworkEffectNode, EvidenceNode
hook: app/modules/mitm_network/local_icmp_redirect.py::LocalIcmpRedirectTechnique.execute
adapter: ScapyPacketAdapter
notes: no_redirect_packets_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, restoration_required=true

### Integración de esta parte con LaIA + X5

LaIA debe:

- leer topología de red desde Módulo 1;
- leer NetworkSegmentNode y HostNode del Attack Surface Graph;
- seleccionar técnica candidata;
- rellenar interface_profile, gateway_profile, victim_profile y dns_profile;
- detectar missing_inputs;
- proponer restoration_profile;
- pedir confirmation_profile si hay acción activa;
- no ejecutar directamente;
- no inventar hosts;
- no marcar posición MITM sin evidence;
- no crear paquetes funcionales desde documentación.

X5/OjoRouter debe:

- validar TechniqueRegistry;
- validar scope;
- validar permission_level;
- validar confirmation_profile;
- validar kill_switch_profile;
- seleccionar worker;
- crear job;
- guardar EvidenceStore;
- actualizar ScoringEngine;
- actualizar Attack Surface Graph;
- ejecutar restoration_profile al cerrar;
- permitir Kill Switch.

Hermes puede proponer en sandbox:

- wrapper de Bettercap;
- wrapper de mitm6;
- adapter Scapy;
- parser de eventos;
- normalizador PCAP;
- schema de evidence;
- panel_fields;
- fixture demo;
- documentación de herramienta.

Hermes no puede:

- tocar producción directamente;
- autoaprobarse;
- ejecutar técnica real;
- marcar stub como funcional;
- eliminar IMPLEMENTACION_USUARIO_REQUERIDA;
- crear lógica de paquetes funcional desde documentación.

## PARTE 2/4 — INTERCEPTACIÓN + CAPTURA

### Regla absoluta de esta parte

NO_DOCKER=true

Runtimes permitidos:

- windows_binary
- windows_app
- wsl2
- python_lib
- packet_capture
- proxy_local
- local_api
- browser_automation
- local_ai
- manual_required

Runtimes prohibidos:

- docker
- docker_compose
- container_runtime

### Versiones oficiales de esta parte

Bettercap: 2.41.4
Bettercap baseline_usuario: 2.34

mitmproxy: 12.2.1
mitmproxy baseline_usuario: 10.2

sslstrip+: latest-release-lock
sslstrip+ notes: fork_requires_review=true

BeEF: latest-release-lock
BeEF notes: versionlock_required=true

tcpdump: 4.99.6
tcpdump baseline_usuario: 4.99

Wireshark/Tshark: 4.6.5
Wireshark baseline_usuario: 4.2

net-creds: latest-release-lock
net-creds baseline_usuario: 1.0
net-creds notes: version_requires_review=true

PCredz: latest-release-lock
PCredz baseline_usuario: 1.0
PCredz notes: version_requires_review=true

dsniff: latest-release-lock
dsniff baseline_usuario: 2.4

### Anclajes reales por herramienta

#### mitmproxy connector

tool_adapter: MitmproxyAdapter
runtime: python_lib_or_windows_app
worker: ProxyToolWorker
connection_fields:

- proxy_profile
- listener_profile
- ca_profile
- flow_profile
- script_profile
- redaction_profile
- evidence_profile
- shutdown_profile

outputs:

- proxy_flow_log
- request_response_summary
- token_or_cookie_artifact_reference
- redacted_capture_reference
- raw_output_path
- normalized_json

hook_base: app/modules/mitm_network/adapters/mitmproxy_adapter.py::MitmproxyAdapter

#### Bettercap proxy connector

tool_adapter: BettercapProxyAdapter
runtime: wsl2
worker: WSLWorker
connection_fields:

- interface_profile
- victim_profile
- gateway_profile
- proxy_profile
- http_proxy_profile
- https_proxy_profile
- injection_profile
- event_stream_profile
- redaction_profile
- evidence_profile
- restoration_profile

outputs:

- bettercap_event_log
- proxy_event_summary
- injection_event_summary
- affected_hosts
- raw_output_path
- normalized_json

hook_base: app/modules/mitm_network/adapters/bettercap_proxy_adapter.py::BettercapProxyAdapter

#### PCAP capture connector

tool_adapter: PcapCaptureAdapter
runtime: packet_capture
worker: CaptureWorker
connection_fields:

- interface_profile
- capture_profile
- filter_profile
- duration_profile
- storage_profile
- redaction_profile
- evidence_profile

outputs:

- pcap_reference
- packet_summary
- protocol_summary
- artifact_candidates
- raw_output_path
- normalized_json

hook_base: app/modules/mitm_network/adapters/pcap_capture_adapter.py::PcapCaptureAdapter

#### Credential parser connector

tool_adapter: CredentialParserAdapter
runtime: wsl2_or_python_lib
worker: PythonToolWorker
connection_fields:

- pcap_reference
- parser_profile
- protocol_profile
- redaction_profile
- confidence_profile
- evidence_profile

outputs:

- credential_artifact_reference
- hash_artifact_reference
- cookie_artifact_reference
- redacted_summary
- parser_summary
- normalized_json

hook_base: app/modules/mitm_network/adapters/credential_parser_adapter.py::CredentialParserAdapter

### Submódulo 6.2 — Interceptación y manipulación de tráfico

submodule_id: mitm_network.intercept
submodule_name: SSLStrip, proxy local, inyección controlada, manipulación de tráfico
primary_worker: MITMWorker
secondary_workers:

- ProxyToolWorker
- WSLWorker
- PythonToolWorker
- CaptureWorker
- AIWorker

Regla del submódulo:

Este submódulo solo documenta conexiones, fields, evidence y hooks.

No se documentan certificados funcionales.
No se documentan scripts de proxy.
No se documentan reglas de interceptación.
No se documentan payloads.
No se documentan pasos de manipulación.
Toda lógica queda como IMPLEMENTACION_USUARIO_REQUERIDA.

#### 7. mitm.intercept.sslstrip_hsts_bypass

tool: sslstrip+ + Bettercap
version: sslstrip+ latest-release-lock + Bettercap 2.41.4
baseline_usuario: sslstrip+ + Bettercap 2.34
runtime: wsl2
worker: WSLWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: interface_profile, victim_profile, gateway_profile, proxy_profile, downgrade_profile, domain_scope_profile, restoration_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: interface_profile:string, victim_profile:string, gateway_profile:string, proxy_profile:string, downgrade_profile:string, domain_scope_profile:string, restoration_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: victim_profile, proxy_profile, domain_scope_profile, timeout_seconds
evidence: downgrade_attempt_summary, affected_hosts, affected_domains, proxy_event_summary, pcap_reference, restoration_status, raw_output_path, normalized_json
graph: WebEndpointNode, TLSNode, ProxyNode, MITMPositionNode, EvidenceNode
hook: app/modules/mitm_network/intercept_sslstrip_hsts_bypass.py::InterceptSslstripHstsBypassTechnique.execute
adapter: BettercapProxyAdapter
notes: no_sslstrip_steps_in_docs, no_cert_logic_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, restoration_required=true

#### 8. mitm.intercept.mitmproxy_https

tool: mitmproxy
version: 12.2.1
baseline_usuario: 10.2
runtime: python_lib_or_windows_app
worker: ProxyToolWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: proxy_profile, listener_profile, ca_profile, flow_profile, script_profile, redaction_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: proxy_profile:string, listener_profile:string, ca_profile:string, flow_profile:string, script_profile:string_optional, redaction_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: proxy_profile, flow_profile, redaction_profile, timeout_seconds
evidence: proxy_flow_log, request_response_summary, redacted_capture_reference, pcap_reference, raw_output_path, normalized_json
graph: ProxyNode, TLSNode, WebEndpointNode, RequestNode, ResponseNode
hook: app/modules/mitm_network/intercept_mitmproxy_https.py::InterceptMitmproxyHttpsTechnique.execute
adapter: MitmproxyAdapter
notes: no_ca_generation_steps_in_docs, no_proxy_script_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true

#### 9. mitm.intercept.inject_beef

tool: Bettercap + BeEF
version: Bettercap 2.41.4 + BeEF latest-release-lock
baseline_usuario: Bettercap 2.34 + BeEF WSL2 package
runtime: wsl2
worker: WSLWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: interface_profile, victim_profile, proxy_profile, injection_profile, browser_context_profile, lab_server_profile, restoration_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: interface_profile:string, victim_profile:string, proxy_profile:string, injection_profile:string, browser_context_profile:string, lab_server_profile:string, restoration_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: victim_profile, injection_profile, browser_context_profile, timeout_seconds
evidence: injection_event_summary, browser_interaction_summary, affected_hosts, raw_output_path, normalized_json
graph: BrowserNode, ProxyNode, InjectionNode, MITMPositionNode, EvidenceNode
hook: app/modules/mitm_network/intercept_inject_beef.py::InterceptInjectBeefTechnique.execute
adapter: BettercapProxyAdapter
notes: no_javascript_payloads_in_docs, no_beef_hook_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, lab_only=true

#### 10. mitm.intercept.replace_images

tool: Bettercap
version: 2.41.4
baseline_usuario: 2.34
runtime: wsl2
worker: WSLWorker
perm: ACTIVE_SENSITIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: interface_profile, victim_profile, proxy_profile, replacement_profile, content_filter_profile, restoration_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: interface_profile:string, victim_profile:string, proxy_profile:string, replacement_profile:string, content_filter_profile:string, restoration_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: replacement_profile, content_filter_profile, timeout_seconds
evidence: content_replacement_summary, affected_hosts, request_response_summary, raw_output_path, normalized_json
graph: ProxyNode, ContentRewriteNode, WebEndpointNode, EvidenceNode
hook: app/modules/mitm_network/intercept_replace_images.py::InterceptReplaceImagesTechnique.execute
adapter: BettercapProxyAdapter
notes: no_replacement_payload_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, lab_only=true

#### 11. mitm.intercept.keylogger

tool: mitmproxy
version: 12.2.1
baseline_usuario: 10.2
runtime: python_lib_or_windows_app
worker: ProxyToolWorker
perm: CREDENTIALS
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: proxy_profile, form_capture_profile, redaction_profile, sensitive_field_policy, storage_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: proxy_profile:string, form_capture_profile:string, redaction_profile:string, sensitive_field_policy:string, storage_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: form_capture_profile, redaction_profile, sensitive_field_policy
evidence: form_submission_summary, redacted_capture_reference, credential_artifact_reference, raw_output_path, normalized_json
graph: ProxyNode, CredentialArtifactNode, WebEndpointNode, EvidenceNode
hook: app/modules/mitm_network/intercept_keylogger.py::InterceptKeyloggerTechnique.execute
adapter: MitmproxyAdapter
notes: no_keylogger_script_in_docs, no_sensitive_values_in_docs, redact_by_default=true, user_logic_required, requires_confirmation=true, kill_switch_required=true, lab_only=true

### Submódulo 6.3 — Captura de credenciales y hashes

submodule_id: mitm_network.capture
submodule_name: PCAP, credenciales, hashes, cookies, protocolos en claro
primary_worker: CaptureWorker
secondary_workers:

- WSLWorker
- WindowsWorker
- PythonToolWorker
- AIWorker
- EvidenceWorker

Regla del submódulo:

Este submódulo solo documenta conexiones, fields, evidence y hooks.

No se documentan filtros funcionales.
No se documentan comandos.
No se muestran credenciales reales.
No se muestran hashes reales.
Toda salida sensible debe estar redactada por defecto.

#### 12. mitm.capture.tcpdump_sniffing

tool: tcpdump + Tshark
version: tcpdump 4.99.6 + Wireshark/Tshark 4.6.5
baseline_usuario: tcpdump 4.99 + Tshark 4.2
runtime: wsl2_and_windows_binary
worker: CaptureWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: interface_profile, capture_profile, filter_profile, duration_profile, storage_profile, redaction_profile, evidence_profile
inputs: interface_profile:string, capture_profile:string, filter_profile:string, duration_profile:string, storage_profile:string, redaction_profile:string, evidence_profile:string
ai: capture_profile, filter_profile, duration_profile, redaction_profile
evidence: pcap_reference, packet_summary, protocol_summary, redacted_artifact_summary, raw_output_path, normalized_json
graph: PCAPNode, ProtocolNode, EvidenceNode, NetworkSegmentNode
hook: app/modules/mitm_network/capture_tcpdump_sniffing.py::CaptureTcpdumpSniffingTechnique.execute
adapter: PcapCaptureAdapter
notes: no_capture_filters_in_docs, no_commands_in_docs, redact_by_default=true, user_logic_required

#### 13. mitm.capture.net_creds

tool: net-creds
version: latest-release-lock
baseline_usuario: 1.0
runtime: wsl2
worker: PythonToolWorker
perm: CREDENTIALS
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: pcap_reference, parser_profile, protocol_profile, redaction_profile, confidence_profile, evidence_profile
inputs: pcap_reference:string, parser_profile:string, protocol_profile:string, redaction_profile:string, confidence_profile:string, evidence_profile:string
ai: parser_profile, protocol_profile, redaction_profile, confidence_profile
evidence: credential_artifact_reference, redacted_summary, parser_summary, raw_output_path, normalized_json
graph: CredentialArtifactNode, PCAPNode, ProtocolNode, EvidenceNode
hook: app/modules/mitm_network/capture_net_creds.py::CaptureNetCredsTechnique.execute
adapter: CredentialParserAdapter
notes: no_credentials_in_docs, no_live_sniffing_steps_in_docs, redact_by_default=true, user_logic_required, requires_confirmation=true, version_requires_review=true

#### 14. mitm.capture.pcredz

tool: PCredz
version: latest-release-lock
baseline_usuario: 1.0
runtime: wsl2
worker: PythonToolWorker
perm: CREDENTIALS
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: pcap_reference, parser_profile, protocol_profile, hash_profile, redaction_profile, confidence_profile, evidence_profile
inputs: pcap_reference:string, parser_profile:string, protocol_profile:string, hash_profile:string, redaction_profile:string, confidence_profile:string, evidence_profile:string
ai: parser_profile, protocol_profile, hash_profile, redaction_profile
evidence: hash_artifact_reference, cookie_artifact_reference, redacted_summary, parser_summary, raw_output_path, normalized_json
graph: HashArtifactNode, CookieArtifactNode, PCAPNode, ProtocolNode, EvidenceNode
hook: app/modules/mitm_network/capture_pcredz.py::CapturePcredzTechnique.execute
adapter: CredentialParserAdapter
notes: no_hash_values_in_docs, no_live_sniffing_steps_in_docs, redact_by_default=true, user_logic_required, requires_confirmation=true, version_requires_review=true

#### 15. mitm.capture.dsniff

tool: dsniff
version: latest-release-lock
baseline_usuario: 2.4
runtime: wsl2
worker: WSLWorker
perm: CREDENTIALS
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: interface_profile, pcap_reference, protocol_profile, parser_profile, redaction_profile, confidence_profile, evidence_profile
inputs: interface_profile:string_optional, pcap_reference:string_optional, protocol_profile:string, parser_profile:string, redaction_profile:string, confidence_profile:string, evidence_profile:string
ai: protocol_profile, parser_profile, redaction_profile, confidence_profile
evidence: credential_artifact_reference, protocol_summary, redacted_summary, raw_output_path, normalized_json
graph: CredentialArtifactNode, ProtocolNode, PCAPNode, EvidenceNode
hook: app/modules/mitm_network/capture_dsniff.py::CaptureDsniffTechnique.execute
adapter: CredentialParserAdapter
notes: no_credentials_in_docs, no_live_sniffing_steps_in_docs, redact_by_default=true, user_logic_required, requires_confirmation=true

### Integración de esta parte con LaIA + X5

LaIA debe:

- leer topología y PCAP summaries;
- proponer perfiles de captura y análisis;
- seleccionar técnica candidata;
- rellenar fields;
- detectar missing_inputs;
- aplicar redaction_profile por defecto;
- pedir confirmation_profile si hay captura sensible;
- no ejecutar directamente;
- no inventar credenciales;
- no inventar hashes;
- no marcar tokens ni cookies sin evidence.

X5/OjoRouter debe:

- validar TechniqueRegistry;
- validar scope;
- validar permission_level;
- validar confirmation_profile;
- validar redaction_profile;
- seleccionar worker;
- crear job;
- guardar EvidenceStore;
- actualizar ScoringEngine;
- actualizar Attack Surface Graph;
- permitir Kill Switch.

Hermes puede proponer en sandbox:

- wrapper de mitmproxy;
- wrapper de Bettercap proxy;
- parser de PCAP;
- parser de credenciales redactadas;
- normalizador de flows;
- schema de evidence;
- panel_fields;
- fixture demo;
- documentación de herramienta.

Hermes no puede:

- tocar producción directamente;
- autoaprobarse;
- ejecutar técnica real;
- marcar stub como funcional;
- eliminar IMPLEMENTACION_USUARIO_REQUERIDA;
- crear lógica funcional de captura desde documentación;
- mostrar secretos sin redacción.

## PARTE 3/4 — SESIONES/MFA + TÚNELES

### Regla absoluta de esta parte

NO_DOCKER=true

Runtimes permitidos:

- windows_binary
- windows_app
- wsl2
- python_lib
- proxy_local
- local_api
- tunnel_runtime
- local_ai
- manual_required

Runtimes prohibidos:

- docker
- docker_compose
- container_runtime

### Versiones oficiales de esta parte

Evilginx: latest-release-lock
Evilginx baseline_usuario: 3.3
Evilginx notes: public_repo_release_old=true, pro_line_exists=true, versionlock_required=true, no_sustituir_sin_aprobacion=true

Bettercap: 2.41.4
Bettercap baseline_usuario: 2.34

mitmproxy: 12.2.2
mitmproxy baseline_usuario: 10.2

dnscat2: latest-release-lock
dnscat2 baseline_usuario: 0.07
dnscat2 notes: versionlock_required=true

iodine: 0.8 baseline_usuario
iodine notes: resolve_real_package_version_in_wsl2_versionlock=true

Chisel: 1.11.3
Chisel baseline_usuario: 1.9

ptunnel-ng: 1.2 baseline_usuario
ptunnel-ng notes: resolve_real_package_version_in_wsl2_versionlock=true

### Anclajes reales por herramienta

#### Evilginx connector

tool_adapter: EvilginxAdapter
runtime: wsl2
worker: WSLWorker
connection_fields:

- lab_domain_profile
- proxy_profile
- target_service_profile
- phishlet_profile
- tls_profile
- capture_profile
- event_stream_profile
- redaction_profile
- evidence_profile
- shutdown_profile

outputs:

- session_capture_summary
- token_artifact_reference
- cookie_artifact_reference
- proxy_event_log
- redacted_capture_reference
- raw_output_path
- normalized_json

hook_base: app/modules/mitm_network/adapters/evilginx_adapter.py::EvilginxAdapter
notes: no_phishlets_in_docs, no_token_use_steps_in_docs

#### Session artifact connector

tool_adapter: SessionArtifactAdapter
runtime: python_lib
worker: PythonToolWorker
connection_fields:

- token_artifact_reference
- cookie_artifact_reference
- session_profile
- validation_profile
- redaction_profile
- evidence_profile

outputs:

- session_artifact_reference
- session_risk_summary
- redacted_summary
- normalized_json

hook_base: app/modules/mitm_network/adapters/session_artifact_adapter.py::SessionArtifactAdapter
notes: no_session_replay_steps_in_docs, redact_by_default=true

#### Tunnel connector

tool_adapter: TunnelAdapter
runtime: tunnel_runtime
worker: TunnelWorker
connection_fields:

- tunnel_tool_profile
- local_endpoint_profile
- remote_endpoint_profile
- protocol_profile
- routing_profile
- authentication_profile
- bandwidth_profile
- evidence_profile
- shutdown_profile

outputs:

- tunnel_artifact_reference
- tunnel_state_summary
- traffic_summary
- endpoint_summary
- raw_output_path
- normalized_json

hook_base: app/modules/mitm_network/adapters/tunnel_adapter.py::TunnelAdapter
notes: no_tunnel_configs_in_docs, shutdown_required=true

### Submódulo 6.4 — Captura de tokens MFA y session hijacking

submodule_id: mitm_network.session
submodule_name: MFA token capture, cookies, OAuth tokens, session artifacts
primary_worker: MITMWorker
secondary_workers:

- WSLWorker
- ProxyToolWorker
- PythonToolWorker
- AIWorker
- EvidenceWorker

Regla del submódulo:

Este submódulo solo documenta conexiones, fields, evidence y hooks.

No se documentan phishlets.
No se documentan certificados funcionales.
No se documentan scripts de proxy.
No se documenta replay de sesión.
No se muestran tokens reales.
No se muestran cookies reales.
Toda salida sensible debe estar redactada por defecto.

#### 16. mitm.session.evilginx_mfa_capture

tool: Evilginx + Bettercap
version: Evilginx latest-release-lock + Bettercap 2.41.4
baseline_usuario: Evilginx 3.3 + Bettercap 2.34
runtime: wsl2
worker: WSLWorker
perm: CREDENTIALS
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: lab_domain_profile, proxy_profile, target_service_profile, phishlet_profile, tls_profile, capture_profile, redaction_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: lab_domain_profile:string, proxy_profile:string, target_service_profile:string, phishlet_profile:string, tls_profile:string, capture_profile:string, redaction_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: target_service_profile, capture_profile, redaction_profile, timeout_seconds
evidence: session_capture_summary, token_artifact_reference, cookie_artifact_reference, redacted_capture_reference, proxy_event_log, raw_output_path, normalized_json
graph: MFANode, TokenArtifactNode, CookieArtifactNode, SessionNode, ProxyNode, EvidenceNode
hook: app/modules/mitm_network/session_evilginx_mfa_capture.py::SessionEvilginxMfaCaptureTechnique.execute
adapter: EvilginxAdapter
notes: cross_module_reference=module_14_phishing, no_phishlets_in_docs, no_token_use_steps_in_docs, redact_by_default=true, user_logic_required, requires_confirmation=true, kill_switch_required=true, lab_only=true

#### 17. mitm.session.cookie_hijacking

tool: Bettercap + mitmproxy
version: Bettercap 2.41.4 + mitmproxy 12.2.2
baseline_usuario: Bettercap 2.34 + mitmproxy 10.2
runtime: wsl2_or_python_lib
worker: ProxyToolWorker
perm: CREDENTIALS
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: proxy_profile, cookie_profile, session_profile, validation_profile, redaction_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: proxy_profile:string, cookie_profile:string, session_profile:string, validation_profile:string, redaction_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: cookie_profile, session_profile, validation_profile, redaction_profile
evidence: cookie_artifact_reference, session_risk_summary, redacted_capture_reference, request_response_summary, raw_output_path, normalized_json
graph: CookieArtifactNode, SessionNode, ProxyNode, WebEndpointNode, EvidenceNode
hook: app/modules/mitm_network/session_cookie_hijacking.py::SessionCookieHijackingTechnique.execute
adapter: SessionArtifactAdapter
notes: no_cookie_replay_steps_in_docs, no_cookie_values_in_docs, redact_by_default=true, user_logic_required, requires_confirmation=true, kill_switch_required=true

#### 18. mitm.session.oauth_token_theft

tool: mitmproxy
version: 12.2.2
baseline_usuario: 10.2
runtime: python_lib_or_windows_app
worker: ProxyToolWorker
perm: CREDENTIALS
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: proxy_profile, oauth_flow_profile, redirect_profile, token_profile, redaction_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: proxy_profile:string, oauth_flow_profile:string, redirect_profile:string, token_profile:string, redaction_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: oauth_flow_profile, redirect_profile, token_profile, redaction_profile
evidence: oauth_flow_summary, token_artifact_reference, redacted_capture_reference, request_response_summary, raw_output_path, normalized_json
graph: OAuthNode, TokenArtifactNode, SessionNode, ProxyNode, EvidenceNode
hook: app/modules/mitm_network/session_oauth_token_theft.py::SessionOauthTokenTheftTechnique.execute
adapter: MitmproxyAdapter
notes: no_token_extraction_logic_in_docs, no_token_values_in_docs, redact_by_default=true, user_logic_required, requires_confirmation=true, kill_switch_required=true

### Submódulo 6.5 — Túneles de exfiltración y C2

submodule_id: mitm_network.tunnel
submodule_name: DNS, ICMP, HTTP/HTTPS tunnels and C2 transport profiles
primary_worker: TunnelWorker
secondary_workers:

- WSLWorker
- WindowsWorker
- PythonToolWorker
- AIWorker
- EvidenceWorker

Regla del submódulo:

Este submódulo solo documenta conexiones, fields, evidence y hooks.

No se documentan configuraciones de túnel funcionales.
No se documentan endpoints reales.
No se documentan claves reales.
No se documentan comandos.
No se documentan scripts.
Toda lógica queda como IMPLEMENTACION_USUARIO_REQUERIDA.

#### 19. mitm.tunnel.dnscat2_c2

tool: dnscat2
version: latest-release-lock
baseline_usuario: 0.07
runtime: wsl2
worker: TunnelWorker
perm: TUNNEL
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: tunnel_profile, dns_domain_profile, local_endpoint_profile, remote_endpoint_profile, authentication_profile, bandwidth_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: tunnel_profile:string, dns_domain_profile:string, local_endpoint_profile:string, remote_endpoint_profile:string, authentication_profile:string, bandwidth_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: tunnel_profile, dns_domain_profile, bandwidth_profile, timeout_seconds
evidence: tunnel_state_summary, dns_tunnel_summary, endpoint_summary, traffic_summary, raw_output_path, normalized_json
graph: TunnelNode, DNSNode, EndpointNode, C2TransportNode, EvidenceNode
hook: app/modules/mitm_network/tunnel_dnscat2_c2.py::TunnelDnscat2C2Technique.execute
adapter: TunnelAdapter
notes: no_tunnel_configs_in_docs, no_keys_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, shutdown_required=true, versionlock_required=true

#### 20. mitm.tunnel.iodine_ip_over_dns

tool: iodine
version: 0.8 baseline_usuario
runtime: wsl2
worker: TunnelWorker
perm: TUNNEL
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: tunnel_profile, dns_domain_profile, local_endpoint_profile, remote_endpoint_profile, routing_profile, authentication_profile, bandwidth_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: tunnel_profile:string, dns_domain_profile:string, local_endpoint_profile:string, remote_endpoint_profile:string, routing_profile:string, authentication_profile:string, bandwidth_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: tunnel_profile, dns_domain_profile, routing_profile, bandwidth_profile
evidence: tunnel_state_summary, dns_tunnel_summary, routing_summary, endpoint_summary, traffic_summary, raw_output_path, normalized_json
graph: TunnelNode, DNSNode, RouteNode, EndpointNode, EvidenceNode
hook: app/modules/mitm_network/tunnel_iodine_ip_over_dns.py::TunnelIodineIpOverDnsTechnique.execute
adapter: TunnelAdapter
notes: no_tunnel_configs_in_docs, no_keys_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, shutdown_required=true, resolve_real_package_version_in_wsl2_versionlock=true

#### 21. mitm.tunnel.chisel_http_tunnel

tool: Chisel
version: 1.11.3
baseline_usuario: 1.9
runtime: windows_binary_or_wsl2
worker: TunnelWorker
perm: TUNNEL
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: tunnel_profile, local_endpoint_profile, remote_endpoint_profile, protocol_profile, authentication_profile, tls_profile, bandwidth_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: tunnel_profile:string, local_endpoint_profile:string, remote_endpoint_profile:string, protocol_profile:http|https|tcp|udp|custom, authentication_profile:string, tls_profile:string, bandwidth_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: tunnel_profile, protocol_profile, tls_profile, bandwidth_profile
evidence: tunnel_state_summary, endpoint_summary, protocol_summary, traffic_summary, raw_output_path, normalized_json
graph: TunnelNode, HTTPNode, EndpointNode, RouteNode, EvidenceNode
hook: app/modules/mitm_network/tunnel_chisel_http_tunnel.py::TunnelChiselHttpTunnelTechnique.execute
adapter: TunnelAdapter
notes: no_tunnel_configs_in_docs, no_keys_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, shutdown_required=true, version_updated_from_user_baseline=true

#### 22. mitm.tunnel.ptunnel_icmp

tool: ptunnel-ng
version: 1.2 baseline_usuario
runtime: wsl2
worker: TunnelWorker
perm: TUNNEL
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: tunnel_profile, icmp_profile, local_endpoint_profile, remote_endpoint_profile, authentication_profile, bandwidth_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: tunnel_profile:string, icmp_profile:string, local_endpoint_profile:string, remote_endpoint_profile:string, authentication_profile:string, bandwidth_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: tunnel_profile, icmp_profile, bandwidth_profile, timeout_seconds
evidence: tunnel_state_summary, icmp_tunnel_summary, endpoint_summary, traffic_summary, raw_output_path, normalized_json
graph: TunnelNode, ICMPNode, EndpointNode, RouteNode, EvidenceNode
hook: app/modules/mitm_network/tunnel_ptunnel_icmp.py::TunnelPtunnelIcmpTechnique.execute
adapter: TunnelAdapter
notes: no_tunnel_configs_in_docs, no_keys_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, shutdown_required=true, resolve_real_package_version_in_wsl2_versionlock=true

### Integración de esta parte con LaIA + X5

LaIA debe:

- leer topología, sesión y artifacts del EvidenceStore;
- proponer técnica candidata;
- rellenar fields;
- detectar missing_inputs;
- aplicar redaction_profile por defecto;
- pedir confirmation_profile en sesión, token o túnel;
- proponer shutdown_profile;
- no ejecutar directamente;
- no inventar tokens;
- no inventar cookies;
- no inventar túneles activos;
- no marcar acceso sin evidence.

X5/OjoRouter debe:

- validar TechniqueRegistry;
- validar scope;
- validar permission_level;
- validar confirmation_profile;
- validar kill_switch_profile;
- seleccionar worker;
- crear job;
- guardar EvidenceStore;
- actualizar ScoringEngine;
- actualizar Attack Surface Graph;
- ejecutar shutdown_profile al cerrar;
- permitir Kill Switch.

Hermes puede proponer en sandbox:

- wrapper de Evilginx;
- adapter de sesión;
- adapter de túneles;
- parser de eventos;
- normalizador de artifacts;
- schema de evidence;
- panel_fields;
- fixture demo;
- documentación de herramienta.

Hermes no puede:

- tocar producción directamente;
- autoaprobarse;
- ejecutar técnica real;
- marcar stub como funcional;
- eliminar IMPLEMENTACION_USUARIO_REQUERIDA;
- crear configuraciones funcionales de túnel desde documentación;
- mostrar tokens/cookies sin redacción.

## PARTE 4/4 — INFRAESTRUCTURA + NETWORK DOS + INTEGRACIÓN FINAL

Regla absoluta de esta parte

NO_DOCKER=true

Runtimes permitidos:

- windows_python
- windows_binary
- wsl2
- python_lib
- packet_capture
- packet_generation
- cross_module
- local_ai
- manual_required

Runtimes prohibidos:

- docker
- docker_compose
- container_runtime

Versiones oficiales de esta parte

Yersinia: latest-release-lock
Yersinia baseline_usuario: 0.8.3
Yersinia notes: version_requires_review=true, resolve_real_package_version_in_wsl2_versionlock=true

Loki: latest-release-lock
Loki baseline_usuario: 0.3
Loki notes: version_requires_review=true, resolve_real_package_version_in_wsl2_versionlock=true

Scapy: 2.7.0
Scapy baseline_usuario: 2.5.0

snmpwalk/snmpset: system package WSL2
snmp notes: resolve_real_package_version_in_wsl2_versionlock=true

hping3: latest-release-lock
hping3 baseline_usuario: 3.0
hping3 notes: package_often_reports_3.0.0_alpha_2, resolve_real_package_version_in_wsl2_versionlock=true

aircrack-ng: 1.7
aircrack-ng notes: cross_module_reference=module_10_wireless_rf_hackrf

Anclajes reales por herramienta

Yersinia connector

tool_adapter: YersiniaAdapter
runtime: wsl2
worker: WSLWorker
connection_fields:

- interface_profile
- protocol_profile
- vlan_profile
- stp_profile
- dtp_profile
- lab_limit_profile
- confirmation_profile
- evidence_profile
- restoration_profile
  outputs:
- layer2_action_summary
- vlan_risk_summary
- switch_state_observation
- pcap_reference
- raw_output_path
- normalized_json
  hook_base: app/modules/mitm_network/adapters/yersinia_adapter.py::YersiniaAdapter
  notes: no_layer2_attack_steps_in_docs, restoration_required=true

Loki routing connector

tool_adapter: LokiRoutingAdapter
runtime: wsl2
worker: WSLWorker
connection_fields:

- interface_profile
- routing_protocol_profile
- route_profile
- neighbor_profile
- lab_limit_profile
- confirmation_profile
- evidence_profile
- restoration_profile
  outputs:
- routing_protocol_summary
- route_injection_risk_summary
- neighbor_observation_summary
- pcap_reference
- raw_output_path
- normalized_json
  hook_base: app/modules/mitm_network/adapters/loki_routing_adapter.py::LokiRoutingAdapter
  notes: no_route_injection_steps_in_docs, restoration_required=true

SNMP connector

tool_adapter: SnmpAdapter
runtime: wsl2
worker: WSLWorker
connection_fields:

- target_profile
- snmp_version_profile
- community_profile
- oid_profile
- access_mode_profile
- redaction_profile
- confirmation_profile
- evidence_profile
- restoration_profile
  outputs:
- snmp_access_summary
- snmp_config_snapshot_reference
- oid_summary
- redacted_summary
- raw_output_path
- normalized_json
  hook_base: app/modules/mitm_network/adapters/snmp_adapter.py::SnmpAdapter
  notes: no_snmp_write_steps_in_docs, redact_by_default=true

Layer2 recon connector

tool_adapter: Layer2ReconAdapter
runtime: windows_python
worker: PacketWorker
connection_fields:

- interface_profile
- protocol_profile
- capture_profile
- topology_profile
- redaction_profile
- evidence_profile
  outputs:
- topology_summary
- cdp_lldp_summary
- device_identity_candidates
- pcap_reference
- raw_output_path
- normalized_json
  hook_base: app/modules/mitm_network/adapters/layer2_recon_adapter.py::Layer2ReconAdapter
  notes: passive_default=true

Network DoS connector

tool_adapter: NetworkDosAdapter
runtime: windows_python_or_wsl2
worker: PacketWorker
connection_fields:

- target_profile
- interface_profile
- dos_profile
- rate_limit_profile
- lab_limit_profile
- stop_condition_profile
- confirmation_profile
- evidence_profile
- restoration_profile
  outputs:
- dos_test_summary
- resilience_observation
- traffic_summary
- stop_condition_result
- pcap_reference
- raw_output_path
- normalized_json
  hook_base: app/modules/mitm_network/adapters/network_dos_adapter.py::NetworkDosAdapter
  notes: no_flood_parameters_in_docs, lab_only=true, kill_switch_required=true

Wireless deauth cross-module connector

tool_adapter: WirelessCrossModuleAdapter
runtime: cross_module
worker: HardwareWorker
connection_fields:

- wireless_target_profile
- interface_profile
- radio_profile
- deauth_profile
- confirmation_profile
- evidence_profile
  outputs:
- cross_module_request_summary
- wireless_action_reference
- evidence_ids
- normalized_json
  hook_base: app/modules/mitm_network/adapters/wireless_cross_module_adapter.py::WirelessCrossModuleAdapter
  notes: implementation_lives_in_module_10, no_wireless_attack_steps_in_docs

### Submódulo 6.6 — Ataques a infraestructura de red

submodule_id: mitm_network.infrastructure
submodule_name: SNMP, VLAN, routing protocols, CDP/LLDP
primary_worker: NetworkWorker
secondary_workers:

- WSLWorker
- PacketWorker
- PythonToolWorker
- AIWorker
- EvidenceWorker

Regla del submódulo:

Este submódulo solo documenta conexiones, fields, evidence y hooks.
No se documentan paquetes concretos.
No se documentan comandos.
No se documentan scripts.
No se documentan pasos de modificación de infraestructura.
Toda lógica queda como IMPLEMENTACION_USUARIO_REQUERIDA.

#### 23. mitm.infra.vlan_hopping

tool: Yersinia + Scapy
version: Yersinia latest-release-lock + Scapy 2.7.0
baseline_usuario: Yersinia 0.8.3 + Scapy 2.5.0
runtime: wsl2 + windows_python
worker: WSLWorker
perm: NETWORK_CONTROL
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: interface_profile, vlan_profile, stp_profile, dtp_profile, lab_limit_profile, confirmation_profile, timeout_seconds, evidence_profile, restoration_profile
inputs: interface_profile:string, vlan_profile:string, stp_profile:string, dtp_profile:string, lab_limit_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string, restoration_profile:string
ai: interface_profile, vlan_profile, stp_profile, dtp_profile, lab_limit_profile
evidence: layer2_action_summary, vlan_risk_summary, switch_state_observation, pcap_reference, restoration_status, raw_output_path, normalized_json
graph: VLANNode, SwitchNode, Layer2Node, NetworkEffectNode, EvidenceNode
hook: app/modules/mitm_network/infra_vlan_hopping.py::InfraVlanHoppingTechnique.execute
adapter: YersiniaAdapter
notes: no_vlan_attack_steps_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, restoration_required=true, lab_only=true

#### 24. mitm.infra.route_injection

tool: Loki
version: latest-release-lock
baseline_usuario: 0.3
runtime: wsl2
worker: WSLWorker
perm: NETWORK_CONTROL
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: interface_profile, routing_protocol_profile, route_profile, neighbor_profile, lab_limit_profile, confirmation_profile, timeout_seconds, evidence_profile, restoration_profile
inputs: interface_profile:string, routing_protocol_profile:string, route_profile:string, neighbor_profile:string, lab_limit_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string, restoration_profile:string
ai: routing_protocol_profile, route_profile, neighbor_profile, lab_limit_profile
evidence: routing_protocol_summary, route_injection_risk_summary, neighbor_observation_summary, pcap_reference, restoration_status, raw_output_path, normalized_json
graph: RouteNode, RouterNode, RoutingProtocolNode, NetworkEffectNode, EvidenceNode
hook: app/modules/mitm_network/infra_route_injection.py::InfraRouteInjectionTechnique.execute
adapter: LokiRoutingAdapter
notes: no_route_injection_steps_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, restoration_required=true, lab_only=true

#### 25. mitm.infra.snmp_exploitation

tool: snmpwalk/snmpset
version: system package WSL2
runtime: wsl2
worker: WSLWorker
perm: NETWORK_CONTROL
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: target_profile, snmp_version_profile, community_profile, oid_profile, access_mode_profile, redaction_profile, confirmation_profile, timeout_seconds, evidence_profile, restoration_profile
inputs: target_profile:string, snmp_version_profile:string, community_profile:string, oid_profile:string, access_mode_profile:read|write|custom, redaction_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string, restoration_profile:string
ai: snmp_version_profile, oid_profile, access_mode_profile, redaction_profile
evidence: snmp_access_summary, snmp_config_snapshot_reference, oid_summary, redacted_summary, restoration_status, raw_output_path, normalized_json
graph: SNMPNode, NetworkDeviceNode, DeviceConfigNode, EvidenceNode
hook: app/modules/mitm_network/infra_snmp_exploitation.py::InfraSnmpExploitationTechnique.execute
adapter: SnmpAdapter
notes: no_snmp_write_steps_in_docs, no_community_values_in_docs, redact_by_default=true, user_logic_required, requires_confirmation=true, restoration_required=true

#### 26. mitm.infra.cdp_recon

tool: Python scripts / Scapy
version: Scapy 2.7.0
baseline_usuario: Scapy 2.5.0
runtime: windows_python
worker: PacketWorker
perm: PASSIVE
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: interface_profile, protocol_profile, capture_profile, topology_profile, redaction_profile, timeout_seconds, evidence_profile
inputs: interface_profile:string, protocol_profile:cdp|lldp|both|custom, capture_profile:string, topology_profile:string, redaction_profile:string, timeout_seconds:int, evidence_profile:string
ai: protocol_profile, topology_profile, redaction_profile
evidence: topology_summary, cdp_lldp_summary, device_identity_candidates, pcap_reference, raw_output_path, normalized_json
graph: NetworkDeviceNode, SwitchNode, RouterNode, TopologyNode, EvidenceNode
hook: app/modules/mitm_network/infra_cdp_recon.py::InfraCdpReconTechnique.execute
adapter: Layer2ReconAdapter
notes: passive_default=true, no_packet_code_in_docs, user_logic_required

### Submódulo 6.7 — Denegación de servicio a nivel de red

submodule_id: mitm_network.network_dos
submodule_name: SYN, UDP, wireless deauth cross-module, MAC flooding
primary_worker: NetworkWorker
secondary_workers:

- PacketWorker
- WSLWorker
- HardwareWorker
- AIWorker
- EvidenceWorker

Regla del submódulo:

Este submódulo solo documenta conexiones, fields, evidence y hooks.
No se documentan floods funcionales.
No se documentan tasas.
No se documentan comandos.
No se documentan scripts.
No se documentan parámetros destructivos.
Toda lógica queda como IMPLEMENTACION_USUARIO_REQUERIDA.

#### 27. mitm.dos.syn_flood

tool: hping3 / Scapy
version: hping3 latest-release-lock + Scapy 2.7.0
baseline_usuario: hping3 3.0 + Scapy 2.5.0
runtime: wsl2 + windows_python
worker: PacketWorker
perm: DOS_CONTROLLED
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: target_profile, interface_profile, dos_profile, rate_limit_profile, lab_limit_profile, stop_condition_profile, confirmation_profile, timeout_seconds, evidence_profile, restoration_profile
inputs: target_profile:string, interface_profile:string, dos_profile:string, rate_limit_profile:string, lab_limit_profile:string, stop_condition_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string, restoration_profile:string
ai: target_profile, dos_profile, rate_limit_profile, lab_limit_profile, stop_condition_profile
evidence: dos_test_summary, resilience_observation, traffic_summary, stop_condition_result, pcap_reference, raw_output_path, normalized_json
graph: NetworkDosNode, TCPNode, ServiceNode, ResilienceFindingNode, EvidenceNode
hook: app/modules/mitm_network/dos_syn_flood.py::DosSynFloodTechnique.execute
adapter: NetworkDosAdapter
notes: no_flood_parameters_in_docs, no_commands_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, lab_only=true, restore_or_stop_required=true

#### 28. mitm.dos.udp_flood

tool: Scapy
version: 2.7.0
baseline_usuario: 2.5.0
runtime: windows_python
worker: PacketWorker
perm: DOS_CONTROLLED
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: target_profile, interface_profile, dos_profile, rate_limit_profile, lab_limit_profile, stop_condition_profile, confirmation_profile, timeout_seconds, evidence_profile, restoration_profile
inputs: target_profile:string, interface_profile:string, dos_profile:string, rate_limit_profile:string, lab_limit_profile:string, stop_condition_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string, restoration_profile:string
ai: target_profile, dos_profile, rate_limit_profile, lab_limit_profile, stop_condition_profile
evidence: dos_test_summary, resilience_observation, traffic_summary, stop_condition_result, pcap_reference, raw_output_path, normalized_json
graph: NetworkDosNode, UDPNode, ServiceNode, ResilienceFindingNode, EvidenceNode
hook: app/modules/mitm_network/dos_udp_flood.py::DosUdpFloodTechnique.execute
adapter: NetworkDosAdapter
notes: no_flood_parameters_in_docs, no_packet_code_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, lab_only=true, restore_or_stop_required=true

#### 29. mitm.dos.deauth_attack

tool: aircrack-ng
version: 1.7
runtime: cross_module
worker: HardwareWorker
perm: DOS_CONTROLLED
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: wireless_target_profile, interface_profile, radio_profile, deauth_profile, lab_limit_profile, confirmation_profile, timeout_seconds, evidence_profile
inputs: wireless_target_profile:string, interface_profile:string, radio_profile:string, deauth_profile:string, lab_limit_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string
ai: wireless_target_profile, radio_profile, lab_limit_profile
evidence: cross_module_request_summary, wireless_action_reference, resilience_observation, evidence_ids, normalized_json
graph: WirelessNode, NetworkDosNode, ClientDeviceNode, EvidenceNode
hook: app/modules/mitm_network/dos_deauth_attack.py::DosDeauthAttackTechnique.execute
adapter: WirelessCrossModuleAdapter
notes: implementation_lives_in_module_10_wireless_rf, no_deauth_steps_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, lab_only=true

#### 30. mitm.dos.mac_flooding

tool: Scapy
version: 2.7.0
baseline_usuario: 2.5.0
runtime: windows_python
worker: PacketWorker
perm: DOS_CONTROLLED
status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
fields: interface_profile, switch_profile, mac_profile, rate_limit_profile, lab_limit_profile, stop_condition_profile, confirmation_profile, timeout_seconds, evidence_profile, restoration_profile
inputs: interface_profile:string, switch_profile:string, mac_profile:string, rate_limit_profile:string, lab_limit_profile:string, stop_condition_profile:string, confirmation_profile:string, timeout_seconds:int, evidence_profile:string, restoration_profile:string
ai: switch_profile, mac_profile, rate_limit_profile, lab_limit_profile, stop_condition_profile
evidence: dos_test_summary, switch_behavior_summary, traffic_summary, stop_condition_result, pcap_reference, raw_output_path, normalized_json
graph: SwitchNode, CAMTableNode, NetworkDosNode, NetworkEffectNode, EvidenceNode
hook: app/modules/mitm_network/dos_mac_flooding.py::DosMacFloodingTechnique.execute
adapter: NetworkDosAdapter
notes: no_mac_flooding_logic_in_docs, no_packet_code_in_docs, user_logic_required, requires_confirmation=true, kill_switch_required=true, lab_only=true, restore_or_stop_required=true

### Submódulo 6.8 — VPNs y túneles

submodule_id: mitm_network.vpn_tunnels
panel: Red / MITM > VPNs
status_default: IMPLEMENTACION_USUARIO_REQUERIDA
workers: NetworkWorker, WSLWorker, PacketWorker, PythonToolWorker, EvidenceWorker, AIWorker
runtimes: wsl2, python_lib, packet_capture, local_ai
toolhealth: ike-scan, ikeforce, hydra, openvpn-bruteforce, wireguard-tools, tcpdump
versionlock: resolve_real_package_version_in_wsl2=true

#### Integración

Si Módulo 1 detecta UDP 500/4500, TCP/UDP 1194 o UDP 51820, crear ServiceFingerprint vpn_server y mostrarlo en Red / MITM > VPNs.

#### Panel

columns: ip, vpn_type, ports, fingerprint, estado, ultima_evidencia
detail_fields: ip, ports, protocol_profile, auth_profile, banner_or_handshake, toolhealth, risk_level
actions: analizar, ataque_inteligente, ejecutar_tecnica, validar_conexion, capturar_trafico, ver_evidencia
states: SIN_ACCESO, ATAQUE_EN_CURSO, CREDENCIAL_OBTENIDA, CONEXION_VALIDADA, PARTIAL, FAILED, MISSING_TOOL, MANUAL_REQUIRED

#### Mistral plan JSON

intent, target_profile, vpn_type, protocol_profile, auth_profile, selected_technique, fallback_chain, tool_profile, evidence_expected, requires_confirmation, stop_condition, user_explanation

#### X5 result JSON

run_id, technique_id, status, credential_reference_redacted, connection_validation, pcap_reference, internal_reachability_summary, evidence_ids, error_code, next_recommended_techniques

#### Común

status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
scope_required: true
requires_confirmation: true
kill_switch_required: true
evidence: vpn_fingerprint_summary, credential_reference_redacted, vpn_connection_validation, internal_reachability_summary, pcap_reference, raw_output_path, normalized_json
graph: VPNNode, IPsecNode, OpenVPNNode, WireGuardNode, CredentialNode, InternalNetworkNode, EvidenceNode
notes: catalog_only,user_logic_required,no_commands_in_docs,no_credentials_in_docs,no_configs_in_docs
hook: app/modules/mitm_network/<id_sin_mitm>.py::<ClasePascal>Technique.execute

#### 31. mitm.vpn.ipsec_psk_bruteforce

tool: ike-scan + ikeforce
version: system_package + latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: CREDENTIALS
fields: target_profile, ike_profile, aggressive_mode_profile, psk_dictionary_profile, timeout_seconds, evidence_profile
adapter: IPsecPskAdapter
success_evidence: psk_reference_redacted, ike_auth_validation, vpn_fingerprint_summary
notes_extra: ipsec_ikev1_profile, credential_redaction_required=true

#### 32. mitm.vpn.ipsec_xauth_bruteforce

tool: Hydra + IPsec/XAuth connector
version: latest-release-lock
baseline_usuario: Hydra 9.7
observed_current_reference: Hydra 9.6
runtime: wsl2
worker: WSLWorker
perm: CREDENTIALS
fields: target_profile, xauth_profile, username_profile, password_profile, timeout_seconds, evidence_profile
adapter: IPsecXAuthAdapter
success_evidence: account_reference_redacted, auth_success_summary
notes_extra: xauth_only_when_detected=true

#### 33. mitm.vpn.openvpn_bruteforce

tool: openvpn-bruteforce + Hydra fallback
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: CREDENTIALS
fields: openvpn_profile, cert_profile, username_profile, password_profile, config_reference, timeout_seconds, evidence_profile
adapter: OpenVpnAuthAdapter
success_evidence: openvpn_auth_success, tunnel_interface_summary, screenshot_reference
notes_extra: toolhealth_required=true, manual_config_reference_allowed=true

#### 34. mitm.vpn.wireguard_handshake_capture

tool: wireguard-tools + tcpdump
version: system_package
runtime: wsl2 + packet_capture
worker: PacketWorker
perm: ACTIVE_SENSITIVE
fields: wireguard_profile, peer_profile, capture_profile, validation_profile, timeout_seconds, evidence_profile
adapter: WireGuardCaptureAdapter
success_evidence: handshake_observation, peer_metadata_summary, pcap_reference
notes_extra: handshake_detection_default=true, offline_bruteforce_low_viability=true, no_private_keys_in_docs=true

#### Hermes

Puede crear wrappers, parsers de ike/openvpn/wireguard, schemas de evidence, panel_fields y fixtures demo en sandbox con target_path real. No ejecuta técnicas reales ni promociona sin aprobación.

#### Nota futura

future_submodule_reference: 11f_rfid_nfc
required_hardware: ACR122U
not_hackrf_compatible: true
No crear 11f en esta ronda.

## Estado documental del módulo

Módulo 6 queda documentado con técnicas 1-34.
Módulo 6 — Red y Man-in-the-Middle queda documentado como catálogo técnico de conexiones, workers, adapters, hooks, evidence y estado de implementación.
Las técnicas quedan marcadas como IMPLEMENTACION_USUARIO_REQUERIDA.
LaIA rellena contexto y analiza evidencia.
X5/OjoRouter valida scope, permisos, inputs, worker, evidence y confirmación.
Hermes solo crea wrappers, parsers o schemas en sandbox si falta una pieza.
Este documento no contiene comandos operativos, payloads, PoC ni guías paso a paso.
