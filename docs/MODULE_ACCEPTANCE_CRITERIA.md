# MODULE ACCEPTANCE CRITERIA — OJO DE DIOS

Cada módulo se acepta si tiene:

- carpeta;
- registry;
- contracts;
- panel_schema;
- evidence;
- ai_assistant;
- worker asignado;
- técnicas visibles;
- estados correctos;
- permisos correctos;
- fields propios por técnica;
- evidence contract;
- slot Hermes;
- demo/dry_run behavior.

## Módulo 1 OSINT

Debe aceptar dominio/IP/rango/email/persona/empresa.
Debe alimentar TargetFingerprint y Attack Surface Graph.

## Módulo 2 Vulnerabilidades

Debe recibir servicios/tecnologías/versiones.
Debe producir CVE candidates y risk context.

## Módulo 3 Servicios de red

Debe partir de ServiceFingerprint.
Debe mapear servicios a técnicas registradas.

## Módulo 4 Web avanzada

Debe aceptar URL, headers, cookies, auth context y scope.
Debe tener campos concretos por técnica web.

## Módulo 5 Credenciales

Debe gestionar fuentes, diccionarios, hashes, tickets y evidence.
Debe cumplir estos criterios documentales:

- [ ] Panel de Credenciales documentado con subpáginas.
- [ ] Tipos oficiales de credencial documentados.
- [ ] Ciclo de vida de credencial documentado.
- [ ] Redacción/visibilidad de secretos documentada.
- [ ] Contratos `credential_finding`, `credential_action`, `credential_handoff` documentados.
- [ ] Handoff desde M13 Android Vector 6 documentado.
- [ ] Handoff hacia Web/Cloud/Android/MITM/OSINT documentado.
- [ ] EvidenceStore y tipos de evidencia documentados.
- [ ] Scoring X5 documentado.
- [ ] Hermes Agent como constructor de parsers/reglas/normalizadores documentado.
- [ ] LaIA como asistente contextual documentada.
- [ ] Cierre seguro e informe PDF documentados.
- [ ] No hay credenciales reales, hashes reales ni comandos operativos.

## Módulo 6 MITM / Red

Debe gestionar interfaces, PCAP, túneles y DNS integrado.

## Módulo 7 Post-explotación

Debe mostrar sesiones/evidence/rutas.
Toda lógica sensible queda como IMPLEMENTACION_USUARIO_REQUERIDA.

## Módulo 8 DoS / Resiliencia

Debe tener métricas, parada, límites y evidence.

## Módulo 9 Scraping X4 + X5 + IA

Debe integrar X4Connector, X5ScrapingPlanner, normalizer y exporter.

## Módulo 10 Wireless / RF general

Debe tener panel HackRF dedicado y hardware status.

## Módulo 11 IoT / Físicos

Debe gestionar dispositivos, cámaras, impresoras, domótica y evidence.

## Módulo 12 Orquestación

Debe contener X5, LaIA, Hermes Agent, DeepSeek y planificación.
Debe cumplir estos criterios documentales:

- documento M12 existe en `docs/techniques/12_ORCHESTRATION_X5_AI_HERMES.md`;
- roles claros: Mistral dirige, X5 ejecuta, Hermes Agent construye, DeepSeek diseña/revisa;
- panel contextual por módulo documentado;
- fallback de capacidades documentado;
- DeepSeek documentado;
- Redis/SQLite/WebSocket diferenciados;
- dependencias con aprobación;
- promoción/rollback documentados;
- módulos 13+ y futuros 17/18 heredan arquitectura.

## Módulo 13 Android

Se acepta documentalmente hasta Vector 11 si contiene paneles, técnicas, herramientas, VersionLock, contratos JSON, evidencias, cierre seguro, LaIA/X5/Hermes/DeepSeek/Policy/Evidence/AuditLog y mantiene las capacidades sensibles como `IMPLEMENTACION_USUARIO_REQUERIDA` hasta implementación futura aprobada.

### Criterios documentales Vector 7 — IMSI Catcher / BTS / RF Móvil

- [ ] Propósito IMSI/BTS/RF documentado.
- [ ] Hardware requerido documentado.
- [ ] Herramientas nominales y VersionLock documentados.
- [ ] Panel **Android > IMSI Catcher** documentado.
- [ ] Subpáginas exactas documentadas.
- [ ] Estados BTS documentados.
- [ ] Estados por dispositivo documentados.
- [ ] Técnicas `android.imsi.*` documentadas.
- [ ] Contratos `imsi_action`, `radio_profile` y `rf_handoff` documentados.
- [ ] Confirmaciones explícitas documentadas.
- [ ] Evidencias documentadas.
- [ ] Enmascarado/redacción documentado.
- [ ] Preflight RF documentado.
- [ ] Errores/recuperación documentados.
- [ ] Cierre seguro documentado.
- [ ] Handoff M10/M6/M5/M12/M13 interno documentado.
- [ ] Hermes Agent documentado.
- [ ] Scoring X5 documentado.
- [ ] Preparación M16 documentada.
- [ ] No se afirma implementación real de emisión/intercepción.

### Criterios documentales Vector 8 — Servicio de Accesibilidad y Registro de Eventos

- [ ] Propósito del Vector 8 documentado.
- [ ] Herramientas nominales y VersionLock documentados.
- [ ] Panel **Android > Accesibilidad** documentado.
- [ ] Subpáginas exactas documentadas.
- [ ] Estados del servicio documentados.
- [ ] Técnicas `android.accessibility.*` documentadas.
- [ ] Contratos `accessibility_action` y `accessibility_handoff` documentados.
- [ ] Confirmaciones explícitas documentadas.
- [ ] Evidencias documentadas.
- [ ] Enmascarado/redacción documentado.
- [ ] Preflight documentado.
- [ ] Errores/recuperación documentados.
- [ ] Cierre seguro documentado.
- [ ] Handoff M5/M12/M13 interno documentado.
- [ ] Hermes Agent documentado.
- [ ] Scoring X5 documentado.
- [ ] Preparación M16 documentada.
- [ ] No se afirma implementación real de registro o monitorización.

### Criterios documentales Vector 9 — Capa de Conectividad

- [ ] Propósito del Vector 9 documentado.
- [ ] Herramientas nominales y VersionLock documentados.
- [ ] Compatibilidad hardware Windows/Kali documentada (`usbipd-win`).
- [ ] Panel **Android > Conectividad** documentado con sus subpáginas.
- [ ] Estados visuales documentados.
- [ ] Técnicas `android.connectivity.*` documentadas con sus `technique_id`.
- [ ] Contrato `connectivity_action` documentado.
- [ ] Contrato `connectivity_handoff` documentado.
- [ ] Flujo de trabajo asistido (Mistral + X5 + Hermes) documentado.
- [ ] Preflight checklist documentado.
- [ ] Errores y recuperación documentados.
- [ ] Handoffs con M10, M6, M5, M12 y M13 interno documentados.
- [ ] Scoring X5 documentado.
- [ ] Preparación para M16 documentada.
- [ ] Confirmaciones explícitas para técnicas de emisión documentadas.
- [ ] No se afirma implementación real de emisión o interceptación.

### Criterios documentales Vector 10 — Carteras de Criptomonedas y Apps Financieras

- [ ] Propósito del Vector 10 documentado.
- [ ] Herramientas nominales y VersionLock documentados: adb, Frida, objection, apktool, jadx, Python, Mistral y Hermes.
- [ ] Panel **Android > Carteras** documentado con sus subpáginas.
- [ ] Pantallas de trabajo por técnica documentadas: extracción, volcado, overlay, portapapeles y manipulación.
- [ ] Técnicas `android.crypto.*` documentadas con sus `technique_id`.
- [ ] Contrato `crypto_action` documentado.
- [ ] Contrato `crypto_handoff` documentado.
- [ ] Estados visuales del submódulo **Carteras** documentados.
- [ ] Flujo de trabajo asistido (Mistral + X5 + Hermes) documentado.
- [ ] Preflight checklist documentado.
- [ ] Errores y recuperación documentados.
- [ ] Handoffs con M5, M12 y M13 interno —Vectores 3, 6 y 8— documentados.
- [ ] Handoffs internos explícitos a Vector 3, Vector 6 y Vector 8 documentados.
- [ ] Scoring X5 documentado.
- [ ] Preparación para M16 documentada.
- [ ] Confirmaciones explícitas para técnicas de overlay y manipulación documentadas.
- [ ] No se afirma implementación real de extracción o manipulación de fondos.

### Criterios documentales Vector 11 — Mensajería

- [ ] Propósito del Vector 11 documentado.
- [ ] Herramientas nominales y VersionLock documentados: adb, android-backup-toolkit, abpt, Frida, objection, jadx, sqlite3, signal-back, hashcat, Mistral y Hermes.
- [ ] Panel **Android > Mensajería** documentado con sus subpáginas.
- [ ] Pantallas de trabajo por técnica documentadas: extracción, backup, notificaciones, hook, multimedia y clonación.
- [ ] Técnicas `android.messaging.*` documentadas con sus `technique_id`.
- [ ] Contratos `messaging_action` y `messaging_handoff` documentados.
- [ ] Flujo de trabajo asistido (Mistral + X5 + Hermes) documentado.
- [ ] Preflight checklist documentado.
- [ ] Errores y recuperación documentados.
- [ ] Handoffs con M5, M12 y M13 interno —Vectores 3, 6 y 8— documentados.
- [ ] Scoring X5 documentado.
- [ ] Preparación para M16 documentada.
- [ ] Confirmaciones explícitas para técnicas de hook y clonación documentadas.
- [ ] No se afirma implementación real de extracción o manipulación.

## Módulo 13bis Apple

Se acepta documentalmente si contiene paneles Apple para iOS/macOS, herramientas nominales, VersionLock, contratos JSON `ios_action`, `macos_action` y `apple_handoff`, evidencias, handoffs, scoring X5, preparación M16 y mantiene capacidades sensibles como `IMPLEMENTACION_USUARIO_REQUERIDA` sin afirmar ejecución real.

### Criterios documentales Módulo 13bis — Apple

- [ ] Propósito del módulo documentado.
- [ ] Herramientas nominales y VersionLock documentados: libimobiledevice-utils, ideviceinstaller, checkra1n, Sliver, ipwndfu, Evilginx3, SET, Bettercap, mitmproxy, Hydra, Frida, objection, Mistral y Hermes.
- [ ] Panel **Apple** documentado con subpestañas **iOS** y **macOS**.
- [ ] Estados visuales del panel documentados.
- [ ] Técnicas `ios.*` y `macos.*` documentadas con sus `technique_id` y contratos JSON.
- [ ] Técnicas de ataque físico USB documentadas.
- [ ] Técnicas de ataque remoto y phishing documentadas.
- [ ] Técnicas de ataque a macOS documentadas.
- [ ] Flujo de trabajo asistido (Mistral + X5 + Hermes) documentado.
- [ ] Handoffs con M5, M12 y M13 documentados.
- [ ] Scoring X5 y preparación para M16 documentados.
- [ ] Preflight checklist y manejo de errores documentados.
- [ ] No se afirma implementación real.

## Módulo 14 Phishing

Debe tener campañas, plantillas, evidence y report.

## Módulo 15 Cloud / Containers / Kubernetes

Debe distinguir read-only de mutation.

## Módulo 16 Ops / Quality

Debe tener healthcheck, readiness, version lock, evidence quality y cleanup runtime.

## Módulo 13bis — Apple (iOS / macOS)
- [ ] Propósito del módulo documentado.
- [ ] Herramientas nominales y VersionLock documentados.
- [ ] Panel 'Apple' con subpestañas 'iOS' y 'macOS' documentado.
- [ ] Estados visuales documentados.
- [ ] Técnicas 'ios.*' y 'macos.*' documentadas con contratos JSON.
- [ ] Ataque físico USB documentado.
- [ ] Ataque remoto y phishing documentado.
- [ ] Ataque a macOS documentado.
- [ ] Flujo asistido (Mistral + X5 + Hermes) documentado.
- [ ] Handoffs con M5, M12 y M13 documentados.
- [ ] Handoffs internos (iOS ↔ macOS) documentados.
- [ ] Scoring X5 y preparación para M16 documentados.
- [ ] No se afirma implementación real.

## Módulo 14 — Campañas de Simulación y Concienciación
- [ ] Propósito del módulo documentado.
- [ ] Herramientas nominales y VersionLock documentados.
- [ ] Panel 'Simulación' documentado con subpáginas.
- [ ] Estados de campaña documentados.
- [ ] Técnicas 'phishing.*' documentadas con contratos JSON.
- [ ] Evidencias esperadas documentadas.
- [ ] Confirmaciones explícitas documentadas.
- [ ] Flujo asistido (Mistral + X5 + Hermes) documentado.
- [ ] Preflight checklist y errores documentados.
- [ ] Handoffs con M1, M5, M12 y M16 documentados.
- [ ] Scoring X5 y preparación para M16 documentados.
- [ ] No se afirma implementación real.

## Módulo 14 — Campañas de Verificación de Seguridad
- [ ] Propósito del módulo documentado.
- [ ] Herramientas nominales y VersionLock documentados.
- [ ] Panel 'Verificación' documentado con subpáginas.
- [ ] Estados de campaña documentados.
- [ ] Técnicas 'phishing.*' documentadas con contratos JSON.
- [ ] Evidencias esperadas documentadas.
- [ ] Confirmaciones explícitas documentadas.
- [ ] Pantallas de trabajo por herramienta documentadas.
- [ ] Roles de IAs documentados.
- [ ] Flujo asistido documentado.
- [ ] Preflight checklist y errores documentados.
- [ ] Handoffs con M1, M5, M12 y M16 documentados.
- [ ] Scoring X5 y preparación para M16 documentados.
- [ ] No se afirma implementación real.

## Módulo 15 — Cloud / Containers / Kubernetes
- [ ] Propósito del módulo documentado.
- [ ] Herramientas nominales y VersionLock documentados.
- [ ] Panel 'Cloud' documentado con subpestañas.
- [ ] Fingerprinting real documentado.
- [ ] Modos de operación documentados.
- [ ] Técnicas 'cloud.*' documentadas con contratos JSON.
- [ ] Pantallas de trabajo documentadas.
- [ ] Flujo asistido documentado.
- [ ] Preflight checklist y errores documentados.
- [ ] Handoffs con M5, M6 y M12 documentados.
- [ ] Scoring X5 y preparación para M16 documentados.
- [ ] No se afirma implementación real.

## Criterios Módulo 16 — Estación LaIA y Hermes Agent

Los Vectores 1 y 2 están documentados y pendientes de validación operativa en Windows. El Módulo 16 no se considera cerrado hasta completar Vectores 3-10.

Criterios pendientes para V1-V2:

- [ ] BATs probados en Windows real.
- [ ] Rutas resueltas desde cualquier directorio.
- [ ] Estados correctos, incluyendo `READY_LOCAL_AI`, `KNOWLEDGE_MISSING`, `KNOWLEDGE_STALE`, `MODEL_MISSING`, `MISSING_TOOL`, `PARTIAL`, `FAILED`, `LAB_WORKSPACE_READY` y `READY_CONTROLLED`.
- [ ] Healthchecks con códigos de salida reales.
- [ ] RAG construido y trazable; falta aislada de RAG no marca LaIA como `FAILED` si Ollama y `CognitiveComputations/dolphin-mistral-nemo:12b` responden.
- [ ] API DeepSeek validada contra `https://api.deepseek.com`, usando `GET /models` para disponibilidad de modelo y `POST /chat/completions` para chat controlado.
- [ ] Ningún secreto en logs, especialmente nunca `DEEPSEEK_API_KEY`.
- [ ] Documentación coherente con `AI_ENABLED` como interruptor global y `MISTRAL_ENABLED`/`ANGEL_ENABLED` evaluados solo si `AI_ENABLED=1`.

Criterios documentales de continuidad:

- [ ] Variables de entorno de LaIA/Mistral documentadas en `.env.example` sin secretos reales.
- [ ] Variables de entorno de Hermes Agent documentadas en `.env.example` sin secretos reales.
- [ ] `MISTRAL_MODEL` apunta siempre a `CognitiveComputations/dolphin-mistral-nemo:12b`.
- [ ] `laia-mistral-con-prompt` queda solo como alias opcional de prueba.
- [ ] System prompt local de LaIA/Mistral documentado en `docs/ai_prompts/laia_mistral_system_prompt.md` y enviado en cada petición.
- [ ] System prompt de Hermes Agent documentado en `docs/ai_prompts/angel_hermes_system_prompt.md`.
- [ ] Instalador independiente de Ollama disponible como batch.
- [ ] Instalador interactivo LaIA/Mistral disponible como batch.
- [ ] Constructor de base de conocimiento local disponible como batch/Python operativo.
- [ ] Healthcheck LaIA/Mistral verifica Ollama, modelo oficial y estado de conocimiento local.
- [ ] Preparador de estación Hermes Agent crea workspace de laboratorio y valida `.env`.
- [ ] Comprobador Hermes Agent realiza petición mínima a DeepSeek y guarda estado runtime sin secretos.
- [ ] Workspace `modules/laboratory/` documenta estados `experimental`, `lab_ready`, `review_required`, `approved_by_user`, `promoted` y `rejected`.
- [ ] Nombre interno `hermes_lab`, nombre visible `Hermes Agent Lab` y alias histórico deprecated normalizados.
- [ ] Cada propuesta usa `PROMOTION_MANIFEST.json` y promociones centrales en `modules/laboratory/_promoted_manifest/`.
- [ ] Hermes Agent no instala dependencias sin confirmación cuando `ANGEL_ALLOW_DEPENDENCY_INSTALL=0`.
- [ ] Hermes Agent no modifica módulos ofensivos fuera del workspace de laboratorio.
- [ ] Hermes Agent no promociona propuestas sin aprobación humana.
- [ ] M16 conserva healthchecks, manifests, revisiones y estados de aprobación.

## Módulo 16 — Excelencia Operativa / Evidence / exportación externa
- [ ] Estación LaIA/Mistral documentada y validada en Windows real.
- [ ] Estación Hermes Agent documentada y validada en Windows real.
- [ ] System prompts endurecidos creados y trazables.
- [ ] Base de conocimiento local (RAG) operativa y trazable.
- [ ] Healthchecks verificados con códigos de salida reales.
- [ ] Workspace de laboratorio preparado como `LAB_WORKSPACE_READY`.
- [ ] Índices globales actualizados.
- [ ] Mano de Dios tratado solo como producto separado según `docs/MANO_DE_DIOS_SEPARATION.md`; M16 puede preparar exportación externa futura, nunca integración interna.

### Checklist Vector 3 — Sistema universal de evidencias y trazabilidad

- [ ] Contratos de evidencia documentados.
- [ ] Timeline y custodia documentados.
- [ ] Manifest y exportación documentados.
- [ ] Tablas futuras documentadas.
- [ ] API futura documentada.
- [ ] Panel Ops/Evidence documentado.
- [ ] Errores y recuperación documentados.
- [ ] No se afirma implementación real.


### Checklist Vector 4 — Panel de IAs y chat unificado

- [ ] Panel de IAs documentado.
- [ ] Roles y estados de agentes documentados.
- [ ] Contratos de sesión, mensaje, acción, aprobación, tarea y revisión documentados.
- [ ] Persistencia futura documentada.
- [ ] Reconexión y recuperación documentadas.
- [ ] Errores documentados.
- [ ] Chat no ejecuta texto libre.
- [ ] Redis no se usa como histórico.
- [ ] No se afirma implementación real.


### Checklist Vector 5 — Healthchecks, logs y auditoría de IAs

- [ ] Componentes críticos listados.
- [ ] Estados oficiales documentados.
- [ ] Contrato "ai_healthcheck_result" documentado.
- [ ] Rutas de logs documentadas.
- [ ] Reglas de no exposición de secretos documentadas.
- [ ] API futura documentada.
- [ ] No se afirma implementación real.


### Checklist Vector 5B — Logs, audit events, retención y panel Health

- [ ] Formato de logs documentado.
- [ ] Eventos de auditoría IA documentados.
- [ ] Retención/rotación documentada.
- [ ] Panel Ops > Health documentado.
- [ ] Errores y recuperación documentados.
- [ ] No se exponen secretos en logs.
- [ ] Redis no se usa como histórico.


### Checklist Vector 6 — VersionLock y ToolHealth

- [ ] VersionLock documentado.
- [ ] ToolHealth documentado.
- [ ] Contratos "tool_version_lock" y "tool_health_result" documentados.
- [ ] Estados documentados.
- [ ] Runtimes documentados.
- [ ] API futura documentada.
- [ ] No se afirma implementación real.


### Checklist Vector 6B — Inventario SBOM, procedencia y cambio de versiones

- [ ] Inventario tipo SBOM documentado.
- [ ] Procedencia documentada.
- [ ] Contrato "tool_inventory_item" documentado.
- [ ] Contrato "tool_version_change" documentado.
- [ ] Cambio de versión documentado.
- [ ] Relación VersionLock-Evidence documentada.
- [ ] No se afirma implementación real.


### Checklist Vector 6C — Revisión de confianza y aprobación de herramientas

- [ ] Revisión de confianza documentada.
- [ ] Contrato "tool_candidate_review" documentado.
- [ ] Decisiones de aprobación documentadas.
- [ ] Riesgo por herramienta documentado.
- [ ] Flujo evolutivo Hermes Agent documentado.
- [ ] No se permite autoaprobación.


### Checklist Vector 6D — Panel ToolHealth, errores y cierre documental

- [ ] Panel ToolHealth documentado.
- [ ] Bloqueos de ejecución documentados.
- [ ] Errores VersionLock/ToolHealth documentados.
- [ ] Flujo Hermes Agent → candidato → aprobación documentado.
- [ ] API futura documentada.
- [ ] X5 no ejecuta herramientas no válidas.
- [ ] VersionLock antiguo no se sobrescribe.
- [ ] No se afirma implementación real.


### Checklist Vector 7 — Integridad de registry, contratos y estados

- [ ] Guardas de integridad documentadas.
- [ ] Contrato "integrity_check_result" documentado.
- [ ] Reglas de registry documentadas.
- [ ] Reglas de contrato JSON documentadas.
- [ ] Estados de técnica documentados.
- [ ] API futura documentada.
- [ ] No se afirma implementación real.


### Checklist Vector 7B — Integridad de paneles, API y workers

- [ ] Integridad de paneles documentada.
- [ ] Integridad de API futura documentada.
- [ ] Integridad de workers documentada.
- [ ] Fases de ejecución documentadas.
- [ ] Errores de integridad documentados.
- [ ] No se afirma implementación real.


### Checklist Vector 7C — Reparación controlada, reporte y cierre documental

- [ ] Reparación controlada documentada.
- [ ] Contrato "integrity_repair_request" documentado.
- [ ] Panel Ops > Integridad documentado.
- [ ] Contrato "integrity_report" documentado.
- [ ] API futura documentada.
- [ ] Hermes Agent no modifica producción automáticamente.
- [ ] Usuario aprueba aplicación final.
- [ ] No se afirma implementación real.


### Checklist Vector 8 — Calidad de evidencia y scoring base

- [ ] Calidad de evidencia documentada.
- [ ] Contratos "evidence_quality_assessment" y "scoring_update_decision" documentados.
- [ ] Reglas de no scoring sin evidencia documentadas.
- [ ] Demo/falso positivo/ruido documentados.
- [ ] No se afirma implementación real.


### Checklist Vector 8B — Memoria de resultados, ruido y falsos positivos

- [ ] Memoria de resultados documentada.
- [ ] Contrato "technique_outcome_memory" documentado.
- [ ] Ruido documentado.
- [ ] Falsos positivos documentados.
- [ ] Panel Ops > Calidad documentado.
- [ ] Reparación Hermes Agent por ruido documentada.
- [ ] No se afirma implementación real.


### Checklist Vector 8C — Panel Ops/Calidad, errores y cierre documental

- [ ] Panel Ops > Calidad documentado.
- [ ] API futura de calidad/scoring documentada.
- [ ] Errores y recuperación documentados.
- [ ] Cierre seguro de scoring documentado.
- [ ] Falsos positivos no borran evidencia.
- [ ] Demo no puntúa como ejecución real.
- [ ] No se afirma implementación real.


### Checklist Vector 9 — Integridad Hermes Agent, promoción y rollback

- [ ] Estados Hermes Agent documentados.
- [ ] "hermes_promotion_manifest" documentado.
- [ ] "hermes_rollback_manifest" documentado.
- [ ] No auto-promoción documentada.
- [ ] Usuario aprueba promoción final.
- [ ] Rollback obligatorio documentado.
- [ ] No se afirma implementación real.


### Checklist Vector 9B — Panel Hermes, errores, API y cierre documental

- [ ] Panel Hermes Agent documentado.
- [ ] Checklist de promoción documentado.
- [ ] Errores y bloqueos documentados.
- [ ] API futura documentada.
- [ ] No auto-promoción documentada.
- [ ] Rollback obligatorio documentado.
- [ ] Usuario decide promoción final.
- [ ] No se afirma implementación real.


### Checklist Vector 10 — Readiness final y exportación externa

- [ ] Readiness final documentado.
- [ ] Contratos "final_readiness_report" y "readiness_gap" documentados.
- [ ] Panel Ops > Readiness documentado.
- [ ] Exportación externa documentada.
- [ ] Mano de Dios separado documentado.
- [ ] No se afirma implementación real.


### Checklist Vector 10B — Paquete final, exportación externa y cierre documental

- [ ] Paquete final documentado.
- [ ] Contrato "readiness_export_package" documentado.
- [ ] Export manifest documentado.
- [ ] Cierre documental M16 documentado.
- [ ] No se declara implementación real.


### Checklist M16 final — Auditoría documental

- [ ] Índice M16 V1-V10 verificado.
- [ ] Contratos obligatorios presentes o listados como pendientes.
- [ ] Sin frases de cierre operativo en M16.
- [ ] `.env.example` mantiene IA desactivada por defecto y sin claves reales.
- [ ] API futura documentada como sin implementar.
- [ ] Flujo LaIA → X5 → EvidenceStore → M16 → Hermes Agent → usuario documentado.
- [ ] M16 cerrado como especificación documental; implementación y validación operativa pendientes.
