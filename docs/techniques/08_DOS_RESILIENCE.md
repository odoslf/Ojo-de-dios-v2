# MÓDULO 8 — DENEGACIÓN DE SERVICIO Y RESILIENCIA

Catálogo declarativo. Sin código, comandos, scripts, tests, requirements, parámetros operativos, payloads, perfiles funcionales ni pasos de ejecución.

module_id: dos_resilience
panel: DoS / Resiliencia
status_default: IMPLEMENTACION_USUARIO_REQUERIDA
docker_allowed: false
runtime_preferente: wsl2_kali
install_profile: kali-linux-large_or_toolhealth
toolhealth: check_binary_and_version
versionlock: resolve_real_version_in_environment
workers: DosWorker, ResilienceWorker, WSLWorker, PythonToolWorker, PacketWorker, HTTPWorker, EvidenceWorker, AIWorker

## Regla operativa del módulo

LaIA/Mistral analiza superficie del Módulo 1, elige prueba, rellena perfiles, define incremento, umbral y parada.
X5/OjoRouter valida scope, allowlist, permisos, worker, inputs, evidence, kill switch y confirmación.
Hermes crea wrappers, parsers, schemas, fixtures y panel_fields en sandbox si falta pieza.
La lógica final queda en IMPLEMENTACION_USUARIO_REQUERIDA.

## Campos comunes

status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
requires_confirmation: true
kill_switch_required: true
scope_required: true
stop_condition_required: true
notes: catalog_only,user_logic_required,no_commands_in_docs,no_parameters_in_docs

## Hook común

app/modules/dos_resilience/<id_sin_dos>.py::<ClasePascal>Technique.execute

## PARTE 1/3 — CAPA 3/4 Y HTTP/1.1

Regla:
Catálogo declarativo para workers, adapters, hooks, evidence y estados.
Sin comandos, parámetros de carga, tasas, volúmenes, payloads, perfiles funcionales ni pasos operativos.

## Submódulo 8.1 — Volumétricos L3/L4

evidence: resilience_summary, packet_loss_summary, traffic_profile_summary, threshold_summary, raw_output_path, normalized_json
graph: TargetNode, ServiceNode, NetworkDosNode, ResilienceFindingNode, EvidenceNode

### Técnicas

#### 1. dos.l34.hping_syn_flood

tool: hping3
version: system_package
runtime: wsl2
worker: WSLWorker
perm: DOS_CONTROLLED
adapter: Hping3Adapter
hook: app/modules/dos_resilience/l34_hping_syn_flood.py::L34HpingSynFloodTechnique.execute
notes_extra: install_profile:kali_toolhealth

#### 2. dos.l34.hping_udp_flood

tool: hping3
version: system_package
runtime: wsl2
worker: WSLWorker
perm: DOS_CONTROLLED
adapter: Hping3Adapter
hook: app/modules/dos_resilience/l34_hping_udp_flood.py::L34HpingUdpFloodTechnique.execute
notes_extra: install_profile:kali_toolhealth

#### 3. dos.l34.hping_icmp_flood

tool: hping3
version: system_package
runtime: wsl2
worker: WSLWorker
perm: DOS_CONTROLLED
adapter: Hping3Adapter
hook: app/modules/dos_resilience/l34_hping_icmp_flood.py::L34HpingIcmpFloodTechnique.execute
notes_extra: install_profile:kali_toolhealth

#### 4. dos.l34.scapy_custom_packets

tool: Scapy
version: 2.7.0
runtime: windows_python_or_wsl2
worker: PacketWorker
perm: DOS_CONTROLLED
adapter: ScapyDosAdapter
hook: app/modules/dos_resilience/l34_scapy_custom_packets.py::L34ScapyCustomPacketsTechnique.execute
notes_extra: custom_packet_profile

#### 5. dos.l34.mhddos_multivector

tool: MHDDoS
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: DOS_CONTROLLED
adapter: MhddosAdapter
hook: app/modules/dos_resilience/l34_mhddos_multivector.py::L34MhddosMultivectorTechnique.execute
notes_extra: versionlock_required

#### 6. dos.l34.incremental_threshold_probe

tool: internal controller
version: internal
runtime: python_lib
worker: DosWorker
perm: DOS_CONTROLLED
adapter: ThresholdProbeAdapter
hook: app/modules/dos_resilience/l34_incremental_threshold_probe.py::L34IncrementalThresholdProbeTechnique.execute
notes_extra: stop_condition_required

## Submódulo 8.2 — Capa 7 HTTP/1.1

evidence: http_status_series, latency_series, connection_state_summary, degradation_graph_reference, raw_output_path, normalized_json
graph: TargetNode, WebServiceNode, HTTPNode, ResilienceFindingNode, EvidenceNode

### Técnicas

#### 7. dos.http1.slowloris

tool: Slowloris
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: DOS_CONTROLLED
adapter: SlowlorisAdapter
hook: app/modules/dos_resilience/http1_slowloris.py::Http1SlowlorisTechnique.execute
notes_extra: low_rate_profile

#### 8. dos.http1.slowhttptest_body

tool: SlowHTTPTest
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: DOS_CONTROLLED
adapter: SlowHttpTestAdapter
hook: app/modules/dos_resilience/http1_slowhttptest_body.py::Http1SlowhttptestBodyTechnique.execute
notes_extra: slow_body_profile

#### 9. dos.http1.slowhttptest_read

tool: SlowHTTPTest
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: DOS_CONTROLLED
adapter: SlowHttpTestAdapter
hook: app/modules/dos_resilience/http1_slowhttptest_read.py::Http1SlowhttptestReadTechnique.execute
notes_extra: slow_read_profile

#### 10. dos.http1.goldeneye_flood

tool: GoldenEye
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: DOS_CONTROLLED
adapter: GoldenEyeAdapter
hook: app/modules/dos_resilience/http1_goldeneye_flood.py::Http1GoldeneyeFloodTechnique.execute
notes_extra: header_profile_required

#### 11. dos.http1.header_profile_ai

tool: Mistral header generator
version: internal
runtime: local_ai
worker: AIWorker
perm: DOS_CONTROLLED
adapter: HeaderProfileAdapter
hook: app/modules/dos_resilience/http1_header_profile_ai.py::Http1HeaderProfileAiTechnique.execute
notes_extra: ai_generated_headers_controlled

#### 12. dos.http1.curl_resilience_monitor

tool: curl + Python monitor
version: system_package
runtime: wsl2_or_python
worker: ResilienceWorker
perm: PASSIVE
adapter: CurlMonitorAdapter
hook: app/modules/dos_resilience/http1_curl_resilience_monitor.py::Http1CurlResilienceMonitorTechnique.execute
notes_extra: monitor_only

## Estado documental de la parte 1

Módulo 8 — Denegación de Servicio y Resiliencia queda iniciado como catálogo técnico declarativo para conexiones, workers, adapters, hooks, evidence y estado de implementación.
Las 12 técnicas de la parte 1 quedan marcadas como IMPLEMENTACION_USUARIO_REQUERIDA.
Todas las técnicas requieren scope, allowlist, confirmación, kill switch, stop condition, validación X5/OjoRouter y evidence útil antes de cualquier implementación futura del usuario.
LaIA/Mistral solo analiza superficie, elige prueba, rellena perfiles y define incremento, umbral y parada.
X5/OjoRouter valida scope, allowlist, permisos, worker, inputs, evidence, kill switch y confirmación.
Hermes solo crea wrappers, parsers, schemas, fixtures o panel_fields en sandbox si falta una pieza.

## PARTE 2/3 — HTTP/2, HTTP/3, REFLEXIÓN Y CDN/WAF

Regla común:
Todas las técnicas mantienen status IMPLEMENTACION_USUARIO_REQUERIDA, docker:false, install_profile:kali-linux-large_or_toolhealth, toolhealth:check_binary_and_version, versionlock:true, requires_confirmation:true, kill_switch_required:true, stop_condition_required:true, scope_required:true, notes:catalog_only,user_logic_required,no_commands_in_docs,no_parameters_in_docs,no_reflector_lists_in_docs.

Hook común:
app/modules/dos_resilience/<id_sin_dos>.py::<ClasePascal>Technique.execute

Regla:
Catálogo declarativo para workers, adapters, hooks, evidence y estados.
Sin comandos, parámetros de carga, tasas, volúmenes, payloads, listas de reflectores, perfiles funcionales ni pasos operativos.

## Submódulo 8.3 — HTTP/2 y HTTP/3 QUIC

evidence: protocol_resilience_summary, stream_state_summary, latency_series, http_status_series, threshold_summary, raw_output_path, normalized_json
graph: TargetNode, WebServiceNode, HTTP2Node, QUICNode, ResilienceFindingNode, EvidenceNode

### Técnicas

#### 13. dos.http2.rapid_reset_probe

tool: Python httpx
version: httpx 0.28.1
runtime: python_lib
worker: HTTPWorker
perm: DOS_CONTROLLED
adapter: Http2RapidResetAdapter
hook: app/modules/dos_resilience/http2_rapid_reset_probe.py::Http2RapidResetProbeTechnique.execute
notes_extra: cve_reference:CVE-2023-44487

#### 14. dos.http2.stream_exhaustion

tool: Python httpx
version: httpx 0.28.1
runtime: python_lib
worker: HTTPWorker
perm: DOS_CONTROLLED
adapter: Http2StreamAdapter
hook: app/modules/dos_resilience/http2_stream_exhaustion.py::Http2StreamExhaustionTechnique.execute
notes_extra: flow_control_profile

#### 15. dos.http2.concurrent_streams_threshold

tool: Python httpx
version: httpx 0.28.1
runtime: python_lib
worker: ResilienceWorker
perm: DOS_CONTROLLED
adapter: Http2ThresholdAdapter
hook: app/modules/dos_resilience/http2_concurrent_streams_threshold.py::Http2ConcurrentStreamsThresholdTechnique.execute
notes_extra: incremental_probe=true

#### 16. dos.http3.quic_flood_probe

tool: Python aioquic
version: aioquic 1.3.0
runtime: python_lib
worker: HTTPWorker
perm: DOS_CONTROLLED
adapter: QuicFloodAdapter
hook: app/modules/dos_resilience/http3_quic_flood_probe.py::Http3QuicFloodProbeTechnique.execute
notes_extra: quic_profile

#### 17. dos.http3.quic_handshake_threshold

tool: Python aioquic
version: aioquic 1.3.0
runtime: python_lib
worker: ResilienceWorker
perm: DOS_CONTROLLED
adapter: QuicThresholdAdapter
hook: app/modules/dos_resilience/http3_quic_handshake_threshold.py::Http3QuicHandshakeThresholdTechnique.execute
notes_extra: incremental_probe=true

## Submódulo 8.4 — Amplificación y reflexión controlada

evidence: amplification_risk_summary, reflection_surface_summary, packet_loss_summary, raw_output_path, normalized_json
graph: TargetNode, ReflectionNode, DNSNode, NTPNode, MemcachedNode, EvidenceNode

### Técnicas

#### 18. dos.reflect.dns_amplification

tool: Scapy
version: 2.7.0
runtime: windows_python_or_wsl2
worker: PacketWorker
perm: DOS_CONTROLLED
adapter: DnsAmplificationAdapter
hook: app/modules/dos_resilience/reflect_dns_amplification.py::ReflectDnsAmplificationTechnique.execute
notes_extra: lab_reflector_profile_only=true

#### 19. dos.reflect.ntp_amplification

tool: Scapy
version: 2.7.0
runtime: windows_python_or_wsl2
worker: PacketWorker
perm: DOS_CONTROLLED
adapter: NtpAmplificationAdapter
hook: app/modules/dos_resilience/reflect_ntp_amplification.py::ReflectNtpAmplificationTechnique.execute
notes_extra: lab_reflector_profile_only=true

#### 20. dos.reflect.mdns_amplification

tool: Scapy
version: 2.7.0
runtime: windows_python_or_wsl2
worker: PacketWorker
perm: DOS_CONTROLLED
adapter: MdnsAmplificationAdapter
hook: app/modules/dos_resilience/reflect_mdns_amplification.py::ReflectMdnsAmplificationTechnique.execute
notes_extra: lab_reflector_profile_only=true

#### 21. dos.reflect.memcached_amplification

tool: Scapy
version: 2.7.0
runtime: windows_python_or_wsl2
worker: PacketWorker
perm: DOS_CONTROLLED
adapter: MemcachedAmplificationAdapter
hook: app/modules/dos_resilience/reflect_memcached_amplification.py::ReflectMemcachedAmplificationTechnique.execute
notes_extra: lab_reflector_profile_only=true

#### 22. dos.reflect.reflection_inventory

tool: internal scanner
version: internal
runtime: python_lib
worker: ResilienceWorker
perm: PASSIVE
adapter: ReflectionInventoryAdapter
hook: app/modules/dos_resilience/reflect_reflection_inventory.py::ReflectReflectionInventoryTechnique.execute
notes_extra: inventory_only=true

## Submódulo 8.5 — CDN/WAF y perfiles de tráfico

evidence: waf_behavior_summary, cdn_response_summary, proxy_route_summary, header_profile_summary, raw_output_path, normalized_json
graph: TargetNode, CDNNode, WAFNode, ProxyNode, HTTPNode, EvidenceNode

### Técnicas

#### 23. dos.waf.tor_proxychains_rotation

tool: Tor + proxychains
version: system_package
runtime: wsl2
worker: WSLWorker
perm: DOS_CONTROLLED
adapter: ProxychainsAdapter
hook: app/modules/dos_resilience/waf_tor_proxychains_rotation.py::WafTorProxychainsRotationTechnique.execute
notes_extra: lab_proxy_profile_only=true

#### 24. dos.waf.socks5_proxy_pool

tool: internal proxy pool
version: internal
runtime: python_lib
worker: HTTPWorker
perm: DOS_CONTROLLED
adapter: SocksProxyPoolAdapter
hook: app/modules/dos_resilience/waf_socks5_proxy_pool.py::WafSocks5ProxyPoolTechnique.execute
notes_extra: authorized_proxy_pool_only=true

#### 25. dos.waf.ai_header_generation

tool: Dolphin Mistral Nemo 12B
version: local_ai
worker: AIWorker
perm: DOS_CONTROLLED
adapter: HeaderProfileAdapter
hook: app/modules/dos_resilience/waf_ai_header_generation.py::WafAiHeaderGenerationTechnique.execute
notes_extra: synthetic_header_profile

#### 26. dos.waf.cookie_variation_profile

tool: Python httpx
version: httpx 0.28.1
runtime: python_lib
worker: HTTPWorker
perm: DOS_CONTROLLED
adapter: CookieProfileAdapter
hook: app/modules/dos_resilience/waf_cookie_variation_profile.py::WafCookieVariationProfileTechnique.execute
notes_extra: no_real_cookies_in_docs

#### 27. dos.waf.cdn_cache_bypass_profile

tool: Python httpx
version: httpx 0.28.1
runtime: python_lib
worker: HTTPWorker
perm: DOS_CONTROLLED
adapter: CdnBehaviorAdapter
hook: app/modules/dos_resilience/waf_cdn_cache_bypass_profile.py::WafCdnCacheBypassProfileTechnique.execute
notes_extra: profile_only=true

#### 28. dos.waf.adaptive_rate_controller

tool: internal controller
version: internal
runtime: python_lib
worker: DosWorker
perm: DOS_CONTROLLED
adapter: AdaptiveRateAdapter
hook: app/modules/dos_resilience/waf_adaptive_rate_controller.py::WafAdaptiveRateControllerTechnique.execute
notes_extra: stop_condition_required

## Estado documental de la parte 2

Módulo 8 — Denegación de Servicio y Resiliencia amplía el catálogo técnico declarativo con HTTP/2, HTTP/3 QUIC, reflexión controlada y perfiles CDN/WAF.
Las técnicas 13 a 28 quedan marcadas como IMPLEMENTACION_USUARIO_REQUERIDA.
Todas las técnicas de la parte 2 mantienen docker:false, install_profile:kali-linux-large_or_toolhealth, toolhealth:check_binary_and_version, versionlock:true, confirmación, kill switch, stop condition, scope requerido y ausencia de comandos, parámetros o listas de reflectores en documentación.
LaIA/Mistral solo analiza superficie, elige prueba, rellena perfiles y define incremento, umbral y parada.
X5/OjoRouter valida scope, allowlist, permisos, worker, inputs, evidence, kill switch y confirmación.
Hermes solo crea wrappers, parsers, schemas, fixtures o panel_fields en sandbox si falta una pieza.

## PARTE 3/3 — MEDICIÓN DE RESILIENCIA Y PANEL

Regla común:
Todas las técnicas mantienen status IMPLEMENTACION_USUARIO_REQUERIDA, docker:false, install_profile:kali-linux-large_or_toolhealth, toolhealth:check_binary_and_version, versionlock:true, scope_required:true, requires_confirmation:true, kill_switch_required:true, stop_condition_required:true, notes:catalog_only,user_logic_required,no_commands_in_docs,no_parameters_in_docs.

Hook común:
app/modules/dos_resilience/<id_sin_dos>.py::<ClasePascal>Technique.execute

Regla:
Catálogo declarativo para workers, adapters, hooks, evidence, medición, panel y estados.
Sin comandos operativos, parámetros destructivos, listas de reflectores, scripts funcionales, perfiles funcionales ni pasos operativos.

## Submódulo 8.6 — Medición y evidencias

evidence: resilience_summary, latency_series, packet_loss_summary, http_status_series, degradation_graph_reference, raw_output_path, normalized_json
graph: TargetNode, ServiceNode, MetricNode, ResilienceFindingNode, EvidenceNode

### Técnicas

#### 29. dos.measure.tshark_packet_loss

tool: tshark
version: system_package
runtime: wsl2
worker: ResilienceWorker
perm: PASSIVE
adapter: TsharkMetricsAdapter
hook: app/modules/dos_resilience/measure_tshark_packet_loss.py::MeasureTsharkPacketLossTechnique.execute
notes_extra: capture_profile

#### 30. dos.measure.curl_http_codes

tool: curl
version: system_package
runtime: wsl2
worker: ResilienceWorker
perm: PASSIVE
adapter: CurlMonitorAdapter
hook: app/modules/dos_resilience/measure_curl_http_codes.py::MeasureCurlHttpCodesTechnique.execute
notes_extra: http_status_monitor

#### 31. dos.measure.python_latency_probe

tool: Python httpx
version: httpx 0.28.1
runtime: python_lib
worker: ResilienceWorker
perm: PASSIVE
adapter: LatencyProbeAdapter
hook: app/modules/dos_resilience/measure_python_latency_probe.py::MeasurePythonLatencyProbeTechnique.execute
notes_extra: latency_series

#### 32. dos.measure.matplotlib_graphs

tool: matplotlib
version: latest-release-lock
runtime: python_lib
worker: EvidenceWorker
perm: PASSIVE
adapter: ResilienceGraphAdapter
hook: app/modules/dos_resilience/measure_matplotlib_graphs.py::MeasureMatplotlibGraphsTechnique.execute
notes_extra: graph_builder

#### 33. dos.measure.threshold_detector

tool: internal controller
version: internal
runtime: python_lib
worker: DosWorker
perm: PASSIVE
adapter: ThresholdDetectorAdapter
hook: app/modules/dos_resilience/measure_threshold_detector.py::MeasureThresholdDetectorTechnique.execute
notes_extra: degradation_threshold

#### 34. dos.measure.stop_condition_guard

tool: internal guard
version: internal
runtime: python_lib
worker: DosWorker
perm: PASSIVE
adapter: StopConditionAdapter
hook: app/modules/dos_resilience/measure_stop_condition_guard.py::MeasureStopConditionGuardTechnique.execute
notes_extra: auto_stop_on_threshold

## Integración LaIA + X5 + Hermes

LaIA/Mistral debe:

- leer servicios expuestos desde Módulo 1 y Attack Surface Graph;
- elegir técnica candidata según protocolo, CDN/WAF y riesgo;
- rellenar target_profile, intensity_profile, header_profile, proxy_profile y stop_condition_profile;
- empezar siempre por medición pasiva y prueba incremental;
- detener si se cumple stop_condition_profile;
- no marcar caída sin evidence.

X5/OjoRouter debe:

- validar scope y allowlist;
- exigir confirmación;
- validar kill switch activo;
- ejecutar worker correcto;
- guardar EvidenceStore;
- registrar métricas y umbral;
- actualizar ScoringEngine y Attack Surface Graph.

Hermes puede proponer en sandbox:

- wrappers de herramientas;
- parsers de tshark/curl/httpx;
- schemas de métricas;
- fixtures demo;
- panel_fields;
- gráficos y exportadores.

Hermes no ejecuta pruebas reales ni promociona sin aprobación.

## Estado documental del módulo

Módulo 8 — DoS y Resiliencia queda documentado como catálogo técnico de pruebas controladas, conexiones, workers, adapters, hooks, evidence, medición, stop conditions, kill switch, LaIA, X5/OjoRouter y Hermes.
El documento no contiene comandos operativos, parámetros destructivos, listas de reflectores ni scripts funcionales.
La lógica privada queda en IMPLEMENTACION_USUARIO_REQUERIDA.
