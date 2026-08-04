# MODULE TOOL INVENTORY — OJO DE DIOS

Cada herramienta debe documentarse como "tool_inventory_item" con "tool_id", "category", "module_ids", "runtime", "source_url", "expected_version", "versionlock_id", "healthcheck_method" y "approved_status".

Categorías exactas:

"binary_tool", "python_package", "node_package", "docker_image", "cloud_api", "local_ai", "external_ai", "hardware", "model", "manual_process".

## Módulo 1 — OSINT

Capacidades:

- resolución de dominio;
- subdominios;
- DNS;
- ASN;
- WHOIS;
- metadatos;
- repositorios;
- filtraciones;
- fingerprint web;
- reconocimiento interno si aplica.

Herramientas/capacidades previstas:

- Nmap;
- masscan;
- Naabu;
- httpx;
- Katana;
- Subfinder;
- Amass;
- Aquatone;
- Shodan API;
- Censys API;
- AlienVault OTX;
- SecurityTrails;
- Have I Been Pwned;
- Dehashed;
- IntelX;
- FOCA;
- exiftool;
- Google Dorks;
- ViewDNS;
- truffleHog;
- Gitleaks;
- WhatWeb;
- Wappalyzer;
- BloodHound.py;
- ldapsearch;
- dnsrecon;
- MassDNS;
- PureDNS.

Estado general:

- pasivo o activo bajo según técnica;
- lógica privada si hay conectores/API privadas;
- evidence normalizada.

## Módulo 2 — Vulnerabilidades

Capacidades:

- CVEs;
- misconfig;
- panel exposure;
- TLS;
- falsos positivos;
- priorización;
- CVSS contextual;
- mapeo exploit.

Herramientas/capacidades:

- Nuclei;
- OpenVAS/GVM;
- Nikto;
- Wapiti;
- testssl.sh;
- Exploit-DB/Searchsploit;
- Metasploit cross-reference;
- PacketStorm;
- AI CVE Tagger;
- Dynamic CVSS;
- soft validation;
- subdomain takeover.

## Módulo 3 — Explotación servicios de red

Capacidades:

- servicios Windows;
- SMB;
- WinRM;
- RDP;
- MSSQL;
- SSH;
- FTP;
- Telnet;
- bases de datos;
- correo;
- VoIP.

Herramientas/capacidades:

- CrackMapExec / NetExec;
- Impacket;
- Metasploit;
- Hydra;
- Medusa;
- sqlmap;
- NoSQLMap;
- Redis tools;
- Elasticsearch checks;
- sipvicious;
- tcpdump.

Estado:

- conexiones, panel, workers y evidence preparados;
- lógica sensible en IMPLEMENTACION_USUARIO_REQUERIDA.

## Módulo 4 — Intrusión web avanzada

Capacidades:

- SQLi;
- NoSQLi;
- command injection;
- SSTI;
- LDAP/XPath injection;
- IDOR;
- lógica de negocio;
- race conditions;
- auth/session;
- JWT;
- OAuth;
- SAML;
- XSS;
- CSRF;
- clickjacking;
- prototype pollution;
- SSRF;
- GraphQL;
- REST;
- SOAP;
- uploads;
- LFI/RFI;
- config read.

Herramientas/capacidades:

- sqlmap;
- NoSQLMap;
- Commix;
- Tplmap;
- Burp/Autorize/Turbo Intruder;
- jwt_tool;
- XSStrike;
- XSS Hunter;
- pp-finder;
- DOM Invader;
- SSRFmap;
- Gopherus;
- Clairvoyance;
- InQL;
- ffuf;
- Fuxploider;
- Weevely3;
- SharPyShell;
- WebShellJScript;
- dotdotpwn.

Estado:

- panel fields específicos por técnica;
- lógica sensible en hooks privados.

## Módulo 5 — Credenciales

Capacidades:

- diccionarios contextuales;
- spraying;
- hashes;
- relay;
- Kerberos;
- cracking offline;
- secrets;
- AD paths.

Herramientas/capacidades:

- Hydra;
- Medusa;
- CrackMapExec / NetExec;
- Responder;
- mitm6;
- Impacket ntlmrelayx;
- GetUserSPNs;
- GetNPUsers;
- Hashcat;
- John the Ripper;
- truffleHog;
- laZagne;
- Certipy;
- BloodHound;
- Mimikatz/DCSync marker.

Estado:

- campos, evidence y workers preparados;
- lógica privada en IMPLEMENTACION_USUARIO_REQUERIDA;
- panel operativo de Credenciales documentado con credenciales normalizadas, ciclo de vida, redacción por defecto y contratos `credential_finding`, `credential_action`, `credential_handoff` y `credential_to_module_action`;
- handoff de entrada/salida documentado para Web, Cloud futuro, Android, MITM/Red, OSINT, EvidenceStore y carga manual;
- Hermes Agent Lab documentado como constructor de parsers, reglas, normalizadores y schemas en laboratorio.

## Módulo 6 — MITM / Red

Capacidades:

- ARP/DNS;
- MITM;
- PCAP;
- túneles;
- SNMP;
- routing;
- VLAN;
- DNS spoof/tunnel/cache.

Herramientas/capacidades:

- Bettercap;
- mitm6;
- Evilginx;
- tshark;
- tcpdump;
- Net-creds;
- PCredz;
- dsniff;
- dnscat2;
- iodine;
- ptunnel;
- Chisel;
- Neo-reGeorg;
- snmpwalk;
- Loki;
- FRRouting;
- Yersinia;
- Scapy.

Estado:

- lógica sensible en IMPLEMENTACION_USUARIO_REQUERIDA;
- DNS no módulo independiente.

## Módulo 7 — Post-explotación

Capacidades:

- C2;
- enumeración local;
- escalada;
- lateral;
- tickets;
- persistencia;
- evasión;
- cleanup.

Herramientas/capacidades:

- Havoc;
- Sliver;
- Empire;
- Covenant;
- ScareCrow;
- Donut;
- Nimplant;
- WinPEAS;
- LinPEAS;
- PowerUp;
- linux-exploit-suggester;
- windows-exploit-suggester;
- CrackMapExec / NetExec;
- Impacket;
- Mimikatz;
- Rubeus.

Estado:

- toda lógica operativa sensible queda en IMPLEMENTACION_USUARIO_REQUERIDA;
- el chasis deja paneles, workers, evidence y hooks.

## Módulo 8 — DoS / Resiliencia

Capacidades:

- degradación controlada;
- métricas;
- recuperación;
- parada;
- evidence de resiliencia.

Herramientas/capacidades:

- hping3;
- MHDDoS;
- Scapy;
- Slowloris;
- SlowHTTPTest;
- HTTP/2 rapid reset scripts;
- DNS/NTP amplification markers.

Estado:

- siempre con kill switch;
- métricas y evidence;
- lógica privada si aplica.

## Módulo 9 — Scraping Inteligente X4 + X5 + IA

Capacidades:

- X4 connector;
- planning X5;
- scraping por lenguaje natural;
- selectores;
- fuentes;
- normalización;
- export JSON/CSV;
- uso de resultados en otros módulos.

Herramientas/capacidades:

- X4;
- Playwright/Selenium si aplica;
- OCR si aplica;
- Mistral;
- X5 planner;
- source registry;
- result normalizer;
- exporter.

Estado:

- X4 se integra como conector;
- no copiar X4 entero;
- lógica privada en hooks.

## Módulo 10 — Wireless / RF general

Capacidades:

- WiFi;
- Bluetooth;
- BLE;
- RFID/NFC;
- Zigbee;
- Z-Wave;
- HackRF SDR;
- recepción;
- waterfall;
- análisis pasivo;
- transmisión con confirmación y lógica privada.

Herramientas/capacidades:

- aircrack-ng;
- hcxdumptool/hcxtools;
- Hashcat;
- Fluxion;
- WiFi Pumpkin;
- PyBluez;
- bleak;
- BlueZ;
- nRF52840 tools;
- Gattacker;
- BtleJuice;
- MouseJack;
- Proxmark3;
- Zigbee2MQTT;
- Z-Wave JS;
- HackRF;
- gqrx;
- Universal Radio Hacker;
- dump1090;
- noaa-apt;
- multimon-ng;
- gr-gsm;
- gr-tetra;
- gr-tetrapol;
- GNURadio;
- pyhackrf.

Estado:

- recepción pasiva puede ser READY_PASSIVE;
- transmisión queda en IMPLEMENTACION_USUARIO_REQUERIDA;
- panel HackRF dedicado.

## Módulo 11 — IoT / físicos

Capacidades:

- impresoras;
- cámaras;
- domótica;
- dispositivos LAN/WiFi/BLE;
- APIs locales;
- evidence por dispositivo.

Herramientas/capacidades:

- PRET;
- PJL scripts;
- snmpwalk;
- Cameradar;
- Metasploit references;
- scripts/API privadas.

Estado:

- chasis, panel, worker y evidence;
- lógica privada en hooks.

## Módulo 12 — Orquestación X5 + IA + Hermes Agent Lab

Documento propio:

- `docs/techniques/12_ORCHESTRATION_X5_AI_HERMES.md`

Resumen:

- Módulo 12 coordina LaIA/Mistral, X5/OjoRouter, Hermes Agent, DeepSeek, Redis, SQLite, EvidenceStore, AuditLog, panel contextual, fallback de capacidades y evolución del arsenal.

Capacidades:

- strategy engine;
- planner;
- scoring;
- fallback;
- reinjection;
- Mistral planner;
- parameter filler;
- evidence analyzer;
- report writer;
- Hermes Agent Lab;
- DeepSeek;
- panel contextual;
- fallback de capacidades;
- API;
- eventos.

Herramientas/capacidades:

- X5/OjoRouter;
- Dolphin Mistral Nemo 12B;
- Ollama;
- llama.cpp preparado;
- Hermes Agent;
- DeepSeek;
- Redis Pub/Sub;
- SQLite;
- EvidenceStore;
- AuditLog;
- FastAPI/Flask routes según arquitectura;
- WebSocket/SSE.

## Módulo 13 — Android

Referencia técnica principal: [`docs/techniques/13_ANDROID.md`](techniques/13_ANDROID.md).

Resumen documental: Android está documentado hasta Vector 11 con USB, payloads, control remoto, ataque físico USB, Red Móvil/MITM, Análisis de Apps, IMSI Catcher/BTS/RF Móvil, Servicio de Accesibilidad/Registro de Eventos, Capa de Conectividad, Carteras de Criptomonedas/Apps Financieras y Mensajería. Las capacidades descritas son especificación documental y no implican ejecución activa sin implementación futura aprobada.

Capacidades:

- interfaz Android con USB Directo y Red Móvil;
- análisis APK;
- permisos;
- generación asistida de payloads;
- control remoto avanzado documental;
- listener/C2 custom bajo contrato y VersionLock;
- ataque físico USB autorizado;
- Red Móvil/MITM autorizado;
- Vector 7 Android IMSI Catcher/BTS/RF móvil como especificación de laboratorio con panel, preflight RF, handoff, scoring, EvidenceStore y M16-ready evidence;
- Vector 8 Android Servicio de Accesibilidad y Registro de Eventos como especificación de laboratorio con panel, preflight, errores/recuperación, handoff M5/M12/M13, scoring X5, EvidenceStore y preparación M16;
- Vector 9 Android Capa de Conectividad como especificación de laboratorio con hardware Windows/Kali WSL2, WiFi, Bluetooth, HackRF, NFC/RFID, técnicas `android.connectivity.*`, handoff M10/M6/M5/M12 y handoff interno a Vectores 3/5/6, scoring X5 y preparación M16;
- Vector 10 Android Carteras de Criptomonedas y Apps Financieras como especificación de laboratorio con panel **Android > Carteras**, técnicas `android.crypto.*`, contrato `crypto_action`, handoff M5/M12/M13, scoring X5 y preparación M16;
- Vector 11 Android Mensajería como especificación de laboratorio con panel **Android > Mensajería**, técnicas `android.messaging.*`, contratos `messaging_action` y `messaging_handoff`, handoff M5/M12/M13, scoring X5 y preparación M16;
- persistencia;
- pivoting;
- evidence.

Herramientas/capacidades:

- apktool;
- jadx;
- androguard;
- msfvenom;
- Metasploit;
- jarsigner;
- apksigner;
- ProGuard/R8;
- Obfuscapk;
- JDK;
- Frida;
- objection;
- ADB;
- YateBTS nominal;
- srsRAN nominal;
- gr-gsm;
- osmocom-bb;
- HackRF tools;
- Wireshark/tshark;
- tcpdump;
- minicom;
- pyserial;
- scapy;
- requests;
- Adaptador WiFi Alfa (RTL8812AU);
- Dongle BT 5.3;
- HackRF One;
- ACR122U;
- aircrack-ng;
- hcxdumptool/hcxtools;
- hostapd;
- dnsmasq;
- Bettercap;
- Airgeddon;
- nmap;
- hydra;
- Metasploit;
- wireshark/tshark;
- mitmproxy;
- BlueZ;
- bleak;
- Gattacker;
- BtleJuice;
- hackrf;
- gr-gsm;
- gr-bluetooth;
- libnfc;
- mfoc;
- mfcuk;
- nfc-tools;
- adb;
- Frida;
- objection;
- apktool;
- jadx;
- Python;
- frida;
- requests;
- bip39-utils;
- Dolphin Mistral Nemo 12B;
- Hermes (DeepSeek API);
- android-backup-toolkit;
- abpt;
- sqlite3;
- signal-back;
- hashcat;
- scripts privados.

Estado:

- panel completo con campos;
- LaIA rellena parámetros;
- lógica sensible en IMPLEMENTACION_USUARIO_REQUERIDA.

## Módulo 13bis — Apple

Referencia técnica principal: [`docs/techniques/13bis_APPLE.md`](techniques/13bis_APPLE.md).

Resumen documental: Apple cubre iOS/iPadOS y macOS como especificación de laboratorio con panel **Apple**, subpestañas **iOS** y **macOS**, acceso físico USB, ataques de red/phishing, técnicas macOS, contratos `ios_action`, `macos_action` y `apple_handoff`, handoffs M5/M12/M13, scoring X5 y preparación M16. Las capacidades descritas no implican ejecución activa sin implementación futura aprobada.

Capacidades:

- detección iOS/iPadOS por USB y macOS en red;
- panel **Apple > iOS** con acceso físico USB y ataques de red/phishing;
- panel **Apple > macOS** con visor de Mac en red y técnicas documentales;
- técnicas `ios.*` y `macos.*` con contratos JSON documentales;
- handoff a M5 para Apple ID, tokens, cookies, llavero y credenciales;
- handoff a M12 para orquestación LaIA/Mistral, X5, Policy, Kill Switch, EvidenceStore y AuditLog;
- handoff a M13 cuando aparezcan APKs o dispositivos Android en el mismo laboratorio;
- preparación M16 con SHA256, `timeline_json`, cadena de custodia y exportación enmascarada por defecto.

Herramientas/capacidades:

- libimobiledevice-utils;
- ideviceinstaller;
- checkra1n;
- Sliver;
- ipwndfu;
- Evilginx3;
- SET;
- Bettercap;
- mitmproxy;
- Hydra;
- Frida;
- objection;
- Dolphin Mistral Nemo 12B;
- Hermes (DeepSeek API).

Reglas críticas:

- Todo lo sensible permanece `IMPLEMENTACION_USUARIO_REQUERIDA`.
- La documentación no instala herramientas, no ejecuta técnicas y no afirma explotación real.
- Credenciales, tokens, llaveros, backups, perfiles, PCAP y keylogs se redactan por defecto y requieren confirmación reforzada para revelado completo.

## Módulo 14 — Phishing

Capacidades:

- campañas;
- OSINT objetivo;
- generación de textos;
- plantillas;
- site clone;
- certificados;
- SMTP;
- panel tiempo real;
- reporte.

Herramientas/capacidades:

- Mistral;
- Evilginx;
- Certbot;
- swaks;
- GoPhish;
- panel propio.

Estado:

- chasis, campos, evidence y report;
- lógica sensible en IMPLEMENTACION_USUARIO_REQUERIDA.

## Módulo 15 — Cloud / Containers / Kubernetes

Capacidades:

- Docker;
- Kubernetes;
- imágenes;
- secrets;
- IAM;
- cloud assets;
- metadata;
- persistence markers.

Herramientas/capacidades:

- nmap;
- kube-hunter;
- Trivy;
- Scout Suite;
- CDK;
- kubeletctl;
- Peirates;
- Prowler;
- kubectl;
- cloud scripts privados.

Estado:

- pasivas READY_PASSIVE;
- mutaciones en IMPLEMENTACION_USUARIO_REQUERIDA.

## Módulo 16 — Ops / Evidence / Calidad

Capacidades:

- readiness;
- healthcheck;
- registry guard;
- evidence quality;
- version lock;
- audit log;
- cleanup runtime;
- Hermes approval;
- report final.

Herramientas/capacidades:

- internal tools;
- validators;
- report builder;
- EvidenceStore;
- VersionLock;
- ScoringEngine.


## Nota Ronda 0-F — Relación con catálogo Kali/tools y CVE

Este inventario enumera capacidades y herramientas previstas por módulo, pero no convierte herramientas en técnicas listas para ejecución. La disponibilidad real depende de registry, worker, parser, evidence contract, permisos, ToolHealth, VersionLock y X5/OjoRouter.

Las fichas detalladas de herramientas deben vivir en `docs/tools/` cuando se creen y seguir [KALI_TOOL_KNOWLEDGE_CATALOG.md](KALI_TOOL_KNOWLEDGE_CATALOG.md). Las vulnerabilidades nuevas deben seguir [VULNERABILITY_INTELLIGENCE_PIPELINE.md](VULNERABILITY_INTELLIGENCE_PIPELINE.md) y no deben marcarse como explotables sin evidence.

## Módulo 13bis — Apple (iOS / macOS)
- libimobiledevice-utils 1.3.0
- ideviceinstaller 1.1.1
- checkra1n 0.12.4
- Sliver 1.0 (bypass de código)
- ipwndfu 1.0
- Evilginx3 3.3
- SET 8.0
- Bettercap 2.34
- mitmproxy 10.2
- Hydra 9.7
- Frida 16.5
- objection 1.13
- Dolphin Mistral Nemo 12B (LaIA)
- Hermes (DeepSeek API)

## Módulo 14 — Campañas de Simulación y Concienciación
- Evilginx (latest-release-lock)
- Gophish (latest-release-lock)
- SET (latest)
- Metasploit Framework (latest-release-lock)
- swaks (latest)
- Certbot (latest)
- Dolphin Mistral Nemo 12B (LaIA)
- Hermes (DeepSeek API)

## Módulo 14 — Campañas de Verificación de Seguridad
- Evilginx (latest-release-lock)
- Gophish (latest-release-lock)
- SET (latest)
- Metasploit Framework (latest-release-lock)
- swaks (latest)
- Certbot (latest)
- Dolphin Mistral Nemo 12B (LaIA)
- DeepSeek (Arquitecto de Laboratorio)
- Hermes (DeepSeek API)

## Módulo 15 — Cloud / Containers / Kubernetes
- Trivy 0.52
- kube-hunter 1.8
- kubeletctl 1.0
- CDK 1.0
- Peirates 1.1
- Scout Suite 5.13
- Prowler 4.0
- cloudsplaining 0.1
- kubectl 1.30
- docker 26.1
- nmap 7.99
- WhatWeb 0.5.5
- Dolphin Mistral Nemo 12B (LaIA)
- Hermes (DeepSeek API)

## IA local y Hermes Agent — Estación de laboratorio

Capacidades:

- LaIA/Mistral local mediante Ollama para planificación, análisis de evidencias, resúmenes y respuestas JSON controladas;
- base de conocimiento local en `storage/knowledge/` para consulta RAG desde documentación del repositorio;
- Hermes Agent Lab (`hermes_lab`, alias histórico deprecated) como arquitecto de laboratorio respaldado por DeepSeek;
- workspace aislado `modules/laboratory/` para propuestas, experimentos, revisiones, manifests, promociones y rechazos;
- healthchecks separados para LaIA/Mistral y Hermes Agent, con Vectores 1-2 pendientes de validación operativa en Windows.

Herramientas/capacidades:

- Ollama para servir Mistral local;
- `CognitiveComputations/dolphin-mistral-nemo:12b` como modelo oficial local; `laia-mistral-con-prompt` solo como alias opcional de prueba;
- ChromaDB para vectorstore local;
- sentence-transformers `all-MiniLM-L6-v2` para embeddings;
- LangChain / langchain-community para carga y troceado documental;
- DeepSeek API para Hermes Agent con base URL `https://api.deepseek.com`, modelos `deepseek-v4-pro` y `deepseek-v4-flash`, `GET /models` y `POST /chat/completions`;
- scripts batch de preparación, comprobación e indexado en `scripts/windows/ia/`.

Estado:

- `AI_ENABLED` es el interruptor global; `MISTRAL_ENABLED` y `ANGEL_ENABLED` solo se evalúan si `AI_ENABLED=1`;
- LaIA/Mistral no ejecuta comandos directamente y devuelve JSON cuando `LAIA_JSON_ONLY=1`;
- falta aislada de RAG produce `KNOWLEDGE_MISSING`, `KNOWLEDGE_STALE` o `PARTIAL`, no `FAILED`, si Ollama y el modelo oficial responden;
- Hermes Agent solo trabaja en `modules/laboratory/`, usa `PROMOTION_MANIFEST.json` por propuesta, centraliza promociones en `modules/laboratory/_promoted_manifest/` y no promociona sin aprobación;
- no se almacenan claves reales en el repositorio;
- los estados de laboratorio son `experimental`, `lab_ready`, `review_required`, `approved_by_user`, `promoted` y `rejected`.

## Módulo 16 — Excelencia Operativa / Evidence / exportación externa
- Ollama (latest)
- Dolphin Mistral Nemo 12B Q4_K_M (LaIA local)
- DeepSeek API (Hermes Agent)
- ChromaDB (base de conocimiento)
- Sentence-Transformers (embeddings)
- LangChain (framework RAG)
- EvidenceStore
- SHA-256
- manifest
- timeline
- trace_id
- span_id


Nota M16-FIX-1: Mano de Dios sigue siendo producto separado según `docs/MANO_DE_DIOS_SEPARATION.md`. M16 solo puede preparar una exportación externa futura y no debe integrarlo internamente. Los Vectores 1 y 2 siguen pendientes de validación operativa en Windows y M16 no se considera cerrado hasta completar Vectores 3-10.


## Requisitos VersionLock / ToolHealth por herramienta

Cada herramienta documentada en este inventario debe tener, antes de considerarse
lista para ejecución futura, los siguientes campos documentales mínimos:

- "tool_id"
- "module_id"
- "runtime"
- "expected_version"
- "source_url"
- "healthcheck_method"
- "status"

Estos campos no crean implementación ni healthchecks reales; fijan la base
documental para M16 Vector 6.


## Herramientas candidatas

Una herramienta candidata debe tener, antes de uso real:

- "tool_candidate_review"
- "tool_inventory_item"
- "tool_version_lock"
- "tool_health_result"

La candidatura no crea implementación ni autoriza ejecución: solo documenta que
la herramienta debe pasar procedencia, VersionLock, ToolHealth, revisión de
riesgo y aprobación humana antes de integrarse al arsenal controlado.

### Normalización M10/M17

M10 es la superficie general de Wireless/RF: WiFi, BLE, RFID/NFC, Zigbee, Z-Wave y radio general. M17 queda reservado como propietario principal de HackRF, SDR avanzada, waterfall, IQ, replay de laboratorio, decoders, GNU Radio, SoapySDR, SDR++, SigDigger, inspectrum y perfiles RF. Otros módulos pueden mostrar acciones espejo mediante `capability_ref`: una capacidad real, múltiples superficies de uso.
