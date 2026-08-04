# MÓDULO 14 — PHISHING AUTOMATIZADO

## Ronda 1 — Base documental del módulo

### 1. Objetivo

Establecer la base documental del Módulo 14. Solo documentación. No implementar código, endpoints, workers, base de datos, tests, requirements ni scripts funcionales. Todo queda como especificación de producto y laboratorio.

### 2. Ubicación

Este contenido se registra en `docs/techniques/14_PHISHING.md` como primera sección documental del módulo.

### 3. Filosofía del módulo

Este módulo automatiza campañas de simulación y concienciación para verificar la resiliencia de una organización frente a intentos de ingeniería social. La IA Mistral personaliza el señuelo, selecciona el portal a clonar y redacta el texto del mensaje. X5 ejecuta las herramientas de Kali WSL2. Hermes evoluciona el arsenal si el portal objetivo cambia su estructura o aparecen nuevas protecciones.

### 4. Herramientas y versiones en Kali WSL2 con versionlock

Todas las herramientas se instalan desde repositorios oficiales de Kali o fuentes verificadas. Las versiones se bloquean en el fichero `version_lock.py` del proyecto.

- Evilginx (latest): `git clone https://github.com/kgretzky/evilginx2`
- Gophish (latest-release-lock): `https://github.com/gophish/gophish`
- SET (latest): `sudo apt install setoolkit`
- Metasploit Framework (latest-release-lock): `sudo apt install metasploit-framework`
- swaks (latest): `sudo apt install swaks`
- Certbot (latest): `sudo apt install certbot`
- Dolphin Mistral Nemo 12B (LaIA): generación de textos de señuelo, personalización con datos de OSINT y redacción de informes.
- Hermes (DeepSeek API): creación de módulos personalizados si el portal objetivo cambia su protección o estructura.

### 5. Panel de control y subpáginas

La pestaña independiente `Simulación` en Ojo de Dios se divide en las siguientes subpáginas.

#### 5.1 Campañas

- Tabla con las campañas activas y pasadas: nombre, objetivo, tipo (credenciales, sesión, payload), estado (draft, sending, active, completed, etc.) y resultados.
- Botón `Nueva Campaña`: inicia el asistente de Mistral.

#### 5.2 Plantillas

- Galería de plantillas de correo predefinidas (restablecimiento de contraseña, verificación de seguridad, notificación de la empresa, etc.).
- Editor de plantillas con variables (nombre, empresa, cargo) que Mistral rellena automáticamente con datos del Módulo 1 (OSINT).

#### 5.3 Portales clonados

- Lista de portales disponibles para clonar: Office 365, Google Workspace, iCloud, Facebook, LinkedIn, etc.
- Botón `Clonar nuevo portal`: Mistral analiza la URL proporcionada y configura Evilginx o Gophish para servir la copia.

#### 5.4 Resultados

- Visor en tiempo real de credenciales y tokens capturados, con redacción o enmascaramiento por defecto.
- Botón `Enviar a Credenciales` para transferir los hallazgos al Módulo 5.
- Historial de campañas con métricas (correos enviados, abiertos, credenciales capturadas).

### 6. Estados de una campaña

- `draft`: la campaña se está configurando.
- `configured`: parámetros completos, pendiente de revisión.
- `pending_approval`: esperando confirmación del usuario.
- `scheduled`: programada para envío futuro.
- `sending`: correos en proceso de envío.
- `active`: portal activo y recolectando credenciales.
- `collecting_results`: campaña finalizada, procesando datos.
- `completed`: finalizada con éxito.
- `paused`: pausada por el usuario.
- `blocked_by_policy`: denegada por el Policy Engine.
- `error`: fallo durante la ejecución.
- `closed`: cerrada y evidencias archivadas.

### 7. Técnicas registradas y contrato JSON

- `phishing.credential_harvesting`: campaña clásica con portal clonado.
- `phishing.session_hijacking`: captura de token de sesión con Evilginx.
- `phishing.spear_phishing_payload`: correo personalizado con adjunto malicioso.
- `phishing.portal_clone`: clonación de un nuevo portal.

Contrato JSON base para una campaña:

```json
{
  "type": "phishing_action",
  "campaign_id": "camp-001",
  "technique_id": "phishing.credential_harvesting",
  "params": {
    "target_emails": ["ceo@example.com", "cfo@example.com"],
    "template": "password_reset",
    "portal": "office365",
    "smtp_server": "smtp.example.com",
    "from_email": "it@example.com"
  },
  "expected_evidence": [
    "campaign_config_json",
    "template_rendered_html",
    "landing_page_snapshot",
    "delivery_log",
    "open_events_json",
    "click_events_json",
    "credential_handoff_json",
    "campaign_metrics_json",
    "screenshots",
    "audit_log",
    "final_campaign_report"
  ],
  "scope": "laboratory",
  "operator": "admin",
  "requires_confirmation": true
}
```

### 8. Confirmaciones explícitas

Las siguientes acciones requieren confirmación del usuario antes de ejecutarse:

- Enviar campaña.
- Activar portal clonado.
- Recolectar credenciales o tokens.
- Enviar payload adjunto.
- Exportar resultados completos.
- Mostrar valores sensibles sin enmascarar.
- Realizar handoff al Módulo 5.

### 9. Handoff con otros módulos

- Módulo 1 (OSINT): Mistral solicita información del objetivo para personalizar el señuelo.
- Módulo 5 (Credenciales): las credenciales y tokens capturados se empaquetan con el contrato `credential_handoff` y se envían a M5.
- Módulo 12 (Orquestación): todas las acciones heredan el flujo M12 (validación, ejecución, scoring, auditoría).
- Módulo 16 (Evidencia / Ops / Calidad): todas las campañas generan handoff a M16 con hashes, timeline, cadena de custodia interna, informe final, exportación enmascarada y métricas completas.

### 10. Intervención de Hermes Agent

Hermes entra en juego si:

- El portal objetivo cambia su estructura y se necesita una nueva plantilla.
- Aparece un nuevo mecanismo anti-phishing no catalogado.
- Se requiere un módulo de envío alternativo (nuevo SMTP, relay, etc.).

En todos los casos, Hermes genera el código en laboratorio, lo prueba en sandbox y, tras aprobación del usuario, lo promociona al arsenal.

Catálogo declarativo de conexiones. Sin código, comandos, tests, requirements, payloads, credenciales reales, configuraciones funcionales ni pasos operativos.

module_id: phishing
title: MÓDULO 14 — PHISHING AUTOMATIZADO
status_default: IMPLEMENTACION_USUARIO_REQUERIDA
docker_allowed: false

## Submódulo 14a — Social Engineering Toolkit SET

submodule_id: phishing.set
panel: Phishing > SET
runtime_preferente: wsl2_kali
install_profile: kali-linux-large_or_toolhealth
toolhealth: setoolkit, metasploit-framework
versionlock: resolve_real_version_in_environment
workers: PhishingWorker, SETWorker, WSLWorker, CampaignWorker, EvidenceWorker, AIWorker
status_default: IMPLEMENTACION_USUARIO_REQUERIDA
docker_allowed: false

### Integración

SET vive dentro del Módulo 14. El panel Phishing muestra acceso rápido “Campaña rápida con SET”.
Mistral decide SET o Evilginx según objetivo: SET para spear-phishing, clonación rápida, payload_profile y listener_profile; Evilginx para token/MFA proxy flow.
X5 valida scope, campaign_authorization, recipients_profile, template_profile, worker, ToolHealth, EvidenceStore y confirmación.
Hermes puede crear wrappers, parsers, schemas, templates y panel_fields en sandbox con target_path real.

### Panel SET

sections: quick_campaign, recipients, template_editor, payload_profile, listener_status, incoming_events, evidence
actions: crear_campaña, previsualizar, ejecutar_con_confirmacion, detener_listener, ver_eventos, exportar_evidencia
fields: campaign_name, target_group, recipients_profile, message_template, landing_profile, payload_profile, listener_profile, evidence_profile
states: DRAFT, READY, CONFIRMATION_REQUIRED, RUNNING, LISTENER_ACTIVE, EVENT_RECEIVED, SUCCESS, FAILED, STOPPED

### Contrato Mistral -> X5

intent, campaign_profile, target_group, recipients_profile, selected_tool, selected_technique, template_profile, payload_profile, listener_profile, evidence_expected, requires_confirmation, user_explanation

### Resultado X5 -> Mistral

run_id, campaign_id, technique_id, status, sent_summary, listener_state, incoming_event_summary, artifact_paths, evidence_ids, error_code, next_recommended_techniques

### Común

status: IMPLEMENTACION_USUARIO_REQUERIDA
docker: false
scope_required: true
campaign_authorization_required: true
requires_confirmation: true
evidence: campaign_summary, sent_log_reference, listener_state_summary, incoming_event_summary, generated_artifact_reference, screenshot_reference, raw_output_path, normalized_json
graph: CampaignNode, RecipientNode, TemplateNode, PayloadArtifactNode, ListenerNode, EvidenceNode
notes: catalog_only,user_logic_required,no_commands_in_docs,no_payload_logic_in_docs,no_credentials_in_docs
hook: app/modules/phishing/<id_sin_phishing>.py::<ClasePascal>Technique.execute

#### 1. phishing.set.spear_phishing

tool: SET setoolkit
version: latest-release-lock
runtime: wsl2
worker: SETWorker
perm: PHISHING_CONTROLLED
adapter: SetSpearPhishingAdapter
fields: recipients_profile, message_template, attachment_profile, payload_profile, sender_profile, evidence_profile
success_evidence: sent_log_reference, delivery_summary, incoming_event_summary

#### 2. phishing.set.site_cloner

tool: SET setoolkit
version: latest-release-lock
runtime: wsl2
worker: SETWorker
perm: PHISHING_CONTROLLED
adapter: SetSiteClonerAdapter
fields: source_site_profile, local_hosting_profile, landing_profile, capture_profile, evidence_profile
success_evidence: cloned_site_reference, local_service_state, interaction_log_reference

#### 3. phishing.set.payload_generator

tool: SET + Metasploit Framework
version: SET latest-release-lock + Metasploit 6.4.131
runtime: wsl2
worker: SETWorker
perm: PHISHING_SENSITIVE
adapter: SetPayloadGeneratorAdapter
fields: payload_profile, platform_profile, output_artifact_profile, evidence_profile
success_evidence: generated_artifact_reference, payload_metadata_redacted, hash_reference

#### 4. phishing.set.listener

tool: SET + Metasploit Framework
version: SET latest-release-lock + Metasploit 6.4.131
runtime: wsl2
worker: SETWorker
perm: PHISHING_SENSITIVE
adapter: SetListenerAdapter
fields: listener_profile, session_profile, event_capture_profile, evidence_profile
success_evidence: listener_state_summary, incoming_event_summary, screenshot_reference

## Anexo 14a — Campos asistidos por Mistral y revisión previa

### Objetivo

Dejar claro cómo Mistral interactúa con el usuario, cómo rellena datos faltantes y cómo entrega un plan validable a X5 antes de ejecutar SET.

### Campos que Mistral puede rellenar

Mistral puede proponer o completar:

- campaign_name
- target_group
- recipients_profile desde OSINT autorizado del Módulo 1
- message_subject
- message_body
- language_profile
- tone_profile
- template_profile
- landing_profile
- selected_tool: SET|Evilginx|manual_required
- selected_technique
- payload_profile
- listener_profile
- evidence_expected
- risk_summary
- user_explanation
- fallback_chain

### Campos que Mistral no puede inventar

Mistral no puede inventar:

- destinatarios reales si no vienen de OSINT/autorización;
- dominio de envío;
- servidor SMTP;
- credenciales SMTP;
- payload_profile autorizado;
- landing real si no está definida;
- evidencia;
- resultados;
- sesiones recibidas.

Si falta un dato obligatorio, debe devolver:

missing_inputs
manual_required: true
question_for_user

### Preguntas automáticas

Si falta recipients_profile:
“Falta la lista de destinatarios autorizados. ¿Quieres importarla desde OSINT o cargarla manualmente?”

Si falta sender_profile:
“Falta el perfil de envío. Indica dominio, SMTP autorizado o modo manual.”

Si falta payload_profile:
“Falta el perfil de payload autorizado. Selecciona uno aprobado o marca la campaña como simulación.”

Si falta landing_profile:
“Falta landing/local host profile. Indica sitio autorizado o usa modo local de laboratorio.”

### Revisión previa en panel

Antes de enviar el plan a X5, el panel Phishing > SET debe mostrar:

- herramienta elegida;
- técnica seleccionada;
- destinatarios;
- asunto;
- plantilla;
- payload_profile;
- listener_profile;
- evidencia esperada;
- riesgos;
- missing_inputs;
- botones: Aprobar, Editar, Cancelar.

Sin aprobación, X5 no ejecuta.

### Plan final Mistral -> X5

mistral_plan_json debe incluir:

intent
campaign_id
campaign_name
target_group
recipients_profile
sender_profile
selected_tool
selected_technique
template_profile
payload_profile
listener_profile
landing_profile
evidence_expected
fallback_chain
missing_inputs
requires_confirmation
risk_summary
user_explanation

### Validación X5

X5 debe validar:

- campaign_authorization;
- recipients_profile;
- sender_profile;
- selected_tool;
- selected_technique;
- ToolHealth SET/Metasploit;
- EvidenceStore;
- confirmation_profile;
- kill_switch si aplica;
- output paths;
- redaction_profile.

Si algo falla:
status: MANUAL_REQUIRED|MISSING_TOOL|CONFIRMATION_REQUIRED|FAILED_VALIDATION

### Hermes

Si falta una pieza, Hermes puede proponer en sandbox:

- template_schema;
- recipients_parser;
- SET wrapper;
- Metasploit listener parser;
- event parser;
- panel_fields;
- evidence_schema;
- fixture_demo.

Toda propuesta debe tener target_path real, revisión Mistral, validación X5 y aprobación del usuario antes de promocionar.

### Regla final

Mistral asiste y estructura.
X5 valida y ejecuta la lógica conectada.
Hermes propone piezas faltantes.
El usuario aprueba.
Nada se marca como funcional sin evidence real.

## Ronda 14B — Flujo asistido, preflight y recuperación

### 1. Objetivo

Definir el flujo de trabajo asistido, el preflight checklist y la recuperación ante errores del Módulo 14. Solo documentación. No implementar código.

### 2. Ubicación

Esta ronda se añade después de la Ronda 14A en `docs/techniques/14_PHISHING.md` y mantiene el carácter de especificación de producto y laboratorio.

### 3. Flujo de trabajo asistido (Mistral + X5 + Hermes)

#### 3.1 Inicio de la campaña con asistente Mistral

- El usuario accede a `Simulación > Campañas` y pulsa `Nueva Campaña`.
- Escribe en lenguaje natural: `Quiero simular un ataque de phishing contra el departamento de finanzas para verificar su concienciación`.
- Mistral consulta automáticamente el Módulo 1 (OSINT) para obtener emails, nombres, cargos y cualquier información pública autorizada del objetivo.
- Con esos datos, Mistral redacta el texto del correo (asunto y cuerpo) usando la plantilla seleccionada, personalizándola con el nombre y cargo del objetivo.
- Mistral selecciona el portal a clonar (Office 365, Google, etc.) y prepara los parámetros declarativos: dominio de simulación, certificados TLS y servidor SMTP.
- El plan completo se muestra en una ventana modal para revisión del usuario.
- La campaña pasa al estado `pending_approval`.

#### 3.2 Ejecución de la campaña

- El usuario revisa el plan (correo, plantilla, portal y lista de destinatarios) y pulsa `Confirmar y lanzar`.
- X5 valida el plan contra Policy Engine, Kill Switch, scope, permisos del operador, VersionLock y EvidenceStore antes de cualquier acción.
- X5 ejecuta únicamente acciones autorizadas dentro del laboratorio:
  - Si es simulación de sesión: despliega el perfil Evilginx autorizado y verifica certificados TLS.
  - Si es simulación clásica: prepara el portal con Gophish o SET según el perfil aprobado.
  - Envía los correos con swaks o el motor SMTP de Gophish cuando el perfil de envío está aprobado.
  - La campaña pasa a `sending` y luego a `active`.
- El panel `Resultados` muestra en tiempo real:
  - Correos enviados y entregados.
  - Correos abiertos, si se usa pixel de seguimiento aprobado.
  - Clics en el enlace.
  - Credenciales y tokens capturados, siempre enmascarados por defecto.
- Las evidencias se almacenan automáticamente en EvidenceStore.

#### 3.3 Intervención de Hermes (evolución del arsenal)

- Si durante la campaña se detecta que el portal objetivo ha cambiado (nueva protección, rediseño de la página de login, etc.), Mistral sugiere: `El portal ha cambiado. ¿Solicito a Hermes una actualización de la plantilla?`.
- El usuario acepta. Hermes analiza el nuevo portal dentro del laboratorio, genera una plantilla actualizada (phishlet de Evilginx o página HTML para Gophish) y la prueba en sandbox.
- Si la prueba es exitosa, Hermes notifica: `Nueva plantilla lista`. El usuario la promociona al arsenal y la campaña se reanuda con la nueva configuración aprobada.
- Si el objetivo usa un servicio de correo con protecciones avanzadas (DMARC, DKIM, SPF estrictos), Hermes puede proponer un perfil de dominio de simulación alternativo o un relay autorizado para mantener la entrega conforme a la política del laboratorio, sin omitir aprobación de usuario ni controles de Policy Engine.

### 4. Preflight checklist antes de lanzar una campaña

- [ ] Objetivo autorizado y dentro del scope del laboratorio.
- [ ] Lista de destinatarios verificada (emails válidos, no externos sin permiso).
- [ ] Plantilla de correo y portal clonado preparados.
- [ ] Dominio de simulación configurado y certificados TLS válidos.
- [ ] Servidor SMTP operativo o relay autorizado configurado.
- [ ] Kill Switch armado.
- [ ] Operador autorizado.
- [ ] Para campañas con payload adjunto: confirmación explícita del usuario y aviso de responsabilidad.
- [ ] VersionLock de herramientas verificado.

### 5. Errores y recuperación

#### 5.1 Portal no se clona correctamente

- El panel muestra `clone_failed`.
- Mistral sugiere verificar la URL, revisar el scope autorizado y solicitar a Hermes una plantilla personalizada en sandbox.

#### 5.2 Correos no se entregan (rebotados o marcados como spam)

- El panel muestra `delivery_failed`.
- Mistral sugiere revisar configuración SPF, DKIM, DMARC, reputación del dominio de simulación o cambiar a un servidor SMTP autorizado.

#### 5.3 El objetivo no interactúa con el correo

- Tras 24 horas sin aperturas, Mistral sugiere reenviar con otro asunto o desde otro remitente autorizado, manteniendo la trazabilidad de EvidenceStore.

#### 5.4 El portal es detectado y bloqueado

- Mistral notifica `portal_blacklisted`.
- X5 pausa la campaña, conserva evidencias y exige revisión del operador antes de cualquier cambio de dominio o infraestructura de laboratorio.

#### 5.5 Kill Switch activado

- Se detiene inmediatamente el envío de correos y se desactiva el portal de simulación.
- Se guardan las evidencias pendientes.
- El estado de la campaña cambia a `closed`.

#### 5.6 Policy bloquea la campaña

- El estado cambia a `blocked_by_policy`.
- Se muestra el motivo del bloqueo.
- La campaña no se ejecuta.

## Ronda 14C — Handoffs, scoring X5 y preparación M16

### 1. Objetivo

Definir los handoffs, el scoring X5 y la preparación para M16 del Módulo 14. Solo documentación. No implementar código.

### 2. Ubicación

Esta ronda se añade después de la Ronda 14B en `docs/techniques/14_PHISHING.md` y conserva el alcance documental, declarativo y de laboratorio.

### 3. Handoff con otros módulos

El Módulo 14 no trabaja aislado. Sus hallazgos y evidencias se comunican con otros módulos mediante contratos auditados y con redacción por defecto.

#### 3.1 Handoff con Módulo 1 — OSINT

- Antes de lanzar una campaña, Mistral solicita al Módulo 1 información autorizada del objetivo (emails, nombres, cargos y empresa).
- Esta información se usa para personalizar el señuelo dentro del scope del laboratorio.
- Contrato JSON:

```json
{
  "type": "osint_request",
  "source_module": "simulacion",
  "target": "Empresa X",
  "fields_required": ["emails", "names", "positions"],
  "scope": "laboratory",
  "operator": "admin"
}
```

#### 3.2 Handoff con Módulo 5 — Credenciales

- Las credenciales (usuario/contraseña), tokens de sesión y cookies capturados se empaquetan como `credential_handoff` y se envían a M5.
- Reglas:
  - `source_module = "simulacion"`.
  - `source_evidence_id` es obligatorio.
  - Redacción por defecto con valores enmascarados.
  - M5 clasifica, deduplica y decide acciones posteriores.
  - Mostrar valores completos requiere confirmación explícita y registro en AuditLog.

#### 3.3 Handoff con Módulo 12 — Orquestación

- Todas las acciones `phishing.*` heredan el flujo M12:
  - LaIA/Mistral genera el plan y rellena parámetros.
  - X5 valida scope, Policy Engine, Kill Switch y VersionLock.
  - EvidenceStore guarda evidencias y artefactos.
  - AuditLog registra decisiones, confirmaciones y accesos.
  - El scoring X5 solo se calcula con evidencia válida.
  - Hermes Agent se activa si falta plantilla, cambia el portal o aparecen nuevas protecciones.

#### 3.4 Handoff con Módulo 16 — Evidencia / Ops / Calidad

- Todas las campañas finalizadas generan un handoff automático a M16 con:
  - Hashes SHA256 de cada evidencia.
  - Timeline completo de la campaña.
  - Cadena de custodia interna (acceso, revelado, exportación y operador).
  - Informe final de campaña.
  - Exportación enmascarada por defecto.
  - Métricas completas (enviados, abiertos, clics y capturados).

### 4. Contrato JSON `phishing_handoff`

```json
{
  "type": "phishing_handoff",
  "source_module": "simulacion",
  "campaign_id": "camp-001",
  "evidence_ids": ["ev-001", "ev-002"],
  "target_module": "M5",
  "handoff_reason": "credentials_captured",
  "redaction_policy": "mask_all",
  "requires_confirmation": true,
  "operator": "admin",
  "created_at": "2026-06-03T10:00:00Z"
}
```

Campos obligatorios:

- `type`
- `source_module`
- `campaign_id`
- `evidence_ids`
- `target_module`
- `handoff_reason`
- `redaction_policy`
- `requires_confirmation`
- `operator`
- `created_at`

### 5. Scoring X5 del Módulo 14

- Solo puntúa si hay evidencia válida: credenciales capturadas, token de sesión, apertura de correo confirmada o clic en enlace.
- `delivery_failed` no penaliza la técnica si el fallo es del servidor SMTP.
- `blocked_by_policy` no penaliza la técnica.
- Una campaña exitosa con credenciales obtenidas sube el score de la técnica correspondiente.
- Una campaña con alta tasa de apertura pero sin credenciales sube parcialmente el score: el señuelo fue efectivo, pero el portal no convirtió.
- Técnicas en estado `IMPLEMENTACION_USUARIO_REQUERIDA` no puntúan hasta promoción.

### 6. Preparación para Módulo 16 (Evidencia / Ops / Calidad)

- Todas las evidencias del Módulo 14 deben cumplir:
  - SHA256 de cada archivo (correo enviado, credenciales, token y capturas).
  - Hashes encadenados en `timeline_json`.
  - Cadena de custodia interna (acceso, revelado, exportación y operador).
  - Exportación enmascarada por defecto.
  - Exportación completa solo con confirmación reforzada.
  - Metadatos: `campaign_id`, `technique_id`, `scope`, `operator` y `VersionLock`.
- Tipos de evidencia:
  - `credentials.json`: credenciales capturadas (usuario/contraseña), enmascaradas por defecto.
  - `session_token.txt`: token de sesión post-MFA, enmascarado por defecto.
  - `campaign_metrics.json`: métricas de la campaña (enviados, abiertos, clics y capturados).
  - `email_sent.eml`: copia del correo enviado.
  - `landing_page_snapshot.png`: captura del portal clonado de laboratorio.
  - `audit_log`: registro de todas las acciones y decisiones.
  - `final_campaign_report`: informe compilado de la campaña.


## Ronda 14C-bis — Pantallas de trabajo, roles IA e interacción

### 1. Objetivo

Corregir las carencias detectadas en las rondas 14A, 14B y 14C, y ampliar la documentación con las pantallas de trabajo detalladas para cada herramienta, los roles explícitos de las IAs (Mistral, DeepSeek, Hermes) y el área de interacción del usuario. Solo documentación. No implementar código.

### 2. Ubicación

Esta sección se inserta después de la Ronda 14C en `docs/techniques/14_PHISHING.md`. Lo aquí añadido complementa lo ya documentado, no lo sustituye.

### 3. Pantallas de trabajo por herramienta

#### 3.1 Pantalla de Evilginx (captura de sesión)

- Campo `Dominio de campaña`: Mistral lo rellena automáticamente con un dominio de laboratorio o uno generado por el usuario.
- Campo `Portal a clonar`: desplegable con opciones (Office 365, Google Workspace, iCloud, VPN corporativa, personalizado). Al seleccionar uno, Mistral precarga la configuración declarativa del phishlet correspondiente.
- Campo `Certificados TLS`: botón `Obtener con Certbot`. Mistral solicita la obtención dentro del entorno autorizado y muestra el progreso en tiempo real.
- Botón `Iniciar proxy inverso`: despliega Evilginx en laboratorio tras confirmación. El panel muestra el estado (activo/inactivo) y las sesiones capturadas en tiempo real en una tabla con columnas: usuario, contraseña, token de sesión, fecha y hora. Los valores sensibles se muestran enmascarados por defecto.
- Botón `Enviar a Credenciales`: transfiere todas las sesiones capturadas al Módulo 5 mediante el contrato `credential_handoff`, con redacción por defecto y AuditLog.
- Botón `Detener`: detiene el proxy y guarda las evidencias.

#### 3.2 Pantalla de GoPhish (campaña de credenciales)

- Campo `Lista de destinatarios`: permite cargar un archivo CSV o pegar directamente los emails. Mistral puede obtener la lista automáticamente desde el Módulo 1 (OSINT) si el usuario lo autoriza.
- Campo `Plantilla de correo`: editor visual con variables (nombre, empresa, cargo) que Mistral rellena con los datos del Módulo 1. La pantalla ofrece previsualización en tiempo real del correo renderizado.
- Campo `Portal clonado`: miniatura del portal. Botón `Clonar nuevo portal` para añadir uno personalizado. Mistral analiza la URL proporcionada y configura la copia dentro del laboratorio autorizado.
- Botón `Programar envío`: permite elegir fecha y hora, o enviar inmediatamente después de aprobación explícita.
- Panel de resultados en tiempo real: muestra correos enviados, entregados, abiertos (si se usa pixel de seguimiento), clics en el enlace y credenciales capturadas. Un gráfico de métricas se actualiza automáticamente.
- Botón `Exportar informe`: genera un informe con todas las métricas y evidencias, con exportación enmascarada por defecto.

#### 3.3 Pantalla de SET (campaña con payload)

- Campo `Tipo de payload`: desplegable (documento Office con macro, PDF con enlace, enlace directo a descarga). Mistral sugiere el más adecuado según el perfil autorizado del objetivo.
- Campo `Payload`: Mistral prepara un perfil declarativo de payload con Metasploit dentro del laboratorio. El usuario puede personalizar el tipo de payload y el puerto de escucha, siempre con confirmación explícita y Policy Engine activo.
- Campo `Plantilla de correo`: editor con variables, igual que en GoPhish.
- Botón `Generar y enviar`: crea el artefacto autorizado, lo empaqueta, envía el correo y levanta el listener de Metasploit dentro del laboratorio. El panel muestra las conexiones entrantes en tiempo real.
- Botón `Detener listener`: cierra el listener y guarda las sesiones obtenidas como evidencia.

### 4. Roles explícitos de las IAs

#### 4.1 Mistral (LaIA — asistente contextual)

- Está presente en cada pantalla del módulo como un chat lateral.
- Traduce las peticiones del usuario en lenguaje natural a planes de campaña.
- Rellena automáticamente los campos (dominio, plantilla, lista de correos, payload) con datos del Módulo 1 (OSINT) si el usuario lo autoriza.
- Redacta el texto del correo y personaliza el asunto y el cuerpo con los datos del objetivo (nombre, cargo, empresa).
- Muestra el plan completo en una ventana modal antes de ejecutar cualquier acción.
- Si algo falla (portal no se clona, correos rebotados), sugiere alternativas o solicita ayuda a Hermes.

#### 4.2 DeepSeek (arquitecto de laboratorio)

- Es accesible desde la pestaña `DeepSeek` del Módulo 12 (Orquestación).
- El usuario puede pedir directamente: `DeepSeek, revisa esta campaña y sugiere mejoras`, `Genera una nueva plantilla para este portal que ha cambiado`, `Corrige el fallo de entrega de correos`.
- DeepSeek genera el diseño, la plantilla o la configuración necesaria y se lo pasa a Hermes para que lo materialice en el laboratorio.
- No tiene autoridad directa sobre producción; todo requiere aprobación explícita del usuario.

#### 4.3 Hermes (ejecutor de laboratorio)

- Recibe las solicitudes de Mistral o DeepSeek.
- Busca en fuentes abiertas (GitHub, foros de seguridad) plantillas, phishlets o configuraciones actualizadas.
- Genera componentes funcionales solo en el laboratorio, bajo rutas aprobadas como `modules/laboratory/`, y los prueba en sandbox contra un entorno controlado.
- Notifica al usuario cuando el nuevo módulo o plantilla está listo para revisión: `Nueva plantilla para Office 365 disponible para pruebas`.
- Si el usuario lo aprueba, lo promociona al arsenal y la campaña se reanuda automáticamente con la nueva configuración.
- Si no encuentra información suficiente, lo comunica al usuario y sugiere aportar manualmente una configuración mediante el hook `IMPLEMENTACION_USUARIO_REQUERIDA`.

### 5. Área de interacción del usuario

En cada pantalla de herramienta, el usuario ve de izquierda a derecha:

- Panel de configuración (campos, botones, previsualizaciones).
- Chat contextual de Mistral (para dar instrucciones en lenguaje natural).
- Visor de resultados (tabla de sesiones, credenciales, métricas), con valores sensibles enmascarados por defecto.
- Barra de estado de la campaña (`draft`, `sending`, `active`, `completed`, etc.).
- Acceso rápido a `DeepSeek` (Módulo 12) para consultas avanzadas.

### 6. Evolución del arsenal (cuándo entra Hermes Agent)

Hermes se activa automáticamente o a petición del usuario cuando:

- El portal objetivo cambia su estructura (nuevo diseño, nueva protección) y las plantillas existentes no funcionan.
- Aparece un nuevo mecanismo anti-phishing no catalogado (nuevo CAPTCHA, detección de proxy, etc.).
- Se requiere un módulo de envío alternativo (nuevo servidor SMTP, relay personalizado o compatibilidad con filtros SPF/DKIM/DMARC dentro del laboratorio autorizado).
- Se solicita una plantilla de correo para un nuevo tipo de objetivo o sector (banca, sanidad, educación).

En todos los casos, Hermes genera el código en laboratorio, lo prueba en sandbox y, tras la aprobación del usuario, lo promociona al arsenal.

## Ronda 14D — Cierre documental, criterios de aceptación e índices

### 1. Objetivo

Cerrar la documentación del Módulo 14 con los criterios de aceptación, la actualización de índices y la nota final. Solo documentación. No implementar código.

### 2. Ubicación

Esta ronda se añade después de la Ronda 14C en `docs/techniques/14_PHISHING.md` y mantiene toda la información anterior sin borrar ni resumir.

### 3. Criterios de aceptación del Módulo 14

El Módulo 14 queda documentalmente cerrado si `docs/techniques/14_PHISHING.md` contiene:

- [ ] Propósito del módulo documentado.
- [ ] Herramientas nominales y VersionLock documentados (Evilginx, Gophish, SET, Metasploit, swaks, Certbot, Mistral, Hermes).
- [ ] Panel `Simulación` documentado con subpáginas (Campañas, Plantillas, Portales Clonados, Resultados).
- [ ] Estados de campaña documentados (`draft`, `configured`, `pending_approval`, `scheduled`, `sending`, `active`, `collecting_results`, `completed`, `paused`, `blocked_by_policy`, `error`, `closed`).
- [ ] Técnicas `phishing.*` documentadas con sus `technique_id` y contrato JSON.
- [ ] Evidencias esperadas documentadas (`campaign_config_json`, `template_rendered_html`, `landing_page_snapshot`, `delivery_log`, `open_events_json`, `click_events_json`, `credential_handoff_json`, `campaign_metrics_json`, `screenshots`, `audit_log`, `final_campaign_report`).
- [ ] Confirmaciones explícitas documentadas (enviar campaña, activar portal, recolectar credenciales, enviar payload, exportar resultados, mostrar valores completos, handoff a M5).
- [ ] Flujo de trabajo asistido (Mistral + X5 + Hermes) documentado.
- [ ] Preflight checklist documentado.
- [ ] Errores y recuperación documentados.
- [ ] Handoffs con M1, M5, M12 y M16 documentados, incluyendo el contrato `phishing_handoff`.
- [ ] Scoring X5 documentado.
- [ ] Preparación para M16 documentada.
- [ ] No se afirma implementación real de campañas fuera del laboratorio.

### 4. Actualización de índices globales

Los índices globales del repositorio se actualizan, si existen, con la información exacta indicada para el Módulo 14:

- `docs/MODULE_TOOL_INVENTORY.md`
- `docs/MODULE_ACCEPTANCE_CRITERIA.md`
- `AI_HANDOFF_OJO_DE_DIOS.md`

### 5. Nota final

El Módulo 14 queda definido como especificación de producto/laboratorio. Esta documentación no crea lógica funcional ni afirma ejecución real de campañas. Las partes sensibles permanecen marcadas como:

- `IMPLEMENTACION_USUARIO_REQUERIDA`

## Ronda 14E — Cierre final de verificación, criterios e índices

### 1. Objetivo

Cerrar la documentación del Módulo 14 con los criterios de aceptación, la actualización de índices y la nota final. Solo documentación. No implementar código.

### 2. Ubicación

Esta ronda se añade después de la Ronda 14D en `docs/techniques/14_PHISHING.md`. No borra, resume ni sustituye lo anterior.

### 3. Criterios de aceptación del Módulo 14

El Módulo 14 queda documentalmente cerrado si `docs/techniques/14_PHISHING.md` contiene:

- [ ] Propósito del módulo documentado.
- [ ] Herramientas nominales y VersionLock documentados (Evilginx, Gophish, SET, Metasploit, swaks, Certbot, Mistral, DeepSeek, Hermes).
- [ ] Panel `Verificación` documentado con subpáginas (Campañas, Plantillas, Portales Clonados, Resultados).
- [ ] Estados de campaña documentados (`draft`, `configured`, `pending_approval`, `scheduled`, `sending`, `active`, `collecting_results`, `completed`, `paused`, `blocked_by_policy`, `error`, `closed`).
- [ ] Técnicas `phishing.*` documentadas con sus `technique_id` y contrato JSON.
- [ ] Evidencias esperadas documentadas.
- [ ] Confirmaciones explícitas documentadas.
- [ ] Pantallas de trabajo por herramienta documentadas (Evilginx, Gophish, SET).
- [ ] Roles explícitos de las IAs (Mistral, DeepSeek, Hermes) documentados.
- [ ] Flujo de trabajo asistido documentado.
- [ ] Preflight checklist y errores documentados.
- [ ] Handoffs con M1, M5, M12 y M16 documentados.
- [ ] Scoring X5 documentado.
- [ ] Preparación para M16 documentada.
- [ ] No se afirma implementación real de campañas fuera del laboratorio.

### 4. Actualización de índices globales

Los índices globales del repositorio se actualizan, si existen, con la información indicada para el Módulo 14 de campañas de verificación de seguridad:

- `docs/MODULE_TOOL_INVENTORY.md`
- `docs/MODULE_ACCEPTANCE_CRITERIA.md`
- `AI_HANDOFF_OJO_DE_DIOS.md`

### 5. Nota final

El Módulo 14 queda definido como especificación de producto/laboratorio. Esta documentación no crea lógica funcional ni afirma ejecución real de campañas. Las partes sensibles permanecen marcadas como:

- `IMPLEMENTACION_USUARIO_REQUERIDA`
