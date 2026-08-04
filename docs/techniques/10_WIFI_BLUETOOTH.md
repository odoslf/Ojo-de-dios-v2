# MÓDULO 10 — WIFI Y BLUETOOTH

Catálogo declarativo de conexiones. Sin código, comandos, scripts, tests, requirements, parámetros operativos, payloads, credenciales reales ni pasos de ejecución.

module_id: wifi_bluetooth
panel: WiFi / Bluetooth
status_default: IMPLEMENTACION_USUARIO_REQUERIDA
docker_allowed: false
runtime_preferente: wsl2_kali + windows_native
hardware: alfa_monitor_adapter, bluetooth_usb_5_3, hackrf_optional, nrf52840_optional
usb_bridge: usbipd-win
toolhealth: check_binary_version_and_usb_presence
versionlock: resolve_real_version_in_environment
workers: WirelessWorker, BluetoothWorker, HardwareWorker, WSLWorker, WindowsWorker, GPUWorker, PacketWorker, EvidenceWorker, AIWorker

## Regla operativa del módulo

LaIA/Mistral detecta hardware, recomienda técnica, rellena perfiles y analiza evidence.
X5/OjoRouter valida scope, hardware_probe, permisos, confirmación, worker, kill switch y evidence.
Hermes crea wrappers, parsers, schemas, hardware_probes y panel_fields en sandbox.
Cada técnica usa:
hook: app/modules/wifi_bluetooth/<id_sin_prefijo>.py::<ClasePascal>Technique.execute

## Campos comunes

status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
requires_confirmation: true
hardware_probe_required: true
notes: catalog_only,user_logic_required,no_commands_in_docs

## PARTE 1/2 — WIFI 802.11 CON ADAPTADOR ALFA

Regla:
Catálogo declarativo para conexiones, hardware, workers, adapters, hooks, evidence y estados.
Sin comandos, parámetros operativos, payloads, credenciales reales, claves reales, tráfico fuera de scope ni pasos operativos.

## Submódulo 10.1 — WiFi

evidence: wifi_capture_summary, handshake_or_pmkid_reference, client_ap_summary, raw_output_path, normalized_json
graph: WirelessNode, AccessPointNode, ClientDeviceNode, CredentialArtifactNode, EvidenceNode

### Técnicas

#### 1. wifi.handshake_capture

tool: aircrack-ng/airodump-ng
version: 1.7
runtime: wsl2
worker: WSLWorker
perm: WIFI_ACTIVE
adapter: AircrackAdapter
hook: app/modules/wifi_bluetooth/handshake_capture.py::HandshakeCaptureTechnique.execute
notes_extra: alfa_monitor_required=true

#### 2. wifi.pmkid_attack

tool: hcxdumptool+hcxtools+Hashcat
version: latest-release-lock + Hashcat v7.1.2
runtime: wsl2+windows_gpu
worker: GPUWorker
perm: WIFI_ACTIVE
adapter: PmkidHashcatAdapter
hook: app/modules/wifi_bluetooth/pmkid_attack.py::PmkidAttackTechnique.execute
notes_extra: offline_crack=true

#### 3. wifi.evil_twin_airgeddon

tool: Airgeddon
version: v12.0
runtime: wsl2
worker: WSLWorker
perm: WIFI_ACTIVE
adapter: AirgeddonAdapter
hook: app/modules/wifi_bluetooth/evil_twin_airgeddon.py::EvilTwinAirgeddonTechnique.execute
notes_extra: captive_portal_profile_required=true

#### 4. wifi.wpa3_downgrade

tool: Dragonblood profile/internal scripts
version: latest-release-lock
runtime: wsl2
worker: WirelessWorker
perm: WIFI_ACTIVE
adapter: Wpa3DowngradeAdapter
hook: app/modules/wifi_bluetooth/wpa3_downgrade.py::Wpa3DowngradeTechnique.execute
notes_extra: user_logic_required=true

#### 5. wifi.beacon_flood

tool: MDK4
version: 4.2
runtime: wsl2
worker: WSLWorker
perm: WIFI_ACTIVE
adapter: Mdk4Adapter
hook: app/modules/wifi_bluetooth/beacon_flood.py::BeaconFloodTechnique.execute
notes_extra: lab_only=true

#### 6. wifi.deauth_massive

tool: MDK4/aireplay-ng
version: 4.2 + aircrack-ng 1.7
runtime: wsl2
worker: WSLWorker
perm: WIFI_ACTIVE
adapter: DeauthAdapter
hook: app/modules/wifi_bluetooth/deauth_massive.py::DeauthMassiveTechnique.execute
notes_extra: kill_switch_required=true

#### 7. wifi.karma_attack

tool: Bettercap
version: v2.41.7
runtime: wsl2
worker: WSLWorker
perm: WIFI_ACTIVE
adapter: BettercapWifiAdapter
hook: app/modules/wifi_bluetooth/karma_attack.py::KarmaAttackTechnique.execute
notes_extra: known_network_profile_required=true

#### 8. wifi.wps_reaver

tool: Reaver
version: 1.6.6
runtime: wsl2
worker: WSLWorker
perm: WIFI_ACTIVE
adapter: ReaverWpsAdapter
hook: app/modules/wifi_bluetooth/wps_reaver.py::WpsReaverTechnique.execute
notes_extra: wps_only=true

## Hardware WiFi

panel_state_enabled_if: alfa_monitor_adapter_detected=true
panel_message_missing: Requiere adaptador WiFi Alfa en modo monitor conectado por usbipd-win.
evidence_extra: hardware_probe_result, monitor_mode_status, channel_support_summary

## Estado documental de la parte 1

Módulo 10 — WiFi y Bluetooth queda iniciado como catálogo técnico declarativo para conexiones, hardware, workers, adapters, hooks, evidence y estado de implementación.
Las 8 técnicas de la parte 1 quedan marcadas como IMPLEMENTACION_USUARIO_REQUERIDA.
Todas las técnicas requieren scope, hardware_probe, confirmación, worker correcto, kill switch cuando aplique y evidence útil antes de cualquier implementación futura del usuario.
LaIA/Mistral solo detecta hardware, recomienda técnica, rellena perfiles y analiza evidence.
X5/OjoRouter valida scope, hardware_probe, permisos, confirmación, worker, kill switch y evidence.
Hermes solo crea wrappers, parsers, schemas, hardware_probes o panel_fields en sandbox si falta una pieza.

## PARTE 2/2 — BLUETOOTH CLÁSICO, BLE Y HACKRF OPCIONAL

Regla común:
Todas las técnicas mantienen status IMPLEMENTACION_USUARIO_REQUERIDA, docker:false, runtime_preferente:wsl2_kali+windows_native, usb_bridge:usbipd-win, toolhealth:check_binary_version_and_usb_presence, versionlock:true, hardware_probe_required:true, requires_confirmation:true, notes:catalog_only,user_logic_required,no_commands_in_docs,no_payloads_in_docs.

Hook común:
app/modules/wifi_bluetooth/<id_sin_prefijo>.py::<ClasePascal>Technique.execute

Regla:
Catálogo declarativo para Bluetooth clásico, BLE, HackRF opcional, nRF52840 opcional, hardware, workers, adapters, hooks, evidence y estados.
Sin comandos, payloads, parámetros operativos, explotación funcional, claves reales, tráfico fuera de scope ni pasos operativos.

## Submódulo 10.2 — Bluetooth clásico y BLE

evidence: bluetooth_scan_summary, ble_gatt_summary, capture_reference, hardware_probe_result, raw_output_path, normalized_json
graph: BluetoothNode, BLEDeviceNode, GATTServiceNode, HardwareNode, EvidenceNode

### Técnicas

#### 9. bt.a2dp_spoofing

tool: BlueZ
version: system_package
runtime: wsl2
worker: BluetoothWorker
perm: BT_ACTIVE
adapter: BlueZA2DPAdapter
hook: app/modules/wifi_bluetooth/a2dp_spoofing.py::A2dpSpoofingTechnique.execute
notes_extra: bluetooth_usb_5_3_required=true

#### 10. bt.bluebore_exploit

tool: HackRF tools + private scripts
version: 2026.01.3
runtime: wsl2
worker: HardwareWorker
perm: BT_HACKRF
adapter: HackRFBlueborneAdapter
hook: app/modules/wifi_bluetooth/bluebore_exploit.py::BlueboreExploitTechnique.execute
notes_extra: hackrf_required=true,no_exploit_steps_in_docs

#### 11. bt.ble_mitm_gattacker

tool: Gattacker
version: latest-release-lock
runtime: wsl2
worker: BluetoothWorker
perm: BLE_ACTIVE
adapter: GattackerAdapter
hook: app/modules/wifi_bluetooth/ble_mitm_gattacker.py::BleMitmGattackerTechnique.execute
notes_extra: bluetooth_usb_5_3_required=true

#### 12. bt.ble_mitm_btlejuice

tool: BtleJuice
version: latest-release-lock
runtime: wsl2
worker: BluetoothWorker
perm: BLE_ACTIVE
adapter: BtleJuiceAdapter
hook: app/modules/wifi_bluetooth/ble_mitm_btlejuice.py::BleMitmBtlejuiceTechnique.execute
notes_extra: bluetooth_usb_5_3_required=true

#### 13. bt.ble_sniffing

tool: Wireshark + BLE dongle
version: Wireshark 4.6.6
runtime: windows_or_wsl2
worker: PacketWorker
perm: BLE_PASSIVE
adapter: BleSniffAdapter
hook: app/modules/wifi_bluetooth/ble_sniffing.py::BleSniffingTechnique.execute
notes_extra: bluetooth_usb_5_3_required=true

#### 14. bt.ble_enum

tool: Bleak
version: 3.0.2
runtime: python_lib
worker: BluetoothWorker
perm: BLE_ACTIVE
adapter: BleakEnumAdapter
hook: app/modules/wifi_bluetooth/ble_enum.py::BleEnumTechnique.execute
notes_extra: bluetooth_usb_5_3_required=true

#### 15. bt.bluejacking_bluesnarfing

tool: PyBluez
version: 0.23
runtime: python_lib
worker: BluetoothWorker
perm: BT_LEGACY
adapter: PyBluezLegacyAdapter
hook: app/modules/wifi_bluetooth/bluejacking_bluesnarfing.py::BluejackingBluesnarfingTechnique.execute
notes_extra: legacy_review_required=true

#### 16. bt.mousejack

tool: nRF52840 scripts
version: latest-release-lock
runtime: wsl2
worker: HardwareWorker
perm: RF_HID
adapter: MouseJackAdapter
hook: app/modules/wifi_bluetooth/mousejack.py::MouseJackTechnique.execute
notes_extra: nrf52840_required=true

#### 17. bt.bluehydra_scan

tool: BlueHydra
version: latest-release-lock
runtime: wsl2
worker: BluetoothWorker
perm: BT_PASSIVE
adapter: BlueHydraAdapter
hook: app/modules/wifi_bluetooth/bluehydra_scan.py::BluehydraScanTechnique.execute
notes_extra: fingerprint_only_default=true

## Hardware y estado de panel

hardware_probes: alfa_monitor_adapter, bluetooth_usb_5_3, hackrf_one, nrf52840
hackrf_panel_enabled_if: hackrf_one_detected=true
hackrf_panel_message_missing: Requiere HackRF conectado. Inserte el dispositivo y reinicie el módulo.
nrf_panel_enabled_if: nrf52840_detected=true
missing_hardware_status: HARDWARE_REQUIRED
auto_disable_if_missing: true

## Integración LaIA + X5 + Hermes

LaIA/Mistral detecta hardware disponible, recomienda técnica, rellena perfiles, analiza captures/evidence y no ejecuta sola.
X5/OjoRouter valida scope, hardware_probe, confirmación, worker, kill switch, EvidenceStore y estado de panel.
Hermes puede crear en sandbox wrappers USB, parsers Wireshark, schemas BLE/GATT, hardware probes y panel_fields.

## Estado documental del módulo

Módulo 10 queda documentado como catálogo WiFi/Bluetooth con Alfa, dongle Bluetooth USB 5.3, HackRF opcional, nRF52840 opcional, ToolHealth, VersionLock, workers, adapters, hooks, evidence, LaIA, X5/OjoRouter y Hermes.
La lógica privada queda en IMPLEMENTACION_USUARIO_REQUERIDA.

## PARTE 3/3 — OPERATIVA IA, PANEL, X5 Y HERMES

Regla:
Solo documentación. No código, tests, requirements, comandos, payloads, parámetros operativos, ejecución real, autoaprobación ni cambios de estado funcional.

## Panel WiFi/Bluetooth

El panel debe permitir:

- ver hardware detectado: Alfa, Bluetooth USB 5.3, HackRF, nRF52840;
- elegir objetivo autorizado;
- modo automático con Mistral;
- modo asistido con confirmación por técnica;
- modo experto;
- ver técnica actual, fallback_chain, evidence y estado;
- desactivar técnicas si falta hardware;
- lanzar kill switch;
- generar informe final.

Estados:
READY, HARDWARE_REQUIRED, MISSING_TOOL, CONFIRMATION_REQUIRED, RUNNING, SUCCESS, FAILED, PARTIAL, STOPPED_BY_KILL_SWITCH, MANUAL_REQUIRED.

## Chat Mistral / LaIA

Mistral recibe lenguaje natural y devuelve JSON validado, nunca texto libre ejecutable.

Contrato mínimo:

- intent
- target_profile
- scope_profile
- hardware_profile
- selected_technique
- fallback_chain
- risk_level
- required_confirmation
- stop_condition
- evidence_expected
- user_explanation

Ejemplo de intención válida:
auditoria_wifi_autorizada

Mistral debe:

- leer ToolHealth y HardwareHealth;
- elegir técnica según hardware, objetivo y evidence previa;
- proponer fallback;
- explicar al usuario qué falta;
- analizar resultados;
- no marcar éxito sin evidence;
- no ejecutar sin X5.

## X5/OjoRouter

X5 debe:

- validar scope;
- validar hardware_probe;
- validar permission_level;
- validar required_confirmation;
- comprobar kill switch;
- elegir worker;
- crear job;
- guardar EvidenceStore;
- actualizar scoring;
- devolver resultado normalizado a Mistral.

Formato de resultado:

- run_id
- technique_id
- status
- hardware_used
- evidence_ids
- summary
- error_code
- next_recommended_techniques

## HardwareHealth

Checks documentados:

- alfa_present
- monitor_mode_available
- wifi_channel_support
- bluetooth_usb_5_3_present
- ble_available
- hackrf_present
- nrf52840_present
- usbipd_bridge_status
- driver_status

Si falta hardware:
panel_state: HARDWARE_REQUIRED
auto_disable_if_missing: true

## ToolHealth

Checks:

- tool_id
- expected_version
- resolved_version
- runtime
- binary_path
- status
- versionlock_status

Si falta herramienta:
panel_state: MISSING_TOOL
install_hint_profile: kali-linux-large_or_toolhealth

## Scoring X5

X5 debe puntuar:

- técnica usada;
- hardware usado;
- tiempo;
- calidad de evidence;
- éxito/parcial/fallo;
- bloqueo detectado;
- próxima técnica recomendada.

No usar conteos rígidos como bloqueo. El registry es ampliable.

## Hermes Agent Lab

Hermes puede proponer en sandbox:

- wrappers de Aircrack, Bettercap, MDK4, Reaver, BlueZ, Bleak, Wireshark, HackRF;
- parsers de captures;
- schemas WiFi/BLE/GATT;
- hardware probes USB;
- panel_fields;
- fixtures demo;
- documentación de instalación.

Hermes no puede:

- ejecutar técnicas reales;
- tocar producción directamente;
- autoaprobarse;
- eliminar IMPLEMENTACION_USUARIO_REQUERIDA;
- marcar stub como funcional.

Flujo Hermes:
draft -> designed -> generated -> tested -> review_required -> approved_by_user -> promoted.

## Informe final

El módulo debe poder generar:

- objetivo auditado;
- hardware detectado;
- técnicas probadas;
- evidence usada;
- resultado;
- fallos;
- recomendaciones defensivas;
- export JSON/PDF futuro.

## Estado documental final

Módulo 10 queda cerrado con catálogo técnico, hardware, ToolHealth, HardwareHealth, panel, Mistral/LaIA, X5/OjoRouter, Hermes, scoring, evidence, hooks, adapters y flujo operativo.
La lógica privada queda en IMPLEMENTACION_USUARIO_REQUERIDA.
