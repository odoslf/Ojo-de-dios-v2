# MÓDULO 5 — CREDENCIALES Y AUTENTICACIÓN

Catálogo declarativo. Sin comandos, payloads, wordlists, credenciales reales ni pasos operativos.

module_id: credentials_auth
panel: Credenciales
status_default: IMPLEMENTACION_USUARIO_REQUERIDA
workers: CredentialsWorker, WSLWorker, PythonToolWorker, GPUWorker, WindowsWorker
ai: LaIA rellena contexto, perfiles y evidencia; no ejecuta sola.
x5: valida scope, permisos, inputs, worker, evidence y confirmación.
hermes: crea wrappers/parsers/schemas solo en sandbox si falta pieza.


## Panel operativo del Módulo 5

El panel **Credenciales** funciona como una consola asistida para catalogar, revisar, validar de forma controlada y entregar hallazgos de credenciales dentro del alcance autorizado. El módulo mantiene las 16 técnicas existentes como catálogo técnico, pero agrega una capa de operación con LaIA/Mistral como cerebro táctico, X5/OjoRouter como validador de alcance y ejecución, Hermes Agent como laboratorio de parsers y reglas, DeepSeek como arquitecto avanzado para diseño documental y EvidenceStore/AuditLog/Policy Engine/Kill Switch/scoring como controles obligatorios.

LaIA/Mistral prioriza, resume riesgo, propone handoffs, explica falsos positivos y solicita revisión humana cuando la confianza no sea suficiente. X5/OjoRouter no revela ni ejecuta acciones sensibles sin verificar scope, permisos, Policy Engine, Kill Switch, confirmaciones y evidencia esperada. Hermes Agent solo construye parsers, normalizadores, reglas de detección y schemas en laboratorio, sin operar sobre secretos reales fuera del flujo controlado. DeepSeek puede proponer taxonomías, mejoras de contratos y matrices de decisión, siempre como documentación o diseño revisable. EvidenceStore conserva evidencias redacted-by-default; AuditLog registra acciones, revelados, exportaciones, cambios de estado y handoffs; el scoring consolida severidad, confianza, duplicados y falsos positivos.

### Páginas y subpestañas del panel

La barra lateral de **Credenciales** incluye las siguientes páginas/subpestañas documentales:

- **Visor general de credenciales**: tabla global filtrable por tipo, origen, severidad, estado, target, fecha y módulo fuente.
- **Detalle de credencial**: vista ampliada con valor enmascarado, metadatos, evidencias, acciones disponibles, handoff y AuditLog.
- **Bandeja de importación**: entradas desde M4 Web, M6 MITM/Red, M9 Scraping, M13 Android, futuros módulos de Phishing/Cloud, carga manual y EvidenceStore.
- **Tokens / Cookies / JWT**: análisis de claims, expiración, dominios, issuer, audience, scopes y riesgo.
- **Hashes**: tareas offline documentales con Hashcat/John, sin valores reales en documentación.
- **Credenciales web/API/cloud**: API keys, OAuth, Bearer, refresh tokens y cloud keys.
- **Credenciales Android importadas**: secrets APK, cookies WebView, tokens de apps, wallets/keystore y metadatos de análisis.
- **Validación controlada**: modos `format_only`, `offline_analysis` y `live_validation` bajo confirmación cuando aplique.
- **Riesgo y scoring**: severidad, confianza, duplicados, falsos positivos y score consolidado.
- **Evidencias**: PCAP, APK analysis, `cookies.json`, `secrets_json`, `source_web_finding`, logs y referencias de EvidenceStore.
- **Historial / AuditLog**: cronología de importación, clasificación, redacción, validación, exportación, handoff, revelado y archivado.
- **Hermes Agent Lab**: parsers, normalizadores, reglas de detección y `evidence_schema` creados o ajustados en laboratorio.

### Tipos oficiales de credenciales

El catálogo oficial de `credential_type` admite los siguientes valores:

- `username_password`
- `hash`
- `cookie`
- `jwt`
- `api_key`
- `oauth_token`
- `refresh_token`
- `bearer_token`
- `session_id`
- `wifi_psk`
- `android_hardcoded_secret`
- `browser_webview_secret`
- `cloud_key`
- `ssh_private_key_candidate`
- `tls_certificate_material_candidate`
- `wallet_seed_or_keystore`
- `unknown_secret_format`

Todo valor sensible se guarda y visualiza enmascarado por defecto. El tipo `unknown_secret_format` existe para hallazgos que requieren clasificación humana, LaIA/Mistral o reglas nuevas de Hermes Agent antes de permitir handoff o validación.

### Ciclo de vida de credencial

El campo `credential_state` usa los siguientes estados documentales:

- `imported`: recibida desde módulo o fuente.
- `classified`: tipo detectado.
- `duplicate`: duplicado unido a credencial existente.
- `needs_review`: requiere revisión humana o asistencia LaIA/Mistral.
- `format_validated`: formato válido sin usar contra servicio.
- `offline_analyzed`: analizado sin conexión externa.
- `live_validation_pending`: pendiente de confirmación.
- `validated`: validación autorizada produjo evidencia.
- `invalid`: validación autorizada falló.
- `false_positive`: marcado como falso positivo.
- `sent_to_module`: enviado a otro módulo.
- `revocation_recommended`: requiere rotación o revocación.
- `archived`: cerrado y conservado por auditoría.

Ninguna credencial debe pasar a `validated` sin una evidencia vinculada en EvidenceStore. Todo cambio de estado debe registrar actor, motivo, origen, timestamp y política aplicada en AuditLog.

### Política de visibilidad y redacción

- Los valores completos nunca son visibles por defecto.
- `value_masked` es obligatorio en todo hallazgo y toda vista de panel.
- `hash_sha256` del valor se conserva para deduplicación sin exponer el secreto.
- El botón **Mostrar secreto** solo está disponible para roles autorizados.
- Cada revelado completo genera un evento AuditLog con operador, motivo, scope, timestamp y credencial afectada.
- Los logs nunca guardan el valor completo.
- Las exportaciones son enmascaradas por defecto.
- La exportación completa solo puede habilitarse con confirmación reforzada, Policy Engine aprobado, scope vigente y Kill Switch inactivo.
- Pantallas, reportes y PDF usan redacción por defecto.
- EvidenceStore conserva referencias y artefactos de soporte sin incluir secretos completos salvo excepción aprobada y auditada.

### Contrato JSON `credential_finding`

Contrato documental de hallazgo de credencial. Los valores mostrados son placeholders no sensibles.

```json
{
  "type": "credential_finding",
  "credential_id": "uuid",
  "credential_state": "imported",
  "source_module": "android_analysis",
  "source_vector": "analysis_apps",
  "source_evidence_id": "ev-1234",
  "target_id": "target-uuid",
  "linked_assets": ["device-android-5678", "api.example.local"],
  "credential_type": "api_key",
  "value_masked": "AKIA**************",
  "hash_sha256": "sha256...",
  "confidence": 0.95,
  "severity": "high",
  "issuer": "aws",
  "audience": null,
  "domains": ["api.example.local"],
  "expires_at": null,
  "redaction_policy": "masked_by_default",
  "rotation_recommended": true,
  "revocation_recommended": true,
  "allowed_actions": ["format_validate", "send_to_cloud", "export_masked"],
  "handoff_targets": ["cloud", "web"],
  "validation_mode": "format_only",
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true,
  "evidence_ids": ["ev-1234"],
  "created_at": "2026-06-02T10:00:00Z"
}
```

### Contrato JSON `credential_action`

Contrato documental de acción sobre credencial. El contrato describe intención, controles, evidencia esperada y condiciones de parada.

```json
{
  "type": "credential_action",
  "credential_id": "uuid",
  "action_type": "format_validate",
  "target_service": null,
  "params": {
    "mode": "format_only",
    "redaction": "masked"
  },
  "expected_evidence": ["validation_log", "screenshot_panel"],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": false,
  "policy_check": true,
  "stop_conditions": ["kill_switch_active", "out_of_scope", "confirmation_missing"]
}
```

Las acciones `live_validation`, `reuse_token`, `send_to_module`, `hash_cracking`, `export_full` y `delete_secret` requieren confirmación explícita. Cualquier acción denegada por Policy Engine, Kill Switch, scope o falta de confirmación termina sin revelar secretos y deja registro en AuditLog.

### Modos de validación

- `format_only`: revisa regex, estructura, prefijo, longitud y tipo. No contacta servicios.
- `offline_analysis`: decodifica JWT, claims, expiración, algoritmo, scopes, atributos de cookie y tipo de hash sin usar el secreto contra un servicio.
- `live_validation`: prueba controlada contra servicio autorizado. Siempre requiere confirmación explícita, Policy Engine aprobado, Kill Switch inactivo, scope vigente y EvidenceStore para registrar el resultado.


## Herramientas, VersionLock y acciones asistidas

Esta sección amplía el Módulo 5 solo como documentación de producto asistido. Las herramientas se describen como capacidades nominales; no se instala nada, no se fijan versiones definitivas, no se añaden comandos y no se documentan credenciales reales. El catálogo técnico existente conserva sus técnicas declarativas con `status: IMPLEMENTACION_USUARIO_REQUERIDA` hasta que el usuario implemente y promocione cada integración.

### Herramientas objetivo y VersionLock

Las siguientes herramientas quedan documentadas como capacidades objetivo, siempre sujetas a VersionLock, `tool_healthcheck`, Policy Engine, scope, confirmación cuando aplique y redacción por defecto:

- **Hashcat**: cracking offline autorizado; la versión real se resuelve por VersionLock.
- **John the Ripper Jumbo**: cracking offline complementario; la versión real se resuelve por VersionLock.
- **TruffleHog**: detección/verificación de secretos; la versión real se resuelve por VersionLock.
- **Gitleaks**: detección de secretos en repositorios o archivos; la versión real se resuelve por VersionLock.
- **jwt_tool o parser interno JWT**: análisis offline de JWT; si se usa herramienta externa, la versión real se resuelve por VersionLock.
- **Name-That-Hash/hashid o parser interno**: identificación de hashes; si se usa herramienta externa, la versión real se resuelve por VersionLock.
- **Impacket, NetExec, Certipy, BloodHound, Responder, mitm6, Hydra, Medusa y LaZagne**: ya aparecen en el catálogo y deben mantenerse como técnicas declarativas `IMPLEMENTACION_USUARIO_REQUERIDA`.

Las versiones finales se resuelven con VersionLock y `tool_healthcheck`, incluyendo fuente, versión, hash del artefacto si aplica, runtime, compatibilidad, motivo de uso o motivo de bloqueo. No se fijan versiones antiguas como definitivas y ninguna herramienta queda habilitada por esta documentación.

### Handoff de entrada al Módulo 5

El Módulo 5 recibe hallazgos desde fuentes autorizadas y los normaliza en la bandeja de importación sin exponer valores completos por defecto:

- **M1 OSINT**: filtraciones, repositorios, paste sites, dominios y emails.
- **M4 Web**: JWT, cookies, API keys, formularios, endpoints y código fuente.
- **M6 MITM/Red**: PCAP, cookies, NTLM, HTTP Basic, tokens y credenciales de tráfico.
- **M9 Scraping Inteligente**: credenciales en fuentes abiertas o repositorios autorizados.
- **M13 Android**: secrets de APK, cookies WebView, tokens, wallets/keystore y API keys.
- **Futuros M14 Phishing y M15 Cloud**: hallazgos importables cuando esos módulos existan y estén dentro de scope.
- **Carga manual del usuario**: entradas explícitas con redacción, operador y scope.
- **Importación desde EvidenceStore**: hallazgos previamente conservados como evidencia redacted-by-default.

Contrato documental `credential_handoff`:

```json
{
  "type": "credential_handoff",
  "source_module": "android",
  "source_vector": "analysis_apps",
  "source_evidence_id": "ev-android-001",
  "credential_finding": {
    "credential_type": "jwt",
    "value_masked": "eyJhbGciOi********",
    "hash_sha256": "sha256...",
    "confidence": 0.92,
    "severity": "high"
  },
  "target_context": {
    "target_id": "target-uuid",
    "app_package": "com.example.app",
    "domain": "api.example.local"
  },
  "requested_action": "import_and_classify",
  "requires_confirmation": false,
  "operator": "admin"
}
```

### Android Vector 6 hacia Módulo 5

Cuando **Android > Análisis de Apps** encuentre API keys, JWT, cookies, OAuth tokens, refresh tokens, hardcoded credentials, wallets o keystore, el panel muestra el botón **Enviar a Credenciales**. Al pulsarlo:

- Empaqueta un `credential_handoff`.
- Conserva `source_evidence_id` para trazabilidad en EvidenceStore.
- Módulo 5 importa el hallazgo a la bandeja de credenciales.
- LaIA clasifica el tipo, resume contexto y explica el riesgo.
- El usuario decide si procede validación controlada, handoff a otro módulo o archivo.

### Handoff de salida desde Módulo 5

El Módulo 5 puede proponer acciones de salida hacia otros módulos, siempre enmascaradas por defecto, con AuditLog y confirmación cuando la acción lo requiera:

- **M4 Web**: cookie, JWT o API key asociada a endpoint.
- **M1 OSINT**: email, dominio, repositorio o fuente abierta asociada a exposición de credenciales.
- **M15 Cloud futuro**: AWS, Azure o GCP key con scope documentado.
- **M13 Android**: credencial WebView o app relacionada.
- **M6 MITM**: cookie o token asociado a tráfico.
- **M12 Orquestación**: plan de validación controlada o fallback.
- **Hermes Agent Lab**: parser, regla o normalizador.

Contrato documental `credential_to_module_action`:

```json
{
  "type": "credential_to_module_action",
  "credential_id": "uuid",
  "target_module": "cloud",
  "handoff_reason": "cloud_key_detected",
  "payload_redaction": "masked",
  "expected_next_action": "enumerate_scope_readonly",
  "requires_confirmation": true,
  "operator": "admin"
}
```

### Evidencias en EvidenceStore

EvidenceStore conserva evidencias vinculadas a credenciales con redacción por defecto y metadatos suficientes para auditoría, scoring y grafo de superficie de ataque. Tipos documentales:

- `secrets_json`
- `cookies_json`
- `jwt_decoded_json`
- `hash_file`
- `hash_type_report`
- `validation_log`
- `source_pcap`
- `source_apk_analysis`
- `source_web_finding`
- `source_repo_scan`
- `screenshot_panel`
- `timeline_json`
- `credential_graph_json`
- `final_credentials_report`

Cada evidencia debe guardar `credential_id`, `source_module`, `source_evidence_id`, `target_id`, `operator`, `timestamp`, `redaction_policy`, `hash_sha256` y `scope`. Ningún tipo de evidencia debe incorporar valores completos por defecto en pantallas, logs, reportes o exportaciones.

### Scoring X5 para credenciales

X5 calcula scoring de credenciales con reglas orientadas a evidencia, control de falsos positivos y estado de implementación:

- Hallazgo sin evidencia: no puntúa.
- Secreto con formato válido: puntuación baja o media según confianza.
- Credencial validada con evidencia: sube el score de la técnica.
- Falso positivo: baja el score del detector o parser.
- Duplicado: no sube score.
- Cracking iniciado pero sin resultado: no sube éxito.
- Cracking con resultado y evidencia: sube score si el scope es válido.
- Live validation bloqueada por política: no penaliza la técnica y registra bloqueo.
- Técnicas `IMPLEMENTACION_USUARIO_REQUERIDA`: no puntúan hasta promoción.

Campos recomendados para eventos de scoring:

- `technique_id`
- `credential_type`
- `source_module`
- `evidence_valid`
- `false_positive`
- `validation_mode`
- `score_before`
- `score_after`
- `score_delta`
- `operator`

### Relación con Attack Surface Graph

Las credenciales no son registros aislados. Deben relacionarse con Target, Host, Servicio, App, Dominio, Usuario/Cuenta, Módulo origen, Técnica origen, Evidencia, Módulo destino y Next Step para que LaIA/Mistral, X5 y M12 puedan explicar impacto y rutas autorizadas de validación o mitigación.

Nodos y relaciones documentales:

- `Credential`
- `Credential OBSERVED_IN Evidence`
- `Credential BELONGS_TO Account`
- `Credential TARGETS Service`
- `Credential DISCOVERED_BY Technique`
- `Credential SUGGESTS_NEXT_STEP ModuleAction`


## LaIA, Hermes Agent, cierre seguro e informe final

Esta sección cierra el refuerzo documental del Módulo 5. Mantiene el módulo como producto asistido, evolutivo y controlado, sin implementar código, endpoints, workers, base de datos, tests ni requisitos nuevos. No contiene credenciales reales, hashes reales, comandos operativos ni valores sensibles completos.

### LaIA/Mistral dentro del Módulo 5

LaIA/Mistral está activa en todo el panel **Credenciales** como asistente contextual y cerebro táctico. No ejecuta acciones sensibles por sí sola; propone, explica, prepara contratos y solicita confirmación cuando corresponde. Sus funciones documentales dentro del Módulo 5 son:

- Clasificar secretos por `credential_type`.
- Explicar riesgo, impacto, confianza y severidad.
- Detectar duplicados mediante metadatos, `hash_sha256` y contexto de origen.
- Relacionar credenciales con target, app, dominio, servicio, usuario/cuenta y evidencia.
- Sugerir validación controlada en modo `format_only`, `offline_analysis` o `live_validation` cuando el scope lo permita.
- Sugerir handoff a Web, Cloud, Android, MITM/Red u OSINT.
- Generar contratos `credential_action` para revisión y ejecución autorizada por X5/OjoRouter.
- Preparar el informe final con redacción por defecto.
- Pedir a Hermes Agent un parser, regla o normalizador si falta capacidad para clasificar, normalizar o explicar un hallazgo.

Contexto que recibe LaIA/Mistral antes de recomendar acciones:

- `credential_finding`.
- `source_module`.
- `source_evidence`.
- `target_context`.
- `scope`.
- Permisos del operador.
- Herramientas disponibles y su estado VersionLock/tool_healthcheck.
- Estado de Kill Switch.
- `redaction_policy`.
- Historial, scoring y cambios de estado.
- Handoff posibles y módulos destino permitidos.

### Hermes Agent en Credenciales

Hermes Agent entra en el Módulo 5 cuando falta una capacidad de análisis, normalización, detección o contrato, siempre en laboratorio y sin operar directamente sobre secretos reales fuera del flujo autorizado. Casos documentales de entrada:

- Formato de token desconocido.
- Cookie, JWT o API key no reconocida.
- Nueva estructura de secreto en APK.
- Regla de detección personalizada.
- Parser para fuente nueva.
- Normalizador de evidencia.
- Detector de cloud key específico.
- `evidence_schema` faltante.
- Integración con nuevo módulo o fuente.
- Validación de formato sin uso real contra servicios.

Acciones estructuradas de Hermes Agent:

- `create_secret_parser`
- `create_cookie_normalizer`
- `create_jwt_analyzer`
- `create_cloud_key_classifier`
- `create_secret_detection_rule`
- `create_evidence_normalizer`
- `create_credential_handoff_adapter`
- `repair_false_positive_filter`
- `generate_credentials_report_template`

Hermes Agent trabaja solo en `modules/laboratory/<technique_id>/` y puede generar artefactos de laboratorio documentados como:

- `technique.json`
- `worker.py`
- Parser específico de la fuente o secreto.
- `evidence_schema.json`
- `requirements.generated.txt`
- `README.md`

La promoción fuera del laboratorio solo procede tras sandbox, revisión, aprobación humana, VersionLock, Policy Engine, Kill Switch, EvidenceStore y AuditLog. Hermes Agent no autoaprueba, no instala, no promociona y no ejecuta validaciones reales sin X5/OjoRouter y confirmación cuando aplique.

### Acciones que requieren confirmación explícita

Requieren confirmación explícita reforzada, scope vigente, Policy Engine aprobado, Kill Switch inactivo y AuditLog:

- Live validation contra servicio.
- Reutilizar cookie o token.
- Enviar credencial a otro módulo para ejecución.
- Convertir hash en tarea de cracking.
- Exportar informe completo.
- Mostrar secreto completo.
- Borrar o limpiar secretos.
- Usar credenciales en un plan automático.
- Cualquier acción fuera de solo lectura.

No requieren confirmación fuerte, aunque mantienen redacción, trazabilidad y controles básicos:

- Clasificar.
- Detectar duplicado.
- Enmascarar.
- Decodificar JWT offline.
- Analizar expiración, issuer o audience.
- Calcular `hash_sha256`.
- Relacionar con evidencia.

### Cierre seguro del Módulo 5

El panel incluye el flujo/botón **Cerrar auditoría de credenciales** para terminar la revisión de forma controlada. Al activarlo, el módulo debe:

1. Detener validaciones activas.
2. Pausar o cerrar tareas de cracking.
3. Guardar evidencias pendientes.
4. Recalcular estados de credenciales.
5. Deduplicar hallazgos.
6. Generar timeline.
7. Generar informe si el usuario confirma.
8. Exportar versión enmascarada por defecto.
9. Registrar AuditLog de cierre y decisiones.
10. Recomendar rotación o revocación cuando aplique.
11. Marcar la auditoría como `closed`.

El cierre seguro no revela secretos completos por defecto y no ejecuta nuevas validaciones. Si una tarea no puede cerrarse de forma inmediata, queda registrada como pendiente, pausada o bloqueada con motivo y evidencia asociada.

### Informe final del Módulo 5

La estructura documental del PDF final del Módulo 5 incluye:

- Resumen ejecutivo.
- Total de credenciales por tipo y severidad.
- Fuentes: M4, M6, M9, M13, manual, EvidenceStore y futuros módulos.
- Tipos encontrados.
- Credenciales enmascaradas.
- Targets, apps, servicios y dominios relacionados.
- Evidencias asociadas.
- Validaciones y control de estado.
- Hashes y tareas offline.
- Handoff a otros módulos.
- Hallazgos falsos positivos y duplicados.
- Recomendaciones LaIA.
- Rotación o revocación sugerida.
- AuditLog de decisiones y aprobaciones.

El informe final usa redacción por defecto. La exportación completa solo puede existir con confirmación reforzada y queda registrada en AuditLog.

### Criterios de aceptación documental M5

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

## PARTE 1/3 — SPRAYING Y RELAY INICIAL

### Formato común

status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
adapter: CredentialServiceAdapter
evidence: credential_test_summary, auth_signal_summary, raw_output_path, normalized_json
notes: no_commands_in_docs,no_wordlists_in_docs,user_logic_required,redaction_required=true,requires_confirmation=true

### Técnicas

#### 1. credentials.hydra_contextual_passwords

tool: THC Hydra
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: CREDENTIALS
hook: app/modules/credentials_auth/hydra_contextual_passwords.py::HydraContextualPasswordsTechnique.execute

#### 2. credentials.medusa_contextual

tool: Medusa
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: CREDENTIALS
hook: app/modules/credentials_auth/medusa_contextual.py::MedusaContextualTechnique.execute

#### 3. credentials.netexec_password_spraying

tool: NetExec
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: CREDENTIALS
hook: app/modules/credentials_auth/netexec_password_spraying.py::NetexecPasswordSprayingTechnique.execute

#### 4. credentials.responder_llmnr_nbtns_mdns

tool: Responder
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: ACTIVE_SENSITIVE
hook: app/modules/credentials_auth/responder_llmnr_nbtns_mdns.py::ResponderLlmnrNbtnsMdnsTechnique.execute

#### 5. credentials.mitm6_dhcpv6_spoofing

tool: mitm6
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: ACTIVE_SENSITIVE
hook: app/modules/credentials_auth/mitm6_dhcpv6_spoofing.py::Mitm6Dhcpv6SpoofingTechnique.execute

## PARTE 2/3 — RELAY, TICKETS, HASHES Y SECRETOS

Regla:
Catálogo declarativo para workers, adapters, hooks, evidence y estados.
Sin comandos, payloads, wordlists, credenciales reales, hashes reales ni pasos operativos.

### Formato común para 6-11

status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
adapter: CredentialServiceAdapter
notes: no_commands_in_docs,no_wordlists_in_docs,no_credentials_in_docs,user_logic_required,redaction_required=true,requires_confirmation=true

#### 6. credentials.impacket_ntlmrelayx

tool: Impacket ntlmrelayx
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: ACTIVE_SENSITIVE
evidence: relay_attempt_summary, auth_signal_summary, raw_output_path, normalized_json
hook: app/modules/credentials_auth/impacket_ntlmrelayx.py::ImpacketNtlmrelayxTechnique.execute

#### 7. credentials.kerberoasting_getuserspns

tool: Impacket GetUserSPNs
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: CREDENTIALS
evidence: kerberos_ticket_summary, account_exposure_summary, raw_output_path, normalized_json
hook: app/modules/credentials_auth/kerberoasting_getuserspns.py::KerberoastingGetuserspnsTechnique.execute

#### 8. credentials.asrep_roasting_getnpusers

tool: Impacket GetNPUsers
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: CREDENTIALS
evidence: asrep_candidate_summary, account_exposure_summary, raw_output_path, normalized_json
hook: app/modules/credentials_auth/asrep_roasting_getnpusers.py::AsrepRoastingGetnpusersTechnique.execute

#### 9. credentials.hashcat_offline

tool: Hashcat
version: latest-release-lock
runtime: gpu_or_cpu
worker: GPUWorker
perm: CREDENTIALS
evidence: hash_cracking_summary, recovered_secret_metadata, redacted_result_path, normalized_json
hook: app/modules/credentials_auth/hashcat_offline.py::HashcatOfflineTechnique.execute
notes_extra: offline_only=true, no_hashes_in_docs, no_cracked_values_in_docs

#### 10. credentials.john_offline

tool: John the Ripper
version: latest-release-lock
runtime: cpu_or_gpu
worker: GPUWorker
perm: CREDENTIALS
evidence: hash_cracking_summary, recovered_secret_metadata, redacted_result_path, normalized_json
hook: app/modules/credentials_auth/john_offline.py::JohnOfflineTechnique.execute
notes_extra: offline_only=true, no_hashes_in_docs, no_cracked_values_in_docs

#### 11. credentials.exposed_config_secret_search

tool: TruffleHog + Gitleaks
version: latest-release-lock
runtime: python_or_binary
worker: PythonToolWorker
perm: CREDENTIALS
evidence: secret_candidate_summary, file_location_summary, redacted_result_path, normalized_json
hook: app/modules/credentials_auth/exposed_config_secret_search.py::ExposedConfigSecretSearchTechnique.execute
notes_extra: redact_all_secrets=true, no_secret_values_in_docs, local_scope_only=true

## PARTE 3/3 — CREDENCIALES LOCALES, CLAVES, ADCS Y RUTAS AD

Regla:
Catálogo declarativo para workers, adapters, hooks, evidence y estados.
Sin comandos, payloads, wordlists, credenciales reales, hashes reales, claves reales ni pasos operativos.

### Formato común para 12-16

status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
adapter: CredentialServiceAdapter
notes: no_commands_in_docs,no_wordlists_in_docs,no_credentials_in_docs,no_keys_in_docs,user_logic_required,redaction_required=true,requires_confirmation=true

#### 12. credentials.lazagne_local_credentials

tool: LaZagne
version: latest-release-lock
runtime: windows_binary_or_python
worker: WindowsWorker
perm: CREDENTIALS
evidence: local_credential_source_summary, redacted_result_path, normalized_json
hook: app/modules/credentials_auth/lazagne_local_credentials.py::LazagneLocalCredentialsTechnique.execute
notes_extra: local_authorized_host_only=true, redact_all_values=true

#### 13. credentials.ssh_private_key_discovery

tool: internal file scanner
version: internal
runtime: python_lib
worker: PythonToolWorker
perm: CREDENTIALS
evidence: key_candidate_summary, file_location_summary, redacted_result_path, normalized_json
hook: app/modules/credentials_auth/ssh_private_key_discovery.py::SshPrivateKeyDiscoveryTechnique.execute
notes_extra: no_key_material_in_evidence=true, local_scope_only=true

#### 14. credentials.certipy_esc1_esc13

tool: Certipy
version: latest-release-lock
runtime: wsl2
worker: WSLWorker
perm: CREDENTIALS
evidence: adcs_exposure_summary, certificate_template_summary, raw_output_path, normalized_json
hook: app/modules/credentials_auth/certipy_esc1_esc13.py::CertipyEsc1Esc13Technique.execute
notes_extra: adcs_assessment_only_default=true, no_certificate_material_in_docs=true

#### 15. credentials.bloodhound_privilege_paths

tool: BloodHound.py + BloodHound CE
version: latest-release-lock
runtime: wsl2_or_local_service
worker: WSLWorker
perm: ACTIVE_SENSITIVE
evidence: privilege_path_summary, graph_export_path, normalized_json
hook: app/modules/credentials_auth/bloodhound_privilege_paths.py::BloodhoundPrivilegePathsTechnique.execute
notes_extra: graph_analysis_only_default=true, no_live_changes=true

#### 16. credentials.dcsync_marker

tool: internal AD risk marker
version: internal
runtime: python_lib
worker: PythonToolWorker
perm: CREDENTIALS
evidence: dcsync_risk_summary, privilege_indicator_summary, normalized_json
hook: app/modules/credentials_auth/dcsync_marker.py::DcsyncMarkerTechnique.execute
notes_extra: marker_only=true, no_replication_action=true, no_secret_extraction=true

## Estado documental del módulo

Módulo 5 — Credenciales y Autenticación queda documentado como catálogo técnico de conexiones, workers, adapters, hooks, evidence y estado de implementación.
Las 16 técnicas quedan marcadas como IMPLEMENTACION_USUARIO_REQUERIDA.
LaIA solo rellena contexto y analiza evidencia.
X5/OjoRouter valida scope, permisos, inputs, worker, evidence y confirmación.
Hermes solo crea wrappers, parsers o schemas en sandbox si falta una pieza.
Este documento no contiene comandos operativos, payloads, wordlists, credenciales reales, hashes reales ni claves reales.
