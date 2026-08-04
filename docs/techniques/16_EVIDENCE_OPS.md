# MÓDULO 16 — EXCELENCIA OPERATIVA / EVIDENCE

## 1. Objetivo y estado actual

El Módulo 16 define la capa documental de inteligencia local, asistencia externa
controlada, evidencias, healthchecks, auditoría, rutas de almacenamiento y
readiness final de Ojo de Dios.

Los Vectores 1-10 quedan cerrados como especificación documental. La
implementación real y la validación operativa en Windows permanecen pendientes
para rondas futuras.

Mano de Dios sigue siendo un producto separado según
`docs/MANO_DE_DIOS_SEPARATION.md`. M16 solo puede preparar una exportación
externa futura hacia ese producto separado; nunca debe integrarlo internamente en
Ojo de Dios ni declarar a Mano de Dios como parte del runtime, paneles, workers,
registry o contratos internos.

## 2. Índice y hoja de ruta oficial M16

1. Estación LaIA/Mistral
2. Estación Hermes Agent
3. Evidencias y trazabilidad
4. Panel de IAs y chat unificado
5. Healthchecks, logs y auditoría
6. VersionLock y ToolHealth
7. Integridad de registry, contratos, paneles, workers y estados
8. Calidad de evidencia y scoring
9. Integridad Hermes Agent, promoción y rollback
10. Readiness final y exportación externa

Esta hoja de ruta es la referencia oficial del cierre documental M16: los Vectores 1 y 2
cubren la normalización documental inicial de LaIA/Mistral y Hermes Agent, y los
Vectores 3-10 completan las áreas restantes sin modificar la filosofía
LaIA → X5 → Hermes → Evidence/AuditLog.

## 3. Estación LaIA/Mistral

### 3.1 Verdad única de modelo y API Ollama

LaIA/Mistral es la estación local de asistencia táctica y documental. Opera con
Ollama en `localhost:11434`, no ejecuta acciones directas y deriva cualquier
intención operativa a X5/OjoRouter mediante handoff revisable.

Verdad única de producción documental:

- Modelo oficial: `CognitiveComputations/dolphin-mistral-nemo:12b`.
- `MISTRAL_MODEL` siempre apunta al modelo oficial.
- `MISTRAL_SYSTEM_PROMPT_PATH` apunta al prompt contractual y su contenido se
  envía en cada petición a Ollama.
- `laia-mistral-con-prompt` queda como alias opcional de prueba; no es el modelo
  oficial de producción.
- Endpoints Ollama documentados:
  - `POST http://localhost:11434/api/generate`
  - `POST http://localhost:11434/api/chat`
  - `GET http://localhost:11434/api/tags`
  - `GET http://localhost:11434/api/ps`

La estación debe respetar Policy Engine, Kill Switch, EvidenceStore y AuditLog.
La falta de RAG no debe marcar LaIA como `FAILED` si Ollama y el modelo oficial
responden; debe reflejarse como estado de conocimiento ausente, obsoleto o
parcial.

### 3.2 Precedencia de variables IA

- `AI_ENABLED` es el interruptor global de IA.
- `MISTRAL_ENABLED` y `ANGEL_ENABLED` solo se evalúan si `AI_ENABLED=1`.
- La instalación puede estar lista con `AI_ENABLED=0`, pero la aplicación no
  debe usar IA hasta activarlo explícitamente.
- `.env.example` debe permanecer seguro por defecto: sin secretos reales y con
  IA global desactivada.

### 3.3 Rutas Ollama

- `OLLAMA_MODELS` es la variable persistente de Ollama en Windows, configurable
  por el operador con `setx`.
- `OLLAMA_MODELS_DIR` es la ruta documental/configurable de Ojo de Dios.
- Ambas deben apuntar a `storage/models/ollama` cuando el operador configure la
  estación local.

### 3.4 Scripts documentados

| Script | Responsabilidad |
| --- | --- |
| `scripts/windows/ia/instalar_laia_mistral.bat` | Menú principal de instalación, descarga del modelo oficial y healthcheck. |
| `scripts/windows/ia/01_instalar_ollama.bat` | Instalación o comprobación aislada de Ollama. |
| `scripts/windows/ia/04_aplicar_system_prompt.bat` | Prepara el alias opcional de prueba con prompt, sin sustituir `MISTRAL_MODEL`. |
| `scripts/windows/ia/03_probar_mistral.bat` | Verifica Ollama, base de conocimiento, modelo y respuesta local. |
| `scripts/windows/ia/construir_base_conocimiento.bat` | Construye la base RAG usando `.venv\Scripts\python.exe`. |

El menú principal conserva la opción avanzada de abliteración fuera del flujo
interactivo. Esa ruta queda marcada como `IMPLEMENTACION_USUARIO_REQUERIDA` y no
forma parte del instalador operativo.

### 3.5 Rutas LaIA/Mistral

| Uso | Ruta |
| --- | --- |
| Modelos Ollama | `storage/models/ollama` |
| Logs IA | `storage/logs/ia` |
| Runtime/status | `storage/runtime` |
| Knowledge/RAG | `storage/knowledge` |
| Prompt contractual | `docs/ai_prompts/laia_mistral_system_prompt.md` |

## 4. Estación Hermes Agent

### 4.1 Verdad única de nombres y workspace

- Nombre oficial: `Hermes Agent`.
- Repositorio oficial: `https://github.com/NousResearch/hermes-agent`.
- Documentación oficial: `https://hermes-agent.nousresearch.com/docs/`.

- Nombre interno: `hermes_lab`.
- Nombre visible: `Hermes Agent Lab`.
- Alias histórico deprecated: no usar como nombre operativo.
- Workspace autorizado: `modules/laboratory/`.
- Archivo por propuesta: `PROMOTION_MANIFEST.json`.
- Archivo central promovido: `modules/laboratory/_promoted_manifest/`.
- Preparación de workspace: `LAB_WORKSPACE_READY`.
- API comprobada + controles válidos: `READY_CONTROLLED`.

Hermes Agent es la estación de asistencia externa controlada para propuestas,
revisión técnica y apoyo cuando LaIA no tiene capacidad local suficiente. Sus
salidas permanecen dentro de `modules/laboratory/` y requieren sandbox,
revisión, aprobación, promoción controlada, rollback posible y registro
documental antes de cualquier adopción.

Hermes Agent no sustituye a X5/OjoRouter, Policy Engine, Kill Switch,
EvidenceStore ni AuditLog. Sus propuestas son material de laboratorio hasta que
exista revisión explícita.

### 4.2 Workspace

Workspace principal: `modules/laboratory/`.

Subáreas esperadas:

- `modules/laboratory/_inbox` para entradas y propuestas pendientes.
- `modules/laboratory/_reviews` para revisión humana o técnica.
- `modules/laboratory/_sandbox` para pruebas controladas.
- `modules/laboratory/_promoted_manifest` para manifiestos promovidos.

### 4.3 API DeepSeek

La estación usa DeepSeek como proveedor externo controlado:

- Base URL: `https://api.deepseek.com`.
- Modelos configurados: `deepseek-v4-pro`, `deepseek-v4-flash`.
- Endpoints documentados:
  - `GET /models`
  - `POST /chat/completions`
- El healthcheck debe validar disponibilidad del modelo mediante `/models` antes
  de considerar la estación lista.
- Nunca se debe imprimir ni registrar `DEEPSEEK_API_KEY`.

Variables declaradas en `.env`:

| Variable | Significado |
| --- | --- |
| `ANGEL_PROVIDER` | Proveedor externo configurado. |
| `DEEPSEEK_API_KEY` | Clave local privada de DeepSeek; no se registra ni se documenta con valor real. |
| `DEEPSEEK_API_URL` | URL base de API: `https://api.deepseek.com`. |
| `DEEPSEEK_MODEL` | Modelo principal: `deepseek-v4-pro`. |
| `DEEPSEEK_FAST_MODEL` | Modelo rápido/fallback/healthcheck: `deepseek-v4-flash`. |
| `ANGEL_WORKSPACE` | Ruta del workspace controlado. |
| `ANGEL_REQUIRE_APPROVAL` | Exige aprobación antes de promoción. |
| `ANGEL_SANDBOX_ONLY` | Mantiene las propuestas en entorno de laboratorio. |

`.env.example` solo contiene marcadores. No se documentan claves reales.

### 4.4 Scripts, logs y healthcheck

| Script | Responsabilidad |
| --- | --- |
| `scripts/windows/ia/preparar_estacion_angel_hermes.bat` | Crea workspace y verifica configuración mínima. |
| `scripts/windows/ia/comprobar_angel_hermes.bat` | Comprueba disponibilidad controlada de DeepSeek API. |

El estado se guarda en `storage/runtime/angel_hermes_status.json` y el log en
`storage/logs/ia/angel_hermes_healthcheck.log`.

## 5. Evidencias y trazabilidad

M16 debe conservar evidencias trazables, hashes, rutas, timestamps, actor,
policy scope, estado del job, artefactos enmascarados por defecto y enlace con
AuditLog. Las evidencias no deben contener secretos ni claves API.

## 6. Panel de IAs y chat unificado

El panel futuro de IAs debe diferenciar LaIA/Mistral local, X5/OjoRouter,
Hermes Agent Lab y DeepSeek. El chat unificado puede orquestar asistencia, pero
no debe saltarse `AI_ENABLED`, Policy Engine, Kill Switch, EvidenceStore,
AuditLog ni los límites del workspace de laboratorio.

## 7. Healthchecks, logs y auditoría

Los healthchecks deben guardar JSON de estado y log operativo sin secretos. Los
códigos de salida reales siguen pendientes de validación en Windows para los
Vectores 1 y 2.

## 8. VersionLock y ToolHealth

M16 debe comprobar VersionLock y ToolHealth antes de declarar readiness de una
capacidad. Las versiones o herramientas ausentes deben quedar como estado
honesto, no como éxito implícito.

## 9. Integridad de registry, paneles, workers, estados y contratos

M16 debe validar que registry, paneles, workers, estados y contratos JSON estén
alineados. No se deben declarar técnicas ejecutables sin implementación aprobada,
worker real, contrato de evidence y control X5/OjoRouter.

## 10. Calidad de evidencia y scoring

La calidad de evidencia debe poder puntuarse con criterios reproducibles:
integridad, completitud, trazabilidad, ausencia de secretos, relación con scope,
redacción de datos sensibles y consistencia de hashes.

## 11. Integridad Hermes, promoción y rollback

Cada propuesta de `hermes_lab` debe tener `PROMOTION_MANIFEST.json`, revisión,
aprobación explícita, manifiesto central en
`modules/laboratory/_promoted_manifest/` si se promociona, y plan de rollback.
La promoción no puede ser automática.

## 12. Readiness final y exportación externa

El readiness final de M16 requiere completar y validar Vectores 3-10 además de
normalizar Vectores 1 y 2. La exportación externa futura puede preparar paquetes
para productos separados como Mano de Dios, pero sin integración interna.

## 13. Estados M16

| Estado | Significado | Estación |
| --- | --- | --- |
| `READY_LOCAL_AI` | LaIA/Mistral local está disponible y el modelo oficial responde. | LaIA/Mistral |
| `KNOWLEDGE_MISSING` | Ollama y modelo responden, pero falta la base RAG. | LaIA/Mistral |
| `KNOWLEDGE_STALE` | Existe RAG, pero está obsoleto frente a documentación o registry. | LaIA/Mistral |
| `MODEL_MISSING` | Ollama está disponible, pero falta el modelo oficial Mistral. | LaIA/Mistral |
| `MISSING_TOOL` | Falta una herramienta requerida, por ejemplo Ollama o Python. | LaIA/Mistral |
| `PARTIAL` | La estación responde, pero una dependencia no crítica está incompleta. | LaIA/Mistral |
| `FAILED` | La comprobación falló de forma bloqueante; no usar para falta aislada de RAG si Ollama y modelo responden. | Ambas |
| `LAB_WORKSPACE_READY` | `modules/laboratory/` existe y está preparado para propuestas. | Hermes Agent |
| `READY_CONTROLLED` | Hermes Agent está listo bajo sandbox, aprobación y controles. | Hermes Agent |
| `MISSING_API_KEY` | Falta `DEEPSEEK_API_KEY` en `.env` local. | Hermes Agent |
| `API_UNREACHABLE` | La API externa configurada no responde o no es alcanzable. | Hermes Agent |

## 14. Rutas de almacenamiento

| Categoría | Ruta | Uso |
| --- | --- | --- |
| Modelos | `storage/models/ollama` | Almacenamiento local de modelos Ollama. |
| Logs | `storage/logs/ia` | Logs de instalación, prompt y healthchecks. |
| Runtime | `storage/runtime` | JSON de estado y artefactos de prueba. |
| Knowledge | `storage/knowledge` | Base de conocimiento local para RAG. |
| Workspace | `modules/laboratory` | Laboratorio controlado Hermes Agent. |
| Manifiestos promovidos | `modules/laboratory/_promoted_manifest/` | Manifiestos centrales promovidos. |
| Prompts | `docs/ai_prompts` | System prompts contractuales. |
| Setup | `docs/setup` | Guías de instalación y operación documental. |

## 15. Criterios de aceptación pendientes V1-V2

Los Vectores 1 y 2 permanecen pendientes hasta validar en entorno real:

- [ ] BATs probados en Windows real.
- [ ] Rutas resueltas desde cualquier directorio.
- [ ] Estados correctos.
- [ ] Healthchecks con códigos de salida reales.
- [ ] RAG construido y trazable.
- [ ] API DeepSeek validada.
- [ ] Ningún secreto en logs.
- [ ] Documentación coherente.


## Vector 3 — Sistema universal de evidencias y trazabilidad

“M16 recibe, relaciona y preserva evidencias procedentes de todos los módulos. Ninguna técnica se considera exitosa únicamente por devolver texto, código de salida o estado OK. Todo resultado debe estar vinculado a una ejecución, objetivo, técnica, herramienta, operador y evidencia verificable.”

Flujo oficial exacto:

Módulo → X5/OjoRouter → Worker → EvidenceStore → ScoringEngine → LaIA/Mistral → M16

Identificadores obligatorios:

- "run_id": ejecución completa de una técnica.
- "trace_id": correlación transversal entre módulos, logs, eventos y handoffs.
- "span_id": operación concreta dentro de un trace.
- "target_id": objetivo autorizado.
- "target_fingerprint_id": versión del perfil del objetivo.
- "module_id": módulo origen.
- "technique_id": técnica registrada.
- "worker_id": worker responsable.
- "evidence_id": evidencia individual.
- "finding_id": hallazgo normalizado.
- "handoff_id": transferencia entre módulos.
- "operator_id": operador responsable.
- "report_id": informe generado.

Este vector documenta el contrato universal de evidencia; no crea
implementación, endpoints, workers ni persistencia nueva.

### Eventos y timeline

Los eventos de evidencia documentan creación, escritura, hash, verificación,
visualización, revelado, redacción, exportación, handoff, enlaces a hallazgos,
enlaces a informes, archivado e integridad fallida. Los contratos oficiales de
`evidence_event` y su timeline están en `docs/EVIDENCE_CONTRACT.md`. Esta
subsección no añade endpoints, tablas ni implementación real.

### Cadena de custodia interna

La cadena de custodia interna documenta actor, técnica, herramienta, versión,
fechas, visualizaciones, revelados, redacciones, exportaciones, handoffs, hashes
y relación con AuditLog. Las reglas oficiales están en
`docs/EVIDENCE_CONTRACT.md`. Esta subsección no afirma capacidad operativa ni
crea persistencia nueva.

### Handoff universal

El handoff universal permite documentar transferencias de evidencia entre
módulos conservando `trace_id`, `run_id`, `evidence_ids`, redacción por defecto
y registro en AuditLog cuando el handoff sea incompleto. El contrato oficial
`evidence_handoff` está en `docs/EVIDENCE_CONTRACT.md`. Esta subsección no crea
workers, APIs ni rutas nuevas.

### Comparación antes/después

La comparación antes/después relaciona evidencias previas y posteriores,
diferencias declaradas, impacto probado, calidad y posible rollback. El contrato
oficial `before_after_comparison` está en `docs/EVIDENCE_CONTRACT.md`. LaIA puede
explicar diferencias documentadas, pero no inventarlas ni modificar scoring sin
contrato y AuditLog.

### Almacenamiento y manifest

La estructura futura de almacenamiento, `evidence_manifest.json`, `timeline.json`,
`artifacts/`, `reports/` y `exports/` queda documentada como contrato, no como
implementación activa. Los contratos oficiales de estructura y
`evidence_manifest` están en `docs/EVIDENCE_CONTRACT.md`. Esta subsección no
añade endpoints, tablas, workers ni rutas creadas en runtime.

### Relaciones de evidencia

Las relaciones entre evidencias, hallazgos, ejecuciones, informes, exports,
handoffs y operadores se documentan para trazabilidad futura. Las relaciones
oficiales están en `docs/EVIDENCE_CONTRACT.md`. Una evidencia derivada nunca
sustituye ni modifica la evidencia original.

### Sensibilidad y redacción

Las políticas de sensibilidad y redacción determinan qué contenido puede verse,
exportarse o entregarse a LaIA. Las políticas oficiales están en
`docs/EVIDENCE_CONTRACT.md`. Esta subsección no afirma aplicación real de
redacción; solo fija el contrato documental.

### Exportación verificable

La exportación verificable exige manifest válido, SHA-256 del paquete, redacción
por defecto y conservación de `run_id`, `trace_id` y `evidence_ids`. El contrato
oficial `evidence_export` está en `docs/EVIDENCE_CONTRACT.md`. Esta subsección
no crea paquetes, endpoints, tablas ni capacidad operativa de exportación.

### Panel futuro Ops > Evidencias

El panel futuro **Ops > Evidencias** queda documentado como diseño de interfaz;
no crea vistas, rutas, endpoints, tablas ni capacidad operativa. Los contratos
oficiales están en `docs/EVIDENCE_CONTRACT.md`.

Subpáginas exactas:

- Visor general
- Ejecuciones
- Traces
- Hallazgos
- Timeline
- Integridad
- Exportaciones
- Handoffs
- Informes
- AuditLog

Filtros exactos:

- módulo
- técnica
- objetivo
- calidad
- estado
- operador
- fecha
- tipo
- sensibilidad
- "trace_id"
- "run_id"

Acciones visibles:

- Ver detalle
- Ver timeline
- Verificar integridad
- Crear handoff
- Exportar enmascarado
- Mostrar completo
- Archivar

### Errores y recuperación

Errores exactos documentados para Vector 3:

- archivo no encontrado;
- hash no coincide;
- manifest corrupto;
- timeline roto;
- evidencia incompleta;
- evidencia duplicada;
- storage no disponible;
- exportación fallida;
- handoff incompleto.

Reglas:

- registrar AuditLog;
- marcar estado correcto;
- preservar lo disponible;
- no sobrescribir;
- no puntuar;
- permitir a LaIA explicar la incidencia;
- sugerir recuperación sin inventar resultado.

## Vector 4 — Panel de control de IAs y chat unificado

“El panel de IAs centraliza el estado, conversaciones, tareas, propuestas y decisiones de LaIA/Mistral, Hermes Agent Lab y DeepSeek. No sustituye los chats contextuales de cada módulo: los reúne, conserva su contexto y permite al usuario supervisar el sistema desde un único punto.”

Este vector documenta estructura y contratos base; no crea implementación, tablas
reales, endpoints reales ni ejecución directa desde el chat. El chat unificado no
sustituye a X5/OjoRouter, Policy Engine, Kill Switch, EvidenceStore ni AuditLog.

### Barra lateral del panel

Subpáginas exactas, en orden:

1. Resumen de agentes
2. Chat unificado
3. Conversaciones
4. Contexto activo
5. Planes de LaIA
6. Tareas de Hermes Agent
7. Revisiones DeepSeek
8. Aprobaciones pendientes
9. Historial y AuditLog
10. Configuración visible

### Roles exactos

- LaIA/Mistral: interpreta intención, analiza contexto, crea planes, rellena parámetros, explica evidencias y propone handoffs.
- X5/OjoRouter: valida y ejecuta planes permitidos; no conversa como agente principal.
- Hermes Agent Lab: crea propuestas de laboratorio, parsers, wrappers, schemas y módulos experimentales.
- DeepSeek: revisa, diseña y ayuda a Hermes Agent; no ejecuta ni promociona.
- Usuario: máxima autoridad para aprobar, rechazar, pausar, reanudar y cerrar.

### Fuentes de contexto del chat

El chat debe recibir siempre:

- "active_module"
- "active_vector"
- "target_id"
- "target_fingerprint_id"
- "run_id"
- "trace_id"
- "selected_technique_id"
- "evidence_ids"
- "finding_ids"
- "operator_id"
- "execution_mode"
- "policy_status"
- "kill_switch_status"

Si un campo no aplica, debe ser "null"; no se elimina del contrato.

### Tiempo real y persistencia

- WebSocket transmite mensajes y estados al panel en tiempo real.
- Redis Pub/Sub distribuye eventos vivos entre componentes.
- Redis no es fuente de verdad ni histórico.
- SQLite/DB persiste sesiones, mensajes, aprobaciones y referencias.
- Cada mensaje conserva "session_id" y "trace_id".
- Una desconexión del panel no debe perder el histórico persistido.

Los contratos base `ai_chat_session` y `ai_chat_message` están documentados en
`docs/AI_X5_HERMES_DEEPSEEK_ROLES.md`. Las rutas futuras del panel están
documentadas en `docs/API.md` sin implementarlas.

### Comportamiento del panel

- "Resumen de agentes" muestra LaIA/Mistral, Hermes Agent, DeepSeek y X5 con estado, modelo, proveedor, última comprobación y último error.
- "Chat unificado" muestra mensajes persistidos, agente activo, módulo activo, target, trace y acciones estructuradas.
- "Contexto activo" muestra todos los campos del contrato; los valores ausentes aparecen como "null".
- "Planes de LaIA" muestra borradores, planes pendientes, aprobados, rechazados y cerrados.
- "Tareas de Hermes Agent" muestra estado, ruta de laboratorio, archivos esperados y aprobación.
- "Revisiones DeepSeek" muestra alcance, resultado, recomendaciones y relación con tarea.
- "Aprobaciones pendientes" permite aprobar o rechazar una sola acción concreta.
- "Historial y AuditLog" muestra eventos ordenados por timestamp.
- "Configuración visible" muestra modelos, endpoints y estados, nunca secretos.

### Acciones estructuradas

Toda intención del chat que pueda crear planes, solicitudes, cambios de estado,
aprobaciones o handoffs debe convertirse en un contrato JSON visible y revisable
antes de cualquier cola, validación o decisión. Los contratos oficiales, incluido
`ai_action_request`, están en `docs/AI_X5_HERMES_DEEPSEEK_ROLES.md`. Esta
subsección no permite ejecución directa desde texto libre.

### Aprobaciones pendientes

Las aprobaciones pendientes documentan decisiones del usuario para ejecución de
planes, tareas Hermes, instalaciones, pruebas sandbox, promociones, revelado de
evidencia, exportaciones y cierre de sesión. El contrato oficial
`ai_approval_request` está en `docs/AI_X5_HERMES_DEEPSEEK_ROLES.md`. Una
aprobación rechazada no se ejecuta y debe generar AuditLog.

### Tareas de Hermes Agent

Las tareas de Hermes Agent se documentan como solicitudes de laboratorio para
parsers, wrappers, schemas, módulos, reparaciones, panel schemas, adaptadores de
handoff o pruebas sandbox. El contrato oficial `hermes_task_request` está en
`docs/AI_X5_HERMES_DEEPSEEK_ROLES.md`. Esta subsección no crea workers ni
archivos reales en `modules/laboratory/`.

### Revisiones DeepSeek

Las revisiones DeepSeek se documentan como revisión de arquitectura, calidad,
contratos, dependencias, evidencia o readiness de promoción. El contrato oficial
`deepseek_review_request` está en `docs/AI_X5_HERMES_DEEPSEEK_ROLES.md`.
DeepSeek solo devuelve revisión y recomendaciones; no cambia producción ni
promociona.

### Reconexión y recuperación

- al reconectar WebSocket, el panel solicita estado persistido de la sesión;
- mensajes no persistidos no se consideran entregados;
- una desconexión no cancela automáticamente planes o tareas;
- el usuario ve aviso de desconexión y último timestamp válido;
- al recuperar conexión se comparan "session_id", "trace_id" y último mensaje;
- duplicados se ignoran por "message_id";
- si hay conflicto, se marca sesión "error" y se registra AuditLog.

### Errores del panel de IAs

Errores exactos documentados para Vector 4:

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

## Vector 5 — Healthchecks, logs y auditoría de IAs

“M16 debe poder verificar el estado real de LaIA/Mistral, Hermes Agent, DeepSeek, RAG, Redis, SQLite, X5 y dependencias críticas. Un agente no se considera listo por existir un archivo o variable: debe superar un healthcheck documentado, generar log, registrar estado y no exponer secretos.”

Este vector documenta contratos y comportamiento esperado; no crea
implementación, endpoints reales, scripts, workers, tablas, DB ni rutas en
`storage/`.

### Componentes a comprobar

Checks exactos:

- "ollama_binary": existe "ollama".
- "ollama_api": responde API local.
- "mistral_model": modelo oficial disponible.
- "mistral_generate": prueba corta con salida válida.
- "mistral_chat": prueba chat válida.
- "rag_index": base de conocimiento existe.
- "rag_manifest": manifiesto RAG con hashes.
- "deepseek_api": API responde.
- "deepseek_model": modelo configurado disponible.
- "angel_workspace": existe "modules/laboratory".
- "angel_sandbox_only": sandbox activo.
- "redis": bus disponible.
- "sqlite": DB disponible.
- "x5_router": estado de enrutador.
- "policy_engine": estado de políticas.
- "kill_switch": estado visible.

### Estados oficiales de healthcheck

Estados exactos:

"READY", "READY_CONTROLLED", "READY_LOCAL_AI", "PARTIAL", "DEGRADED", "MISSING_TOOL", "MODEL_MISSING", "API_UNREACHABLE", "KNOWLEDGE_MISSING", "KNOWLEDGE_STALE", "DISABLED", "FAILED".

Reglas:

- "READY" exige checks críticos OK.
- "PARTIAL" si una parte no crítica falta.
- "DEGRADED" si responde pero con limitaciones.
- "DISABLED" si variable global lo desactiva.
- "FAILED" solo si falla un componente crítico.
- nunca marcar "READY_CONTROLLED" sin API o controles validados.

### Contrato JSON ai_healthcheck_result

```json
{
  "type": "ai_healthcheck_result",
  "check_id": "hc-uuid",
  "component": "laia_mistral",
  "checks": {
    "ollama_api": "ok",
    "mistral_model": "ok",
    "rag_manifest": "missing"
  },
  "status": "PARTIAL",
  "model": "CognitiveComputations/dolphin-mistral-nemo:12b",
  "provider": "ollama",
  "api_url": "http://localhost:11434",
  "checked_at": "2026-06-01T12:00:00Z",
  "operator_id": "admin",
  "errors": [],
  "warnings": ["KNOWLEDGE_MISSING"],
  "secrets_redacted": true
}
```

### Logs de healthcheck y auditoría

Rutas futuras documentadas:

- "storage/logs/ia/laia_mistral_healthcheck.log"
- "storage/logs/ia/angel_hermes_healthcheck.log"
- "storage/logs/ia/rag_build.log"
- "storage/logs/ops/healthcheck.log"
- "storage/runtime/ai_health_status.json"

Reglas:

- logs rotables;
- no guardar claves;
- no guardar prompts con datos sensibles completos;
- cada línea debe tener timestamp, componente, estado y trace_id si aplica;
- errores no deben incluir "DEEPSEEK_API_KEY".

Las rutas futuras de API para este vector están documentadas en `docs/API.md`
sin implementarlas.

### Formato estándar de logs M16

Cada línea futura de log debe seguir este esquema lógico:

```json
{
  "timestamp": "2026-06-01T12:00:00Z",
  "level": "INFO",
  "component": "laia_mistral",
  "event": "healthcheck_completed",
  "trace_id": "trace-uuid",
  "run_id": null,
  "operator_id": "admin",
  "status": "PARTIAL",
  "message": "RAG no construido",
  "details": {},
  "secrets_redacted": true
}
```

Reglas:

- timestamps en ISO 8601 UTC;
- "trace_id" obligatorio si el evento pertenece a una sesión;
- nunca registrar claves, tokens, prompts sensibles completos ni rutas con secretos;
- logs rotables;
- un error no debe ocultarse ni marcarse como éxito;
- si el evento afecta a evidencia, incluir "evidence_id".

### Eventos de auditoría IA

Eventos exactos:

- "agent_enabled"
- "agent_disabled"
- "healthcheck_started"
- "healthcheck_completed"
- "healthcheck_failed"
- "model_missing"
- "rag_missing"
- "rag_stale"
- "api_unreachable"
- "approval_requested"
- "approval_approved"
- "approval_rejected"
- "secret_redacted"
- "secret_reveal_attempted"
- "tool_blocked"
- "kill_switch_triggered"
- "session_archived"

Todo evento de auditoría debe conservar:
"event_id", "timestamp", "component", "operator_id", "trace_id", "action", "result", "reason", "metadata".

### Retención y rotación

- logs IA: retención recomendada 30 días;
- logs ops/health: retención recomendada 90 días;
- audit events: conservar mientras exista el proyecto/auditoría;
- exports: conservar según política de M16;
- rotación por tamaño y/o fecha;
- no borrar evidencias desde rotación de logs;
- borrar/archivar requiere AuditLog.

### Panel Ops > Health

Subpáginas exactas:

- Estado general
- IA local
- Hermes Agent
- DeepSeek
- RAG / base de conocimiento
- Redis / bus
- SQLite / persistencia
- X5 / OjoRouter
- Policy / Kill Switch
- Logs
- AuditLog

Acciones visibles:

- Ejecutar healthcheck
- Ver último resultado
- Ver log
- Ver auditoría
- Reintentar componente
- Marcar incidencia revisada
- Exportar diagnóstico enmascarado

### Errores y recuperación Health

Errores exactos:

- log no escribible;
- log corrupto;
- API local caída;
- API externa caída;
- modelo ausente;
- RAG ausente;
- RAG obsoleto;
- Redis no disponible;
- SQLite no disponible;
- X5 no responde;
- Policy Engine no responde;
- Kill Switch no verificable.

Reglas:

- marcar estado correcto;
- registrar AuditLog;
- no fingir disponibilidad;
- mostrar explicación de LaIA si está disponible;
- permitir reintento manual;
- no usar un agente en "FAILED".

## Vector 6 — VersionLock y ToolHealth

“M16 debe registrar la versión real, ruta, origen, estado y compatibilidad de cada herramienta usada por Ojo de Dios. Ninguna técnica debe ejecutarse contra una herramienta desconocida, incompatible, no verificada o fuera de política. VersionLock fija lo que existe; ToolHealth verifica si puede usarse.”

Este vector documenta contratos y reglas futuras; no crea implementación,
endpoints reales, workers, tablas, DB ni comprobaciones reales.

### Diferencia exacta

- "VersionLock": registro estable de versión, ruta, fuente, hash y decisión.
- "ToolHealth": comprobación viva de disponibilidad y funcionamiento.
- "MODULE_TOOL_INVENTORY": inventario documental esperado.
- "versionlock_id": referencia concreta usada por una ejecución o evidencia.

### Contrato JSON tool_version_lock

```json
{
  "type": "tool_version_lock",
  "versionlock_id": "vl-uuid",
  "tool_id": "ollama",
  "tool_name": "Ollama",
  "module_id": "m16",
  "expected_version": "documented",
  "resolved_version": "0.x.x",
  "binary_path": "C:/Users/user/AppData/Local/Programs/Ollama/ollama.exe",
  "source_url": "https://ollama.com",
  "runtime": "windows",
  "binary_sha256": "sha256-or-null",
  "checked_at": "2026-06-01T12:00:00Z",
  "status": "LOCKED",
  "notes": "Herramienta disponible y aceptada"
}
```

Estados exactos:

"LOCKED", "MISSING", "NEEDS_REVIEW", "INCOMPATIBLE", "DISABLED", "MANUAL_REQUIRED".

### Contrato JSON tool_health_result

```json
{
  "type": "tool_health_result",
  "health_id": "health-uuid",
  "tool_id": "ollama",
  "versionlock_id": "vl-uuid",
  "module_id": "m16",
  "command_checked": "ollama --version",
  "available": true,
  "responds": true,
  "exit_code": 0,
  "status": "READY",
  "checked_at": "2026-06-01T12:00:00Z",
  "errors": [],
  "warnings": []
}
```

Estados exactos:

"READY", "PARTIAL", "MISSING_TOOL", "FAILED", "BLOCKED_BY_POLICY", "NEEDS_REVIEW".

### Reglas obligatorias

- toda ejecución futura guarda "versionlock_id";
- toda evidencia guarda "source_tool_version" y "versionlock_id";
- herramienta "MISSING" bloquea ejecución;
- herramienta "INCOMPATIBLE" bloquea ejecución;
- "NEEDS_REVIEW" exige aprobación;
- "MANUAL_REQUIRED" permite documentación, no ejecución automática;
- "ToolHealth" no sustituye a VersionLock;
- cambio de versión crea nuevo "versionlock_id";
- no usar versiones hardcodeadas como verdad final;
- si una herramienta no devuelve versión fiable, registrar "resolved_version: unknown" y "NEEDS_REVIEW".

### Tipos de runtime

Runtimes exactos:

"windows", "wsl_kali", "docker", "hardware", "android_device", "cloud_api", "local_ai", "external_api", "manual".

Las rutas futuras de API para VersionLock y ToolHealth están documentadas en
`docs/API.md` sin implementarlas.

### Inventario SBOM y procedencia

“M16 mantiene un inventario documental tipo SBOM para herramientas, modelos IA, dependencias, wrappers, conectores y componentes externos usados por Ojo de Dios. El objetivo es saber qué versión existe, de dónde viene, quién la aprobó, qué módulo la usa y qué evidencias produjo.”

#### Contrato JSON tool_inventory_item

```json
{
  "type": "tool_inventory_item",
  "tool_id": "ollama",
  "tool_name": "Ollama",
  "category": "local_ai",
  "module_ids": ["m16", "m12"],
  "runtime": "windows",
  "source_url": "https://ollama.com",
  "vendor_or_project": "Ollama",
  "expected_version": "documented",
  "versionlock_id": "vl-uuid",
  "healthcheck_method": "command_and_api",
  "approved_status": "approved",
  "notes": "Herramienta IA local"
}
```

Estados "approved_status" exactos:

"approved", "needs_review", "blocked", "manual_only", "deprecated".

#### Procedencia

Reglas:

- todo componente externo registra "source_url";
- si viene de GitHub, guardar repo y release/tag si existe;
- si viene de API externa, guardar proveedor y endpoint base;
- si es modelo IA, guardar proveedor, nombre, cuantización si aplica y tamaño si se conoce;
- si es hardware, guardar fabricante/modelo y método healthcheck;
- si no se conoce procedencia, estado "needs_review".

### Cambio de versión

Reglas exactas:

- un cambio de versión crea nuevo "versionlock_id";
- no se edita el "versionlock_id" anterior;
- la versión anterior pasa a "deprecated" o "archived";
- el cambio requiere motivo;
- si afecta a ejecución, requiere aprobación;
- si rompe contrato, bloquea hasta revisión;
- evidencias antiguas conservan su "versionlock_id" original.

Contrato:

```json
{
  "type": "tool_version_change",
  "change_id": "change-uuid",
  "tool_id": "ollama",
  "old_versionlock_id": "vl-old",
  "new_versionlock_id": "vl-new",
  "reason": "model_update",
  "requires_approval": true,
  "approved_by": null,
  "created_at": "2026-06-01T12:00:00Z",
  "status": "pending_review"
}
```

Estados:

"pending_review", "approved", "rejected", "rolled_back".

### Relación con evidencias

- "evidence_record.versionlock_id" apunta a la herramienta/modelo usado;
- un informe debe listar herramientas y versiones usadas;
- si VersionLock cambia, no se reescriben evidencias antiguas;
- LaIA puede explicar impacto de versión;
- X5 no ejecuta si la herramienta está "blocked", "incompatible" o "missing".

### Revisión de confianza y aprobación de herramientas

“Cuando LaIA/Mistral, Hermes Agent o el usuario propongan una herramienta nueva, M16 debe registrarla como candidata. Ninguna herramienta candidata pasa a uso real hasta tener procedencia, estado VersionLock, ToolHealth, riesgo, aprobación humana y relación con técnica/evidencia.”

#### Contrato JSON tool_candidate_review

```json
{
  "type": "tool_candidate_review",
  "review_id": "tool-review-uuid",
  "tool_id": "tool-id",
  "proposed_by": "angel_hermes",
  "source_url": "https://example.com/repo",
  "module_id": "m16",
  "intended_use": "parser para evidencia",
  "related_technique_ids": [],
  "risk_level": "medium",
  "trust_signals": {
    "official_source": false,
    "release_available": true,
    "license_detected": true,
    "recent_activity": true,
    "known_maintainer": false,
    "checksum_available": false
  },
  "required_checks": [
    "source_review",
    "versionlock",
    "toolhealth",
    "sandbox_test",
    "human_approval"
  ],
  "decision": "pending_review",
  "created_at": "2026-06-01T12:00:00Z",
  "operator_id": "admin"
}
```

Estados "decision" exactos:

"pending_review", "approved", "rejected", "blocked", "manual_only", "sandbox_only".

#### Reglas de aprobación

- "approved": puede entrar en inventario y usarse por X5 si Policy lo permite.
- "sandbox_only": solo se usa en "modules/laboratory/".
- "manual_only": documentado, requiere intervención del usuario.
- "blocked": no puede usarse.
- "rejected": queda archivado con motivo.
- una herramienta sin "source_url" queda "pending_review";
- una herramienta con procedencia dudosa queda "sandbox_only" o "blocked";
- una herramienta propuesta por Hermes Agent nunca se aprueba sola;
- el usuario decide promoción final.

#### Riesgo por herramienta

Niveles exactos:

"low", "medium", "high", "critical".

Reglas:

- herramienta solo lectura puede ser "low" o "medium";
- herramienta que modifica estado puede ser "high";
- herramienta que instala dependencias o toca sistema puede ser "high" o "critical";
- herramienta hardware/emisión/laboratorio queda como mínimo "high";
- riesgo "critical" exige aprobación reforzada.

#### Uso evolutivo

“La filosofía evolutiva de Ojo de Dios permite que Hermes Agent cree o proponga herramientas nuevas cuando falte capacidad. M16 no bloquea la evolución: la encauza. Toda herramienta nueva nace en laboratorio, se revisa, se prueba, se registra, se aprueba y solo después puede integrarse como parte del arsenal controlado.”

### Panel Ops > ToolHealth

Subpáginas exactas:

- Inventario
- VersionLock
- Healthchecks
- Herramientas candidatas
- Cambios de versión
- Bloqueos
- Aprobaciones
- Historial / AuditLog

Columnas obligatorias de tabla:

- "tool_id"
- "tool_name"
- "module_ids"
- "runtime"
- "expected_version"
- "resolved_version"
- "status"
- "health_status"
- "approved_status"
- "source_url"
- "versionlock_id"
- "last_checked_at"

Acciones visibles:

- Ver detalle
- Ejecutar healthcheck
- Resolver VersionLock
- Marcar "NEEDS_REVIEW"
- Aprobar herramienta
- Bloquear herramienta
- Crear cambio de versión
- Rollback de versión
- Ver evidencias relacionadas

### Bloqueo de ejecución

Reglas exactas:

- X5 no ejecuta si herramienta está "MISSING".
- X5 no ejecuta si herramienta está "INCOMPATIBLE".
- X5 no ejecuta si herramienta está "blocked".
- X5 pide aprobación si herramienta está "NEEDS_REVIEW".
- X5 solo usa "sandbox_only" dentro de "modules/laboratory/".
- "manual_only" nunca se ejecuta automáticamente.
- Una técnica con herramienta bloqueada queda "blocked_by_toolhealth".
- El panel debe mostrar el motivo exacto del bloqueo.

### Errores de VersionLock y ToolHealth

Errores exactos:

- herramienta no encontrada;
- versión no detectable;
- versión incompatible;
- ruta binaria inválida;
- hash no calculable;
- hash cambiado;
- fuente desconocida;
- herramienta candidata sin revisión;
- healthcheck sin respuesta;
- permiso insuficiente;
- runtime no disponible;
- hardware ausente;
- API externa no disponible.

Reglas:

- registrar AuditLog;
- no fingir "READY";
- marcar estado correcto;
- sugerir recuperación;
- conservar resultado anterior;
- no borrar VersionLock antiguo;
- LaIA puede explicar el error, no desbloquearlo.

### Relación con Hermes Agent

“Hermes Agent puede proponer herramientas, wrappers o dependencias nuevas. M16 las registra como candidatas. La herramienta no entra en arsenal controlado hasta pasar revisión, VersionLock, ToolHealth, sandbox y aprobación humana.”

Estados de herramienta creada por Ángel:

- "candidate"
- "sandbox_only"
- "needs_review"
- "approved"
- "blocked"
- "deprecated"

## Vector 7 — Integridad de registry, contratos, paneles, workers y estados

“M16 debe impedir incoherencias internas antes de que X5 ejecute planes. Una técnica no es válida solo por existir en documentación: debe tener registro, contrato, estado, módulo, evidencia esperada, permisos, worker futuro o marcador manual, y relación con panel/API cuando aplique.”

Este vector documenta guardas y criterios futuros; no crea implementación,
endpoints reales, workers, tablas, DB ni validadores reales.

### Guardas oficiales

Capacidades documentadas:

- "registry_integrity_guard"
- "contract_integrity_guard"
- "state_integrity_guard"
- "panel_integrity_guard"
- "worker_binding_guard"
- "execution_phase_gate"

Definiciones exactas:

- "registry_integrity_guard": comprueba que toda técnica documentada exista en TechniqueRegistry futuro.
- "contract_integrity_guard": comprueba que cada técnica tenga contrato JSON esperado.
- "state_integrity_guard": comprueba estados válidos de módulo, técnica, agente y evidencia.
- "panel_integrity_guard": comprueba que las acciones del panel apunten a técnicas conocidas.
- "worker_binding_guard": comprueba worker futuro o "IMPLEMENTACION_USUARIO_REQUERIDA".
- "execution_phase_gate": bloquea ejecución si falta contrato, scope, herramienta, evidencia esperada o aprobación.

### Contrato JSON integrity_check_result

```json
{
  "type": "integrity_check_result",
  "check_id": "integrity-uuid",
  "check_name": "registry_integrity_guard",
  "scope": "all_modules",
  "module_id": "android",
  "technique_id": "android.analysis.secrets",
  "status": "PASS",
  "severity": "medium",
  "errors": [],
  "warnings": [],
  "checked_at": "2026-06-01T12:00:00Z",
  "operator_id": "admin"
}
```

Estados exactos:

"PASS", "WARN", "FAIL", "BLOCKED", "NOT_APPLICABLE".

Severidad exacta:

"low", "medium", "high", "critical".

### Reglas de registry

- ninguna técnica desconocida puede entrar en un plan LaIA;
- X5 rechaza "technique_id" no registrado;
- técnica documentada sin contrato queda "WARN";
- técnica ejecutable sin evidencia esperada queda "FAIL";
- técnica sin worker y sin marcador manual queda "FAIL";
- técnica con "IMPLEMENTACION_USUARIO_REQUERIDA" puede existir, pero no ejecutarse automáticamente;
- Hermes Agent puede crear técnica experimental solo en laboratorio.

### Reglas de contrato JSON

- contratos usan JSON válido;
- contratos deben conservar "type", "technique_id", "scope", "operator", "requires_confirmation", "expected_evidence";
- campos ausentes no se inventan;
- JSON inválido bloquea ejecución;
- cambios de contrato requieren nueva versión documental;
- LaIA puede proponer contrato, pero X5 valida.

### Estados oficiales de técnica

"documented", "experimental", "lab_ready", "review_required", "approved_by_user", "promoted", "manual_required", "hardware_required", "disabled", "blocked_by_policy", "rejected".

Reglas:

- por debajo de "approved_by_user", X5 no ejecuta automáticamente;
- "manual_required" solo muestra instrucciones/contrato;
- "hardware_required" exige ToolHealth/hardware;
- "rejected" no vuelve a plan sin nueva revisión;
- "promoted" exige manifest, evidencia y aprobación.

Las rutas futuras de API para integridad están documentadas en `docs/API.md`
sin implementarlas.

### Integridad de paneles

“Cada botón, acción o formulario visible en panel debe apuntar a una técnica conocida, contrato documentado y endpoint futuro previsto. El panel no decide lógica por sí mismo: solo recoge intención, muestra contexto, pide confirmación y envía contrato a X5/OjoRouter.”

Reglas exactas:

- ningún botón usa "technique_id" desconocido;
- todo formulario conserva "scope", "operator", "requires_confirmation" y "expected_evidence";
- acciones sensibles muestran modal antes de ejecución;
- un panel puede mostrar técnica "IMPLEMENTACION_USUARIO_REQUERIDA", pero no marcarla como lista para ejecución;
- si falta contrato, el botón queda desactivado;
- si falta Policy/Kill Switch, el botón queda bloqueado;
- todos los bloqueos generan explicación visible y AuditLog.

### Integridad de API futura

Reglas exactas:

- toda ruta futura debe tener "module_id";
- toda ruta que ejecute acción debe recibir contrato JSON;
- toda ruta futura debe tener "operation_id" único;
- rutas de solo lectura no modifican estado;
- rutas de acción requieren autenticación, Policy y Kill Switch;
- rutas no deben devolver secretos completos por defecto;
- errores devuelven estado claro, no éxito falso.

Contrato documental mínimo para ruta futura:

```json
{
  "type": "api_route_contract",
  "route_id": "api-uuid",
  "method": "POST",
  "path": "/api/modules/{module_id}/actions",
  "operation_id": "create_module_action",
  "module_id": "android",
  "requires_auth": true,
  "requires_policy_check": true,
  "requires_kill_switch_check": true,
  "request_contract": "technique_action",
  "response_contract": "execution_result",
  "status": "documented"
}
```

### Integridad de workers

“Un worker futuro solo puede ejecutar técnicas registradas y contratos validados por X5. Si la técnica requiere lógica privada, hardware o intervención manual, el worker debe quedar como binding documental o marcador controlado, no como ejecución falsa.”

Estados de binding:

"bound", "missing_worker", "manual_required", "hardware_required", "lab_only", "blocked", "not_applicable".

Reglas exactas:

- "bound" exige worker futuro identificado;
- "missing_worker" bloquea ejecución;
- "manual_required" no ejecuta automático;
- "lab_only" solo trabaja en "modules/laboratory/";
- "hardware_required" exige ToolHealth;
- "blocked" impide plan;
- ningún worker marca éxito sin "evidence_ids".

### Fases de ejecución

Estados oficiales:

"draft", "validated", "waiting_confirmation", "queued", "running", "collecting_evidence", "completed", "partial", "failed", "blocked", "cancelled", "closed".

Reglas:

- "draft": LaIA propone.
- "validated": X5 valida contrato.
- "waiting_confirmation": falta decisión del usuario.
- "queued": listo para worker futuro.
- "running": ejecución activa.
- "collecting_evidence": guardando EvidenceStore.
- "completed": finalizado con evidencia válida.
- "partial": resultado incompleto.
- "failed": error real.
- "blocked": Policy, ToolHealth o integridad bloquean.
- "cancelled": usuario cancela.
- "closed": cierre seguro terminado.

### Errores de integridad

Errores exactos:

- técnica desconocida;
- contrato ausente;
- JSON inválido;
- estado no permitido;
- panel apunta a técnica inexistente;
- endpoint futuro sin contrato;
- worker ausente;
- worker no coincide con técnica;
- evidencia esperada vacía;
- herramienta bloqueada;
- aprobación ausente;
- scope ausente.

Reglas:

- marcar "FAIL" o "BLOCKED";
- no ejecutar;
- registrar AuditLog;
- LaIA puede explicar el fallo;
- Hermes Agent puede crear propuesta de reparación en laboratorio si falta contrato, parser, wrapper o panel_schema.


### Reparación controlada de integridad

“Cuando M16 detecta una incoherencia, no debe corregir producción automáticamente. LaIA explica el fallo. Hermes Agent puede crear una propuesta de reparación en laboratorio. El usuario decide si se aprueba, se rechaza o se deja pendiente.”

Contrato "integrity_repair_request":

```json
{
  "type": "integrity_repair_request",
  "repair_id": "repair-uuid",
  "check_id": "integrity-uuid",
  "trace_id": "trace-uuid",
  "module_id": "android",
  "technique_id": "android.analysis.secrets",
  "problem_type": "missing_contract",
  "description": "Falta contrato JSON documentado",
  "requested_by": "laia_mistral",
  "target_path": "modules/laboratory/integrity-repair/",
  "expected_files": [
    "README.md",
    "CONTRACT_PATCH.md",
    "PANEL_SCHEMA_PATCH.md",
    "PROMOTION_MANIFEST.json"
  ],
  "requires_approval": true,
  "status": "draft",
  "created_at": "2026-06-01T12:00:00Z"
}
```

Valores exactos de "problem_type":

"unknown_technique", "missing_contract", "invalid_json", "missing_worker_binding", "missing_expected_evidence", "panel_action_orphan", "api_route_orphan", "invalid_state", "missing_policy_gate", "missing_toolhealth".

Estados exactos:

"draft", "lab_ready", "review_required", "approved_by_user", "applied", "rejected", "archived".

Reglas de reparación:

- producción no se modifica automáticamente;
- toda reparación nace en "modules/laboratory/";
- Hermes Agent genera propuesta, no promoción directa;
- DeepSeek puede revisar arquitectura, contratos o dependencias;
- LaIA puede explicar impacto, no aprobar;
- X5 no ejecuta técnicas afectadas hasta resolver bloqueo;
- el usuario decide aplicación final;
- toda aplicación genera AuditLog;
- si la reparación afecta contratos, se registra nueva versión documental.

### Panel Ops > Integridad

Subpáginas exactas:

- Resumen
- Registry
- Contratos
- Paneles
- API futura
- Workers
- Estados
- Reparaciones
- AuditLog

Acciones visibles:

- Ejecutar revisión
- Ver fallo
- Pedir reparación a Hermes Agent
- Enviar a DeepSeek para revisión
- Aprobar reparación
- Rechazar reparación
- Archivar incidencia

### Reporte "integrity_report"

Contrato "integrity_report":

```json
{
  "type": "integrity_report",
  "report_id": "integrity-report-uuid",
  "trace_id": "trace-uuid",
  "scope": "all_modules",
  "total_checks": 120,
  "passed": 110,
  "warnings": 8,
  "failed": 2,
  "blocked": 0,
  "repair_request_ids": ["repair-uuid"],
  "created_at": "2026-06-01T12:00:00Z",
  "status": "NEEDS_REVIEW"
}
```

Estados exactos:

"PASS", "NEEDS_REVIEW", "FAILED", "BLOCKED".


## Vector 8 — Calidad de evidencia y scoring

“M16 decide si un resultado tiene valor operativo mediante calidad de evidencia, contexto, trazabilidad y scoring. Un resultado no sube score por aparecer como texto correcto: debe tener "evidence_ids", "run_id", "trace_id", técnica registrada, estado válido y calidad mínima.”

Capacidades oficiales:

- "evidence_quality_score": calcula calidad documental de la evidencia.
- "impact_proof_schema": estructura que demuestra impacto con evidencia.
- "before_after_comparison": compara estado antes/después.
- "technique_outcome_memory": historial de resultados por técnica/target.
- "noise_level": mide ruido o señales poco fiables.
- "false_positive_tracking": registra falsos positivos.
- "demo_result_guard": separa demo/simulación de ejecución real.
- "scoring_evidence_gate": bloquea scoring sin evidencia válida.

Contrato "evidence_quality_assessment":

```json
{
  "type": "evidence_quality_assessment",
  "assessment_id": "qa-uuid",
  "run_id": "run-uuid",
  "trace_id": "trace-uuid",
  "evidence_ids": ["ev-001"],
  "finding_id": "finding-uuid",
  "technique_id": "android.analysis.secrets",
  "quality": "high",
  "confidence": 0.92,
  "noise_level": "low",
  "false_positive": false,
  "demo_mode": false,
  "impact_proven": true,
  "reason": "Evidencia verificable con hash y relación directa",
  "created_at": "2026-06-01T12:00:00Z",
  "operator_id": "admin"
}
```

Valores "quality":

"none", "low", "medium", "high", "critical".

Valores "noise_level":

"none", "low", "medium", "high".

Reglas de scoring:

- sin "evidence_ids" válidos no hay subida de score;
- evidencia "none" o "corrupted" no puntúa;
- demo/simulación no puntúa como ejecución real;
- "blocked_by_policy" no penaliza técnica;
- "hardware_missing" no penaliza técnica;
- falso positivo baja score de detector/parser/clasificador;
- evidencia duplicada no sube score;
- evidencia "critical" puede subir confianza;
- LaIA explica scoring, no lo modifica sola;
- X5 actualiza score solo tras EvidenceStore.

Contrato "scoring_update_decision":

```json
{
  "type": "scoring_update_decision",
  "score_event_id": "score-uuid",
  "run_id": "run-uuid",
  "trace_id": "trace-uuid",
  "technique_id": "android.analysis.secrets",
  "target_type": "android_app",
  "score_before": 0.50,
  "score_after": 0.62,
  "score_delta": 0.12,
  "evidence_quality": "high",
  "evidence_ids": ["ev-001"],
  "false_positive": false,
  "demo_mode": false,
  "decision": "increase",
  "reason": "Resultado con evidencia válida",
  "created_at": "2026-06-01T12:00:00Z"
}
```

Valores "decision":

"increase", "decrease", "no_change", "blocked".


### Memoria de resultados de técnicas

“M16 conserva memoria documental de resultados por técnica, tipo de objetivo, herramienta, calidad de evidencia y contexto. La memoria no sustituye la aprobación del usuario ni la validación de X5: sirve para ordenar recomendaciones, detectar ruido y evitar repetir errores.”

Contrato "technique_outcome_memory":

```json
{
  "type": "technique_outcome_memory",
  "memory_id": "memory-uuid",
  "technique_id": "android.analysis.secrets",
  "module_id": "android",
  "target_type": "android_app",
  "tool_id": "apkleaks",
  "versionlock_id": "vl-uuid",
  "total_runs": 12,
  "successful_runs": 7,
  "partial_runs": 3,
  "failed_runs": 2,
  "false_positive_count": 1,
  "average_evidence_quality": "medium",
  "average_noise_level": "low",
  "last_score": 0.62,
  "last_seen_at": "2026-06-01T12:00:00Z",
  "recommended_next_action": "use_with_review"
}
```

Valores "recommended_next_action":

"use", "use_with_review", "avoid", "needs_hermes_repair", "needs_toolhealth", "manual_only".

### Nivel de ruido

Reglas:

- "none": señal limpia.
- "low": pocos datos irrelevantes.
- "medium": requiere revisión humana.
- "high": no debe subir scoring sin revisión.
- ruido alto puede activar Hermes Agent para mejorar parser, filtro o schema.

### Falsos positivos

Reglas:

- falso positivo confirmado baja score del detector, parser o clasificador;
- no borra evidencia original;
- genera evento de auditoría;
- puede crear tarea Hermes Agent de reparación;
- LaIA puede explicar por qué se considera falso positivo;
- el usuario puede marcar revisión final.

Contrato mínimo:

```json
{
  "type": "false_positive_record",
  "false_positive_id": "fp-uuid",
  "finding_id": "finding-uuid",
  "evidence_ids": ["ev-001"],
  "technique_id": "android.analysis.secrets",
  "reason": "hallazgo no reproducible",
  "confirmed_by": "admin",
  "created_at": "2026-06-01T12:00:00Z",
  "score_impact": "decrease_detector"
}
```

### Panel Ops > Calidad

Subpáginas exactas:

- Resumen
- Calidad por módulo
- Calidad por técnica
- Ruido
- Falsos positivos
- Memoria de resultados
- Recomendaciones LaIA
- Reparaciones Hermes Agent
- AuditLog

Acciones visibles:

- Ver evidencia
- Marcar falso positivo
- Pedir reparación a Hermes Agent
- Recalcular calidad
- Ver historial de técnica
- Exportar resumen enmascarado


### Panel Ops > Calidad y scoring

Subpáginas exactas:

- Resumen
- Calidad por módulo
- Calidad por técnica
- Calidad por objetivo
- Scoring
- Ruido
- Falsos positivos
- Comparaciones antes/después
- Memoria de resultados
- Reparaciones Hermes Agent
- AuditLog

Columnas obligatorias:

- "run_id"
- "trace_id"
- "module_id"
- "technique_id"
- "target_id"
- "evidence_quality"
- "noise_level"
- "false_positive"
- "demo_mode"
- "score_before"
- "score_after"
- "score_delta"
- "decision"
- "created_at"

Acciones visibles:

- Ver evidencia
- Ver comparación antes/después
- Marcar falso positivo
- Recalcular calidad
- Solicitar reparación a Hermes Agent
- Ver memoria de técnica
- Exportar resumen enmascarado

### Errores y recuperación de calidad/scoring

Errores exactos:

- evidencia inexistente;
- evidencia corrupta;
- comparación antes/después incompleta;
- calidad no calculable;
- ruido alto;
- falso positivo pendiente;
- scoring sin "evidence_ids";
- score inconsistente;
- memoria de técnica no disponible;
- exportación de resumen fallida.

Reglas:

- marcar estado visible;
- registrar AuditLog;
- no subir score;
- conservar resultado anterior;
- permitir revisión manual;
- LaIA explica causa y siguiente paso;
- Hermes Agent puede proponer reparación si falta parser, normalizador o schema.

### Cierre seguro de scoring

Reglas:

- un "score_after" nunca sustituye historial;
- todo cambio crea "scoring_update_decision";
- cada decisión conserva "score_before", "score_after" y "score_delta";
- resultados demo quedan separados;
- falsos positivos no borran evidencia;
- scoring bloqueado conserva motivo;
- informes finales muestran score y explicación.


## Vector 9 — Integridad Hermes Agent, promoción y rollback

“Hermes Agent es el constructor evolutivo de laboratorio. Puede crear parsers, wrappers, schemas, paneles, adaptadores, documentación y módulos experimentales cuando LaIA o el usuario detectan una capacidad faltante. Ninguna propuesta se integra en el arsenal controlado sin revisión, evidencias, VersionLock, ToolHealth, aprobación humana y manifiesto de promoción.”

Estados oficiales:

"experimental", "lab_ready", "review_required", "approved_by_user", "promoted", "rejected", "rolled_back", "archived".

Reglas de estado:

- "experimental": creado en "modules/laboratory/".
- "lab_ready": estructura completa y lista para revisión.
- "review_required": requiere revisión LaIA/DeepSeek/usuario.
- "approved_by_user": aprobado por usuario, aún no promovido.
- "promoted": integrado como arsenal controlado.
- "rejected": no se usa.
- "rolled_back": retirado tras promoción.
- "archived": conservado histórico.

Contrato "hermes_promotion_manifest":

```json
{
  "type": "hermes_promotion_manifest",
  "manifest_id": "promo-uuid",
  "proposal_id": "proposal-uuid",
  "technique_id": "custom.technique.id",
  "source_path": "modules/laboratory/custom.technique.id/",
  "target_path": "modules/custom/custom.technique.id/",
  "created_files": [
    "technique.json",
    "worker.py",
    "evidence_schema.json",
    "requirements.generated.txt",
    "README.md"
  ],
  "versionlock_ids": ["vl-uuid"],
  "evidence_ids": ["ev-lab-001"],
  "review_ids": ["review-001"],
  "approved_by": "admin",
  "approved_at": "2026-06-01T12:00:00Z",
  "status": "approved_by_user",
  "rollback_manifest_id": "rollback-uuid"
}
```

Contrato "hermes_rollback_manifest":

```json
{
  "type": "hermes_rollback_manifest",
  "rollback_manifest_id": "rollback-uuid",
  "manifest_id": "promo-uuid",
  "technique_id": "custom.technique.id",
  "restore_paths": [],
  "remove_paths": [],
  "reason": "user_requested",
  "created_at": "2026-06-01T12:00:00Z",
  "status": "ready"
}
```

Estados rollback:

"ready", "applied", "failed", "archived".

Reglas de promoción:

- Hermes Agent nunca promociona solo.
- DeepSeek revisa, no aprueba.
- LaIA explica impacto, no aprueba.
- usuario aprueba promoción final.
- todo requiere "PROMOTION_MANIFEST.json".
- toda promoción requiere rollback preparado.
- dependencias nuevas requieren aprobación separada.
- evidencias de laboratorio no puntúan como producción.
- X5 no ejecuta técnicas por debajo de "approved_by_user".
- "modules/custom/" solo recibe técnicas promovidas.


### Panel Ops > Hermes Agent Lab

Subpáginas exactas:

- Resumen
- Propuestas
- Laboratorio
- Revisiones
- Dependencias
- Evidencias sandbox
- Promoción
- Rollback
- Historial / AuditLog

Columnas obligatorias:

- "proposal_id"
- "technique_id"
- "status"
- "source_path"
- "target_path"
- "created_files"
- "requirements_file"
- "versionlock_ids"
- "evidence_ids"
- "review_ids"
- "approved_by"
- "last_updated_at"

Acciones visibles:

- Ver propuesta
- Ver archivos esperados
- Enviar a DeepSeek
- Marcar "review_required"
- Aprobar propuesta
- Rechazar propuesta
- Preparar promoción
- Aplicar rollback
- Archivar

### Checklist obligatorio antes de "promoted"

- [ ] "technique.json" existe.
- [ ] "worker.py" existe o "manual_required" está justificado.
- [ ] "evidence_schema.json" existe.
- [ ] "requirements.generated.txt" existe.
- [ ] "README.md" existe.
- [ ] "PROMOTION_MANIFEST.json" existe.
- [ ] "hermes_rollback_manifest" existe.
- [ ] VersionLock resuelto.
- [ ] ToolHealth válido o "manual_only".
- [ ] Evidencia sandbox asociada.
- [ ] Revisión LaIA/DeepSeek registrada.
- [ ] Usuario aprobó promoción.

### Errores y bloqueos Hermes Agent

Errores exactos:

- propuesta sin manifest;
- rollback ausente;
- dependencia no aprobada;
- evidence_schema ausente;
- worker ausente sin justificación;
- VersionLock pendiente;
- ToolHealth fallido;
- revisión DeepSeek fallida;
- evidencia sandbox ausente;
- intento de auto-promoción;
- destino fuera de "modules/custom/";
- modificación directa de producción.

Reglas:

- marcar estado "review_required", "blocked" o "rejected";
- no promocionar;
- registrar AuditLog;
- LaIA explica causa;
- Hermes Agent puede preparar reparación en laboratorio;
- usuario decide.


## Vector 10 — Readiness final y exportación externa

“M16 calcula el estado final de preparación de Ojo de Dios. No declara terminado el proyecto por intuición: revisa documentación, evidencias, IA, X5, Hermes Agent, ToolHealth, VersionLock, paneles, contratos, handoffs, scoring, errores y bloqueos.”

Estados readiness:

"READY", "READY_WITH_WARNINGS", "NEEDS_REVIEW", "BLOCKED", "INCOMPLETE".

Reglas:

- "READY": sin bloqueos críticos.
- "READY_WITH_WARNINGS": usable con advertencias.
- "NEEDS_REVIEW": requiere decisión humana.
- "BLOCKED": existe bloqueo crítico.
- "INCOMPLETE": faltan piezas documentales o contratos.

Contrato "final_readiness_report":

```json
{
  "type": "final_readiness_report",
  "report_id": "readiness-uuid",
  "trace_id": "trace-uuid",
  "scope": "all_modules",
  "status": "NEEDS_REVIEW",
  "modules_checked": ["m1", "m2", "m16"],
  "critical_blockers": [],
  "warnings": [],
  "missing_items": [],
  "evidence_summary": {},
  "toolhealth_summary": {},
  "versionlock_summary": {},
  "ai_summary": {},
  "hermes_summary": {},
  "scoring_summary": {},
  "created_at": "2026-06-01T12:00:00Z",
  "operator_id": "admin"
}
```

### Brechas y plan de cierre

Contrato "readiness_gap":

```json
{
  "type": "readiness_gap",
  "gap_id": "gap-uuid",
  "module_id": "m16",
  "area": "toolhealth",
  "severity": "high",
  "description": "Falta healthcheck validado",
  "recommended_action": "Completar validación",
  "assigned_to": "operator",
  "status": "open"
}
```

Estados:

"open", "in_progress", "resolved", "accepted_risk", "rejected".

### Separación Mano de Dios

“M16 no integra Mano de Dios internamente. Solo prepara exportación externa futura compatible con "docs/MANO_DE_DIOS_SEPARATION.md".”

### Panel Ops > Readiness

Subpáginas:

- Resumen
- Módulos
- Bloqueos
- Warnings
- Herramientas
- Evidencias
- IA
- Hermes Agent
- Scoring
- Exportación externa
- AuditLog

Acciones visibles:

- Ejecutar revisión
- Ver brecha
- Marcar riesgo aceptado
- Solicitar reparación a Hermes Agent
- Exportar informe enmascarado
- Preparar paquete externo Mano de Dios


### Paquete final de readiness

“El paquete final de M16 no es una ejecución. Es una exportación documental y verificable del estado de Ojo de Dios: módulos, evidencias, herramientas, IA, Hermes Agent, scoring, brechas, decisiones y readiness. Sirve para auditoría interna y para una exportación externa futura compatible con Mano de Dios.”

Contrato "readiness_export_package":

```json
{
  "type": "readiness_export_package",
  "package_id": "pkg-uuid",
  "readiness_report_id": "readiness-uuid",
  "trace_id": "trace-uuid",
  "scope": "all_modules",
  "included_sections": [
    "modules",
    "evidence",
    "toolhealth",
    "versionlock",
    "ai",
    "hermes",
    "scoring",
    "gaps",
    "auditlog"
  ],
  "redaction_policy": "masked_by_default",
  "package_path": "storage/reports/readiness/pkg-uuid.zip",
  "package_sha256": "sha256...",
  "created_at": "2026-06-01T12:00:00Z",
  "operator_id": "admin",
  "status": "prepared"
}
```

Estados:

"prepared", "verified", "exported", "failed", "archived".

### Contenido del paquete final

El paquete incluye:

- "final_readiness_report.json"
- "readiness_gaps.json"
- "module_status_summary.json"
- "evidence_summary.json"
- "toolhealth_summary.json"
- "versionlock_summary.json"
- "ai_status_summary.json"
- "hermes_status_summary.json"
- "scoring_summary.json"
- "auditlog_summary.json"
- "EXPORT_MANIFEST.json"

Reglas:

- todo archivo exportado tiene SHA-256;
- no se exportan secretos por defecto;
- exportación completa requiere confirmación;
- "EXPORT_MANIFEST.json" lista archivos, hashes y redacción aplicada;
- fallo de exportación no se marca como éxito.

### Criterios globales M16

- [ ] V1 LaIA/Mistral documentado.
- [ ] V2 Hermes Agent documentado.
- [ ] V3 Evidencias documentado.
- [ ] V4 Panel IAs documentado.
- [ ] V5 Health/logs documentado.
- [ ] V6 VersionLock/ToolHealth documentado.
- [ ] V7 Integridad documentado.
- [ ] V8 Calidad/scoring documentado.
- [ ] V9 Promoción/rollback Hermes documentado.
- [ ] V10 Readiness/exportación documentado.
- [ ] Mano de Dios separado documentado.
- [ ] No se afirma implementación real.

### Estado final documental

“Con Vectores 1-10 completos, M16 queda cerrado como especificación documental. La implementación real queda pendiente para rondas de programación futuras. Los BAT de IA siguen pendientes de validación operativa en Windows hasta ejecución real por el usuario.”

## 16. Nota de continuidad

El Módulo 16 queda definido como una capa en progreso de inteligencia,
evidencias y operaciones controladas de Ojo de Dios. Las partes sensibles
permanecen marcadas como `IMPLEMENTACION_USUARIO_REQUERIDA` y toda ejecución
debe pasar por X5, Policy Engine, Kill Switch, EvidenceStore y AuditLog.

## Arquitectura modular evolutiva

M16 no limita el producto a 16, 18 o 20 módulos. Los slots M17-M20 son reserva actual con nombres oficiales, no un techo final. El core debe mantenerse abierto mediante `ModuleRegistry`, `TechniqueRegistry`, `PanelRegistry` y `WorkerRegistry`; cada módulo debe poder declarar `module_registry_entry` y las superficies duplicadas deben enlazar capacidades reales con `capability_ref`. Queda prohibido hardcodear un número máximo de módulos como condición de validez del producto.
