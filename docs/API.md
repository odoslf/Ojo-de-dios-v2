# API — Ojo de Dios

## API futura Ops / Evidence

Estas rutas futuras se documentan como contrato previsto; no se implementan en
esta ronda y no declaran endpoints reales disponibles:

- "GET /api/ops/evidence"
- "GET /api/ops/evidence/{evidence_id}"
- "GET /api/ops/evidence/{evidence_id}/timeline"
- "GET /api/ops/runs/{run_id}/evidence"
- "GET /api/ops/traces/{trace_id}"
- "POST /api/ops/evidence/{evidence_id}/verify"
- "POST /api/ops/evidence/{evidence_id}/handoff"
- "POST /api/ops/evidence/export"

Reglas:

- todas requieren autenticación;
- revelar contenido completo exige permiso y AuditLog;
- "verify" valida hash y manifest;
- "handoff" usa contrato "evidence_handoff";
- "export" usa contrato "evidence_export";
- respuestas de error nunca deben fingir éxito;
- no devolver rutas absolutas del host.


## API futura Panel de IAs / Chat unificado

Estas rutas futuras se documentan como contrato previsto; no se implementan en
esta ronda, no crean endpoints reales y no permiten ejecución directa desde el
chat:

- "GET /api/ops/ai/agents"
- "GET /api/ops/ai/sessions"
- "GET /api/ops/ai/sessions/{session_id}"
- "POST /api/ops/ai/sessions"
- "POST /api/ops/ai/sessions/{session_id}/messages"
- "GET /api/ops/ai/sessions/{session_id}/messages"
- "WS /api/ops/ai/ws"

Reglas:

- todas requieren autenticación;
- cada sesión y mensaje conserva "trace_id";
- los mensajes enviados por WebSocket deben persistirse si forman parte del histórico;
- Redis Pub/Sub no es fuente de verdad ni histórico;
- el chat solo propone, explica o solicita aprobación; no ejecuta directamente.


## API futura Aprobaciones y tareas de IAs

Estas rutas futuras se documentan como contrato previsto; no se implementan en
esta ronda, no crean endpoints reales y no permiten ejecución directa desde
texto libre:

- "GET /api/ops/ai/approvals"
- "POST /api/ops/ai/approvals/{approval_id}/approve"
- "POST /api/ops/ai/approvals/{approval_id}/reject"
- "GET /api/ops/ai/hermes/tasks"
- "GET /api/ops/ai/deepseek/reviews"

Reglas:

- todas requieren autenticación;
- approve/reject genera AuditLog;
- las aprobaciones usan contrato "ai_approval_request";
- las tareas de Hermes Agent usan contrato "hermes_task_request";
- las revisiones DeepSeek usan contrato "deepseek_review_request";
- ninguna ruta futura ejecuta texto libre directamente.


## API futura Estado y ciclo de vida del chat de IAs

Estas rutas futuras se documentan como contrato previsto; no se implementan en
esta ronda, no crean endpoints reales y no permiten ejecución directa desde
texto libre:

- "GET /api/ops/ai/agents/{agent_id}"
- "GET /api/ops/ai/sessions/{session_id}/status"
- "POST /api/ops/ai/sessions/{session_id}/pause"
- "POST /api/ops/ai/sessions/{session_id}/resume"
- "POST /api/ops/ai/sessions/{session_id}/close"
- "POST /api/ops/ai/sessions/{session_id}/archive"

Reglas:

- todas requieren autenticación;
- pause, resume, close y archive generan AuditLog;
- cerrar sesión no elimina el histórico;
- archivar sesión la deja en modo solo lectura;
- los errores no deben fingir éxito.


## API futura Healthchecks Ops / IAs

Estas rutas futuras se documentan como contrato previsto; no se implementan en
esta ronda, no crean endpoints reales y no ejecutan healthchecks reales:

- "GET /api/ops/health"
- "GET /api/ops/health/ai"
- "POST /api/ops/health/ai/run"
- "GET /api/ops/health/logs"
- "GET /api/ops/health/status"

Reglas:

- todas requieren autenticación;
- las respuestas no deben exponer secretos;
- los errores no deben incluir "DEEPSEEK_API_KEY";
- el estado devuelto debe seguir el contrato "ai_healthcheck_result";
- una respuesta de error nunca debe fingir estado OK.


## API futura Health audit, componentes e incidencias

Estas rutas futuras se documentan como contrato previsto; no se implementan en
esta ronda, no crean endpoints reales ni ejecutan recuperación real:

- "GET /api/ops/health/audit-events"
- "GET /api/ops/health/components/{component}"
- "POST /api/ops/health/components/{component}/retry"
- "POST /api/ops/health/incidents/{incident_id}/ack"

Reglas:

- todas requieren autenticación;
- las respuestas no deben exponer secretos;
- retry no debe fingir disponibilidad si el componente sigue fallando;
- ack solo marca la incidencia como revisada, no corrige el fallo;
- los audit events persistidos son la referencia histórica.


## API futura VersionLock / ToolHealth

Estas rutas futuras se documentan como contrato previsto; no se implementan en
esta ronda, no crean endpoints reales ni ejecutan comprobaciones reales:

- "GET /api/ops/tools"
- "GET /api/ops/tools/{tool_id}"
- "POST /api/ops/tools/{tool_id}/healthcheck"
- "GET /api/ops/versionlock"
- "POST /api/ops/versionlock/resolve"
- "POST /api/ops/versionlock/{versionlock_id}/approve"

Reglas:

- todas requieren autenticación;
- healthcheck usa contrato "tool_health_result";
- resolve usa contrato "tool_version_lock";
- approve registra AuditLog;
- una herramienta no válida no debe fingir disponibilidad.


## API futura Inventario SBOM y cambios de versión

Estas rutas futuras se documentan como contrato previsto; no se implementan en
esta ronda, no crean endpoints reales ni modifican inventario real:

- "GET /api/ops/tools/inventory"
- "GET /api/ops/tools/inventory/{tool_id}"
- "POST /api/ops/tools/version-change"
- "POST /api/ops/tools/version-change/{change_id}/approve"
- "POST /api/ops/tools/version-change/{change_id}/rollback"

Reglas:

- todas requieren autenticación;
- inventory usa contrato "tool_inventory_item";
- version-change usa contrato "tool_version_change";
- approve y rollback generan AuditLog;
- rollback no reescribe evidencias antiguas.


## API futura Panel ToolHealth

Estas rutas futuras se documentan como contrato previsto; no se implementan en
esta ronda, no crean endpoints reales ni ejecutan acciones reales sobre
herramientas:

- "GET /api/ops/toolhealth"
- "GET /api/ops/toolhealth/{tool_id}"
- "POST /api/ops/toolhealth/{tool_id}/run"
- "POST /api/ops/toolhealth/{tool_id}/block"
- "POST /api/ops/toolhealth/{tool_id}/approve"
- "POST /api/ops/toolhealth/{tool_id}/mark-review"

Reglas:

- todas requieren autenticación;
- run usa contrato "tool_health_result";
- block, approve y mark-review generan AuditLog;
- ninguna respuesta debe fingir herramienta válida si VersionLock o ToolHealth fallan;
- estas rutas futuras no autorizan ejecución de técnicas.


## API futura Integridad de registry, contratos y estados

Estas rutas futuras se documentan como contrato previsto; no se implementan en
esta ronda, no crean endpoints reales ni ejecutan validadores reales:

- "GET /api/ops/integrity"
- "POST /api/ops/integrity/run"
- "GET /api/ops/integrity/results"
- "GET /api/ops/integrity/modules/{module_id}"
- "GET /api/ops/integrity/techniques/{technique_id}"

Reglas:

- todas requieren autenticación;
- run devuelve resultados con contrato "integrity_check_result" en implementación futura;
- una respuesta de error no debe fingir integridad correcta;
- una técnica bloqueada por integridad no debe ejecutarse por X5;
- los resultados deben preservar módulo, técnica, severidad y estado.


## Contratos API futuros por módulo

Toda ruta futura por módulo debe documentar, como mínimo, estos campos antes de
considerarse lista para implementación. Esta sección no crea endpoints reales ni
autoriza ejecución:

- "operation_id"
- "module_id"
- "request_contract"
- "response_contract"
- "auth"
- "policy_check"
- "kill_switch_check"

Reglas:

- "operation_id" debe ser único;
- "module_id" vincula la ruta con el módulo dueño;
- "request_contract" y "response_contract" deben existir documentalmente;
- "auth", "policy_check" y "kill_switch_check" no se omiten en rutas de acción;
- rutas incompletas no deben figurar como implementadas.


## API futura de reparación de integridad

Estas rutas futuras se documentan como contrato previsto; no se implementan en
esta ronda, no crean endpoints reales, no modifican producción y no aplican
reparaciones automáticamente:

- "GET /api/ops/integrity/report"
- "POST /api/ops/integrity/repair-request"
- "GET /api/ops/integrity/repairs"
- "POST /api/ops/integrity/repairs/{repair_id}/approve"
- "POST /api/ops/integrity/repairs/{repair_id}/reject"

Reglas:

- todas requieren autenticación;
- repair-request usa contrato "integrity_repair_request";
- report usa contrato "integrity_report";
- approve y reject requieren decisión explícita del usuario;
- ninguna ruta aplica cambios en producción sin aprobación final;
- toda decisión genera AuditLog.


## API futura de calidad y scoring

Estas rutas futuras se documentan como contrato previsto; no se implementan en
esta ronda, no crean endpoints reales, no calculan score y no modifican
persistencia real:

- "GET /api/ops/quality"
- "GET /api/ops/quality/modules/{module_id}"
- "GET /api/ops/quality/techniques/{technique_id}"
- "GET /api/ops/quality/runs/{run_id}"
- "POST /api/ops/quality/{assessment_id}/mark-false-positive"
- "POST /api/ops/quality/{assessment_id}/recalculate"
- "GET /api/ops/scoring"
- "GET /api/ops/scoring/techniques/{technique_id}"

Reglas:

- solo lectura no modifica score;
- marcar falso positivo requiere AuditLog;
- recalcular exige evidencia válida;
- no devolver datos sensibles completos por defecto;
- errores no devuelven éxito falso.


## API futura Hermes Agent Lab

Estas rutas futuras se documentan como contrato previsto; no se implementan en
esta ronda, no crean endpoints reales, no promocionan propuestas y no modifican
producción:

- "GET /api/ops/hermes/proposals"
- "GET /api/ops/hermes/proposals/{proposal_id}"
- "POST /api/ops/hermes/proposals/{proposal_id}/review"
- "POST /api/ops/hermes/proposals/{proposal_id}/approve"
- "POST /api/ops/hermes/proposals/{proposal_id}/reject"
- "POST /api/ops/hermes/proposals/{proposal_id}/prepare-promotion"
- "POST /api/ops/hermes/proposals/{proposal_id}/rollback"
- "GET /api/ops/hermes/audit"

Reglas API:

- aprobar requiere usuario autorizado;
- ninguna ruta promociona sin manifest;
- rollback requiere "rollback_manifest_id";
- respuestas no deben ocultar bloqueos;
- no devolver claves ni secretos.


## API futura de readiness final

Estas rutas futuras se documentan como contrato previsto; no se implementan en
esta ronda, no crean endpoints reales, no calculan readiness real y no preparan
paquetes externos reales:

- "GET /api/ops/readiness"
- "POST /api/ops/readiness/run"
- "GET /api/ops/readiness/gaps"
- "POST /api/ops/readiness/gaps/{gap_id}/resolve"
- "POST /api/ops/readiness/export"

Reglas:

- run usa contrato "final_readiness_report" en implementación futura;
- gaps usa contrato "readiness_gap";
- export no integra Mano de Dios internamente;
- errores no devuelven éxito falso;
- toda acción genera AuditLog.


## API futura de paquetes readiness

Estas rutas futuras se documentan como contrato previsto; no se implementan en
esta ronda, no crean endpoints reales, no verifican paquetes reales y no
archivan artefactos reales:

- "GET /api/ops/readiness/export/{package_id}"
- "POST /api/ops/readiness/export/{package_id}/verify"
- "POST /api/ops/readiness/export/{package_id}/archive"

Reglas:

- verify usa hashes y "EXPORT_MANIFEST.json" en implementación futura;
- archive conserva AuditLog;
- ninguna ruta expone secretos por defecto;
- errores no devuelven éxito falso.
