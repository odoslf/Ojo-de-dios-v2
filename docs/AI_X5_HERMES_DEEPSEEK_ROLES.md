# Ojo de Dios — Reparto de roles IA, X5, Hermes Agent Lab y DeepSeek Assist

Documento de arquitectura para dejar fijado el reparto correcto entre Mistral/LaIA, X5/OjoRouter, Hermes Agent Lab y DeepSeek Assist dentro de Ojo de Dios.

Este documento no es una ronda de Codex. Es documentación estratégica del plan maestro.

## 1. Decisión oficial

Ojo de Dios tendrá cuatro piezas inteligentes diferenciadas:

- **Mistral/LaIA** como cerebro operativo local.
- **X5/OjoRouter** como motor de validación, orquestación y ejecución.
- **Hermes Agent Lab / Evolution Engine** como laboratorio constructor de nuevas capacidades.
- **DeepSeek Assist** como apoyo externo opcional y barato para investigación técnica y generación asistida cuando sea necesario.

Estas piezas no compiten entre sí. Cada una tiene una función distinta.

Regla principal:

```text
Mistral piensa y rellena.
X5 valida y ejecuta.
Hermes crea y evoluciona en laboratorio.
DeepSeek ayuda a investigar y diseñar cuando hace falta.
El panel gobierna.
O2 aprueba.
```

## 2. Quién rellena campos en una pantalla

Cuando el usuario esté en una pantalla de Ojo de Dios, por ejemplo Android, Web, Scraping, Cloud, HackRF o cualquier módulo, y quiera crear un payload, lanzar una técnica o rellenar un formulario, el responsable principal será **Mistral/LaIA**.

Mistral/LaIA debe poder:

- Entender lo que pide el usuario en lenguaje natural.
- Detectar el módulo correcto.
- Detectar la técnica correcta.
- Rellenar campos del formulario.
- Sugerir parámetros.
- Explicar qué falta.
- Explicar errores.
- Preparar un plan de ejecución.
- Decir qué técnicas se pueden probar.
- Ordenar técnicas por probabilidad, riesgo, permisos y contexto.
- Crear JSON estructurado para X5.
- No inventar datos.
- No ejecutar directamente.
- No saltarse X5.
- No saltarse el panel.

Ejemplo conceptual:

El usuario está en Android y quiere preparar una acción autorizada.

Mistral/LaIA debe:

- Interpretar el objetivo.
- Rellenar nombre, tipo, plataforma, modo, permisos, salida esperada y evidencia.
- Marcar campos obligatorios incompletos.
- Proponer técnica registrada.
- Enviar plan estructurado a X5.
- Explicar al usuario qué se va a hacer antes de ejecutar.

Hermes no debe rellenar ese formulario directamente salvo que falte una capacidad nueva que todavía no exista.

## 3. Quién prueba técnicas automáticamente

La prueba automática o semiautomática de técnicas autorizadas corresponde a **X5/OjoRouter**, no a Hermes.

X5/OjoRouter debe:

- Recibir plan de Mistral.
- Consultar TechniqueRegistry.
- Verificar permisos.
- Verificar scope/allowlist.
- Verificar modo de ejecución.
- Verificar si requiere confirmación.
- Verificar si la técnica está completa o marcada como `IMPLEMENTACION_USUARIO_REQUERIDA`.
- Verificar herramientas disponibles.
- Lanzar workers autorizados.
- Registrar evidencia.
- Devolver resultado.
- Permitir parada con kill switch.
- No ejecutar técnicas fuera de scope.
- No ejecutar técnicas no registradas.
- No ejecutar técnicas generadas por Hermes si no están promocionadas.

Mistral puede proponer la cadena.

X5 decide si puede ejecutarse.

El panel pide confirmación cuando toque.

Hermes no ejecuta cadenas reales de ataque.

## 4. Qué hace Hermes

Hermes Agent Lab / Evolution Engine será el laboratorio constructor de Ojo de Dios.

Hermes entra cuando:

- Falta una técnica.
- Falta una herramienta.
- Falta un wrapper.
- Falta documentación.
- Falta un parser.
- Falta un schema.
- Falta un payload contract.
- Falta un worker.
- Falta un panel.
- Falta una prueba estructural.
- Falta una integración.
- Aparece una CVE nueva.
- Una técnica falla muchas veces.
- X5 detecta que no tiene capacidad suficiente.
- Mistral detecta que la arquitectura necesita una pieza nueva.

Hermes debe poder crear:

- `TechniqueProposal`.
- Skill Hermes.
- Wrapper de laboratorio.
- Worker de laboratorio.
- Schema de entrada/salida.
- Panel de laboratorio.
- Evidence writer.
- Parser.
- Adapter.
- Documentación.
- Tests estructurales.
- Diff promocionable.
- Manifest de propuesta.
- Rollback.
- Informe de revisión.

Hermes no debe:

- Ejecutar sobre objetivos reales.
- Rellenar formularios de ejecución real.
- Saltarse X5.
- Saltarse el panel.
- Activar técnicas nuevas automáticamente.
- Promocionarse a sí mismo.
- Tocar producción sin aprobación.
- Fingir capacidad.
- Marcar como operativo algo que solo es stub.
- Ejecutar ataques nuevos directamente.

## 5. Hermes como laboratorio de CVE y técnicas nuevas

Cuando aparezca una CVE nueva o el usuario pida una capacidad que no existe, Hermes debe funcionar así:

1. Crear una propuesta en laboratorio.
2. Buscar documentación permitida.
3. Pedir ayuda a DeepSeek Assist si Mistral no llega o si falta documentación técnica.
4. Resumir fuentes.
5. Crear contrato de técnica.
6. Crear schema.
7. Crear wrapper si procede.
8. Crear worker de laboratorio.
9. Crear evidence writer.
10. Crear panel si hace falta.
11. Crear tests estructurales.
12. Marcar lógica privada como `IMPLEMENTACION_USUARIO_REQUERIDA`.
13. Pedir revisión a Mistral.
14. Pedir dry-run a X5 si procede.
15. Guardar evidencia.
16. Mostrar diff en panel.
17. Esperar aprobación de O2.
18. Promocionar solo si se aprueba.

Hermes + DeepSeek podrá crear herramientas propias para el arsenal de Ojo de Dios, pero siempre primero en laboratorio.

Nada creado por Hermes entra automáticamente en ejecución real.

## 6. Rol de DeepSeek Assist

DeepSeek Assist será un proveedor externo opcional para ayudar a Hermes cuando haga falta investigar o generar mejor.

DeepSeek se usará para:

- Resumir documentación técnica.
- Ayudar con CVE nuevas.
- Explicar errores complejos.
- Crear contratos de payload.
- Crear schemas.
- Crear wrappers de laboratorio.
- Crear adapters.
- Crear tests estructurales.
- Crear documentación.
- Comparar opciones de diseño.
- Ayudar a crear una propuesta de técnica nueva.

DeepSeek no debe:

- Ejecutar.
- Decidir solo.
- Promocionar.
- Tocar producción.
- Recibir secretos.
- Recibir más contexto del necesario.
- Activar ataques.
- Saltarse Mistral.
- Saltarse X5.
- Saltarse el panel.

DeepSeek debe estar apagado por defecto y usarse con presupuesto controlado.

Variables recomendadas:

```env
DEEPSEEK_ENABLED=0
DEEPSEEK_API_KEY=ALAZAN_REEMPLAZAR_EN_ENV_LOCAL
DEEPSEEK_API_KEY=ALAZAN_REEMPLAZAR_EN_ENV_LOCAL
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro
DEEPSEEK_MAX_TOKENS_PER_REQUEST=2500
DEEPSEEK_DAILY_TOKEN_LIMIT=50000
DEEPSEEK_MONTHLY_EUR_LIMIT=10
DEEPSEEK_REQUIRE_CONFIRMATION_OVER_TOKENS=8000
DEEPSEEK_CACHE_ENABLED=1
DEEPSEEK_CACHE_TTL_DAYS=30
HERMES_DEEPSEEK_ENABLED=0
HERMES_DEEPSEEK_MODE=assist_only
```

## 7. Flujo correcto en una pantalla de Ojo de Dios

Ejemplo: el usuario está en una pantalla de Android y quiere preparar una acción autorizada.

Flujo correcto:

1. El usuario escribe lo que quiere.
2. Mistral/LaIA interpreta la intención.
3. Mistral detecta técnica, campos y parámetros.
4. Mistral rellena el formulario o propone valores.
5. El panel muestra la propuesta.
6. X5 valida registry, permisos, scope y modo.
7. Si falta una capacidad, X5/Mistral lo notifican.
8. Hermes crea una propuesta de laboratorio para esa capacidad faltante.
9. Si falta documentación, Hermes consulta DeepSeek Assist con coste controlado.
10. Hermes genera schema, wrapper, worker, tests y docs en sandbox.
11. Mistral revisa.
12. X5 hace dry-run si procede.
13. El panel muestra diff y evidencia.
14. O2 aprueba o rechaza.
15. Si se aprueba, se promociona.
16. X5 podrá usarlo en futuras ejecuciones controladas.

## 8. Flujo para “probar todas las técnicas”

No debe existir un botón ciego de “probar todo sin control”.

Debe existir un modo de cadena controlada.

Mistral/LaIA:

- Ordena técnicas candidatas.
- Explica por qué propone cada una.
- Calcula riesgo.
- Calcula prioridad.
- Descarta lo que no encaja.
- No ejecuta.

X5/OjoRouter:

- Valida cada técnica.
- Comprueba scope.
- Comprueba permisos.
- Comprueba allowlist.
- Comprueba modo.
- Comprueba herramientas.
- Ejecuta solo lo permitido.
- Guarda evidencia.
- Detiene si hay error crítico.
- Respeta kill switch.

Panel:

- Muestra cadena.
- Pide confirmación si toca.
- Permite parar.
- Permite saltar pasos.
- Muestra resultados.

Hermes:

- Solo entra si falta una técnica, wrapper, parser, schema o documentación.
- No prueba técnicas reales directamente.

## 9. Estados de propuesta Hermes

Toda propuesta creada por Hermes debe tener uno de estos estados:

```text
draft
designed
generated
tested
review_required
approved_by_user
promoted
rejected
archived
```

Nada puede pasar a producción sin:

```text
tested
review_required
approved_by_user
promoted
```

## 10. Carpeta recomendada

```text
app/
  ai/
    hermes_lab/
      __init__.py
      registry.py
      proposal_service.py
      skill_service.py
      skill_schema.py
      sandbox_runner.py
      approval_service.py
      evidence_writer.py
      promotion_service.py
      risk_classifier.py
      deepseek_assist.py
      mistral_review_bridge.py
      x5_bridge.py
      templates/
        skill_template/
        technique_template/
        module_template/
        wrapper_template/
        panel_template/
        worker_template/
        evidence_template/
      proposals/
      sandbox/

storage/
  hermes_lab/
    proposals/
    evidence/
    diffs/
    logs/
    approvals/
    rejected/
    promoted/
    deepseek/
      requests/
      responses/
      summaries/
      token_usage/
      cached_docs/
```

## 11. Evidence obligatoria

Cada acción de Hermes debe guardar:

- Qué pidió el usuario.
- Qué entendió Mistral.
- Por qué se necesita Hermes.
- Si se usó DeepSeek.
- Qué documentación se consultó.
- Qué coste estimado tuvo.
- Qué archivos se generaron.
- Qué tests se añadieron.
- Qué riesgo tiene.
- Qué revisó Mistral.
- Qué validó X5.
- Qué aprobó O2.
- Cómo revertirlo.

Formato mínimo:

```text
storage/hermes_lab/evidence/YYYYMMDD_HHMMSS_proposal_id/
  manifest.json
  summary.md
  diff.patch
  files_created.txt
  files_modified.txt
  tests.txt
  deepseek_usage.json
  mistral_review.md
  x5_dry_run.json
  approval.json
  rollback.md
```

## 12. Permisos

Permisos que Hermes puede tener:

```text
read_project
write_lab
write_tests
run_tests
create_docs
create_skill
create_wrapper
create_worker_stub
create_schema
create_panel_stub
create_evidence_writer
request_deepseek_assist
request_mistral_review
request_x5_dry_run
request_promotion
```

Permisos bloqueados por defecto:

```text
write_production
modify_x5_core
execute_live_target
network_active_scan
credential_testing
rf_transmit
android_device_action
phishing_delivery
cloud_mutation
persistence_action
auto_promote
auto_approve
```

## 13. Regla sobre técnicas sensibles

Si una técnica, payload, acción o capacidad requiere lógica privada o sensible, Hermes debe crear la estructura profesional completa, pero dejar claramente:

```text
IMPLEMENTACION_USUARIO_REQUERIDA
```

Debe crear:

- Archivo.
- Clase.
- Registry.
- Schema.
- Panel.
- Worker stub.
- Evidence contract.
- Tests estructurales.
- Documentación.
- Marcador de pendiente.

No puede fingir que funciona.

## 14. Quién decide qué hacer

Mistral/LaIA decide qué recomendar.

X5 decide qué se puede ejecutar.

Hermes decide qué se puede crear en laboratorio.

DeepSeek ayuda a investigar o diseñar.

El panel decide qué se permite.

O2 decide qué se aprueba.

## 15. Regla final

Hermes no es el piloto de ejecución real.

Hermes es el taller donde se fabrican nuevas herramientas.

Mistral es el copiloto que rellena campos y entiende el objetivo.

X5 es el motor que ejecuta lo permitido.

DeepSeek es el consultor externo barato para investigar y diseñar mejor.

El panel es el gobierno.

O2 es la autoridad final.

Frase oficial:

> En Ojo de Dios, cuando el usuario esté en una pantalla y quiera rellenar campos, crear un payload o lanzar una cadena de técnicas, actuará Mistral/LaIA como parameter filler y planner, y X5/OjoRouter como validador y ejecutor. Hermes Agent Lab solo entrará cuando falte una capacidad: investigará, diseñará y generará en laboratorio una herramienta, técnica, wrapper, parser, schema, panel, worker, evidence y tests, con ayuda opcional de DeepSeek Assist, para que O2 pueda supervisarla e incorporarla al arsenal de Ojo de Dios de forma controlada.

## 13. Normalización M16-FIX-1 de LaIA, Hermes Agent y DeepSeek

Los Vectores 1 y 2 de M16 están documentados y pendientes de validación
operativa en Windows. El Módulo 16 no se considera cerrado hasta completar
Vectores 3-10.

### LaIA/Mistral

- Modelo oficial: `CognitiveComputations/dolphin-mistral-nemo:12b`.
- `MISTRAL_MODEL` siempre apunta al modelo oficial.
- `MISTRAL_SYSTEM_PROMPT_PATH` se envía en cada petición.
- `laia-mistral-con-prompt` es un alias opcional de prueba, no un modelo oficial
  de producción.
- API Ollama documentada: `POST http://localhost:11434/api/generate`,
  `POST http://localhost:11434/api/chat`, `GET http://localhost:11434/api/tags`
  y `GET http://localhost:11434/api/ps`.
- La falta aislada de RAG no marca LaIA como `FAILED` si Ollama y el modelo
  oficial responden; deben usarse estados como `KNOWLEDGE_MISSING`,
  `KNOWLEDGE_STALE` o `PARTIAL`.

### Precedencia IA

- `AI_ENABLED` es el interruptor global.
- `MISTRAL_ENABLED` y `ANGEL_ENABLED` solo se evalúan si `AI_ENABLED=1`.
- La instalación puede estar lista con `AI_ENABLED=0`, pero la aplicación no debe
  usar IA hasta activarlo.
- `.env.example` debe permanecer seguro por defecto y sin secretos reales.

### Hermes Agent Lab

- Nombre interno: `hermes_lab`.
- Nombre visible: `Hermes Agent Lab`.
- Alias histórico deprecated: no usar como nombre operativo.
- Workspace: `modules/laboratory/`.
- Archivo por propuesta: `PROMOTION_MANIFEST.json`.
- Archivo central promovido: `modules/laboratory/_promoted_manifest/`.
- Preparación de workspace: `LAB_WORKSPACE_READY`.
- API comprobada + controles válidos: `READY_CONTROLLED`.

### DeepSeek

- Base URL: `https://api.deepseek.com`.
- Modelos configurados: `deepseek-v4-pro`, `deepseek-v4-flash`.
- Endpoints: `GET /models` y `POST /chat/completions`.
- El healthcheck valida disponibilidad del modelo mediante `/models`.
- Nunca se imprime ni registra `DEEPSEEK_API_KEY`.

Mano de Dios sigue siendo producto separado según
`docs/MANO_DE_DIOS_SEPARATION.md`. M16 solo puede preparar una exportación
externa futura, nunca integrar Mano de Dios internamente en Ojo de Dios.


## 14. Contratos base M16 Vector 4 — Panel de IAs y chat unificado

Estos contratos son documentación para el panel de IAs y chat unificado. No crean
tablas reales, endpoints reales ni ejecución directa desde el chat.

### Contrato JSON ai_chat_session

```json
{
  "type": "ai_chat_session",
  "session_id": "chat-uuid",
  "trace_id": "trace-uuid",
  "agent": "laia_mistral",
  "active_module": "android",
  "active_vector": "analysis_apps",
  "target_id": "target-uuid",
  "target_fingerprint_id": "fp-uuid",
  "run_id": null,
  "operator_id": "admin",
  "execution_mode": "assisted",
  "status": "active",
  "created_at": "2026-06-01T12:00:00Z",
  "updated_at": "2026-06-01T12:00:00Z"
}
```

Estados exactos:

"active", "paused", "waiting_approval", "completed", "error", "archived".

### Contrato JSON ai_chat_message

```json
{
  "type": "ai_chat_message",
  "message_id": "msg-uuid",
  "session_id": "chat-uuid",
  "trace_id": "trace-uuid",
  "sender": "user",
  "recipient": "laia_mistral",
  "message_kind": "instruction",
  "content": "Analiza las evidencias seleccionadas",
  "evidence_ids": ["ev-001"],
  "finding_ids": [],
  "requires_confirmation": false,
  "created_at": "2026-06-01T12:00:00Z",
  "operator_id": "admin"
}
```

Valores exactos de "sender" y "recipient":

"user", "laia_mistral", "angel_hermes", "deepseek", "x5_system".

Valores exactos de "message_kind":

"instruction", "question", "answer", "plan", "proposal", "review", "approval_request", "approval_response", "notification", "error".

Reglas documentales:

- cada mensaje conserva "session_id" y "trace_id";
- el chat no permite ejecución directa;
- X5/OjoRouter valida cualquier plan antes de ejecución permitida;
- las aprobaciones del usuario se registran antes de promover o ejecutar flujos;
- Redis Pub/Sub y WebSocket transportan eventos vivos, pero SQLite/DB futura es la fuente persistente.

## Acciones estructuradas del chat unificado

“El chat nunca ejecuta texto libre. Toda intención que pueda crear un plan, solicitar una tarea, modificar estado, aprobar una propuesta o generar un handoff debe convertirse primero en un contrato JSON visible y revisable.”

Esta sección es solo documental: no crea implementación, tablas reales, workers,
endpoints reales ni autorización de ejecución directa desde texto libre.

### Contrato JSON ai_action_request

```json
{
  "type": "ai_action_request",
  "request_id": "req-uuid",
  "session_id": "chat-uuid",
  "trace_id": "trace-uuid",
  "requested_by": "user",
  "agent": "laia_mistral",
  "action_type": "create_plan",
  "active_module": "android",
  "target_id": "target-uuid",
  "technique_id": null,
  "evidence_ids": [],
  "finding_ids": [],
  "parameters": {},
  "requires_confirmation": true,
  "status": "draft",
  "created_at": "2026-06-01T12:00:00Z",
  "operator_id": "admin"
}
```

Valores exactos de "action_type":

"create_plan", "explain_finding", "summarize_evidence", "create_handoff", "request_hermes_task", "request_deepseek_review", "approve_proposal", "reject_proposal", "pause_plan", "resume_plan", "close_session".

Estados exactos:

"draft", "waiting_confirmation", "approved", "rejected", "queued", "completed", "failed", "cancelled".

### Contrato JSON ai_approval_request

```json
{
  "type": "ai_approval_request",
  "approval_id": "approval-uuid",
  "request_id": "req-uuid",
  "session_id": "chat-uuid",
  "trace_id": "trace-uuid",
  "approval_type": "plan_execution",
  "summary": "Resumen visible de la acción",
  "risk_level": "medium",
  "affected_resources": ["target-uuid"],
  "evidence_ids": [],
  "expires_at": null,
  "status": "pending",
  "created_at": "2026-06-01T12:00:00Z",
  "operator_id": "admin"
}
```

Valores exactos de "approval_type":

"plan_execution", "hermes_task", "dependency_install", "sandbox_test", "technique_promotion", "evidence_reveal", "evidence_export", "session_close".

Estados exactos:

"pending", "approved", "rejected", "expired", "cancelled".

Reglas exactas:

- toda aprobación conserva "request_id", "session_id" y "trace_id";
- una aprobación no se reutiliza para otra acción;
- la respuesta del usuario genera AuditLog;
- una aprobación rechazada no se ejecuta;
- Redis distribuye el evento, pero DB conserva la decisión.

### Contrato JSON hermes_task_request

```json
{
  "type": "hermes_task_request",
  "task_id": "hermes-task-uuid",
  "session_id": "chat-uuid",
  "trace_id": "trace-uuid",
  "requested_by": "laia_mistral",
  "task_type": "create_parser",
  "technical_goal": "Crear parser para evidencia no reconocida",
  "input_evidence_ids": ["ev-001"],
  "target_path": "modules/laboratory/technique-id/",
  "expected_files": [
    "technique.json",
    "worker.py",
    "evidence_schema.json",
    "requirements.generated.txt",
    "README.md",
    "PROMOTION_MANIFEST.json"
  ],
  "requires_approval": true,
  "status": "draft"
}
```

Valores exactos de "task_type":

"create_parser", "create_wrapper", "create_evidence_schema", "create_module", "repair_module", "create_panel_schema", "create_handoff_adapter", "prepare_sandbox_test".

### Contrato JSON deepseek_review_request

```json
{
  "review_id": "review-uuid",
  "session_id": "chat-uuid",
  "trace_id": "trace-uuid",
  "task_id": "hermes-task-uuid",
  "proposal_path": "modules/laboratory/technique-id/",
  "review_scope": "architecture",
  "input_evidence_ids": ["ev-001"],
  "requested_by": "angel_hermes",
  "status": "draft",
  "created_at": "2026-06-01T12:00:00Z"
}
```

Valores de "review_scope":

"architecture", "code_quality", "contracts", "dependencies", "evidence", "promotion_readiness".

DeepSeek solo devuelve revisión y recomendaciones; no cambia producción ni promociona.


## Estados oficiales de agente M16 Vector 4

Estados oficiales:

"offline", "starting", "ready", "busy", "waiting_approval", "degraded", "error", "disabled".

Reglas exactas:

- "ready" solo si el healthcheck del agente es válido;
- "degraded" si responde pero falta RAG, modelo secundario o dependencia no crítica;
- "disabled" si la variable de entorno correspondiente está desactivada;
- ningún estado se deduce solo por texto de la IA;
- todo cambio de estado genera AuditLog.

## Persistencia futura del panel de IAs

Estas tablas futuras se documentan sin crearlas, sin migraciones y sin afirmar
capacidad operativa:

- "ai_chat_sessions"
- "ai_chat_messages"
- "ai_action_requests"
- "ai_approval_requests"
- "hermes_task_requests"
- "deepseek_review_requests"
- "ai_agent_status_events"

Reglas exactas:

- "session_id", "trace_id" y "operator_id" se conservan en todas las tablas aplicables;
- los mensajes no se sobrescriben;
- las aprobaciones no se reutilizan;
- Redis distribuye eventos vivos, pero DB es fuente de verdad;
- cerrar sesión no elimina su histórico;
- archivar sesión la deja en modo solo lectura.

## Reconexión, recuperación y errores del chat unificado

Reglas de reconexión y recuperación:

- al reconectar WebSocket, el panel solicita estado persistido de la sesión;
- mensajes no persistidos no se consideran entregados;
- una desconexión no cancela automáticamente planes o tareas;
- el usuario ve aviso de desconexión y último timestamp válido;
- al recuperar conexión se comparan "session_id", "trace_id" y último mensaje;
- duplicados se ignoran por "message_id";
- si hay conflicto, se marca sesión "error" y se registra AuditLog.

Errores exactos:

- agente no disponible;
- modelo no disponible;
- API externa no responde;
- RAG ausente o desactualizado;
- mensaje inválido;
- contrato JSON inválido;
- aprobación expirada;
- tarea Hermes incompleta;
- revisión DeepSeek fallida;
- WebSocket desconectado;
- Redis no disponible;
- persistencia no disponible.

Reglas:

- no fingir éxito;
- mostrar error visible;
- conservar histórico;
- no ejecutar acción;
- permitir reintento manual;
- registrar AuditLog;
- LaIA puede explicar el error, no ocultarlo.

Hermes Agent puede crear capacidades nuevas de forma evolutiva, pero siempre en laboratorio. Su salida mínima es: contrato, wrapper, schema, README, requirements.generated.txt, evidencias de sandbox, PROMOTION_MANIFEST y rollback.

Hermes Agent puede crear capacidades nuevas, pero su salida solo es válida si incluye manifest, rollback, evidencia sandbox y revisión. DeepSeek puede revisar. LaIA puede explicar y recomendar. X5 solo integra lo promovido y válido.
