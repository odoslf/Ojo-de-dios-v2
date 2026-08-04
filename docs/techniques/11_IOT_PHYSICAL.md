# MÓDULO 11 — IOT Y DISPOSITIVOS FÍSICOS

Catálogo declarativo de conexiones. Sin código, comandos, tests, requirements, payloads, credenciales reales, configuraciones funcionales ni pasos operativos.

module_id: iot_physical
panel: IoT & Dispositivos Físicos
status_default: IMPLEMENTACION_USUARIO_REQUERIDA
docker_allowed: false
runtime_preferente: windows_python + wsl2_kali
install_profile: kali-linux-large_or_toolhealth
toolhealth: check_binary_version_service_and_device
versionlock: resolve_real_version_in_environment
storage: SQLite + EvidenceStore
workers: IoTWorker, CameraWorker, PrinterWorker, DomoticsWorker, RouterNasWorker, WSLWorker, WindowsWorker, PythonToolWorker, BrowserWorker, EvidenceWorker, AIWorker

## Regla operativa del módulo

Ojo de Dios centraliza detección, clasificación, panel, evidence y report.
LaIA/Mistral clasifica dispositivo, prioriza técnicas, genera plan JSON, analiza progreso y propone fallback.
X5/OjoRouter valida scope, permisos, worker, toolhealth, evidence, confirmación y ejecuta la lógica privada conectada por el usuario.
Hermes crea wrappers, parsers, schemas, fingerprints, terminal helpers y panel_fields en sandbox.
Toda lógica final queda en IMPLEMENTACION_USUARIO_REQUERIDA.

## PARTE 1/6 — FRAMEWORK COMÚN

Regla:
Catálogo declarativo para conexiones, clasificación, panel, contratos JSON, evidence, terminal virtual y estados.
Sin comandos, tests, requirements, payloads, credenciales reales, configuración funcional ni lógica de explotación.

## Panel principal IoT

tabs: Todos, Cámaras, Impresoras, Domótica, Routers/NAS
columns: tipo, ip, fabricante, modelo, estado, ultima_evidencia
detail_views: camera_detail, printer_detail, domotics_detail, router_nas_detail
actions: analizar, ataque_inteligente, ejecutar_tecnica, abrir_terminal_virtual, ver_evidencia, generar_informe

## Clasificador IoT

inputs: host, ip, mac, ports, services, banners, http_titles, snmp_oids, mdns_ssdp, module1_fingerprint
outputs: device_type, vendor, model, confidence, route_to_panel
routes:

- camera: ports 554/8000/8999 or Hikvision/Dahua/ONVIF
- printer: ports 9100/515/631/161 or HP/Brother/Xerox/Printer
- domotics: ports 1883/8883/5683 or Hue/Xiaomi/Sonoff/MQTT
- router_nas: ports 22/23/80/443/5000/5001/8080/8443 or Synology/QNAP/DD-WRT/OpenWrt/pfSense

## Contrato Mistral -> X5

mistral_plan_json:

- intent
- device_id
- device_type
- target_profile
- selected_technique
- fallback_chain
- tool_profile
- input_profile
- evidence_expected
- risk_level
- requires_confirmation
- stop_condition
- user_explanation

## Resultado X5 -> Mistral

x5_result_json:

- run_id
- device_id
- technique_id
- status
- evidence_ids
- stdout_reference
- artifact_paths
- summary
- error_code
- next_recommended_techniques

## Estados panel

READY, NO_ACCESS, ACCESS_OBTAINED, ATTACK_RUNNING, HARDWARE_REQUIRED, MISSING_TOOL, CONFIRMATION_REQUIRED, SUCCESS, FAILED, PARTIAL, MANUAL_REQUIRED, STOPPED_BY_KILL_SWITCH

## Evidence común

base_path: evidence/iot/
metadata: device_id, technique_id, timestamp, type, path, hash, summary
types: stream, image, document, config, pcap, screenshot, log, json, csv, mp4
report: iot_block_pdf_report_future

## Terminal virtual

terminal_mode: xtermjs_to_wsl2
default_mode: automatic_x5
terminal_logs: stored_in_evidence
use_case: tools_interactivas_PRET_RouterSploit_Metasploit
human_intervention: allowed_when_mistral_requests_or_user_opens_terminal

## Estado documental de la parte 1

Módulo 11 — IoT y Dispositivos Físicos queda iniciado como framework común documental para detección, clasificación, panel, contratos JSON, evidence, terminal virtual y reportes futuros.
LaIA/Mistral solo clasifica dispositivo, prioriza técnicas, genera plan JSON, analiza progreso y propone fallback.
X5/OjoRouter valida scope, permisos, worker, toolhealth, evidence y confirmación antes de cualquier lógica privada conectada por el usuario.
Hermes solo crea wrappers, parsers, schemas, fingerprints, terminal helpers o panel_fields en sandbox si falta una pieza.
Toda lógica final queda en IMPLEMENTACION_USUARIO_REQUERIDA.

## PARTE 2/6 — CÁMARAS IP Y VIDEOVIGILANCIA

Regla:
Solo documentación de conexiones. Sin código, tests, requirements, comandos, credenciales reales, payloads, configuraciones funcionales ni pasos operativos.

## Panel Cámaras

route: IoT > Cámaras
list_columns: ip, mac, fabricante, modelo, estado, ultima_evidencia
detail_fields: ip, mac, ports, services, rtsp, http, onvif, banner, firmware_guess
actions: analizar, ataque_inteligente, ejecutar_tecnica, abrir_stream, grabar_clip, descargar_evidencia
viewer: html5_or_opencv_bridge
auto_clip: 15s_mp4
states: SIN_ACCESO, ACCESO_OBTENIDO, ATAQUE_EN_CURSO, STREAM_VALIDADO, FALLIDO

## Flujo IA/X5

Mistral recibe fingerprint, prioriza técnicas, estima probabilidad, genera fallback_chain y explica decisión.
X5 valida scope, credenciales, worker, toolhealth, evidence, confirmación y ejecuta lógica privada.
Si hay stream RTSP/ONVIF válido, se activa visor y grabación.
Si falla todo, Mistral propone diccionario específico o análisis de firmware.

## Submódulo 11.1 — Técnicas cámaras

### Común

status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
scope_required: true
requires_confirmation: true
evidence: camera_access_summary, stream_validation_result, screenshot_reference, clip_reference, credential_reference, raw_output_path, normalized_json
graph: CameraNode, RTSPNode, ONVIFNode, CredentialNode, EvidenceNode
notes: catalog_only,user_logic_required,no_commands_in_docs,no_credentials_in_docs
hook: app/modules/iot_physical/<id_sin_iot>.py::<ClasePascal>Technique.execute

### Técnicas

#### 1. iot.camera.fingerprint

tool: Nmap NSE + WhatWeb + ML local
version: Nmap 7.99 + latest-release-lock
runtime: wsl2_or_python
worker: CameraWorker
perm: PASSIVE
adapter: CameraFingerprintAdapter
hook: app/modules/iot_physical/camera_fingerprint.py::CameraFingerprintTechnique.execute

#### 2. iot.camera.rtsp_discovery

tool: Cameradar
version: v6.1.1
runtime: wsl2_or_windows_binary
worker: CameraWorker
perm: IOT_ACTIVE
adapter: CameradarAdapter
hook: app/modules/iot_physical/camera_rtsp_discovery.py::CameraRtspDiscoveryTechnique.execute

#### 3. iot.camera.onvif_discovery

tool: onvif-zeep
version: 0.2.12
runtime: python_lib
worker: CameraWorker
perm: IOT_ACTIVE
adapter: OnvifAdapter
hook: app/modules/iot_physical/camera_onvif_discovery.py::CameraOnvifDiscoveryTechnique.execute
notes_extra: legacy_review_required=true

#### 4. iot.camera.hydra_rtsp_http

tool: Hydra
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: CREDENTIALS
adapter: CameraHydraAdapter
hook: app/modules/iot_physical/camera_hydra_rtsp_http.py::CameraHydraRtspHttpTechnique.execute

#### 5. iot.camera.metasploit_camera_modules

tool: Metasploit Framework
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: IOT_SENSITIVE
adapter: MetasploitCameraAdapter
hook: app/modules/iot_physical/camera_metasploit_camera_modules.py::CameraMetasploitCameraModulesTechnique.execute

#### 6. iot.camera.python_rtsp_validate

tool: OpenCV
version: 4.13.0.92
runtime: windows_python
worker: CameraWorker
perm: IOT_ACTIVE
adapter: OpenCvRtspAdapter
hook: app/modules/iot_physical/camera_python_rtsp_validate.py::CameraPythonRtspValidateTechnique.execute

#### 7. iot.camera.stream_viewer

tool: OpenCV/HTML5 bridge
version: 4.13.0.92
runtime: windows_python
worker: CameraWorker
perm: IOT_ACTIVE
adapter: CameraViewerAdapter
hook: app/modules/iot_physical/camera_stream_viewer.py::CameraStreamViewerTechnique.execute

#### 8. iot.camera.clip_recorder

tool: OpenCV writer
version: 4.13.0.92
runtime: windows_python
worker: EvidenceWorker
perm: PASSIVE
adapter: CameraClipEvidenceAdapter
hook: app/modules/iot_physical/camera_clip_recorder.py::CameraClipRecorderTechnique.execute

#### 9. iot.camera.firmware_cve_lookup

tool: CVE KB + Mistral
version: internal
runtime: local_ai
worker: AIWorker
perm: PASSIVE
adapter: CameraFirmwareCveAdapter
hook: app/modules/iot_physical/camera_firmware_cve_lookup.py::CameraFirmwareCveLookupTechnique.execute

## Evidence cámaras

store_path: evidence/iot/cameras/
artifacts: screenshot_png, clip_mp4_15s, stream_metadata_json, credentials_redacted_json, attack_log_txt
db_links: device_id, technique_id, run_id, evidence_ids

## Estado documental de la parte 2

Módulo 11 — Cámaras IP y Videovigilancia queda documentado como catálogo de conexiones para panel de cámaras, flujo IA/X5, técnicas, evidence y artefactos.
Las 9 técnicas de cámaras quedan marcadas como IMPLEMENTACION_USUARIO_REQUERIDA.
Mistral solo prioriza, estima probabilidad, genera fallback_chain, explica decisión y analiza resultados.
X5/OjoRouter valida scope, credenciales, worker, toolhealth, evidence y confirmación antes de ejecutar lógica privada conectada por el usuario.
Si hay stream RTSP/ONVIF válido, el panel puede activar visor y grabación como capacidad documental futura.

## PARTE 3/6 — IMPRESORAS Y MULTIFUNCIONES

Regla:
Solo documentación de conexiones. Sin código, tests, requirements, comandos, credenciales reales, contenido de documentos, payloads, configuraciones funcionales ni pasos operativos.

## Panel Impresoras

route: IoT > Impresoras
list_columns: ip, mac, fabricante, modelo, estado, ultima_evidencia
detail_fields: ip, mac, ports, services, raw_9100, lpd, ipp, snmp, http, banner
actions: analizar, ataque_inteligente, ejecutar_tecnica, imprimir_prueba, cambiar_lcd, volcar_config, ver_trabajos, captura_panel, abrir_terminal_virtual
states: SIN_ACCESO, ACCESO_OBTENIDO, ATAQUE_EN_CURSO, EVIDENCIA_CONFIRMADA, FALLIDO

## Flujo IA/X5

Mistral clasifica fabricante/modelo, prioriza técnicas, estima éxito, genera fallback_chain y explica riesgo.
X5 valida scope, worker, toolhealth, credenciales, confirmation_profile y evidence.
Si hay acceso, se habilitan acciones del panel y se guarda prueba tangible.

## Submódulo 11.2 — Técnicas impresoras

### Común

status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
scope_required: true
requires_confirmation: true
evidence: printer_access_summary, config_snapshot_reference, printed_test_reference, lcd_change_reference, job_artifact_reference, screenshot_reference, raw_output_path, normalized_json
graph: PrinterNode, PJLNode, IPPNode, SNMPNode, CredentialNode, EvidenceNode
notes: catalog_only,user_logic_required,no_commands_in_docs,no_credentials_in_docs,no_document_contents_in_docs
hook: app/modules/iot_physical/<id_sin_iot>.py::<ClasePascal>Technique.execute

### Técnicas

#### 10. iot.printer.fingerprint

tool: Nmap NSE + HTTP/SNMP parser
version: Nmap 7.99 + internal
runtime: wsl2_or_python
worker: PrinterWorker
perm: PASSIVE
adapter: PrinterFingerprintAdapter
hook: app/modules/iot_physical/printer_fingerprint.py::PrinterFingerprintTechnique.execute

#### 11. iot.printer.pret_control

tool: PRET
version: latest-release-lock
runtime: wsl2
worker: PrinterWorker
perm: IOT_SENSITIVE
adapter: PretAdapter
hook: app/modules/iot_physical/printer_pret_control.py::PrinterPretControlTechnique.execute
notes_extra: terminal_virtual_supported=true

#### 12. iot.printer.pjl_actions

tool: PJL/internal connector
version: internal
runtime: python_lib
worker: PrinterWorker
perm: IOT_SENSITIVE
adapter: PjlAdapter
hook: app/modules/iot_physical/printer_pjl_actions.py::PrinterPjlActionsTechnique.execute

#### 13. iot.printer.ipp_assessment

tool: IPP/internal connector
version: internal
runtime: python_lib
worker: PrinterWorker
perm: IOT_ACTIVE
adapter: IppAdapter
hook: app/modules/iot_physical/printer_ipp_assessment.py::PrinterIppAssessmentTechnique.execute

#### 14. iot.printer.snmp_config_dump

tool: Net-SNMP + pysnmp
version: 5.9.4 + 7.1.27
runtime: wsl2_or_python
worker: WSLWorker
perm: IOT_ACTIVE
adapter: SnmpPrinterAdapter
hook: app/modules/iot_physical/printer_snmp_config_dump.py::PrinterSnmpConfigDumpTechnique.execute

#### 15. iot.printer.hydra_web_panel

tool: Hydra
version: latest-release-lock
baseline: 9.6
runtime: wsl2
worker: WSLWorker
perm: CREDENTIALS
adapter: PrinterHydraAdapter
hook: app/modules/iot_physical/printer_hydra_web_panel.py::PrinterHydraWebPanelTechnique.execute

#### 16. iot.printer.metasploit_auxiliary

tool: Metasploit Framework
version: 6.4.131
runtime: wsl2
worker: WSLWorker
perm: IOT_SENSITIVE
adapter: MetasploitPrinterAdapter
hook: app/modules/iot_physical/printer_metasploit_auxiliary.py::PrinterMetasploitAuxiliaryTechnique.execute

#### 17. iot.printer.web_admin_capture

tool: Browser automation
version: Playwright latest-release-lock
runtime: windows_python
worker: BrowserWorker
perm: PASSIVE
adapter: PrinterWebCaptureAdapter
hook: app/modules/iot_physical/printer_web_admin_capture.py::PrinterWebAdminCaptureTechnique.execute

#### 18. iot.printer.evidence_test_page

tool: PDF generator/internal
version: internal
runtime: python_lib
worker: EvidenceWorker
perm: IOT_ACTIVE
adapter: PrinterTestPageAdapter
hook: app/modules/iot_physical/printer_evidence_test_page.py::PrinterEvidenceTestPageTechnique.execute

## Evidence impresoras

store_path: evidence/iot/printers/
artifacts: test_page_pdf, panel_screenshot_png, config_json_csv, job_artifact_reference, lcd_proof_reference, attack_log_txt
db_links: device_id, technique_id, run_id, evidence_ids
redaction: redact_credentials_and_document_contents=true

## Estado documental de la parte 3

Módulo 11 — Impresoras y Multifunciones queda documentado como catálogo de conexiones para panel de impresoras, flujo IA/X5, técnicas, evidence y redacción de contenido sensible.
Las técnicas 10 a 18 quedan marcadas como IMPLEMENTACION_USUARIO_REQUERIDA.
Mistral solo clasifica fabricante/modelo, prioriza técnicas, estima éxito, genera fallback_chain y explica riesgo.
X5/OjoRouter valida scope, worker, toolhealth, credenciales, confirmation_profile y evidence antes de ejecutar lógica privada conectada por el usuario.
Si hay acceso, el panel puede habilitar acciones y guardar prueba tangible como capacidad documental futura.

## PARTE 4/6 — DOMÓTICA, MQTT, HTTP, COAP Y BLE

Regla:
Solo documentación de conexiones. Sin código, tests, requirements, comandos, credenciales reales, payloads, configuraciones funcionales ni pasos operativos.

## Panel Domótica

route: IoT > Domótica
list_columns: ip, mac, tipo, fabricante, modelo, estado, ultima_evidencia
detail_fields: ip, mac, ports, services, mqtt, coap, http_api, ble, mdns_ssdp, banner
controls: on_off, color, brightness, plug_power, energy_reading, thermostat_temp, hvac_mode
actions: analizar, ataque_inteligente, ejecutar_tecnica, control_dispositivo, capturar_pcap, ver_estado_antes_despues
states: SIN_ACCESO, CONTROL_OBTENIDO, ATAQUE_EN_CURSO, ESTADO_VALIDADO, FALLIDO

## Flujo IA/X5

Mistral identifica tipo de dispositivo, protocolo dominante, técnica inicial y fallback_chain.
X5 valida scope, worker, toolhealth, confirmation_profile, estado antes/después y evidence.
Si hay control real, el panel muestra controles físicos y registra respuesta del dispositivo.

## Submódulo 11.3 — Técnicas domótica

### Común

status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
scope_required: true
requires_confirmation: true
evidence: domotics_access_summary, state_before_after, command_response_summary, pcap_reference, screenshot_or_video_reference, raw_output_path, normalized_json
graph: IoTDeviceNode, MQTTNode, CoAPNode, BLENode, StateChangeNode, EvidenceNode
notes: catalog_only,user_logic_required,no_commands_in_docs,no_credentials_in_docs
hook: app/modules/iot_physical/<id_sin_iot>.py::<ClasePascal>Technique.execute

### Técnicas

#### 19. iot.domotics.fingerprint

tool: Nmap NSE + mDNS/SSDP + ML local
version: Nmap 7.99 + internal
runtime: wsl2_or_python
worker: DomoticsWorker
perm: PASSIVE
adapter: DomoticsFingerprintAdapter
hook: app/modules/iot_physical/domotics_fingerprint.py::DomoticsFingerprintTechnique.execute

#### 20. iot.domotics.mqtt_open_broker

tool: paho-mqtt
version: 2.1.0
runtime: python_lib
worker: DomoticsWorker
perm: IOT_ACTIVE
adapter: MqttBrokerAdapter
hook: app/modules/iot_physical/domotics_mqtt_open_broker.py::DomoticsMqttOpenBrokerTechnique.execute

#### 21. iot.domotics.mqtt_topic_inventory

tool: paho-mqtt
version: 2.1.0
runtime: python_lib
worker: DomoticsWorker
perm: IOT_ACTIVE
adapter: MqttTopicInventoryAdapter
hook: app/modules/iot_physical/domotics_mqtt_topic_inventory.py::DomoticsMqttTopicInventoryTechnique.execute

#### 22. iot.domotics.mqtt_control

tool: paho-mqtt
version: 2.1.0
runtime: python_lib
worker: DomoticsWorker
perm: IOT_SENSITIVE
adapter: MqttControlAdapter
hook: app/modules/iot_physical/domotics_mqtt_control.py::DomoticsMqttControlTechnique.execute
notes_extra: state_change_required=true

#### 23. iot.domotics.http_api_control

tool: requests
version: 2.34.2
runtime: python_lib
worker: DomoticsWorker
perm: IOT_SENSITIVE
adapter: HttpApiControlAdapter
hook: app/modules/iot_physical/domotics_http_api_control.py::DomoticsHttpApiControlTechnique.execute
notes_extra: state_change_required=true

#### 24. iot.domotics.coap_probe

tool: CoAP client/internal
version: latest-release-lock
runtime: python_lib
worker: DomoticsWorker
perm: IOT_ACTIVE
adapter: CoapProbeAdapter
hook: app/modules/iot_physical/domotics_coap_probe.py::DomoticsCoapProbeTechnique.execute

#### 25. iot.domotics.ble_enum

tool: Bleak
version: 3.0.2
runtime: python_lib
worker: DomoticsWorker
perm: BLE_ACTIVE
adapter: BleakDomoticsAdapter
hook: app/modules/iot_physical/domotics_ble_enum.py::DomoticsBleEnumTechnique.execute

#### 26. iot.domotics.ble_control

tool: Bleak
version: 3.0.2
runtime: python_lib
worker: DomoticsWorker
perm: BLE_SENSITIVE
adapter: BleControlAdapter
hook: app/modules/iot_physical/domotics_ble_control.py::DomoticsBleControlTechnique.execute
notes_extra: state_change_required=true

#### 27. iot.domotics.hydra_web_panel

tool: Hydra
version: latest-release-lock
baseline: 9.6
runtime: wsl2
worker: WSLWorker
perm: CREDENTIALS
adapter: DomoticsHydraAdapter
hook: app/modules/iot_physical/domotics_hydra_web_panel.py::DomoticsHydraWebPanelTechnique.execute

#### 28. iot.domotics.metasploit_iot_aux

tool: Metasploit Framework
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: IOT_SENSITIVE
adapter: MetasploitIoTAdapter
hook: app/modules/iot_physical/domotics_metasploit_iot_aux.py::DomoticsMetasploitIotAuxTechnique.execute

#### 29. iot.domotics.tcpdump_mqtt_pcap

tool: tcpdump
version: system_package
runtime: wsl2
worker: WSLWorker
perm: PASSIVE
adapter: TcpdumpMqttAdapter
hook: app/modules/iot_physical/domotics_tcpdump_mqtt_pcap.py::DomoticsTcpdumpMqttPcapTechnique.execute

## Evidence domótica

store_path: evidence/iot/domotics/
artifacts: state_before_after_json, pcap_30s, command_response_json, video_or_photo_reference, attack_log_txt
db_links: device_id, technique_id, run_id, evidence_ids
validation: state_change_or_protocol_response_required=true

## Estado documental de la parte 4

Módulo 11 — Domótica, MQTT, HTTP, CoAP y BLE queda documentado como catálogo de conexiones para panel de domótica, flujo IA/X5, técnicas, evidence y validación de estado antes/después.
Las técnicas 19 a 29 quedan marcadas como IMPLEMENTACION_USUARIO_REQUERIDA.
Mistral solo identifica tipo de dispositivo, protocolo dominante, técnica inicial, fallback_chain y analiza resultados.
X5/OjoRouter valida scope, worker, toolhealth, confirmation_profile, estado antes/después y evidence antes de ejecutar lógica privada conectada por el usuario.
Si hay control real, el panel puede mostrar controles físicos y registrar respuesta del dispositivo como capacidad documental futura.

## PARTE 5/6 — ROUTERS, NAS Y ALMACENAMIENTO EN RED

Regla:
Solo documentación de conexiones. Sin código, tests, requirements, comandos, credenciales reales, contenidos privados de configuración, payloads, configuraciones funcionales ni pasos operativos.

## Panel Routers/NAS

route: IoT > Routers/NAS
list_columns: ip, mac, tipo, fabricante, modelo, estado, ultima_evidencia
detail_fields: ip, mac, ports, services, ssh, telnet, http_admin, snmp, nas_panel, banner, firmware_guess
actions: analizar, ataque_inteligente, ejecutar_tecnica, capturar_panel, volcar_config, extraer_wifi_info, prueba_nas_archivo, abrir_terminal_virtual
states: SIN_ACCESO, ACCESO_ADMIN, ATAQUE_EN_CURSO, EVIDENCIA_CONFIRMADA, FALLIDO

## Flujo IA/X5

Mistral identifica router/NAS, prioriza técnica, consulta CVE KB, estima probabilidad y genera fallback_chain.
X5 valida scope, credenciales, worker, toolhealth, confirmation_profile, EvidenceStore y cambios permitidos.
Si hay acceso admin, se habilita panel de evidencia y acciones específicas.

## Submódulo 11.4 — Técnicas Routers/NAS

### Común

status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
scope_required: true
requires_confirmation: true
evidence: router_nas_access_summary, admin_screenshot_reference, config_dump_reference, wifi_secret_reference, nas_file_proof_reference, raw_output_path, normalized_json
graph: RouterNode, NASNode, SNMPNode, AdminPanelNode, ConfigArtifactNode, EvidenceNode
notes: catalog_only,user_logic_required,no_commands_in_docs,no_credentials_in_docs,no_config_contents_in_docs
hook: app/modules/iot_physical/<id_sin_iot>.py::<ClasePascal>Technique.execute

### Técnicas

#### 30. iot.router_nas.fingerprint

tool: Nmap NSE + HTTP/SNMP parser
version: Nmap 7.99 + internal
runtime: wsl2_or_python
worker: RouterNasWorker
perm: PASSIVE
adapter: RouterNasFingerprintAdapter
hook: app/modules/iot_physical/router_nas_fingerprint.py::RouterNasFingerprintTechnique.execute

#### 31. iot.router_nas.routersploit_autopwn

tool: RouterSploit
version: latest-release-lock
runtime: wsl2
worker: RouterNasWorker
perm: IOT_SENSITIVE
adapter: RouterSploitAdapter
hook: app/modules/iot_physical/router_nas_routersploit_autopwn.py::RouterNasRoutersploitAutopwnTechnique.execute
notes_extra: terminal_virtual_supported=true

#### 32. iot.router_nas.hydra_admin_login

tool: Hydra
version: latest-release-lock
baseline: 9.6
runtime: wsl2
worker: WSLWorker
perm: CREDENTIALS
adapter: RouterNasHydraAdapter
hook: app/modules/iot_physical/router_nas_hydra_admin_login.py::RouterNasHydraAdminLoginTechnique.execute

#### 33. iot.router_nas.metasploit_modules

tool: Metasploit Framework
version: 6.4.131
runtime: wsl2
worker: WSLWorker
perm: IOT_SENSITIVE
adapter: MetasploitRouterNasAdapter
hook: app/modules/iot_physical/router_nas_metasploit_modules.py::RouterNasMetasploitModulesTechnique.execute

#### 34. iot.router_nas.snmp_config_audit

tool: Net-SNMP + pysnmp
version: 5.9.4 + 7.1.27
runtime: wsl2_or_python
worker: WSLWorker
perm: IOT_ACTIVE
adapter: SnmpRouterNasAdapter
hook: app/modules/iot_physical/router_nas_snmp_config_audit.py::RouterNasSnmpConfigAuditTechnique.execute

#### 35. iot.router_nas.ssh_paramiko_admin

tool: Paramiko
version: latest-release-lock
runtime: python_lib
worker: RouterNasWorker
perm: CREDENTIALS
adapter: ParamikoSshAdapter
hook: app/modules/iot_physical/router_nas_ssh_paramiko_admin.py::RouterNasSshParamikoAdminTechnique.execute

#### 36. iot.router_nas.telnet_assessment

tool: Telnet/internal connector
version: internal
runtime: python_lib
worker: RouterNasWorker
perm: CREDENTIALS
adapter: TelnetRouterAdapter
hook: app/modules/iot_physical/router_nas_telnet_assessment.py::RouterNasTelnetAssessmentTechnique.execute

#### 37. iot.router_nas.web_admin_capture

tool: Browser automation
version: Playwright latest-release-lock
runtime: windows_python
worker: BrowserWorker
perm: PASSIVE
adapter: RouterNasWebCaptureAdapter
hook: app/modules/iot_physical/router_nas_web_admin_capture.py::RouterNasWebAdminCaptureTechnique.execute

#### 38. iot.router_nas.config_dump

tool: HTTP/SNMP/SSH connector
version: internal
runtime: python_lib
worker: RouterNasWorker
perm: IOT_SENSITIVE
adapter: ConfigDumpAdapter
hook: app/modules/iot_physical/router_nas_config_dump.py::RouterNasConfigDumpTechnique.execute

#### 39. iot.router_nas.wifi_secret_extract

tool: Config parser/internal
version: internal
runtime: python_lib
worker: RouterNasWorker
perm: CREDENTIALS
adapter: WifiSecretExtractAdapter
hook: app/modules/iot_physical/router_nas_wifi_secret_extract.py::RouterNasWifiSecretExtractTechnique.execute

#### 40. iot.router_nas.nas_file_proof

tool: SMB/HTTP/WebDAV connector
version: internal
runtime: python_lib
worker: RouterNasWorker
perm: IOT_ACTIVE
adapter: NasFileProofAdapter
hook: app/modules/iot_physical/router_nas_nas_file_proof.py::RouterNasNasFileProofTechnique.execute

## Evidence Routers/NAS

store_path: evidence/iot/router_nas/
artifacts: admin_screenshot_png, config_json_xml_csv, wifi_secret_redacted_json, nas_file_proof_reference, attack_log_txt
db_links: device_id, technique_id, run_id, evidence_ids
redaction: redact_passwords_tokens_and_private_config=true
validation: admin_access_or_config_or_file_proof_required=true

## Estado documental de la parte 5

Módulo 11 — Routers, NAS y Almacenamiento en Red queda documentado como catálogo de conexiones para panel Routers/NAS, flujo IA/X5, técnicas, evidence y redacción de configuración sensible.
Las técnicas 30 a 40 quedan marcadas como IMPLEMENTACION_USUARIO_REQUERIDA.
Mistral solo identifica router/NAS, prioriza técnica, consulta CVE KB, estima probabilidad, genera fallback_chain y analiza resultados.
X5/OjoRouter valida scope, credenciales, worker, toolhealth, confirmation_profile, EvidenceStore y cambios permitidos antes de ejecutar lógica privada conectada por el usuario.
Si hay acceso admin, el panel puede habilitar evidence y acciones específicas como capacidad documental futura.

## PARTE 6/6 — CIERRE OPERATIVO DEL BLOQUE IOT

Regla:
Solo documentación de conexiones y contratos operativos. No código, tests, requirements, comandos, payloads, credenciales reales, contenidos privados ni cambios en otros módulos.

## Contrato operativo común

Cada técnica del Módulo 11 debe quedar conectada a:

- panel específico;
- device_id;
- technique_id;
- worker;
- adapter;
- hook;
- ToolHealth;
- VersionLock;
- EvidenceStore;
- ScoringEngine;
- Attack Surface Graph;
- Mistral plan JSON;
- X5 result JSON;
- Hermes sandbox proposal si falta pieza.

No cambiar nombres de técnicas ya documentadas.
No crear código.
No crear tests.
No tocar otros módulos.

## Modo Ataque Inteligente

Flujo:

1. usuario pulsa Ataque Inteligente;
2. Mistral lee device_profile, fingerprint, evidence previa y scoring;
3. genera fallback_chain ordenada;
4. X5 valida scope, permisos, toolhealth, confirmación y worker;
5. X5 ejecuta técnica conectada por el usuario;
6. se guarda EvidenceStore;
7. Mistral analiza resultado;
8. si falla, pasa a siguiente técnica;
9. si obtiene evidencia real, marca acceso/control/evidencia confirmada;
10. genera resumen final.

## Scoring X5 IoT

Guardar por ejecución:

- device_type
- vendor
- model
- technique_id
- tool_id
- worker
- adapter
- status
- runtime_seconds
- evidence_quality
- access_obtained
- control_obtained
- error_code
- next_recommended_techniques

Scoring:

- SUCCESS con evidence real sube.
- PARTIAL con evidence útil sube poco.
- FAILED baja.
- MISSING_TOOL no bloquea módulo, marca ToolHealth.
- HARDWARE_REQUIRED desactiva técnica en panel.
- MANUAL_REQUIRED no se considera fallo.

## Hermes Agent Lab

Hermes puede proponer en sandbox:

- wrapper de herramienta;
- parser de salida;
- schema de evidence;
- panel_fields;
- hardware/service probe;
- fixture demo;
- adapter;
- documentación de integración;
- mejora de scoring.

Estados Hermes:
draft, designed, generated, tested, review_required, approved_by_user, promoted, rejected, archived.

Hermes no puede:

- ejecutar técnica real;
- tocar producción directamente;
- autoaprobarse;
- eliminar IMPLEMENTACION_USUARIO_REQUERIDA;
- marcar stub como funcional;
- inventar evidencia.

## Evidence común IoT

Ruta:
evidence/iot/

Subrutas:

- cameras/
- printers/
- domotics/
- router_nas/

Tipos:

- stream_mp4
- screenshot_png
- printed_pdf
- config_json
- config_xml
- config_csv
- pcap
- log_txt
- state_before_after_json
- credential_reference_redacted
- admin_panel_capture
- nas_file_proof_reference

Toda evidencia debe enlazar:
device_id, run_id, technique_id, timestamp, hash, path, summary, quality.

## Informe final IoT

El informe debe incluir:

- dispositivos detectados;
- clasificación;
- técnicas probadas;
- herramientas usadas;
- evidencias conseguidas;
- accesos o control obtenidos;
- fallos;
- recomendaciones defensivas;
- export JSON/PDF futuro.

## Estado documental del módulo

Módulo 11 queda documentado con técnicas 1-45 e incluye RFID/NFC ACR122U.
La lógica privada queda en IMPLEMENTACION_USUARIO_REQUERIDA.
Las conexiones, hooks, adapters, paneles, evidence y contratos quedan definidos para programación futura.

## ANEXO — HERMES LAB: PROPUESTA, VERIFICACIÓN Y PROMOCIÓN

Este anexo aclara cómo debe funcionar Hermes cuando falta una pieza en el Módulo 11.

Objetivo:
El usuario no debe copiar archivos manualmente ni revisar código línea por línea.
El usuario solo debe decidir:

- aprobar;
- rechazar;
- pedir cambios.

## Flujo oficial

Hermes propone.
Mistral revisa.
X5/OjoRouter valida.
Tests estructurales confirman.
El usuario aprueba.
El sistema promociona automáticamente al destino correcto.

## Sandbox Hermes

Hermes trabaja dentro del propio proyecto, en una zona segura:

storage/hermes_lab/proposals/
storage/hermes_lab/generated/
storage/hermes_lab/tests/

Cada propuesta debe incluir:

- proposal_id
- module_id: iot_physical
- device_family: cameras|printers|domotics|router_nas
- missing_piece_type: wrapper|parser|schema|adapter|hardware_probe|panel_field|fixture|doc
- target_path
- target_adapter
- target_technique
- target_panel
- target_evidence_schema
- generated_files
- tests
- diff_preview
- mistral_review
- x5_validation
- risk_summary
- promotion_status

## Regla de destino real

Hermes nunca debe generar archivos sueltos sin destino.

Toda propuesta debe declarar exactamente dónde irá si se aprueba:

target_path: app/modules/iot_physical/...
target_panel: camera_detail|printer_detail|domotics_detail|router_nas_detail
target_adapter: nombre_adapter
target_schema: nombre_schema
target_worker: worker_objetivo

## Revisión Mistral

Mistral debe comprobar:

- que la propuesta encaja con el Módulo 11;
- que respeta TechniqueRegistry;
- que mantiene IMPLEMENTACION_USUARIO_REQUERIDA cuando hay lógica privada;
- que no inventa evidence;
- que no rompe panel, adapters, workers ni schemas;
- que explica al usuario qué mejora aporta.

Resultado:
mistral_review_status: approved_candidate|needs_changes|rejected

## Validación X5/OjoRouter

X5 debe comprobar:

- scope;
- permisos;
- worker;
- adapter;
- ToolHealth;
- VersionLock;
- EvidenceStore;
- estados;
- kill switch si aplica;
- que el stub no se marca como funcional sin lógica real.

Resultado:
x5_validation_status: valid|invalid|manual_required

## Tests estructurales

Antes de pedir aprobación al usuario, deben pasar:

- import si aplica;
- schema válido;
- panel field válido;
- evidence contract válido;
- registry contract válido;
- no stub funcional falso;
- no promoción automática sin aprobación.

## Pantalla de aprobación

El panel debe mostrar:

- proposal_id
- qué falta
- qué generó Hermes
- dónde se instalaría
- qué revisó Mistral
- qué validó X5
- tests pasados/fallidos
- riesgo
- diff_preview
- botones: Aprobar, Rechazar, Pedir cambios

## Promoción automática

Si el usuario aprueba, Ojo de Dios promociona automáticamente desde sandbox al destino real.

El usuario no copia archivos manualmente.

Estados:
draft -> designed -> generated -> tested -> review_required -> approved_by_user -> promoted
draft -> rejected
promoted -> archived

## Prohibiciones

Hermes no puede:

- tocar producción sin aprobación;
- autoaprobarse;
- ejecutar técnicas reales;
- eliminar IMPLEMENTACION_USUARIO_REQUERIDA;
- marcar stubs como funcionales;
- inventar evidence;
- saltarse Mistral;
- saltarse X5;
- pedir al usuario copiar archivos a mano.

## Frase oficial

Hermes crea la pieza en sandbox con destino real declarado.
Mistral revisa.
X5 valida.
El usuario decide sí/no.
Si aprueba, el sistema promociona automáticamente al lugar correcto.

## ANEXO — SUBMÓDULO 11f RFID/NFC CON ACR122U

submodule_id: iot_physical.rfid_nfc
panel: IoT > RFID/NFC
hardware_required: ACR122U
hackrf_compatible: false
missing_hardware_status: HARDWARE_REQUIRED
missing_hardware_message: Lector ACR122U no detectado. Conéctelo al puerto USB para habilitar RFID/NFC.
runtime_preferente: wsl2_kali + windows_python
usb_bridge: usbipd-win
workers: RfidNfcWorker, HardwareWorker, WSLWorker, PythonToolWorker, EvidenceWorker, AIWorker
toolhealth: acr122u_presence, libnfc, mfoc, mfcuk, nfc-tools, nfcpy
versionlock: resolve_real_version_in_environment

### Panel

hardware_indicator: ACR122U verde/rojo
sections: tarjetas_leidas, acciones_tarjeta, evidencia, chat_mistral
card_fields: uid, card_type, ats_atqa_sak, sector_status, last_evidence
actions: leer_uid, crackear_claves, volcar_tarjeta, clonar_tarjeta, emular_tarjeta, ver_evidencia

### Mistral

detecta tipo de tarjeta, prioriza técnica, genera fallback_chain, explica si falta ACR122U y analiza evidence.

### X5

valida hardware_probe, scope, permisos, confirmation_profile, worker, ToolHealth, EvidenceStore y estado de panel.

### Hermes

puede crear wrappers, parsers, schemas, hardware probes y panel_fields en sandbox con target_path real.

### Común

status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
scope_required: true
hardware_probe_required: true
requires_confirmation: true
evidence: rfid_card_summary, key_reference_redacted, dump_reference, emulation_result_summary, access_log_reference, screenshot_reference, raw_output_path, normalized_json
graph: RfidNode, NfcReaderNode, CardNode, SectorNode, CredentialArtifactNode, EvidenceNode
notes: catalog_only,user_logic_required,no_commands_in_docs,no_keys_in_docs,no_dumps_inline_in_docs
hook: app/modules/iot_physical/<id_sin_iot>.py::<ClasePascal>Technique.execute

#### 41. iot.rfid.read_uid

tool: libnfc/nfc-tools + nfcpy
version: libnfc 1.8.0 + nfcpy 1.0.4
runtime: wsl2_or_python
worker: RfidNfcWorker
perm: RFID_PASSIVE
adapter: RfidUidReadAdapter
fields: reader_profile, card_detect_profile, evidence_profile
success_evidence: uid_reference, card_type_summary, hardware_probe_result

#### 42. iot.rfid.mifare_crack_mfoc

tool: mfoc
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: RFID_SENSITIVE
adapter: MfocAdapter
fields: reader_profile, mifare_profile, dictionary_profile, timeout_seconds, evidence_profile
success_evidence: key_reference_redacted, sector_access_summary, dump_reference
notes_extra: kali_package_or_source_review_required=true

#### 43. iot.rfid.mifare_crack_mfcuk

tool: mfcuk
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: RFID_SENSITIVE
adapter: MfcukAdapter
fields: reader_profile, mifare_profile, attack_profile, timeout_seconds, evidence_profile
success_evidence: key_reference_redacted, darkside_result_summary, dump_reference
notes_extra: no_attack_parameters_in_docs=true

#### 44. iot.rfid.clone_card

tool: libnfc/nfc-tools + nfcpy
version: libnfc 1.8.0 + nfcpy 1.0.4
runtime: wsl2_or_python
worker: RfidNfcWorker
perm: RFID_SENSITIVE
adapter: RfidCloneAdapter
fields: reader_profile, source_dump_reference, blank_card_profile, confirmation_profile, evidence_profile
success_evidence: clone_result_summary, written_card_reference, verification_readback

#### 45. iot.rfid.emulate_card

tool: nfcpy
version: 1.0.4
runtime: python_lib
worker: PythonToolWorker
perm: RFID_SENSITIVE
adapter: RfidEmulationAdapter
fields: reader_profile, dump_reference, emulation_profile, lab_reader_profile, evidence_profile
success_evidence: emulation_result_summary, access_log_reference, screenshot_reference

Módulo 11 queda documentado con técnicas 1-45 e incluye RFID/NFC ACR122U.
